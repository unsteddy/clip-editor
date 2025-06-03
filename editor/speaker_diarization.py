import os
import tempfile
import subprocess

from pyannote.audio import Pipeline
import whisper
import torch


def extract_audio(video_path: str) -> str:
    """Extract mono 16kHz WAV audio from input video using ffmpeg."""
    temp_wav = tempfile.mktemp(suffix=".wav")
    command = [
        "ffmpeg", "-i", video_path,
        "-ar", "16000",  # 16kHz sample rate
        "-ac", "1",  # mono
        "-y", temp_wav  # overwrite if exists
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return temp_wav


def run_diarization(input_path: str, hf_token: str):
    """Run speaker diarization on audio extracted from a video or audio file."""
    audio_path = extract_audio(input_path)

    # Load pyannote pipeline
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization@2.1",
        use_auth_token=hf_token
    )

    # Run diarization
    diarization = pipeline(audio_path)

    # Collect speaker-labeled segments
    speaker_segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_segments.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })

    # Clean up temp file
    os.remove(audio_path)

    return speaker_segments


def run_whisper_transcription(audio_path: str, model_size="medium"):
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["segments"]


def align_segments_to_speakers(whisper_segs, diarized_segs):
    aligned = []
    for wseg in whisper_segs:
        w_start, w_end, text = wseg['start'], wseg['end'], wseg['text']
        label = "UNKNOWN"

        # Find overlapping diarization segment
        for dseg in diarized_segs:
            if (w_start >= dseg["start"] and w_start <= dseg["end"]) or \
                    (w_end >= dseg["start"] and w_end <= dseg["end"]):
                label = dseg["speaker"]
                break

        aligned.append({
            "start": w_start,
            "end": w_end,
            "text": text.strip(),
            "speaker": label
        })
    return aligned
