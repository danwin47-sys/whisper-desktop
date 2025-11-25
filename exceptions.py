# coding: utf-8
"""
自定義異常模組
定義應用程式專用的異常類別，提供更清晰的錯誤語意
"""


class WhisperBaseException(Exception):
    """Whisper 應用程式基礎異常"""
    pass


class ModelLoadError(WhisperBaseException):
    """模型載入失敗異常
    
    使用情境：
    - Whisper 模型下載失敗
    - 模型檔案損壞
    - 裝置不支援指定的計算類型
    """
    pass


class TranscriptionError(WhisperBaseException):
    """轉錄處理失敗異常
    
    使用情境：
    - 音訊格式不支援
    - 轉錄過程中發生錯誤
    - VAD 參數設置不當
    """
    pass


class AudioDeviceError(WhisperBaseException):
    """音訊裝置錯誤異常
    
    使用情境：
    - 無法存取麥克風
    - 音訊裝置被其他程式佔用
    - 不支援的採樣率或聲道數
    """
    pass


class ConfigurationError(WhisperBaseException):
    """配置錯誤異常
    
    使用情境：
    - 配置檔案格式錯誤
    - 參數值超出有效範圍
    - 缺少必需的配置項
    """
    pass


class SubtitleGenerationError(WhisperBaseException):
    """字幕生成錯誤異常
    
    使用情境：
    - SRT 檔案寫入失敗
    - 時間戳格式錯誤
    - 無法創建輸出檔案
    """
    pass
