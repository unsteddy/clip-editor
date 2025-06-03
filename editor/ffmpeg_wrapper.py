import subprocess


class FFmpegStacker:
    def __init__(self, input_path: str, output_path: str, streamer_name: str = "",
                 logo_path: str = "assets/twitch_logo_40px.png"):
        self.input_path = input_path
        self.output_path = output_path
        self.streamer_name = streamer_name.replace("'", "\\\\'")
        self.logo_path = logo_path
        self.filter_parts = []

        self.streamer_srt = None
        self.others_srt = None

    def add_subtitle_layers(self, streamer_srt: str, others_srt: str):
        self.streamer_srt = streamer_srt
        self.others_srt = others_srt

        self.filter_parts.append(
            f"[0:v]subtitles='{streamer_srt}':force_style='FontName=NotoSansCJK-Regular,Alignment=1'[s1]"
        )
        self.filter_parts.append(
            f"[s1]subtitles='{others_srt}':force_style='FontName=NotoSansCJK-Regular,Alignment=9'[vsubbed]"
        )

    def add_main_clip(self):
        # Scale to width 1080 and pad to 1920 height, keeping aspect ratio
        self.filter_parts.append("[vsubbed]scale=1080:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2[main]")

    def build_filter_complex(self):
        self.filter_parts.clear()

        if self.streamer_srt and self.others_srt:
            self.add_subtitle_layers(self.streamer_srt, self.others_srt)
        else:
            # Just pass the video unchanged
            self.filter_parts.append("[0:v]format=yuv420p[vsubbed]")

        self.add_main_clip()
        return ";".join(self.filter_parts)

    def run(self):
        filter_complex = self.build_filter_complex()

        cmd = [
            "ffmpeg",
            "-i", self.input_path,
            "-i", self.logo_path,
            "-filter_complex", filter_complex,
            "-map", "[main]",
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
