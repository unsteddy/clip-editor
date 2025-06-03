import os


def write_srt(subs, path):
    """
    Writes a list of subtitle segments to an .srt file.
    Each item in `subs` must be a dict with 'start', 'end', and 'text'.
    """

    def format_timestamp(t):
        hrs, rem = divmod(t, 3600)
        mins, secs = divmod(rem, 60)
        millis = int((secs - int(secs)) * 1000)
        return f"{int(hrs):02}:{int(mins):02}:{int(secs):02},{millis:03}"

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(subs, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
