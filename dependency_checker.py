# coding: utf-8
"""
依賴檢查模組
用於檢查和驗證所有必需的依賴套件，並提供友好的錯誤訊息
"""
import sys
from typing import List, Tuple, Optional


class DependencyChecker:
    """依賴檢查器"""
    
    # 必需的依賴套件及其用途
    REQUIRED_DEPENDENCIES = {
        "faster_whisper": "Whisper 語音辨識核心引擎",
        "sounddevice": "音訊錄製功能",
        "PyQt6": "圖形使用者介面",
        "numpy": "音訊資料處理",
        "onnxruntime": "VAD (語音活動偵測) 功能",
    }
    
    # 可選的依賴套件
    OPTIONAL_DEPENDENCIES = {
        "keyboard": "全域快捷鍵 (F2) 支援",
    }
    
    @classmethod
    def check_dependency(cls, module_name: str) -> Tuple[bool, Optional[str]]:
        """
        檢查單個依賴套件是否已安裝
        
        Args:
            module_name: 模組名稱
            
        Returns:
            (是否已安裝, 錯誤訊息)
        """
        try:
            __import__(module_name)
            return True, None
        except ImportError as e:
            return False, str(e)
    
    @classmethod
    def check_all_dependencies(cls, show_optional: bool = True) -> List[str]:
        """
        檢查所有依賴套件
        
        Args:
            show_optional: 是否顯示可選依賴的狀態
            
        Returns:
            缺失的必需依賴列表
        """
        missing_required = []
        missing_optional = []
        
        print("=" * 70)
        print("[*] 檢查依賴套件...")
        print("=" * 70)
        
        # 檢查必需依賴
        print("\n[+] 必需依賴:")
        for module, purpose in cls.REQUIRED_DEPENDENCIES.items():
            is_installed, error = cls.check_dependency(module)
            if is_installed:
                print(f"  [OK] {module:20s} - {purpose}")
            else:
                print(f"  [NG] {module:20s} - {purpose} [缺失]")
                missing_required.append(module)
        
        # 檢查可選依賴
        if show_optional:
            print("\n[!] 可選依賴:")
            for module, purpose in cls.OPTIONAL_DEPENDENCIES.items():
                is_installed, error = cls.check_dependency(module)
                if is_installed:
                    print(f"  [OK] {module:20s} - {purpose}")
                else:
                    print(f"  [ ] {module:20s} - {purpose} [未安裝，部分功能可能不可用]")
                    missing_optional.append(module)
        
        print("=" * 70)
        
        return missing_required
    
    @classmethod
    def check_vad_support(cls) -> Tuple[bool, str]:
        """
        特別檢查 VAD 功能支援
        
        Returns:
            (是否支援, 狀態訊息)
        """
        is_installed, error = cls.check_dependency("onnxruntime")
        
        if is_installed:
            return True, "[OK] VAD 功能已啟用 (onnxruntime 已安裝)"
        else:
            return False, "[!] VAD 功能不可用 (需要安裝 onnxruntime)"
    
    @classmethod
    def get_installation_command(cls, missing_packages: List[str]) -> str:
        """
        生成安裝缺失套件的命令
        
        Args:
            missing_packages: 缺失的套件列表
            
        Returns:
            pip 安裝命令
        """
        if not missing_packages:
            return ""
        
        packages_str = " ".join(missing_packages)
        return f"pip install {packages_str}"
    
    @classmethod
    def show_error_and_exit(cls, missing_packages: List[str]):
        """
        顯示錯誤訊息並退出程式
        
        Args:
            missing_packages: 缺失的套件列表
        """
        print("\n" + "=" * 70)
        print("[ERROR] 缺少必需的依賴套件")
        print("=" * 70)
        print("\n缺失的套件:")
        
        for pkg in missing_packages:
            purpose = cls.REQUIRED_DEPENDENCIES.get(pkg, "未知用途")
            print(f"  - {pkg} - {purpose}")
        
        print("\n請執行以下命令安裝缺失的套件:")
        print(f"\n  {cls.get_installation_command(missing_packages)}")
        
        print("\n或安裝所有依賴:")
        print("\n  pip install -r requirements.txt")
        
        print("\n" + "=" * 70)
        sys.exit(1)
    
    @classmethod
    def verify_and_run(cls, show_optional: bool = True) -> bool:
        """
        驗證所有依賴並決定是否可以繼續執行
        
        Args:
            show_optional: 是否顯示可選依賴的狀態
            
        Returns:
            是否可以繼續執行
        """
        missing = cls.check_all_dependencies(show_optional=show_optional)
        
        if missing:
            cls.show_error_and_exit(missing)
            return False
        
        print("\n[OK] 所有必需的依賴套件已就緒！\n")
        return True


def check_vad_availability() -> bool:
    """
    快速檢查 VAD 是否可用（給其他模組使用）
    
    Returns:
        是否可用
    """
    is_available, _ = DependencyChecker.check_vad_support()
    return is_available


if __name__ == "__main__":
    # 測試用
    DependencyChecker.verify_and_run()
