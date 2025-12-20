import fitz  # PyMuPDF
import sys
import os
import platform

try:
    import pymupdf_fonts
    EMOJI_FONT_AVAILABLE = True
except ImportError:
    EMOJI_FONT_AVAILABLE = False


def get_text_input():
    """接收使用者輸入的文字（支援多行）"""
    print("請輸入要放入 PDF 的文字（輸入完成後按兩次 Enter 結束）：")
    print("（或按 Ctrl+Z + Enter (Windows) / Ctrl+D (Linux/Mac) 結束）")
    print()
    
    lines = []
    empty_line_count = 0
    
    try:
        while True:
            line = input()
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2 and lines:
                    # 連續兩個空行，結束輸入
                    break
                elif lines:
                    # 單個空行，加入空行到內容中
                    lines.append("")
                    empty_line_count = 0
            else:
                empty_line_count = 0
                lines.append(line)
    except EOFError:
        # Ctrl+Z (Windows) 或 Ctrl+D (Unix) 被按下
        pass
    
    return "\n".join(lines)


def get_filename():
    """詢問並取得檔案名稱"""
    filename = input("請輸入 PDF 檔案名稱（不含副檔名，預設為 output）: ").strip()
    
    if not filename:
        filename = "output"
    
    # 確保副檔名是 .pdf
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    
    return filename


def find_windows_font_file(font_name):
    """在 Windows 系統中查找字體文件"""
    if platform.system() != "Windows":
        return None
    
    # Windows 字體目錄
    font_dirs = [
        os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
    ]
    
    # 可能的字體文件名（Segoe UI Emoji）
    possible_names = [
        "seguiemj.ttf",  # Segoe UI Emoji
        "seguiemj.ttc",
        "segoeuiemoji.ttf",
    ]
    
    for font_dir in font_dirs:
        if not os.path.exists(font_dir):
            continue
        for name in possible_names:
            font_path = os.path.join(font_dir, name)
            if os.path.exists(font_path):
                return font_path
    
    return None


def get_emoji_font():
    """取得支援 emoji 的字體"""
    # 優先使用 pymupdf-fonts 中的 NotoColorEmoji
    if EMOJI_FONT_AVAILABLE:
        try:
            # pymupdf-fonts 提供字體物件，可以直接使用
            return pymupdf_fonts.NotoColorEmoji
        except AttributeError:
            pass
    
    # 嘗試使用 Windows 內建的 Segoe UI Emoji
    if platform.system() == "Windows":
        font_path = find_windows_font_file("Segoe UI Emoji")
        if font_path:
            return font_path
    
    # 如果都不可用，返回 None 使用預設字體
    return None


def create_pdf(text, filename):
    """使用 PyMuPDF 創建 PDF 檔案"""
    # 創建新的 PDF 文件
    doc = fitz.open()
    
    # 添加一個頁面（A4 大小）
    page = doc.new_page(width=595, height=842)  # A4 尺寸（點數）
    
    # 設定文字格式
    font_size = 12
    margin = 50
    line_height = font_size * 1.5  # 行高
    
    # 取得支援 emoji 的字體
    emoji_font_source = get_emoji_font()
    
    # 準備 insert_text 的參數
    text_params = {
        "fontsize": font_size,
        "color": (0, 0, 0),
    }
    
    # 載入字體
    font_obj = None
    font_name_used = None
    if emoji_font_source:
        # 如果是字體文件路徑，使用 fitz.Font 載入字體
        if isinstance(emoji_font_source, str) and os.path.exists(emoji_font_source):
            try:
                # 載入字體文件
                font_obj = fitz.Font(fontfile=emoji_font_source)
                # 嘗試使用字體對象的 name 屬性，如果包含空格則使用簡短名稱
                font_name = font_obj.name
                # 如果字體名稱包含空格，使用簡短名稱並將字體嵌入頁面
                if ' ' in font_name:
                    # 使用簡短名稱
                    font_name_short = "emoji_font"
                    # 將字體嵌入頁面
                    page.insert_font(fontname=font_name_short, fontfile=emoji_font_source)
                    text_params["fontname"] = font_name_short
                    font_name_used = "Segoe UI Emoji"
                else:
                    text_params["fontname"] = font_name
                    font_name_used = font_name
            except Exception as e:
                print(f"警告：無法載入字體文件 {emoji_font_source}：{e}")
                font_obj = None
        else:
            # pymupdf-fonts 提供的字體物件可以直接使用
            text_params["fontname"] = emoji_font_source
            font_name_used = "NotoColorEmoji"
    
    # 計算可用區域
    text_rect = fitz.Rect(margin, margin, page.rect.width - margin, page.rect.height - margin)
    max_width = text_rect.width
    
    # 分割文字為行
    lines = text.split('\n')
    
    # 當前位置
    x = text_rect.x0
    y = text_rect.y0 + font_size
    
    # 逐行插入文字
    for line in lines:
        if not line.strip():
            # 空行，只換行
            y += line_height
        else:
            # 處理長行自動換行
            words = line.split(' ')
            current_line = ""
            
            for word in words:
                # 測試添加這個字後是否超出寬度
                test_line = current_line + (" " if current_line else "") + word
                
                # 估算文字寬度
                # 對於 emoji，寬度可能更大，使用更寬鬆的估算
                text_width = len(test_line) * font_size * 0.7
                
                if text_width > max_width and current_line:
                    # 當前行已滿，先寫入當前行
                    page.insert_text(
                        (x, y),
                        current_line,
                        **text_params
                    )
                    y += line_height
                    current_line = word
                    
                    # 檢查是否需要新頁面
                    if y + line_height > text_rect.y1:
                        page = doc.new_page(width=595, height=842)
                        # 在新頁面上也嵌入字體（如果需要）
                        if font_obj and isinstance(emoji_font_source, str) and os.path.exists(emoji_font_source):
                            try:
                                font_name_short = "emoji_font"
                                page.insert_font(fontname=font_name_short, fontfile=emoji_font_source)
                            except:
                                pass
                        text_rect = fitz.Rect(margin, margin, page.rect.width - margin, page.rect.height - margin)
                        max_width = text_rect.width
                        y = text_rect.y0 + font_size
                else:
                    current_line = test_line
            
            # 寫入剩餘的文字
            if current_line:
                page.insert_text(
                    (x, y),
                    current_line,
                    **text_params
                )
                y += line_height
                
                # 檢查是否需要新頁面
                if y + line_height > text_rect.y1:
                    page = doc.new_page(width=595, height=842)
                    # 在新頁面上也嵌入字體（如果需要）
                    if font_obj and isinstance(emoji_font_source, str) and os.path.exists(emoji_font_source):
                        try:
                            font_name_short = "emoji_font"
                            page.insert_font(fontname=font_name_short, fontfile=emoji_font_source)
                        except:
                            pass
                    text_rect = fitz.Rect(margin, margin, page.rect.width - margin, page.rect.height - margin)
                    max_width = text_rect.width
                    y = text_rect.y0 + font_size
    
    # 儲存 PDF
    doc.save(filename)
    doc.close()
    
    if font_name_used:
        if isinstance(emoji_font_source, str) and emoji_font_source.endswith(('.ttf', '.ttc')):
            font_info = f"（使用字體：Segoe UI Emoji）"
        else:
            font_info = f"（使用字體：NotoColorEmoji）"
    else:
        font_info = "（使用預設字體，可能不支援 emoji）"
    print(f"\nPDF 檔案已成功建立：{filename} {font_info}")


def main():
    """主程式"""
    print("=" * 50)
    print("PDF 生成器")
    print("=" * 50)
    
    # 接收輸入文字
    text = get_text_input()
    
    if not text.strip():
        print("錯誤：未輸入任何文字！")
        sys.exit(1)
    
    # 取得檔案名稱
    filename = get_filename()
    
    # 檢查檔案是否存在
    if os.path.exists(filename):
        response = input(f"檔案 {filename} 已存在，是否要覆蓋？(y/n，預設為 y): ").strip().lower()
        if response != '' and response != 'y':
            print("操作已取消。")
            sys.exit(0)
    
    # 創建 PDF
    try:
        create_pdf(text, filename)
    except Exception as e:
        print(f"錯誤：無法建立 PDF 檔案：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
