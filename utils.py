# coding: utf-8
"""
工具函數模組
包含 SRT 格式化、片段切分等工具函數
"""
import datetime


def format_timestamp(seconds: float):
    """將秒數轉換為 SRT 格式 (HH:MM:SS,mmm)"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - total_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_into_segments(words, min_duration=2.0, max_duration=8.0):
    """
    將單字列表重新組合成 2~8 秒的片段
    
    Args:
        words: list of dict or object with 'start', 'end', 'word'
        min_duration: 最小片段長度（秒）
        max_duration: 最大片段長度（秒）
        
    Returns:
        list: 切分後的片段列表
    """
    new_segments = []
    current_segment = []
    current_start = 0.0
    
    if not words:
        return []

    current_start = words[0].start
    
    for word in words:
        current_segment.append(word)
        current_duration = word.end - current_start
        
        # 判斷是否斷句
        is_pause = False
        if len(current_segment) > 1:
            # 簡單判斷：標點符號結尾 (Whisper 的 word 通常包含標點)
            text = word.word.strip()
            if text.endswith(('，', '。', '？', '！', ',', '.', '?', '!')):
                is_pause = True
        
        # 強制切分條件
        force_split = current_duration >= max_duration
        
        # 可切分條件
        can_split = current_duration >= min_duration and is_pause
        
        if force_split or can_split:
            text = "".join([w.word for w in current_segment]).strip()
            new_segments.append({
                "start": current_start,
                "end": word.end,
                "text": text
            })
            current_segment = []
            # 下一個片段的開始時間設為目前 word 的結束時間
            current_start = word.end 
            
    # 處理剩餘的
    if current_segment:
        text = "".join([w.word for w in current_segment]).strip()
        new_segments.append({
            "start": current_start,
            "end": current_segment[-1].end,
            "text": text
        })
        
    return new_segments


def write_srt(segments, output_path):
    """
    將轉錄結果寫入 SRT 檔案
    
    Args:
        segments: 片段列表
        output_path: 輸出檔案路徑
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            # 兼容 dict (自定義切分) 和 object (原始 segment)
            start_time = segment["start"] if isinstance(segment, dict) else segment.start
            end_time = segment["end"] if isinstance(segment, dict) else segment.end
            text = segment["text"] if isinstance(segment, dict) else segment.text
            
            start = format_timestamp(start_time)
            end = format_timestamp(end_time)
            text = text.strip()
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
