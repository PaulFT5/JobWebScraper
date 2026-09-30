from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent

cv_raw = root / "data" / "cv" / "raw"
cv_processed = root / "data" / "cv" / "processed"

def data_folder_setup():
    cv_raw.mkdir(parents=True, exist_ok=True)
    cv_processed.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    data_folder_setup()
