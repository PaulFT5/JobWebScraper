from operator import truediv
from Utils.LLM import LLM_activation
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
pathToCV = BASE_DIR / "Data/CV/raw/Test.pdf"
pathToRawData = BASE_DIR / "Data/CV/raw/CV_Raw_Extracted_Data.txt"
PathToProcessedData = BASE_DIR / "Data/CV/processed/CV_Processed_Extracted_Data.txt"


def parse_cv():
    cv_data_extract()
    process_write_extracted_data()


def cv_data_extract():
    with pdfplumber.open(pathToCV) as pdf:
        for page in pdf.pages:
            current_page_text = page.extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False, x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None)
            append_raw_data_text(current_page_text)


def append_raw_data_text(input_text):
    f = open(pathToRawData, "a", encoding="utf-8")
    f.write(input_text)
    f.close()


def read_raw_data():
    f = open(pathToRawData, "r", encoding="utf-8")
    raw_data = f.read()
    f.close()
    return raw_data


def process_write_extracted_data():
    raw_data = read_raw_data()

    promt = "You are a professional recruiter analyzing a candidate's CV. Extract all skills from the CV text below and return them as a JSON object. Follow these rules strictly: Technical skills — categorize each by experience level using any explicit dates or context clues in the CV. If no experience level can be determined, default to Entry-level. entry_level (0–2 years) junior (2–3 years) mid_level (3–5 years) senior (5+ years) Soft skills — split into two lists: stated: skills explicitly mentioned by the candidate inferred: skills implied by their experiences and achievements. For each inferred skill you must provide a brief evidence field quoting or referencing the specific CV content that supports it. Do not infer a skill without evidence. Avoid generic filler skills unless strongly supported. Return only valid JSON. No explanation, no markdown, no code fences. "
    f = open(PathToProcessedData, "w", encoding="utf-8")
    f.write(LLM_activation(promt, raw_data))
    f.close()


#def process_data(text):
#    raw_extracted_data_write(text)
#   processed_extracted_data_write()


#def raw_extracted_data_write(input_text):
#    f = open(pathToRawData, "w", encoding="utf-8")
#    f.write(input_text)
#    f.close()
