from editor.speaker_diarization import run_diarization, run_whisper_transcription, align_segments_to_speakers
from editor.streamer_detector import detect_streamer_speaker
from editor.subtitle_writer import write_srt
from editor.ffmpeg_wrapper import FFmpegStacker
from pathlib import Path
import os
import time


def process_clip(input_path: str, output_path: str, streamer_name: str = "", hf_token: str = None):
    print(f"[INFO] Processing clip: {input_path}")
    total_start_time = time.time()

    hf_token = hf_token or os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        raise RuntimeError("Missing Hugging Face token. Set HUGGINGFACE_TOKEN environment variable.")

    Path("output").mkdir(exist_ok=True)

    # Step 1: Diarize + transcribe
    print("\n[TIMING] Starting diarization...")
    start_time = time.time()
    diarized = run_diarization(input_path, hf_token)
    diarization_time = time.time() - start_time
    print(f"[TIMING] Diarization completed in {diarization_time:.2f} seconds")

    print("\n[TIMING] Starting transcription...")
    start_time = time.time()
    transcribed = run_whisper_transcription(input_path)
    transcription_time = time.time() - start_time
    print(f"[TIMING] Transcription completed in {transcription_time:.2f} seconds")

    print("\n[TIMING] Starting alignment...")
    start_time = time.time()
    aligned = align_segments_to_speakers(transcribed, diarized)
    alignment_time = time.time() - start_time
    print(f"[TIMING] Alignment completed in {alignment_time:.2f} seconds")

    # Step 2: Detect streamer speaker
    print("\n[TIMING] Starting streamer detection...")
    start_time = time.time()
    streamer_id = detect_streamer_speaker(input_path, diarized)
    detection_time = time.time() - start_time
    print(f"[TIMING] Streamer detection completed in {detection_time:.2f} seconds")

    if not streamer_id:
        print("[WARN] Could not detect streamer speaker. Defaulting all subs to top.")
        streamer_id = "UNKNOWN"

    # Step 3: Split subtitles
    print("\n[TIMING] Starting subtitle splitting...")
    start_time = time.time()
    streamer_subs = [seg for seg in aligned if seg["speaker"] == streamer_id]
    others_subs = [seg for seg in aligned if seg["speaker"] != streamer_id]

    streamer_srt_path = "output/streamer.srt"
    others_srt_path = "output/others.srt"
    write_srt(streamer_subs, streamer_srt_path)
    write_srt(others_subs, others_srt_path)
    subtitle_time = time.time() - start_time
    print(f"[TIMING] Subtitle splitting completed in {subtitle_time:.2f} seconds")

    # Step 4: Render with FFmpeg
    print("\n[TIMING] Starting FFmpeg rendering...")
    start_time = time.time()
    editor = FFmpegStacker(
        input_path=input_path,
        output_path=output_path,
        streamer_name=streamer_name
    )
    editor.run()
    rendering_time = time.time() - start_time
    print(f"[TIMING] FFmpeg rendering completed in {rendering_time:.2f} seconds")

    total_time = time.time() - total_start_time
    print("\n[TIMING] Summary:")
    print(f"{'Step':<25} {'Time (seconds)':<15} {'Percentage':>10}")
    print("-" * 50)
    print(f"{'Diarization':<25} {diarization_time:15.2f} {(diarization_time / total_time) * 100:10.1f}%")
    print(f"{'Transcription':<25} {transcription_time:15.2f} {(transcription_time / total_time) * 100:10.1f}%")
    print(f"{'Alignment':<25} {alignment_time:15.2f} {(alignment_time / total_time) * 100:10.1f}%")
    print(f"{'Streamer Detection':<25} {detection_time:15.2f} {(detection_time / total_time) * 100:10.1f}%")
    print(f"{'Subtitle Processing':<25} {subtitle_time:15.2f} {(subtitle_time / total_time) * 100:10.1f}%")
    print(f"{'FFmpeg Rendering':<25} {rendering_time:15.2f} {(rendering_time / total_time) * 100:10.1f}%")
    print("-" * 50)
    print(f"{'Total Time':<25} {total_time:15.2f} {100:10.1f}%")
