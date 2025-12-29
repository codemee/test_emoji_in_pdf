#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用 FPDF2 生成 PDF（支援彩色 emoji）"""

import sys
import os
from fpdf import FPDF


def get_text_input():
    """接收使用者輸入的文字（支援多行）"""
    # 檢查命令列參數（優先於測試模式）
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"從檔案讀取輸入文字：{input_file}")
            print(f"檔案內容長度：{len(content)} 字元")
            return content
        except FileNotFoundError:
            print(f"錯誤：找不到檔案 '{input_file}'")
            print("將使用預設輸入模式...")
        except Exception as e:
            print(f"錯誤：讀取檔案失敗：{e}")
            print("將使用預設輸入模式...")

    # 檢查是否處於測試模式
    if os.environ.get('TEST_MODE') == '1':
        return "測試 emoji 😀🌟🚶‍♀️👨‍👩‍👧‍👦 中文測試"

    print("請輸入要放入 PDF 的文字（輸入完成後按兩次 Enter 結束）：")
    print("（或按 Ctrl+Z + Enter (Windows) / Ctrl+D (Linux/Mac) 結束）")
    print("提示：您也可以使用命令列參數指定文字檔案，例如：python main.py input.txt")
    print()

    lines = []
    empty_line_count = 0

    try:
        while True:
            line = input()
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2 and lines:
                    break
                elif lines:
                    lines.append("")
                    empty_line_count = 0
            else:
                empty_line_count = 0
                lines.append(line)
    except EOFError:
        pass

    return "\n".join(lines)


def get_filename():
    """詢問並取得檔案名稱"""
    # 檢查是否處於測試模式
    if os.environ.get('TEST_MODE') == '1':
        return "test_main_fpdf2.pdf"

    filename = input("請輸入 PDF 檔案名稱（不含副檔名，預設為 output_fpdf2）: ").strip()

    if not filename:
        filename = "output_fpdf2"

    if not filename.endswith(".pdf"):
        filename += ".pdf"

    return filename


def register_fonts(pdf):
    """註冊字體"""
    fonts_registered = {}

    # 嘗試註冊中文字體（優先，因為更重要）
    chinese_paths = [
        (os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "msjh.ttc"), "msjh"),  # 微軟正黑體 TTC
        (os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "kaiu.ttf"), "kaiu"),  # 標楷體 TTF
        (os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "mingliu.ttc"), "mingliu"),  # 細明體 TTC
    ]

    for path, font_name in chinese_paths:
        if os.path.exists(path):
            try:
                # FPDF2 支持 TTC 文件
                pdf.add_font(font_name, fname=path)
                fonts_registered['main'] = font_name
                print(f"[OK] 成功註冊字體: {os.path.basename(path)}")
                break
            except Exception as e:
                print(f"  嘗試註冊 {os.path.basename(path)} 失敗: {e}")

    # 優先嘗試註冊 Noto Color Emoji 字體（支援彩色 emoji）
    emoji_font_path = "NotoColorEmoji_WindowsCompatible.ttf"
    if os.path.exists(emoji_font_path):
        try:
            pdf.add_font("NotoColorEmoji", fname=emoji_font_path)
            fonts_registered['emoji'] = "NotoColorEmoji"
            print(f"[OK] 成功註冊彩色 emoji 字體: {emoji_font_path}")
        except Exception as e:
            print(f"  註冊 Noto Color Emoji 字體失敗: {e}")

    # 如果 Noto Color Emoji 字體失敗，嘗試系統的 Segoe UI Emoji 作為備用
    if 'emoji' not in fonts_registered:
        emoji_font_paths = [
            (os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "seguiemj.ttf"), "SegoeUIEmoji"),  # Segoe UI Emoji
            (os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "seguisym.ttf"), "SegoeUISymbol"),  # Segoe UI Symbol (備用)
        ]

        for emoji_path, font_name in emoji_font_paths:
            if os.path.exists(emoji_path):
                try:
                    pdf.add_font(font_name, fname=emoji_path)
                    fonts_registered['emoji'] = font_name
                    print(f"[OK] 使用備用 emoji 字體: {os.path.basename(emoji_path)}")
                    break
                except Exception as e:
                    print(f"  註冊 {os.path.basename(emoji_path)} 失敗: {e}")

    if 'emoji' not in fonts_registered:
        print(f"[WARN] 找不到 emoji 字體檔案")

    # 如果中文字體也註冊失敗，使用內建字體
    if 'main' not in fonts_registered:
        print("[WARN] 無法註冊中文字體，使用內建 Helvetica（中文可能無法顯示）")
        fonts_registered['main'] = 'Helvetica'

    return fonts_registered


def create_pdf_fpdf2(text, filename):
    """使用 FPDF2 創建 PDF"""
    print("\n開始生成 PDF...")

    # 創建 PDF 物件
    pdf = FPDF()
    pdf.add_page()

    # 註冊字體
    fonts = register_fonts(pdf)

    # 設定參數
    margin = 20  # 邊距（mm）
    font_size = 12
    line_height = 6  # 行高（mm）
    y_position = margin

    # 使用註冊的字體
    current_font = fonts.get('main', 'Helvetica')
    emoji_font = fonts.get('emoji')
    print(f"[INFO] 使用主要字體: {current_font}")
    if emoji_font:
        print(f"[INFO] 使用 emoji 字體: {emoji_font}")

    pdf.set_font(current_font, size=font_size)

    # 處理文字
    lines = text.split('\n')

    for line in lines:
        # 檢查是否需要新頁面
        if y_position > 297 - margin - line_height:  # A4 高度約 297mm
            pdf.add_page()
            pdf.set_font(current_font, size=font_size)
            y_position = margin

        # 空行也要處理（保持間距）
        if not line.strip():
            y_position += line_height
            continue

        # 逐字元處理：emoji 用 emoji 字體，其他字元用主要字體
        def is_emoji(char):
            """檢查單個字元是否為 emoji"""
            code = ord(char)
            return (
                # 表情符號及相關
                0x1F600 <= code <= 0x1F64F or  # 表情符號
                0x1F300 <= code <= 0x1F5FF or  # 符號 & 圖片
                0x1F680 <= code <= 0x1F6FF or  # 交通 & 地圖
                0x1F1E6 <= code <= 0x1F1FF or  # 國旗
                # 擴展範圍
                0x2600 <= code <= 0x26FF or    # 雜項符號 (星星、氣象等)
                0x2700 <= code <= 0x27BF or    # 裝飾符號
                0x2B00 <= code <= 0x2BFF or    # 更多符號
                # 愛心及表情修飾符
                0x2764 <= code <= 0x2764 or    # 愛心
                0x1F90C <= code <= 0x1F93A or  # 手勢
                0x1F3FB <= code <= 0x1F3FF or  # 膚色修飾符
                # 組合字元 (用於複合表情符號)
                code == 0x200D or              # ZWJ (零寬連接符)
                code == 0xFE0F or              # VS-16 (emoji 樣式選擇器)
                code == 0xFE0E                 # VS-15 (文字樣式選擇器)
            )

        # 將一行文字拆分成連續的相同類型字元組
        segments = []
        current_segment = ""
        current_is_emoji = None

        for char in line:
            char_is_emoji = is_emoji(char)

            # 輸出字元對照字碼資訊
            char_code = ord(char)
            char_type = "表情符號" if char_is_emoji else "一般字元"
            try:
                # 嘗試正常輸出
                print(f"字元: '{char}' | 字碼: {char_code} (0x{char_code:04X}) | 類型: {char_type}")
            except UnicodeEncodeError:
                # 如果無法顯示字元，用 Unicode 表示方式輸出
                print(f"字元: U+{char_code:04X} | 字碼: {char_code} (0x{char_code:04X}) | 類型: {char_type}")

            # 如果當前段落類型改變，開始新段落
            if current_is_emoji != char_is_emoji:
                if current_segment:
                    segments.append((current_segment, current_is_emoji))
                current_segment = char
                current_is_emoji = char_is_emoji
            else:
                current_segment += char

        # 添加最後一段
        if current_segment:
            segments.append((current_segment, current_is_emoji))

        # 繪製每一段文字
        try:
            pdf.set_xy(margin, y_position)

            for segment_text, segment_is_emoji in segments:
                if segment_is_emoji and emoji_font:
                    pdf.set_font(emoji_font, size=font_size)
                else:
                    pdf.set_font(current_font, size=font_size)

                # 計算這段文字的寬度
                segment_width = pdf.get_string_width(segment_text)
                pdf.cell(segment_width, line_height, segment_text, align='L')

            # 換行
            y_position += line_height
        except Exception as e:
            # 如果繪製失敗，記錄錯誤並跳過
            print(f"[WARN] 無法繪製行: {line[:30]}... 錯誤: {str(e)[:50]}")
            y_position += line_height

    # 儲存 PDF
    pdf.output(filename)

    print(f"\n[OK] PDF 檔案已成功建立：{filename}")
    print(f"[OK] 使用主要字體：{current_font}")
    if emoji_font:
        print(f"[OK] 支援彩色 emoji：{emoji_font}")
    else:
        print("[WARN] 未找到 emoji 字體，emoji 可能無法正確顯示")

    if current_font == 'Helvetica':
        print("\n[WARN] 使用預設字體，中文可能無法顯示")

    print("\n注意：")
    print("  - FPDF2 支援彩色字體格式")
    print("  - Emoji 應該能以彩色正確顯示")
    print("  - 使用系統的 Segoe UI Emoji 字體 (seguiemj.ttf)")
    print("  - 如果 emoji 顯示不正常，系統會自動嘗試備用字體")


def main():
    """主程式"""
    print("=" * 60)
    print("PDF 生成器 (FPDF2 - 支援彩色 Emoji)")
    print("=" * 60)
    print()
    print("使用方法：")
    print("  手動輸入：python main.py")
    print("  檔案輸入：python main.py <文字檔案>")
    print("  測試模式：TEST_MODE=1 python main.py")
    print()

    # 接收輸入文字
    text = get_text_input()

    if not text.strip():
        print("錯誤：未輸入任何文字！")
        sys.exit(1)

    # 取得檔案名稱
    filename = get_filename()

    # 檢查檔案是否存在
    if os.path.exists(filename):
        if os.environ.get('TEST_MODE') != '1':
            response = input(f"檔案 {filename} 已存在，是否要覆蓋？(y/n，預設為 y): ").strip().lower()
            if response != '' and response != 'y':
                print("操作已取消。")
                sys.exit(0)
        # 測試模式下自動覆蓋

    # 創建 PDF
    try:
        create_pdf_fpdf2(text, filename)
    except Exception as e:
        print(f"錯誤：無法建立 PDF 檔案：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
