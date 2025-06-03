import sys
import os
from editor.editor_pipeline import process_clip

def main():
    if len(sys.argv) < 3:
        print("Usage: python examples/run_clip_edit.py <input_path> <output_path> [streamer_name]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    streamer_name = sys.argv[3] if len(sys.argv) > 3 else ""

    if not os.path.exists(input_path):
        print(f"Error: input file not found at {input_path}")
        sys.exit(1)

    process_clip(input_path=input_path, output_path=output_path, streamer_name=streamer_name)

if __name__ == "__main__":
    main()
