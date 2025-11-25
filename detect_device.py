"""
裝置偵測工具
自動偵測系統可用的運算裝置 (CUDA GPU / CPU)
並選擇最佳的 device 和 compute_type
"""
import torch


def get_optimal_device():
    """
    偵測並返回最佳運算裝置配置
    
    Returns:
        tuple: (device, compute_type, device_name)
            - device: 'cuda' 或 'cpu'
            - compute_type: 'float16' (GPU) 或 'int8' (CPU)
            - device_name: 裝置描述字串
    """
    if torch.cuda.is_available():
        # CUDA GPU 可用
        device = "cuda"
        compute_type = "float16"
        device_name = f"CUDA GPU: {torch.cuda.get_device_name(0)}"
        return device, compute_type, device_name
    else:
        # 僅 CPU 可用
        device = "cpu"
        compute_type = "int8"
        device_name = "CPU (無 GPU 加速)"
        return device, compute_type, device_name


def get_device_info():
    """
    取得詳細的裝置資訊
    
    Returns:
        dict: 包含裝置資訊的字典
    """
    info = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }
    
    if info["cuda_available"]:
        info["device_name"] = torch.cuda.get_device_name(0)
        info["cuda_version"] = torch.version.cuda
        # 取得 GPU 記憶體資訊 (以 GB 為單位)
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        info["total_memory_gb"] = round(total_memory, 2)
    
    return info


if __name__ == "__main__":
    # 測試腳本
    print("=== 裝置偵測測試 ===")
    device, compute_type, device_name = get_optimal_device()
    print(f"最佳裝置: {device}")
    print(f"計算類型: {compute_type}")
    print(f"裝置名稱: {device_name}")
    print()
    
    print("=== 詳細資訊 ===")
    info = get_device_info()
    for key, value in info.items():
        print(f"{key}: {value}")
