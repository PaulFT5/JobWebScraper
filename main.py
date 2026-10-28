# main.py
from backend.api.main import app
from backend.utils.data_setup import data_folder_setup

data_folder_setup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
