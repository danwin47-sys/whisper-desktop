# Whisper Desktop 桌面語音轉錄工具

一個基於 [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) 的桌面語音轉錄應用程式，支援即時轉錄與批次檔案處理。

## 功能特色

### 🎤 即時轉錄

- 即時捕捉系統音訊或麥克風輸入
- 浮動字幕視窗，方便觀看
- 支援 VAD (Voice Activity Detection) 提升準確度

### 📁 批次檔案轉錄

- 支援多檔案批次處理
- 自動生成 SRT 字幕檔
- 轉錄時間預估與統計

### ⚙️ 彈性配置

- 可選擇不同 Whisper 模型 (tiny, base, small, medium, large)
- 調整 VAD 參數
- 自訂語言與任務類型

### 🎨 現代化 UI

- 簡潔直觀的操作介面
- 支援深色模式
- 按鈕 Hover 視覺反饋

## 系統需求

- **作業系統**: Windows 10/11, macOS, Linux
- **Python**: 3.8 或以上版本
- **記憶體**: 建議 8GB 以上 (取決於使用的模型)
- **GPU** (選用): NVIDIA GPU 可大幅提升轉錄速度

## 安裝步驟

### 1. 克隆專案

```bash
git clone https://github.com/danwin47-sys/whisper-desktop.git
cd whisper-desktop
```

### 2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

**requirements.txt 內容：**

```
faster-whisper
PyQt5
pyaudio
onnxruntime
```

### 3. (選用) GPU 加速

如果您有 NVIDIA GPU，可安裝 CUDA 版本以加速：

```bash
pip install onnxruntime-gpu
```

## 使用說明

### 啟動應用程式

```bash
python main.py
```

### 即時轉錄

1. 選擇 **「即時轉錄」** 分頁
2. 選擇音訊來源 (系統音訊/麥克風)
3. 選擇 Whisper 模型 (建議從 `small` 開始)
4. 點擊 **「▶ 開始即時轉錄」** 或按 `F2`
5. 勾選 **「浮動字幕視窗」** 可顯示即時字幕

### 檔案轉錄

1. 選擇 **「檔案轉錄」** 分頁
2. 點擊 **「加入檔案」** 選擇音訊/影片檔案
3. 選擇 Whisper 模型
4. 點擊 **「開始批次轉錄」**
5. 完成後會在原檔案目錄生成 `.srt` 字幕檔

### 支援的檔案格式

- 音訊: `.mp3`, `.wav`, `.m4a`, `.flac`
- 影片: `.mp4`, `.avi`, `.mkv`, `.mov`

## 配置說明

### Whisper 模型選擇

| 模型 | 記憶體需求 | 速度 | 準確度 |
|------|-----------|------|--------|
| tiny | ~1GB | 極快 | ⭐⭐ |
| base | ~1GB | 快 | ⭐⭐⭐ |
| small | ~2GB | 中等 | ⭐⭐⭐⭐ |
| medium | ~5GB | 慢 | ⭐⭐⭐⭐⭐ |
| large | ~10GB | 很慢 | ⭐⭐⭐⭐⭐ |

**建議**：

- 即時轉錄：使用 `small` 或 `base`
- 檔案轉錄：使用 `medium` 或 `large` (如硬體允許)

### VAD 參數

- **啟用 VAD**: 可減少雜音影響，提升準確度
- **最小靜音時長**: 調整語句分割敏感度 (預設 2000ms)

## 專案結構

```
whisper-desktop/
├── main.py                 # 主程式 (GUI)
├── workers.py              # 轉錄工作執行緒
├── config.py               # 配置管理
├── constants.py            # 常量定義
├── exceptions.py           # 自定義異常
├── utils.py                # 工具函數
├── ui/
│   ├── __init__.py
│   └── overlay.py          # 浮動字幕視窗
├── requirements.txt        # 依賴列表
└── README.md              # 本文件
```

## 常見問題

### Q: 轉錄速度很慢怎麼辦？

A:

1. 嘗試使用較小的模型 (如 `small` 或 `base`)
2. 如有 NVIDIA GPU，安裝 `onnxruntime-gpu`
3. 確保系統資源充足

### Q: 字幕檔在哪裡？

A: 與原始音訊/影片檔案同目錄，檔名相同但副檔名為 `.srt`

### Q: 支援哪些語言？

A: Whisper 模型支援 99 種語言，包含繁體中文、英文、日文等

### Q: 即時轉錄延遲很高？

A:

1. 降低模型大小
2. 調整 VAD 參數
3. 確保音訊驅動程式為最新版本

## 技術細節

### 架構設計

- **GUI 框架**: PyQt5
- **轉錄引擎**: Faster-Whisper (基於 CTranslate2)
- **VAD**: Silero VAD
- **多執行緒**: QThread 避免 UI 凍結

### 優化特色

- 使用 VAD 過濾靜音片段
- 批次處理減少 API 呼叫
- 記憶體管理優化
- 轉錄統計與日誌記錄

## 授權

本專案採用 MIT 授權條款。

## 貢獻

歡迎提交 Issue 或 Pull Request！

## 致謝

- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Silero VAD](https://github.com/snakers4/silero-vad)
