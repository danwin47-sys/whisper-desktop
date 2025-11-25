# coding: utf-8
"""
配置模組
整合所有配置項，包含基礎配置和進階優化配置
支援從 whisper_settings.json 載入使用者自訂配置
"""
import os
import json
from detect_device import get_optimal_device, get_device_info


def _load_user_settings():
    """載入使用者配置（如果存在）"""
    settings_file = "whisper_settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                print(f"✅ 已載入使用者配置: {settings_file}")
                return settings
        except Exception as e:
            print(f"⚠️ 載入配置失敗: {e}，使用預設值")
    return {}


class Config:
    """Whisper 應用程式配置"""
    
    # 載入使用者自訂配置
    _user_settings = _load_user_settings()
    
    # === 裝置配置 ===
    # 自動偵測最佳運算裝置
    DEVICE, COMPUTE_TYPE, DEVICE_NAME = get_optimal_device()
    
    # === 基礎設定 ===
    MODEL_SIZE = _user_settings.get("model_size", "tiny")
    SAMPLE_RATE = 16000
    CHANNELS = 1
    
    # === 效能設定 ===
    BEAM_SIZE = _user_settings.get("beam_size", 1)  # 預設使用最快速度 (1), 可選 3 或 5 以提升準確度
    BATCH_SIZE = _user_settings.get("batch_size", 16)  # 批次處理大小，提升多檔案處理效能
    CONDITION_ON_PREVIOUS_TEXT = _user_settings.get("condition_on_previous_text", False)  # 停用上下文依賴以加速長音訊處理
    
    # === 語音設定 ===
    LANGUAGE = _user_settings.get("language", "zh")  # 預設繁體中文
    # Temperature 必須至少為 0.1，否則 faster-whisper 可能不會產生 clip_timestamps 導致轉錄失敗
    TEMPERATURE = max(0.1, _user_settings.get("temperature", 0.2))  # 確保至少為 0.1
    TASK = "transcribe"  # transcribe or translate
    INITIAL_PROMPT = "繁體中文"
    
    # === VAD 設定 (語音活動偵測) ===
    VAD_ENABLED = _user_settings.get("vad_enabled", False)  # 預設停用 VAD，確保完整轉錄所有音訊
    VAD_MIN_SILENCE_MS = _user_settings.get("vad_min_silence_ms", 300)  # 靜音片段最小持續時間
    VAD_THRESHOLD = _user_settings.get("vad_threshold", 0.5)  # VAD 敏感度 (0.0-1.0)
    VAD_MIN_SPEECH_MS = _user_settings.get("vad_min_speech_ms", 250)  # 語音片段最小持續時間
    VAD_SPEECH_PAD_MS = _user_settings.get("vad_speech_pad_ms", 400)  # 語音片段前後填充時間
    
    # === 即時轉錄設定 ===
    SILENCE_THRESHOLD = 0.01
    SILENCE_DURATION = 1.0
    TRANSCRIBE_INTERVAL = 0.5
    LOG_FILE = "transcription_log.txt"
    
    # === 模型選項 ===
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"]
    AVAILABLE_LANGUAGES = {
        "自動偵測 (Auto)": None,
        "繁體中文 (Chinese)": "zh",
        "英文 (English)": "en",
        "日文 (Japanese)": "ja",
        "韓文 (Korean)": "ko",
        "西班牙文 (Spanish)": "es",
        "法文 (French)": "fr",
        "德文 (German)": "de"
    }
    
    @classmethod
    def get_vad_parameters(cls):
        """
        取得完整的 VAD 參數字典
        
        Returns:
            dict: VAD 參數字典
        """
        return {
            "min_silence_duration_ms": cls.VAD_MIN_SILENCE_MS,
            "threshold": cls.VAD_THRESHOLD,
            "min_speech_duration_ms": cls.VAD_MIN_SPEECH_MS,
            "max_speech_duration_s": float('inf'),
            "speech_pad_ms": cls.VAD_SPEECH_PAD_MS
        }
    
    @classmethod
    def get_device_info_dict(cls):
        """取得裝置資訊"""
        return get_device_info()
    
    @classmethod
    def print_config(cls):
        """印出當前配置"""
        print("=" * 60)
        print("Whisper 配置資訊")
        print("=" * 60)
        print(f"運算裝置: {cls.DEVICE_NAME}")
        print(f"計算類型: {cls.COMPUTE_TYPE}")
        print(f"模型大小: {cls.MODEL_SIZE}")
        print(f"Beam Size: {cls.BEAM_SIZE}")
        print(f"批次大小: {cls.BATCH_SIZE}")
        print(f"VAD 啟用: {cls.VAD_ENABLED}")
        if cls.VAD_ENABLED:
            print(f"VAD 參數: {cls.get_vad_parameters()}")
        print("=" * 60)
