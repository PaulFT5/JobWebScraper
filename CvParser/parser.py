from Utils.LLM import LLM_activation
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
pathToCV = BASE_DIR / "Data/CV/raw/Test.pdf"
pathToRawData = BASE_DIR / "Data/CV/raw/CV_Raw_Extracted_Data.txt"
pathToProcessedData = BASE_DIR / "Data/CV/processed/CV_Processed_Extracted_Data.txt"


def parse_cv():
    total_text = cv_data_extract()
    write_raw_data(total_text)
    process_write_extracted_data(total_text)


def cv_data_extract():
    total_text = ""
    with pdfplumber.open(pathToCV) as pdf:
        for page in pdf.pages:
            current_page_text = page.extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False, x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None)
            total_text += current_page_text
    return total_text


def write_raw_data(input_text):
    f = open(pathToRawData, "w", encoding="utf-8")
    f.write(input_text)
    f.close()


def process_write_extracted_data(input_raw_text):
    promt = "You are a professional recruiter analyzing a candidate's CV. Extract all skills from the CV text below and return them as a JSON object. Follow these rules strictly: Technical skills — categorize each by experience level using any explicit dates or context clues in the CV. If no experience level can be determined, default to Entry-level. entry_level (0–2 years) junior (2–3 years) mid_level (3–5 years) senior (5+ years) Soft skills — split into two lists: stated: skills explicitly mentioned by the candidate inferred: skills implied by their experiences and achievements. For each inferred skill you must provide a brief evidence field quoting or referencing the specific CV content that supports it. Do not infer a skill without evidence. Avoid generic filler skills unless strongly supported. Return only valid JSON. No explanation, no markdown, no code fences. Languages - return user's known languages"
    f = open(pathToProcessedData, "w", encoding="utf-8")
    f.write(LLM_activation(promt, input_raw_text))
    f.close()

