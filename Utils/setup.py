import os
from pathlib import Path
#This will create the Data folder with subfolders

Base_path = Path(__file__).parent.parent

#cv dir
CV_dir_path = Base_path / "Data/CV"
Cv_processed_path = Base_path / "Data/CV/processed"
Cv_raw_path = Base_path / "Data/CV/raw"

#job dir
Job_dir_path = Base_path / "Data/Jobs"
Job_raw_path = Base_path / "Data/Jobs/raw"
Job_processed_path = Base_path / "Data/Jobs/processed"


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
