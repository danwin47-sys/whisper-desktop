# coding: utf-8
"""
配置管理工具
讓使用者可以輕鬆調整所有優化參數，無需修改代碼
"""
import json
import os


class ConfigManager:
    """配置管理器"""
    
    CONFIG_FILE = "whisper_settings.json"
    
    DEFAULT_SETTINGS = {
        "model_size": "tiny",
        "language": "zh",
        "beam_size": 1,
        "batch_size": 16,
        "vad_enabled": True,
        "vad_min_silence_ms": 300,
        "vad_threshold": 0.5,
        "vad_min_speech_ms": 250,
        "vad_speech_pad_ms": 400,
        "condition_on_previous_text": False,
        "temperature": 0.0
    }
    
    @classmethod
    def load_settings(cls):
        """載入配置"""
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 合併預設值（確保所有鍵都存在）
                    return {**cls.DEFAULT_SETTINGS, **settings}
            except Exception as e:
                print(f"載入配置失敗: {e}，使用預設值")
                return cls.DEFAULT_SETTINGS.copy()
        return cls.DEFAULT_SETTINGS.copy()
    
    @classmethod
    def save_settings(cls, settings):
        """儲存配置"""
        try:
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已儲存到 {cls.CONFIG_FILE}")
            return True
        except Exception as e:
            print(f"❌ 儲存配置失敗: {e}")
            return False
    
    @classmethod
    def update_config_from_file(cls):
        """從配置檔更新 Config 類別"""
        settings = cls.load_settings()
        
        # 動態更新 Config
        from config import Config
        Config.MODEL_SIZE = settings.get("model_size", "tiny")
        Config.LANGUAGE = settings.get("language", "zh")
        Config.BEAM_SIZE = settings.get("beam_size", 1)
        Config.BATCH_SIZE = settings.get("batch_size", 16)
        Config.VAD_ENABLED = settings.get("vad_enabled", True)
        Config.VAD_MIN_SILENCE_MS = settings.get("vad_min_silence_ms", 300)
        Config.VAD_THRESHOLD = settings.get("vad_threshold", 0.5)
        Config.VAD_MIN_SPEECH_MS = settings.get("vad_min_speech_ms", 250)
        Config.VAD_SPEECH_PAD_MS = settings.get("vad_speech_pad_ms", 400)
        Config.CONDITION_ON_PREVIOUS_TEXT = settings.get("condition_on_previous_text", False)
        Config.TEMPERATURE = settings.get("temperature", 0.0)
        
        return settings
    
    @classmethod
    def print_current_settings(cls):
        """顯示當前配置"""
        settings = cls.load_settings()
        
        print("\n" + "=" * 60)
        print("當前 Whisper 配置")
        print("=" * 60)
        print(f"模型大小: {settings['model_size']}")
        print(f"語言: {settings['language']}")
        print("\n【效能優化】")
        print(f"  Beam Size: {settings['beam_size']} (1=最快, 3=平衡, 5=最準確)")
        print(f"  批次大小: {settings['batch_size']} (檔案轉錄)")
        print(f"  上下文依賴: {'停用' if not settings['condition_on_previous_text'] else '啟用'}")
        print("\n【VAD 語音偵測】")
        print(f"  啟用: {'是' if settings['vad_enabled'] else '否'}")
        print(f"  敏感度: {settings['vad_threshold']}")
        print(f"  最小語音長度: {settings['vad_min_speech_ms']}ms")
        print(f"  靜音閾值: {settings['vad_min_silence_ms']}ms")
        print(f"  語音填充: {settings['vad_speech_pad_ms']}ms")
        print("\n【其他】")
        print(f"  溫度: {settings['temperature']}")
        print("=" * 60 + "\n")
    
    @classmethod
    def interactive_config(cls):
        """互動式配置"""
        print("\n" + "🎛️  Whisper 配置工具" + "\n")
        settings = cls.load_settings()
        
        while True:
            print("\n選擇要調整的項目:")
            print("1. Beam Size (速度/品質平衡)")
            print("2. 批次大小 (檔案轉錄速度)")
            print("3. VAD 參數 (語音偵測)")
            print("4. 模型大小")
            print("5. 語言設定")
            print("6. 檢視當前配置")
            print("7. 重置為預設值")
            print("0. 儲存並退出")
            
            choice = input("\n請選擇 (0-7): ").strip()
            
            if choice == "1":
                print(f"\n當前 Beam Size: {settings['beam_size']}")
                print("1 = 最快速度 (可能較不準確)")
                print("3 = 平衡")
                print("5 = 最準確 (較慢)")
                new_val = input("輸入新值 (1/3/5): ").strip()
                if new_val in ["1", "3", "5"]:
                    settings['beam_size'] = int(new_val)
                    print("✅ 已更新")
                    
            elif choice == "2":
                print(f"\n當前批次大小: {settings['batch_size']}")
                print("8 = 省記憶體")
                print("16 = 預設")
                print("32 = 快速")
                print("64 = 最快 (需要更多記憶體)")
                new_val = input("輸入新值 (8/16/32/64): ").strip()
                if new_val in ["8", "16", "32", "64"]:
                    settings['batch_size'] = int(new_val)
                    print("✅ 已更新")
                    
            elif choice == "3":
                print("\nVAD 參數調整:")
                print(f"1. 啟用VAD: {settings['vad_enabled']}")
                print(f"2. 敏感度: {settings['vad_threshold']}")
                print(f"3. 最小語音: {settings['vad_min_speech_ms']}ms")
                print(f"4. 靜音閾值: {settings['vad_min_silence_ms']}ms")
                sub = input("選擇要調整的 (1-4, 0返回): ").strip()
                
                if sub == "1":
                    settings['vad_enabled'] = input("啟用? (y/n): ").lower() == 'y'
                elif sub == "2":
                    val = input("敏感度 (0.0-1.0): ")
                    try:
                        settings['vad_threshold'] = float(val)
                    except:
                        print("❌ 無效值")
                elif sub == "3":
                    val = input("最小語音長度 (ms): ")
                    try:
                        settings['vad_min_speech_ms'] = int(val)
                    except:
                        print("❌ 無效值")
                elif sub == "4":
                    val = input("靜音閾值 (ms): ")
                    try:
                        settings['vad_min_silence_ms'] = int(val)
                    except:
                        print("❌ 無效值")
                        
            elif choice == "4":
                print(f"\n當前模型: {settings['model_size']}")
                print("可選: tiny, base, small, medium, large-v3")
                new_val = input("輸入新模型: ").strip()
                if new_val:
                    settings['model_size'] = new_val
                    print("✅ 已更新")
                    
            elif choice == "5":
                print(f"\n當前語言: {settings['language']}")
                print("常用: zh (中文), en (英文), ja (日文)")
                new_val = input("輸入語言代碼: ").strip()
                if new_val:
                    settings['language'] = new_val
                    print("✅ 已更新")
                    
            elif choice == "6":
                cls.print_current_settings()
                
            elif choice == "7":
                if input("確定重置為預設值? (y/n): ").lower() == 'y':
                    settings = cls.DEFAULT_SETTINGS.copy()
                    print("✅ 已重置")
                    
            elif choice == "0":
                if cls.save_settings(settings):
                    print("\n✅ 配置已儲存！重啟應用程式後生效。")
                break
            
            else:
                print("❌ 無效選擇")


def main():
    """主程式"""
    import sys
    
    mgr = ConfigManager()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "show":
            mgr.print_current_settings()
        elif cmd == "reset":
            mgr.save_settings(mgr.DEFAULT_SETTINGS)
            print("✅ 已重置為預設值")
        else:
            print("用法:")
            print("  python config_manager.py         # 互動式配置")
            print("  python config_manager.py show    # 顯示當前配置")
            print("  python config_manager.py reset   # 重置為預設值")
    else:
        mgr.interactive_config()


if __name__ == "__main__":
    main()
