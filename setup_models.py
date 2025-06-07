# setup_models.py
import os
import urllib.request

model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "frozen_east_text_detection.pb")
url = "https://github.com/oyyd/frozen_east_text_detection.pb/raw/master/frozen_east_text_detection.pb"

if not os.path.exists(model_path):
    print("📥 Downloading EAST model...")
    urllib.request.urlretrieve(url, model_path)
    print("✅ Download complete.")
else:
    print("✔️ EAST model already exists.")
