import os
from editor.ffmpeg_wrapper import stack_main_and_reaction


def main():
    input_file = "assets/sample_clip.mp4"
    output_file = "output/vertical_clip.mp4"

    # Make sure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"Processing: {input_file}")
    stack_main_and_reaction(input_file, output_file)
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()
