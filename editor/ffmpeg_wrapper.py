import subprocess


class FFmpegStacker:
    def __init__(self, input_path: str, output_path: str, streamer_name: str = "",
                 logo_path: str = "assets/twitch_logo_40px.png"):
        self.input_path = input_path
        self.output_path = output_path
        self.streamer_name = streamer_name.replace("'", "\\\\'")
        self.logo_path = logo_path
        self.filter_parts = []

    def add_main_clip(self):
        # Top part: game area
        self.filter_parts.append("[0:v]crop=1024:1080:448:0,scale=1080:1632[main]")

    def add_facecam_crop(self):
        # Bottom part: cropped facecam area
        self.filter_parts.append("[0:v]crop=300:350:0:730,scale=1080:-1[cam]")

    def add_text_overlay(self):
        # Add drawbox and drawtext on the facecam crop
        text = (
            "[cam]drawbox=0:0:iw:ih:white@1:4,"
            f"drawtext=text='{self.streamer_name}':"
            "fontcolor=white:fontsize=28:x=w-tw-20:y=h-th-20:"
            "box=1:boxcolor=black@0.5:boxborderw=4[react_text]"
        )
        self.filter_parts.append(text)

    def add_logo_overlay(self):
        # Scale the logo and overlay onto facecam + text
        self.filter_parts.append("[1:v]scale=40:40[logo]")
        self.filter_parts.append("[react_text][logo]overlay=x=W-w-160:y=H-h-20[react]")

    def add_vstack(self):
        # Final vertical stack
        self.filter_parts.append("[main][react]vstack=inputs=2[out]")

    def build_filter_complex(self):
        self.add_main_clip()
        self.add_facecam_crop()
        self.add_text_overlay()
        self.add_logo_overlay()
        self.add_vstack()
        return ";".join(self.filter_parts)

    def run(self):
        filter_complex = self.build_filter_complex()

        cmd = [
            "ffmpeg",
            "-i", self.input_path,
            "-i", self.logo_path,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "24",
            "-c:a", "copy",
            "-y",
            self.output_path
        ]

        print("Running FFmpeg command:")
        print(" ".join(cmd))
        subprocess.run(cmd, check=True)
