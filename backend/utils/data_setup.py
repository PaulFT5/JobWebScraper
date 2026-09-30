import os
from pathlib import Path

Base_path = Path(__file__).parent.parent

#cv dir
CV_dir_path = Base_path / "data/CV"
Cv_processed_path = Base_path / "data/CV/processed"
Cv_raw_path = Base_path / "data/CV/raw"

#job dir
Job_dir_path = Base_path / "data/Jobs"
Job_raw_path = Base_path / "data/Jobs/raw"
Job_processed_path = Base_path / "data/Jobs/processed"


def data_folder_setup():
    main_data_dir_setup(CV_dir_path) #create data/CV
    main_data_dir_setup(Cv_processed_path) #create data/CV/processed
    main_data_dir_setup(Cv_raw_path) #create data/CV/raw
    main_data_dir_setup(Job_dir_path) #create data/Jobs
    main_data_dir_setup(Job_raw_path)
    main_data_dir_setup(Job_processed_path)

def main_data_dir_setup(path):
    nested_directory = path

    try:
        #os.makedirs(nested_directory)
        nested_directory.mkdir(parents=True, exist_ok=True) #parents creates folders in between, exists prevents errors if file exists
        print(f"Nested directories '{nested_directory}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
