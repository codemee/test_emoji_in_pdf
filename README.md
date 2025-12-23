# PDF 生成器

將文字轉換為 PDF 文件的工具集。

## 📦 安裝依賴

```bash
uv sync
```

## 🚀 使用方法

本專案提供三種 PDF 生成方案：

### 1. **main_html.py** - HTML 方案 ⭐ 推薦

**最佳選擇！完美支援彩色 emoji。**

```bash
uv run python main_html.py
```

**特點：**
- ✅ 完美的彩色 emoji 顯示
- ✅ 簡單易用
- ✅ 可在瀏覽器中轉為 PDF
- ✅ 檔案小、速度快

**使用步驟：**
1. 運行程序，輸入文字
2. 生成 HTML 文件
3. 瀏覽器打開 HTML
4. 點擊「儲存為 PDF」按鈕
5. 選擇「Microsoft Print to PDF」或「另存為 PDF」

### 2. **main.py** - PyMuPDF 方案

**適合接受黑白 emoji 的情況。**

```bash
uv run python main.py
```

**特點：**
- ✅ 直接生成 PDF
- ✅ 功能完整、速度快
- ⚠️ Emoji 顯示為黑白輪廓

### 3. **main_reportlab.py** - ReportLab 方案

**實驗性方案。**

```bash
uv run python main_reportlab.py
```

**特點：**
- ✅ 直接生成 PDF
- ⚠️ Emoji 可能無法正確顯示

## 📝 Emoji 支援說明

### 為什麼 PDF 中的 emoji 是黑白的？

**技術原因：**
- PyMuPDF 和 ReportLab 都不支援**彩色字體格式**
- 彩色字體格式包括：CBDT/CBLC、COLR/CPAL、SVG
- 這些庫只能渲染字體的**輪廓**，無法渲染內建的彩色資訊

**解決方案：**
- 使用 `main_html.py` 生成 HTML，再轉為 PDF
- HTML 完美支援彩色 emoji

### 字體文件

專案包含兩個 Noto Color Emoji 字體：
- `NotoColorEmoji_WindowsCompatible.ttf` - Windows 兼容版本
- `NotoColorEmoji.ttf` - 標準版本

## 🎨 功能比較

| 功能 | main_html.py | main.py | main_reportlab.py |
|------|-------------|---------|-------------------|
| 彩色 emoji | ✅ 完美支援 | ❌ 黑白輪廓 | ❌ 不顯示 |
| 中文支援 | ✅ | ✅ | ✅ |
| 直接生成 PDF | ❌ 需轉換 | ✅ | ✅ |
| 檔案大小 | 小 | 中 | 中 |
| 使用難度 | 簡單 | 簡單 | 簡單 |
| **推薦度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

## 💡 建議

- **需要彩色 emoji** → 使用 `main_html.py`
- **接受黑白 emoji** → 使用 `main.py`
- **不在意 emoji** → 使用 `main.py` 或 `main_reportlab.py`

## 🔧 依賴套件

- `pymupdf` - PDF 生成（main.py）
- `reportlab` - PDF 生成（main_reportlab.py）
- `pillow` - 圖片處理
- `pymupdf-fonts` - 字體支援

## 📄 授權

本專案使用的 Noto Color Emoji 字體由 Google 提供，採用 SIL Open Font License。

