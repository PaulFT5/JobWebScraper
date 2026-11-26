import json
from backend.services.llm_service import llm_service
from backend.services.llm_output_validator import validate_cv_skills
import io
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
pathToCV = BASE_DIR / "data" / "cv" / "raw" / "Test.pdf"
pathToRawData = BASE_DIR / "data" / "cv" / "raw" / "CV_Raw_Extracted_Data.txt"
pathToProcessedData = BASE_DIR / "data" / "cv" / "processed" / "CV_Processed_Extracted_Data.json"

CV_PROMPT = """
    You are a professional recruiter analyzing a candidate's CV.
    Extract hard skills mentioned in the text below — concrete, verifiable tools, software, systems, certifications, methodologies, or specialized domain knowledge
    (e.g. Python, SQL, SAP, Google Ads, GDPR compliance, phlebotomy, payroll processing, AutoCAD). Do not include soft skills (e.g. "communication," "teamwork," "leadership") and do not include spoken/written language requirements (e.g. "English", "fluent in German") in the hard skills.

    Write every skill in English, even when the CV is in Romanian or another language. Translate generic skills into their usual English term (e.g. "contabilitate primară" -> "bookkeeping", "diagnosticare" -> "medical diagnosis"). Keep product, software, standard and certification names exactly as written (e.g. SAP, AutoCAD, ISO 9001, PCI DSS); do not translate or expand them.

    Each list item must be exactly one skill, written as a short noun phrase. If the text lists several skills together (in brackets, with commas, or joined by "and" or "/"), return each one as its own item. Keep a name as written when it is a single tool, standard or concept (e.g. CI/CD, TCP/IP, SAP S/4HANA). Do not include duties, tasks or degrees.

    Put each hard skill in exactly one experience tier, based only on professional work experience: paid jobs, internships and freelance work, using their dates in the CV.
    entry (0-2 years), mid (2-5 years), senior (5+ years).
    Education, courses, certifications, university projects and personal projects never count as years of experience, even when they have dates; a skill that appears only there goes in entry.
    A skill used in a job counts only the duration of the jobs where it is used, not the candidate's whole career.
    If a skill is mentioned without any job or education context to place it, put it in unknown.

    Also list the spoken/written languages the candidate knows, in English (e.g. "English", "German").

    Return only a JSON object in exactly this shape, with no explanation, no markdown, no code fences:
{
  "hard_skills": {"entry": [], "mid": [], "senior": [], "unknown": []},
  "languages": []
}

    Every key is always present; use an empty list when there is nothing for it, never omit a key or use null."""


def parse_cv():
    total_text = cv_data_extract()
    write_raw_data(total_text)
    return process_write_extracted_data(total_text)


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
    cv_skills = validate_cv_skills(llm_service(CV_PROMPT, input_raw_text))
    with open(pathToProcessedData, "w", encoding="utf-8") as f:
        json.dump(cv_skills, f, ensure_ascii=False, indent=2)
    return cv_skills


def parse_cv_pdf(pdf_bytes):
    """Uploaded PDF (bytes) -> validated CV dict. Reads in memory and writes no files (session-only CV)."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = "".join(page.extract_text(x_tolerance=3, y_tolerance=3) or "" for page in pdf.pages)
    if not text.strip():
        raise ValueError("The PDF has no extractable text (scanned image?)")
    return validate_cv_skills(llm_service(CV_PROMPT, text))


if __name__ == "__main__": print(parse_cv())

