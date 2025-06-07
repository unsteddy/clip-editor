# setup_models.py
import os
import subprocess

# Ensure debug directory exists
os.makedirs("debug_frames", exist_ok=True)

# Install stable versions
print("📦 Installing paddlepaddle-gpu 2.6.1 and paddleocr 2.6.0.1...")

try:
    subprocess.run(
        [
            "pip", "install", "paddlepaddle-gpu==2.6.1",
            "-f", "https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html"
        ],
        check=True
    )
    subprocess.run(
        ["pip", "install", "paddleocr==2.7.0.3"],
        check=True
    )

except subprocess.CalledProcessError:
    print("❌ Failed to install paddlepaddle-gpu or paddleocr. Please install manually.")
    exit(1)

print("✅ PaddleOCR and PaddlePaddle GPU installed.")
