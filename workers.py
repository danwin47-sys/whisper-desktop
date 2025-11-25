# coding: utf-8
"""
Worker 模組
包含即時轉錄和檔案轉錄的 Worker 類別
已整合進階優化：批次處理、完整VAD參數、條件文本控制
"""
import time
import datetime
import queue
import numpy as np
import sounddevice as sd
import traceback
import os
from PyQt6.QtCore import QThread, pyqtSignal
from faster_whisper import WhisperModel

# 嘗試導入批次處理支援
try:
    from faster_whisper import BatchedInferencePipeline
    BATCHED_AVAILABLE = True
except ImportError:
    BATCHED_AVAILABLE = False

from config import Config
from utils import split_into_segments, write_srt
from logging_utils import log_error, log_transcription_stats


class LiveTranscriptionWorker(QThread):
    """即時轉錄 Worker（已整合進階優化）"""
    text_updated = pyqtSignal(str) 
    status_updated = pyqtSignal(str)

    def __init__(self, device_index=None, model_size="tiny", preloaded_model=None):
        super().__init__()
        self.device_index = device_index
        self.model_size = model_size
        self.is_recording = False
        self.running = True
        self.audio_queue = queue.Queue()
        self.current_phrase_buffer = []
        self.model = preloaded_model
        self.last_speech_time = 0
        self.last_transcribe_time = 0

    def load_model(self):
        """載入模型"""
        if self.model is None:
            self.status_updated.emit(f"載入模型中 ({self.model_size})...")
            try:
                self.model = WhisperModel(
                    self.model_size, 
                    device=Config.DEVICE, 
                    compute_type=Config.COMPUTE_TYPE
                )
                self.status_updated.emit(f"模型已載入 ({self.model_size})")
            except Exception as e:
                error_msg = f"模型載入失敗: {e}\n{traceback.format_exc()}"
                log_error(error_msg)
                self.status_updated.emit(f"模型載入失敗: {e}")

    def run(self):
        """執行即時轉錄"""
        self.load_model()
        if not self.model:
            return

        self.status_updated.emit("待機中")
        
        while self.running:
            if self.is_recording:
                try:
                    with sd.InputStream(
                        samplerate=Config.SAMPLE_RATE, 
                        channels=Config.CHANNELS, 
                        device=self.device_index,
                        dtype='float32', 
                        callback=self.audio_callback
                    ):
                        self.status_updated.emit("錄音中...")
                        self.last_speech_time = time.time()
                        
                        while self.is_recording and self.running:
                            try:
                                while True:
                                    data = self.audio_queue.get_nowait()
                                    self.current_phrase_buffer.append(data)
                                    energy = np.linalg.norm(data) / len(data)
                                    if energy > Config.SILENCE_THRESHOLD:
                                        self.last_speech_time = time.time()
                            except queue.Empty:
                                pass
                            
                            now = time.time()
                            has_audio = len(self.current_phrase_buffer) > 0
                            
                            if has_audio and (now - self.last_speech_time > Config.SILENCE_DURATION):
                                self.finalize_phrase()
                            elif has_audio and (now - self.last_transcribe_time > Config.TRANSCRIBE_INTERVAL):
                                self.interim_transcribe()
                                
                            time.sleep(0.05)
                            
                    if self.current_phrase_buffer:
                        self.finalize_phrase()
                    else:
                        self.status_updated.emit("待機中")

                except Exception as e:
                    error_msg = f"錄音錯誤: {e}\n{traceback.format_exc()}"
                    log_error(error_msg)
                    self.status_updated.emit(f"錄音錯誤: {e}")
            else:
                time.sleep(0.1)

    def audio_callback(self, indata, frames, time_info, status):
        """音訊回調"""
        if status:
            print(f"音訊狀態: {status}")
        self.audio_queue.put(indata.copy().flatten())

    def finalize_phrase(self):
        """完成一個語句的轉錄"""
        if len(self.current_phrase_buffer) == 0:
            return
        audio_data = np.concatenate(self.current_phrase_buffer)
        self.current_phrase_buffer = []
        self.last_transcribe_time = time.time()
        text = self.transcribe_audio(audio_data)
        if text:
            self.text_updated.emit(text)
            with open(Config.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now()}] {text}\n")

    def interim_transcribe(self):
        """臨時轉錄"""
        if len(self.current_phrase_buffer) == 0:
            return
        audio_data = np.concatenate(self.current_phrase_buffer)
        self.last_transcribe_time = time.time()
        text = self.transcribe_audio(audio_data)
        if text:
            self.text_updated.emit(text + " ...")

    def transcribe_audio(self, audio_data):
        """
        轉錄音訊（已整合進階優化）
        - 使用完整 VAD 參數
        - 使用條件文本控制
        """
        try:
            # 溫度處理
            temp = Config.TEMPERATURE
            if temp is None or not isinstance(temp, (int, float)):
                temp = 0.0
            
            # 使用完整 VAD 參數
            vad_params = Config.get_vad_parameters()
            
            segments, info = self.model.transcribe(
                audio_data, 
                beam_size=Config.BEAM_SIZE,
                initial_prompt=Config.INITIAL_PROMPT, 
                language=Config.LANGUAGE,
                task=Config.TASK,
                temperature=temp,
                vad_filter=Config.VAD_ENABLED,
                vad_parameters=vad_params,  # 完整 VAD 參數
                condition_on_previous_text=Config.CONDITION_ON_PREVIOUS_TEXT  # 條件控制
            )
            result = " ".join([seg.text for seg in segments]).strip()
            return result
        except Exception as e:
            error_msg = f"轉錄錯誤: {e}\n{traceback.format_exc()}"
            log_error(error_msg)
            self.status_updated.emit(f"轉錄錯誤: {e}")
            return ""

    def start_recording(self):
        """開始錄音"""
        self.is_recording = True

    def stop_recording(self):
        """停止錄音"""
        self.is_recording = False

    def stop(self):
        """停止 Worker"""
        self.running = False
        self.is_recording = False


class FileTranscriptionWorker(QThread):
    """檔案轉錄 Worker（已整合批次處理優化）"""
    progress_updated = pyqtSignal(int, int)
    file_status_updated = pyqtSignal(str, str)
    finished_all = pyqtSignal()

    def __init__(self, file_paths, model_size="tiny", preloaded_model=None):
        super().__init__()
        self.file_paths = file_paths
        self.model_size = model_size
        self.model = preloaded_model

    def run(self):
        """執行檔案轉錄（使用批次處理）"""
        # 如果沒有預載模型，才載入
        if self.model is None:
            try:
                base_model = WhisperModel(
                    self.model_size, 
                    device=Config.DEVICE, 
                    compute_type=Config.COMPUTE_TYPE
                )
                
                # 嘗試使用批次處理（僅在 VAD 啟用時）
                # BatchedInferencePipeline 需要 VAD 或 clip_timestamps，因此只在 VAD 啟用時使用
                if BATCHED_AVAILABLE and Config.VAD_ENABLED:
                    try:
                        model = BatchedInferencePipeline(model=base_model)
                        use_batched = True
                        print(f"✅ 使用批次處理模式 (batch_size={Config.BATCH_SIZE})")
                    except Exception as e:
                        model = base_model
                        use_batched = False
                        print(f"⚠️ 批次處理初始化失敗，使用標準模式: {e}")
                else:
                    model = base_model
                    use_batched = False
                    if not Config.VAD_ENABLED:
                        print("ℹ️ VAD 未啟用，使用標準模式（批次處理需要 VAD）")
                    else:
                        print("ℹ️ BatchedInferencePipeline 不可用，使用標準模式")
                    
            except Exception as e:
                error_msg = f"模型載入失敗: {e}\n{traceback.format_exc()}"
                log_error(error_msg)
                self.file_status_updated.emit("System", f"模型載入失敗: {e}")
                return
        else:
            model = self.model
            use_batched = False

        for i, file_path in enumerate(self.file_paths, start=1):
            self.progress_updated.emit(i, len(self.file_paths))
            self.file_status_updated.emit(file_path, "轉錄中...")
            
            start_time = time.time()
            try:
                # 溫度處理
                temp = Config.TEMPERATURE
                if temp is None or not isinstance(temp, (int, float)):
                    temp = 0.0
                
                # 使用完整 VAD 參數
                vad_params = Config.get_vad_parameters()
                
                # 準備轉錄參數
                # 注意：word_timestamps 需要 VAD 或 clip_timestamps 支援
                # 當 VAD 停用時，使用 segment 級別的時間戳
                use_word_timestamps = Config.VAD_ENABLED
                
                transcribe_params = {
                    "beam_size": Config.BEAM_SIZE,
                    "initial_prompt": Config.INITIAL_PROMPT,
                    "language": Config.LANGUAGE,
                    "task": Config.TASK,
                    "temperature": temp,
                    "word_timestamps": use_word_timestamps,
                    "vad_filter": Config.VAD_ENABLED,
                    "condition_on_previous_text": Config.CONDITION_ON_PREVIOUS_TEXT
                }
                
                # 只有在啟用 VAD 時才傳遞 VAD 參數
                if Config.VAD_ENABLED:
                    transcribe_params["vad_parameters"] = vad_params
                
                # 如果使用批次處理，加入 batch_size
                # 注意：批次處理在某些情況下也需要 clip_timestamps，所以只在 VAD 啟用時使用
                if use_batched and Config.VAD_ENABLED:
                    transcribe_params["batch_size"] = Config.BATCH_SIZE
                
                # === DEBUG: 打印實際參數 ===
                print("=" * 40)
                print(f"DEBUG: VAD_ENABLED (Config) = {Config.VAD_ENABLED}")
                print(f"DEBUG: use_word_timestamps = {use_word_timestamps}")
                print(f"DEBUG: transcribe_params = {transcribe_params}")
                print("=" * 40)
                
                # 轉錄
                try:
                    segments, info = model.transcribe(file_path, **transcribe_params)
                except RuntimeError as e:
                    if "No clip timestamps found" in str(e):
                        # 提供清晰的解決方案
                        error_msg = (
                            f"檔案 {file_path} 轉錄失敗。\n"
                            f"原因: {e}\n\n"
                            f"解決方案（二選一）：\n"
                            f"1. 在「設定」分頁中，將 Temperature 調整為 0.1 或以上\n"
                            f"2. 在「設定」分頁中，勾選「啟用 VAD」（需要安裝 onnxruntime）\n"
                            f"\n建議使用方案 1（將 Temperature 改為 0.2）"
                        )
                        print(f"❌ {error_msg}")
                        log_error(error_msg)
                        self.file_status_updated.emit(
                            file_path, 
                            "失敗：請將 Temperature 設為 0.1 以上"
                        )
                        continue
                    else:
                        raise e
                
                # 收集所有單字或片段
                all_words = []
                optimized_segments = []
                
                if use_word_timestamps:
                    # VAD 啟用：使用單字級別處理
                    for segment in segments:
                        if segment.words:
                            all_words.extend(segment.words)
                    
                    # 重新切分
                    if all_words:
                        optimized_segments = split_into_segments(all_words, min_duration=2.0, max_duration=8.0)
                else:
                    # VAD 停用：直接使用 segment 級別
                    for segment in segments:
                        optimized_segments.append({
                            "start": segment.start,
                            "end": segment.end,
                            "text": segment.text
                        })
                
                # 儲存
                base_name = os.path.splitext(file_path)[0]
                srt_path = f"{base_name}.srt"
                write_srt(optimized_segments, srt_path)
                
                # 顯示完整路徑和片段數量
                self.file_status_updated.emit(file_path, f"完成! 字幕已儲存: {srt_path} (共 {len(optimized_segments)} 個片段)")

                
                end_time = time.time()
                duration = end_time - start_time
                log_transcription_stats(file_path, duration, self.model_size)
                
            except Exception as e:
                error_msg = f"檔案轉錄失敗 ({file_path}): {e}\n{traceback.format_exc()}"
                log_error(error_msg)
                self.file_status_updated.emit(file_path, f"失敗: {e}")
        
        self.finished_all.emit()
