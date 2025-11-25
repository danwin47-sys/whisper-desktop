# coding: utf-8
"""
常量模組
集中管理應用程式中的魔法數字和字串常量
"""

# === UI 相關常量 ===
DEFAULT_WINDOW_WIDTH = 600
DEFAULT_WINDOW_HEIGHT = 500
OVERLAY_WIDTH = 800
OVERLAY_HEIGHT = 200
OVERLAY_BOTTOM_MARGIN = 250

# 字型設定
SUBTITLE_FONT_SIZE = 24
SUBTITLE_FONT_FAMILY = "Microsoft JhengHei"

# 自動清除延遲（毫秒）
AUTO_CLEAR_DELAY = 8000

# === 檔案格式 ===
SUPPORTED_AUDIO_FORMATS = ('.mp3', '.mp4', '.wav', '.m4a', '.mkv')
AUDIO_FILTER_STRING = "音訊/影片 (*.mp3 *.mp4 *.wav *.m4a *.mkv)"

# === 日誌檔案 ===
ERROR_LOG_FILE = "error_log.txt"
TRANSCRIPTION_STATS_FILE = "transcription_stats.csv"
TRANSCRIPTION_LOG_FILE = "transcription_log.txt"

# === UI 樣式 ===
PRIMARY_BUTTON_STYLE = "background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;"
SECONDARY_BUTTON_STYLE = "background-color: #2196F3; color: white; font-size: 16px; padding: 10px;"
DANGER_BUTTON_STYLE = "background-color: #F44336; color: white; font-size: 16px; padding: 10px;"
INFO_LABEL_STYLE = "background-color: #E3F2FD; padding: 8px; border-radius: 4px; font-weight: bold;"
SUBTITLE_STYLE = "color: white; background-color: rgba(0, 0, 0, 160); border-radius: 12px; padding: 12px;"

# === 音訊處理 ===
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1
AUDIO_SLEEP_INTERVAL = 0.05  # 秒

# === 片段切分參數 ===
MIN_SEGMENT_DURATION = 2.0  # 秒
MAX_SEGMENT_DURATION = 8.0  # 秒
PAUSE_PUNCTUATION = ('，', '。', '？', '！', ',', '.', '?', '!')
