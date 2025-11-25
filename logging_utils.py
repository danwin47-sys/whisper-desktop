# coding: utf-8
"""
日誌功能模組
處理錯誤日誌和轉錄統計記錄
"""
import datetime
import csv
import os


def log_error(error_msg):
    """
    記錄錯誤到 error_log.txt
    
    Args:
        error_msg: 錯誤訊息
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ERROR:\n{error_msg}\n")
        f.write("-" * 50 + "\n")


def log_transcription_stats(file_path, duration, model_size):
    """
    記錄轉錄統計到 transcription_stats.csv
    
    Args:
        file_path: 檔案路徑
        duration: 處理時長（秒）
        model_size: 模型大小
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    extension = os.path.splitext(file_path)[1]
    
    # 如果檔案不存在，先寫入標頭
    file_exists = os.path.isfile("transcription_stats.csv")
    
    with open("transcription_stats.csv", "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "File Path", "Extension", "Model Size", "Duration (s)"])
        writer.writerow([timestamp, file_path, extension, model_size, f"{duration:.2f}"])
