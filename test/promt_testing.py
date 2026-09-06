from Scraper.bestjobs_v3 import DOMAINS, database_connect
from Utils.LLM import LLM_activation


def get_sample_descriptions_by_domain(cursor, samples_per_domain=1):
    samples = {}
    for domain_name in DOMAINS.keys():
        cursor.execute(
            "SELECT slug, description FROM Jobs "
            "WHERE domain_name = ? AND description IS NOT NULL "
            "LIMIT ?",
            (domain_name, samples_per_domain)
        )
        samples[domain_name] = cursor.fetchall()
    return samples


def skills_extraction(description):
    prompt = """
    You are a professional recruiter analyzing a job description.
    Extract hard skills mentioned in the text below — concrete, verifiable tools, software, systems, certifications, methodologies, or specialized domain knowledge
    (e.g. Python, SQL, SAP, Google Ads, GDPR compliance, phlebotomy, payroll processing, AutoCAD). Do not include soft skills (e.g. "communication," "teamwork," "leadership").
    Classify each skill into his categoriy: required_skills: skills presented as mandatory (e.g. listed under Requirements, Must-have, Qualifications).
    If the posting does not distinguish between mandatory and optional, classify all extracted skills as required_skills.
    Return only a JSON object in exactly this shape, with no explanation, no markdown, no code fences:
{
  "required_skills": ["Python", "SQL"],
}
    If there are no skills for a category, return an empty list for that key — never omit the key or use null."""
    data = LLM_activation(prompt, description)
    return data


if __name__ == "__main__":
    cursor, conn = database_connect()
    samples = get_sample_descriptions_by_domain(cursor, samples_per_domain=1)

    for domain_name, rows in samples.items():
        print(f"\n===== {domain_name} =====")
        for slug, description in rows:
            print(f"\n--- {slug} ---")
            result = skills_extraction(description)
            print(result)

    conn.close()