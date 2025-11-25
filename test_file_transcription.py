# coding: utf-8
"""
檔案轉錄測試腳本
直接使用 FileTranscriptionWorker 進行轉錄測試
"""
import sys
import os
from PyQt6.QtCore import QCoreApplication
from workers import FileTranscriptionWorker
from config import Config

def on_progress(current, total):
    """進度更新"""
    percentage = int(current / total * 100)
    print(f"進度: {current}/{total} ({percentage}%)")

def on_status(file_path, status):
    """狀態更新"""
    print(f"[{os.path.basename(file_path)}] {status}")

def on_finished():
    """轉錄完成"""
    print("\n[OK] 所有檔案轉錄完成！")
    QCoreApplication.quit()

def main():
    """主測試函數"""
    # 指定要轉錄的檔案（使用專案目錄下的測試檔案）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "video1.mp3")
    
    # 檢查檔案是否存在
    if not os.path.exists(file_path):
        print(f"[ERROR] 錯誤: 找不到檔案 {file_path}")
        print(f"請確認檔案路徑是否正確")
        return
    
    print("=" * 60)
    print("Whisper 檔案轉錄測試")
    print("=" * 60)
    print(f"檔案: {file_path}")
    print(f"模型: {Config.MODEL_SIZE}")
    print(f"運算裝置: {Config.DEVICE_NAME}")
    print(f"Temperature: {Config.TEMPERATURE}")
    print(f"VAD 啟用: {Config.VAD_ENABLED}")
    print("=" * 60)
    print()
    
    # 創建 QCoreApplication（Worker 需要事件循環）
    app = QCoreApplication(sys.argv)
    
    # 創建 Worker
    worker = FileTranscriptionWorker([file_path], model_size=Config.MODEL_SIZE)
    
    # 連接信號
    worker.progress_updated.connect(on_progress)
    worker.file_status_updated.connect(on_status)
    worker.finished_all.connect(on_finished)
    
    # 啟動轉錄
    print("開始轉錄...")
    worker.start()
    
    # 運行事件循環
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
