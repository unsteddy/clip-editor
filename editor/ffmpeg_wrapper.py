import subprocess

def stack_main_and_reaction(input_path: str, output_path: str):
    """
    Final version: top is a wider 1024px crop, zoomed to 1080; bottom is bottom-300px reaction cam.
    Stacks both into a clean 1080x1920 vertical video.
    """

    filter_complex = (
        "[0:v]crop=1024:1080:448:0,scale=1080:1632[main];"          # zoomed-out main crop
        "[0:v]crop=300:300:0:780,scale=1080:-1[react];"             # bottom facecam, zoomed to full width
        "[main][react]vstack=inputs=2[out]"
    )

    cmd = [
        "ffmpeg",
        "-i", input_path,
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
