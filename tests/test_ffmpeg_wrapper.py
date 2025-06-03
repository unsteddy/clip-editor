import pytest
from editor.ffmpeg_wrapper import FFmpegStacker
from unittest.mock import patch


def test_filter_construction_minimal():
    editor = FFmpegStacker("input.mp4", "output.mp4", "TestStreamer")
    editor.add_main_clip()
    editor.add_facecam_crop()
    editor.add_text_overlay()
    editor.add_logo_overlay()
    editor.add_vstack()
    filter_complex = editor.build_filter_complex()

    assert "[0:v]crop=1024:1080:448:0,scale=1080:1632[main]" in filter_complex
    assert "[0:v]crop=300:350:0:730,scale=1080:-1[cam]" in filter_complex
    assert "drawtext=text='TestStreamer'" in filter_complex
    assert "overlay=x=W-w-160:y=H-h-20[react]" in filter_complex
    assert "[main][react]vstack=inputs=2[out]" in filter_complex


@patch("editor.ffmpeg_wrapper.subprocess.run")
def test_ffmpeg_command_runs(mock_run):
    editor = FFmpegStacker("fake_input.mp4", "fake_output.mp4", "Streamer")
    editor.run()

    called_args = mock_run.call_args[0][0]
    assert "ffmpeg" in called_args[0]
    assert "fake_input.mp4" in called_args
    assert "fake_output.mp4" in called_args
    assert "-filter_complex" in called_args
    assert any("drawtext" in arg for arg in called_args if isinstance(arg, str))
    mock_run.assert_called_once()


def test_escaped_streamer_name():
    name = "O'Brien"
    editor = FFmpegStacker("input.mp4", "output.mp4", name)
    editor.add_text_overlay()
    part = next((f for f in editor.filter_parts if "drawtext" in f), "")
    expected_escaped = name.replace("'", "\\\\'")
    assert expected_escaped in part


def test_custom_logo_path():
    custom_logo = "assets/custom_logo.png"
    editor = FFmpegStacker("input.mp4", "output.mp4", "Streamer", logo_path=custom_logo)
    assert editor.logo_path == custom_logo


def test_empty_streamer_name_safe():
    editor = FFmpegStacker("input.mp4", "output.mp4", "")
    editor.add_text_overlay()
    part = next((f for f in editor.filter_parts if "drawtext" in f), "")
    assert "drawtext=text=''" in part


@pytest.mark.parametrize("name", ["O'Reilly", "John & Sons", "Text:Name"])
def test_streamer_name_escape_variants(name):
    editor = FFmpegStacker("input.mp4", "output.mp4", name)
    editor.add_text_overlay()
    part = next((f for f in editor.filter_parts if "drawtext" in f), "")
    expected = name.replace("'", "\\\\'")
    assert expected in part
