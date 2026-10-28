export type Option = { id: string | number; name: string };

export type Job = {
    source: string;
    slug: string;
    title: string;
    company: string | null;
    salary: string | null;
    estimated_salary: string | null;
    work_type: string | null;
    experience_level: string | null;
    city: string | null;
    domain: string | null;
    required_skills: string | null;
    ad_link: string | null;
};