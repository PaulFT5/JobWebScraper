# main.py
from backend.cv_parser.parser import parse_cv
from backend.utils.data_setup import data_folder_setup


def main():
    data_folder_setup()
    parse_cv()

main()