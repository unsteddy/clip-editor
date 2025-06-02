import subprocess


def stack_main_and_reaction(input_path: str, output_path: str, streamer_name: str = ""):
    """
    Final output with Twitch logo and streamer name in styled lower border.
    - Logo (40x40) is placed left of the name.
    """

    safe_name = streamer_name.replace("'", "\\\\'")

    filter_complex = (
        # Top: slightly zoomed-out main subject
        "[0:v]crop=1024:1080:448:0,scale=1080:1632[main];"

        # Bottom: crop facecam, zoom to full width
        "[0:v]crop=300:350:0:730,scale=1080:-1[cam];"

        # Draw box and name overlay
        "[cam]drawbox=0:0:iw:ih:white@1:4,"
        f"drawtext=text='{safe_name}':"
        "fontcolor=white:fontsize=28:x=w-tw-20:y=h-th-20:"
        "box=1:boxcolor=black@0.5:boxborderw=4[react_text];"

        # Overlay logo (input 1) before the name
        "[1:v]scale=40:40[logo];"
        "[react_text][logo]overlay=x=W-w-160:y=H-h-20[react];"

        # Stack vertically
        "[main][react]vstack=inputs=2[out]"
    )

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-i", "assets/twitch_logo_40px.png",  # logo input
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "24",
        "-c:a", "copy",
        "-y",
        output_path
    ]

    print("Running FFmpeg command:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
