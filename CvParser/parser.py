from operator import truediv
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
pathToCV = "Data/CV/raw/Test.pdf"

def parse_cv():
    x = pdfplumber.open(pathToCV)
    text = x.pages[0].extract_text_simple()
    print(text)
    return text


