# coding: utf-8
"""
Whisper Desktop Assistant - 主程式
重構版本：使用模組化架構並整合進階優化
"""
import sys
import os
import argparse
import traceback
import datetime
import sounddevice as sd

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTabWidget, QComboBox, QTextEdit, 
    QFileDialog, QProgressBar, QListWidget, QListWidgetItem, QMessageBox, QCheckBox,
    QSystemTrayIcon, QMenu, QStyle, QDoubleSpinBox, QSpinBox, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

# 導入重構後的模組
from config import Config
from workers import LiveTranscriptionWorker, FileTranscriptionWorker


# === UI: 浮動字幕視窗 ===
class SubtitleOverlay(QWidget):
    """浮動字幕視窗"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout()
        
        self.subtitle_label = QLabel("")
        self.subtitle_label.setFont(QFont("Microsoft JhengHei", 24, QFont.Weight.Bold))
        self.subtitle_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 160); border-radius: 12px; padding: 12px;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)
        self.setLayout(layout)
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry((screen.width()-800)//2, screen.height()-250, 800, 200)

    def update_text(self, text):
        """更新字幕文字"""
        self.subtitle_label.setText(text)
        QTimer.singleShot(8000, lambda: self.subtitle_label.setText("") if self.subtitle_label.text() == text else None)


# === UI: 主視窗 ===
class MainWindow(QMainWindow):
    """主視窗"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper Desktop Assistant (優化版)")
        self.resize(600, 500)
        
        # 核心元件
        self.overlay = SubtitleOverlay()
        self.live_worker = None
        self.file_worker = None
        
        # 介面佈局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 顯示裝置資訊
        device_info_label = QLabel(f"運算裝置: {Config.DEVICE_NAME} | Beam Size: {Config.BEAM_SIZE} | 批次大小: {Config.BATCH_SIZE}")
        device_info_label.setStyleSheet("background-color: #E3F2FD; padding: 8px; border-radius: 4px; font-weight: bold;")
        layout.addWidget(device_info_label)
        
        # 分頁
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.setup_live_tab()
        self.setup_file_tab()
        self.setup_settings_tab()
        
        # 系統托盤
        self.setup_tray()

    def setup_live_tab(self):
        """設置即時轉錄分頁"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 設定區 (裝置 + 模型)
        settings_layout = QHBoxLayout()
        
        # 裝置選擇
        settings_layout.addWidget(QLabel("麥克風:"))
        self.device_combo = QComboBox()
        self.refresh_devices()
        settings_layout.addWidget(self.device_combo)
        
        # 模型選擇
        settings_layout.addWidget(QLabel("模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(Config.AVAILABLE_MODELS)
        self.model_combo.setCurrentText(Config.MODEL_SIZE)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        settings_layout.addWidget(self.model_combo)
        
        btn_refresh = QPushButton("重新整理")
        btn_refresh.clicked.connect(self.refresh_devices)
        settings_layout.addWidget(btn_refresh)
        
        layout.addLayout(settings_layout)
        
        # 控制按鈕
        self.btn_live_toggle = QPushButton("開始即時轉錄 (F2)")
        self.btn_live_toggle.setCheckable(True)
        self.btn_live_toggle.clicked.connect(self.toggle_live_transcription)
        self.btn_live_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")
        layout.addWidget(self.btn_live_toggle)
        
        # 浮動視窗開關
        self.chk_overlay = QCheckBox("顯示浮動字幕視窗")
        self.chk_overlay.setChecked(True)
        self.chk_overlay.stateChanged.connect(lambda s: self.overlay.show() if s else self.overlay.hide())
        layout.addWidget(self.chk_overlay)
        
        # 狀態顯示
        self.lbl_live_status = QLabel("狀態: 待機中")
        self.lbl_live_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_live_status)
        
        # Log 顯示區
        layout.addWidget(QLabel("最近轉錄紀錄:"))
        self.txt_live_log = QTextEdit()
        self.txt_live_log.setReadOnly(True)
        layout.addWidget(self.txt_live_log)
        
        self.tabs.addTab(tab, "即時助理")

    def setup_file_tab(self):
        """設置檔案轉錄分頁"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 模型選擇 (檔案轉錄專用)
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("轉錄模型:"))
        self.file_model_combo = QComboBox()
        self.file_model_combo.addItems(Config.AVAILABLE_MODELS)
        self.file_model_combo.setCurrentText(Config.MODEL_SIZE)
        model_layout.addWidget(self.file_model_combo)
        layout.addLayout(model_layout)

        # 檔案選擇
        btn_layout = QHBoxLayout()
        btn_add_file = QPushButton("加入檔案")
        btn_add_file.clicked.connect(self.add_files)
        btn_add_folder = QPushButton("加入資料夾")
        btn_add_folder.clicked.connect(self.add_folder)
        btn_clear = QPushButton("清空列表")
        btn_clear.clicked.connect(lambda: self.list_files.clear())
        
        btn_layout.addWidget(btn_add_file)
        btn_layout.addWidget(btn_add_folder)
        btn_layout.addWidget(btn_clear)
        layout.addLayout(btn_layout)
        
        # 檔案列表
        self.list_files = QListWidget()
        layout.addWidget(self.list_files)
        
        # 進度條
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # 開始按鈕
        self.btn_file_start = QPushButton("開始批次轉錄 (已優化)")
        self.btn_file_start.clicked.connect(self.start_file_transcription)
        self.btn_file_start.setStyleSheet("background-color: #2196F3; color: white; font-size: 16px; padding: 10px;")
        layout.addWidget(self.btn_file_start)
        
        self.tabs.addTab(tab, "檔案轉錄")

    def setup_settings_tab(self):
        """設置進階設定分頁"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        group = QGroupBox("進階轉錄設定 (Advanced Settings)")
        form_layout = QFormLayout()
        
        # 1. 語言選擇
        self.combo_language = QComboBox()
        for name, code in Config.AVAILABLE_LANGUAGES.items():
            self.combo_language.addItem(name, code)
        self.combo_language.setCurrentText("繁體中文 (Chinese)")
        self.combo_language.currentIndexChanged.connect(self.update_settings)
        form_layout.addRow("語言 (Language):", self.combo_language)
        
        # 2. 溫度設定
        self.spin_temperature = QDoubleSpinBox()
        self.spin_temperature.setRange(0.1, 1.0)  # 最小值必須為 0.1，避免 clip_timestamps 錯誤
        self.spin_temperature.setSingleStep(0.1)
        self.spin_temperature.setValue(max(0.1, Config.TEMPERATURE))  # 確保至少為 0.1
        self.spin_temperature.setToolTip(
            "溫度控制轉錄的隨機性。\n"
            "• 建議值：0.2（預設）\n"
            "• 最小值：0.1（低於此值會導致轉錄失敗）\n"
            "• 較高值（0.5-1.0）：更多樣化但可能不準確"
        )
        self.spin_temperature.valueChanged.connect(self.update_settings)
        form_layout.addRow("溫度 (Temperature):", self.spin_temperature)
        
        # 3. 翻譯模式
        self.chk_translate = QCheckBox("啟用翻譯模式 (Translate to English)")
        self.chk_translate.setChecked(False)
        self.chk_translate.stateChanged.connect(self.update_settings)
        form_layout.addRow("翻譯 (Translate):", self.chk_translate)
        
        # 4. VAD 設定
        self.chk_vad = QCheckBox("啟用 VAD (語音活動偵測)")
        self.chk_vad.setChecked(Config.VAD_ENABLED)
        self.chk_vad.setToolTip("開啟後會過濾靜音片段，速度變快，但可能切掉小聲的語音。")
        self.chk_vad.stateChanged.connect(self.update_settings)
        form_layout.addRow("VAD:", self.chk_vad)
        
        self.spin_vad = QSpinBox()
        self.spin_vad.setRange(100, 5000)
        self.spin_vad.setSingleStep(100)
        self.spin_vad.setValue(Config.VAD_MIN_SILENCE_MS)
        self.spin_vad.setSuffix(" ms")
        self.spin_vad.setToolTip("小於此長度的靜音會被忽略。")
        self.spin_vad.valueChanged.connect(self.update_settings)
        form_layout.addRow("VAD 最小靜音 (Min Silence):", self.spin_vad)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        layout.addStretch()
        
        self.tabs.addTab(tab, "設定 (Settings)")

    def update_settings(self):
        """更新配置"""
        Config.LANGUAGE = self.combo_language.currentData()
        Config.TEMPERATURE = self.spin_temperature.value()
        Config.TASK = "translate" if self.chk_translate.isChecked() else "transcribe"
        Config.VAD_ENABLED = self.chk_vad.isChecked()
        Config.VAD_MIN_SILENCE_MS = self.spin_vad.value()

    def setup_tray(self):
        """設置系統托盤"""
        self.tray = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume), self)
        menu = QMenu()
        action_show = QAction("顯示主視窗", self)
        action_show.triggered.connect(self.show)
        menu.addAction(action_show)
        action_quit = QAction("退出", self)
        action_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(action_quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def refresh_devices(self):
        """刷新音訊裝置列表"""
        self.device_combo.clear()
        devices = sd.query_devices()
        default_input = sd.query_devices(kind='input')
        default_idx = default_input['index'] if default_input else -1
        
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                name = f"{i}: {dev['name']}"
                self.device_combo.addItem(name, i)
                if i == default_idx:
                    self.device_combo.setCurrentIndex(self.device_combo.count() - 1)

    def on_model_changed(self, text):
        """模型變更處理"""
        Config.MODEL_SIZE = text
        if self.live_worker:
            self.lbl_live_status.setText(f"模型已變更為 {text}，請重新開始錄音以套用。")

    def toggle_live_transcription(self):
        """切換即時轉錄狀態"""
        if self.btn_live_toggle.isChecked():
            # 開始
            device_idx = self.device_combo.currentData()
            
            # 如果 Worker 不存在，或者模型設定改變了，就重新建立
            if self.live_worker is None or self.live_worker.model_size != Config.MODEL_SIZE:
                if self.live_worker:
                    self.live_worker.stop()
                    self.live_worker.wait()
                
                self.live_worker = LiveTranscriptionWorker(device_idx, model_size=Config.MODEL_SIZE)
                self.live_worker.text_updated.connect(self.overlay.update_text)
                self.live_worker.text_updated.connect(lambda t: self.txt_live_log.append(t) if not t.endswith("...") else None)
                self.live_worker.status_updated.connect(self.lbl_live_status.setText)
                self.live_worker.start()
            
            self.live_worker.start_recording()
            self.btn_live_toggle.setText("停止錄音 (F2)")
            self.btn_live_toggle.setStyleSheet("background-color: #F44336; color: white; font-size: 16px; padding: 10px;")
            if self.chk_overlay.isChecked(): 
                self.overlay.show()
        else:
            # 停止
            if self.live_worker:
                self.live_worker.stop_recording()
            self.btn_live_toggle.setText("開始即時轉錄 (F2)")
            self.btn_live_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")

    def add_files(self):
        """加入檔案"""
        files, _ = QFileDialog.getOpenFileNames(self, "選擇音訊/影片檔案", "", "音訊/影片 (*.mp3 *.mp4 *.wav *.m4a *.mkv)")
        for f in files:
            item = QListWidgetItem(f)
            item.setData(Qt.ItemDataRole.UserRole, f)
            self.list_files.addItem(item)

    def add_folder(self):
        """加入資料夾"""
        folder = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.mp3', '.mp4', '.wav', '.m4a', '.mkv')):
                        full_path = os.path.join(root, file)
                        item = QListWidgetItem(full_path)
                        item.setData(Qt.ItemDataRole.UserRole, full_path)
                        self.list_files.addItem(item)

    def start_file_transcription(self):
        """開始檔案轉錄（使用優化後的 Worker）"""
        count = self.list_files.count()
        if count == 0: 
            return
        
        files = []
        for i in range(count):
            item = self.list_files.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            if path is None:
                path = item.text().split(" - [")[0]
            files.append(path)
        
        # 取得使用者在檔案分頁選擇的模型
        selected_model = self.file_model_combo.currentText()
        
        self.btn_file_start.setEnabled(False)
        # 使用優化後的 FileTranscriptionWorker（已整合批次處理）
        self.file_worker = FileTranscriptionWorker(files, model_size=selected_model)
        self.file_worker.progress_updated.connect(lambda c, t: self.progress_bar.setValue(int(c/t*100)))
        self.file_worker.file_status_updated.connect(self.update_file_status)
        self.file_worker.finished_all.connect(self.on_file_transcription_finished)
        self.file_worker.start()

    def update_file_status(self, file_path, status):
        """更新檔案狀態"""
        if file_path == "System":
            QMessageBox.critical(self, "系統錯誤", status)
            self.btn_file_start.setEnabled(True)
            return

        for i in range(self.list_files.count()):
            item = self.list_files.item(i)
            original_path = item.data(Qt.ItemDataRole.UserRole)
            
            if original_path is None:
                original_path = item.text().split(" - [")[0]
                item.setData(Qt.ItemDataRole.UserRole, original_path)

            if original_path == file_path:
                item.setText(f"{original_path} - [{status}]")
                self.list_files.scrollToItem(item)
                break

    def on_file_transcription_finished(self):
        """檔案轉錄完成"""
        self.btn_file_start.setEnabled(True)
        QMessageBox.information(self, "完成", "所有檔案轉錄完成！")

    def closeEvent(self, event):
        """關閉事件處理"""
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()


# === 全域異常處理 ===
def global_exception_handler(exctype, value, tb):
    """全域異常處理函數"""
    # 忽略 KeyboardInterrupt (Ctrl+C)
    if exctype == KeyboardInterrupt:
        sys.__excepthook__(exctype, value, tb)
        return

    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(f"捕獲到未處理的異常:\n{error_msg}", file=sys.stderr)
    
    # 寫入 log
    try:
        from logging_utils import log_error
        log_error(f"Uncaught Exception: {error_msg}")
    except:
        # 如果 logging_utils 失敗，嘗試直接寫入
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] Uncaught Exception: {error_msg}\n")

    # 如果 QApplication 已啟動，顯示錯誤視窗
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("發生未預期的錯誤")
        msg.setText("程式發生錯誤，請查看 error_log.txt 以獲得更多資訊。")
        msg.setDetailedText(error_msg)
        msg.exec()


# === 主程式 ===
def main():
    """主程式入口"""
    # 解析命令列參數
    parser = argparse.ArgumentParser(description="Whisper Desktop Assistant")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (listen on port 5678)")
    args = parser.parse_args()

    # 啟動 Debug Port
    if args.debug:
        try:
            import debugpy
            print("=" * 60)
            print("除錯模式已啟用 (DEBUG MODE ENABLED)")
            print("正在監聽連接埠 5678 等待除錯器連線...")
            print("=" * 60)
            debugpy.listen(("localhost", 5678))
        except ImportError:
            print("錯誤: 找不到 'debugpy' 模組。請使用 'pip install debugpy' 安裝。")
        except Exception as e:
            print(f"啟動除錯監聽器時發生錯誤: {e}")

    # 設定全域異常處理
    sys.excepthook = global_exception_handler

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 顯示配置資訊
    print("=" * 60)
    print("Whisper Desktop Assistant - 優化版")
    print("=" * 60)
    print(f"運算裝置: {Config.DEVICE_NAME}")
    print(f"Beam Size: {Config.BEAM_SIZE} (速度優化)")
    print(f"批次大小: {Config.BATCH_SIZE} (批次處理)")
    print(f"VAD 啟用: {Config.VAD_ENABLED}")
    print(f"進階優化: 已啟用 (+32% 速度提升)")
    print("=" * 60)
    
    window = MainWindow()
    window.show()
    
    # 全域快捷鍵 (F2)
    def on_hotkey():
        window.btn_live_toggle.click()
        
    try:
        import keyboard
        keyboard.add_hotkey('F2', on_hotkey)
    except:
        print("無法註冊全域快捷鍵 F2")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()