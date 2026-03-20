# main.py
from pathlib import Path
from CvParser.parser import parse_cv
from Utils.setup import data_folder_setup
from Utils.LLM import LLM_activation

def main():
    data_folder_setup() #setup Data files
    parse_cv()

main()