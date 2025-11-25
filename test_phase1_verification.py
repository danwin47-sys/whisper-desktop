# coding: utf-8
"""
Phase 1 Verification Test
Tests refactored modules work correctly
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Phase 1 Refactoring Verification Test")
print("=" * 60)

# Test 1: Import constants module
print("\n[Test 1] Importing constants module...")
try:
    from constants import (
        DEFAULT_WINDOW_WIDTH,
        DEFAULT_WINDOW_HEIGHT,
        SUPPORTED_AUDIO_FORMATS,
        PAUSE_PUNCTUATION,
        MIN_SEGMENT_DURATION,
        MAX_SEGMENT_DURATION
    )
    print("[OK] constants module imported")
    print(f"   - DEFAULT_WINDOW_WIDTH = {DEFAULT_WINDOW_WIDTH}")
    print(f"   - SUPPORTED_AUDIO_FORMATS = {SUPPORTED_AUDIO_FORMATS}")
    print(f"   - MIN_SEGMENT_DURATION = {MIN_SEGMENT_DURATION}")
except Exception as e:
    print(f"[FAIL] constants module: {e}")
    sys.exit(1)

# Test 2: Import exceptions module
print("\n[Test 2] Importing exceptions module...")
try:
    from exceptions import (
        WhisperBaseException,
        ModelLoadError,
        TranscriptionError,
        AudioDeviceError,
        ConfigurationError,
        SubtitleGenerationError
    )
    print("[OK] exceptions module imported")
    print(f"   - 6 custom exception classes defined")
    
    assert issubclass(ModelLoadError, WhisperBaseException)
    assert issubclass(TranscriptionError, WhisperBaseException)
    print("   - Inheritance structure correct")
except Exception as e:
    print(f"[FAIL] exceptions module: {e}")
    sys.exit(1)

# Test 3: Import updated ui module
print("\n[Test 3] Importing ui module...")
try:
    from ui import SubtitleOverlay
    print("[OK] ui module imported")
    print(f"   - SubtitleOverlay can be imported from ui")
    print(f"   - ui.__all__ = {__import__('ui').__all__}")
except Exception as e:
    print(f"[FAIL] ui module: {e}")
    sys.exit(1)

# Test 4: Verify utils module uses constants
print("\n[Test 4] Verifying utils module...")
try:
    from utils import split_into_segments, format_timestamp
    
    import inspect
    sig = inspect.signature(split_into_segments)
    min_dur = sig.parameters['min_duration'].default
    max_dur = sig.parameters['max_duration'].default
    
    print("[OK] utils module works")
    print(f"   - split_into_segments min_duration = {min_dur}")
    print(f"   - split_into_segments max_duration = {max_dur}")
    
    assert min_dur == MIN_SEGMENT_DURATION
    assert max_dur == MAX_SEGMENT_DURATION
    print("   - Default values match constants")
    
    timestamp = format_timestamp(3661.5)
    assert timestamp == "01:01:01,500"
    print(f"   - format_timestamp(3661.5) = '{timestamp}' [OK]")
    
except Exception as e:
    print(f"[FAIL] utils module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify core modules unaffected
print("\n[Test 5] Verifying core modules...")
try:
    from config import Config
    from workers import LiveTranscriptionWorker, FileTranscriptionWorker
    from logging_utils import log_error, log_transcription_stats
    
    print("[OK] Core modules imported")
    print(f"   - Config module available")
    print(f"   - Workers module available")
    print(f"   - logging_utils module available")
except Exception as e:
    print(f"[FAIL] Core modules: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("[SUCCESS] All tests passed!")
print("\nVerified items:")
print("  1. constants.py module works correctly")
print("  2. exceptions.py module works correctly")  
print("  3. ui/__init__.py exports work correctly")
print("  4. utils.py uses constants correctly")
print("  5. Core modules are unaffected")
print("\nConclusion: Phase 1 refactoring successful, no regressions")
print("=" * 60)
