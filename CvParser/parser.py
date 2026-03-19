from operator import truediv
from Utils.LLM import LLM_activation
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
pathToCV = "Data/CV/raw/Test.pdf"


def parse_cv():
    x = pdfplumber.open(pathToCV)
    text = x.pages[0].extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False, x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None)
    raw_extracted_data_write(text)
    processed_extracted_data_write()
    return text


def raw_extracted_data_write(input_text):
    f = open("C:/Users/User/PycharmProjects/JobWebScraper/Data/CV/raw/CV_Raw_Extracted_Data.txt", "w", encoding="utf-8")
    f.write(input_text)
    f.close()


def processed_extracted_data_write(): #goes through LLM
    f = open("C:/Users/User/PycharmProjects/JobWebScraper/Data/CV/raw/CV_Raw_Extracted_Data.txt", "r", encoding="utf-8")
    raw_data = f.read()
    f.close()

    promt = "Return skills as a JSON object with two keys: 'technical' and 'soft', each containing a list of skills. Technical will be split in: Entry-level (0–2 years), Junior (2–3 years), Mid-level (3–5 years), Senior (5+ years). If no experience level is mentioned, skills shall be put as entry level. Return only the JSON"
    LLM = LLM_activation(promt, raw_data)
    f = open("C:/Users/User/PycharmProjects/JobWebScraper/Data/CV/processed/CV_Processed_Extracted_Data.txt", "w", encoding="utf-8")
    f.write(LLM)
    f.close()




