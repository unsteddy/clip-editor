import pytest
from unittest.mock import patch
from editor.ffmpeg_wrapper import FFmpegStacker


@patch("editor.ffmpeg_wrapper.detect_facecam_region")
def test_filter_construction_dynamic_facecam(mock_detect):
    # Mock facecam region result
    mock_detect.return_value = (10, 700, 320, 300)

    editor = FFmpegStacker("input.mp4", "output.mp4", "TestStreamer")
    editor.add_main_clip()
    editor.add_facecam_crop()
    editor.add_text_overlay()
    editor.add_logo_overlay()
    editor.add_vstack()
    filter_complex = editor.build_filter_complex()

    assert "crop=320:300:10:700" in filter_complex
    assert "drawtext=text='TestStreamer'" in filter_complex
    assert "vstack=inputs=2" in filter_complex


@patch("editor.ffmpeg_wrapper.detect_facecam_region")
@patch("editor.ffmpeg_wrapper.subprocess.run")
def test_ffmpeg_command_runs(mock_run, mock_detect):
    mock_detect.return_value = (0, 720, 300, 300)

    editor = FFmpegStacker("fake_input.mp4", "fake_output.mp4", "Streamer")
    editor.run()

    called_args = mock_run.call_args[0][0]
    assert "ffmpeg" in called_args[0]
    assert "fake_input.mp4" in called_args
    assert "-filter_complex" in called_args
    mock_run.assert_called_once()


@patch("editor.ffmpeg_wrapper.detect_facecam_region")
def test_escaped_streamer_name(mock_detect):
    mock_detect.return_value = (0, 720, 300, 300)

    editor = FFmpegStacker("input.mp4", "output.mp4", "O'Brien")
    editor.add_text_overlay()
    part = next((f for f in editor.filter_parts if "drawtext" in f), "")
    assert "O\\\\'Brien" in part


@patch("editor.ffmpeg_wrapper.detect_facecam_region")
def test_empty_streamer_name_safe(mock_detect):
    mock_detect.return_value = (0, 720, 300, 300)

    editor = FFmpegStacker("input.mp4", "output.mp4", "")
    editor.add_text_overlay()
    part = next((f for f in editor.filter_parts if "drawtext" in f), "")
    assert "drawtext=text=''" in part
