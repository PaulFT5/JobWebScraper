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
export type CvSkill = { name: string; tier: string; status: 'match' | 'ambiguous' | 'not found' };

export type MatchResponse = {
    session_id: string;
    skills: CvSkill[];
    // job key ("source/slug") -> score 0-100
    scores: Record<string, number>;
};

export type MatchReport = {
    score: number | null;
    requirements: { requirement: string; best_cv_skill: string | null; value: number }[];
    missing: string[];
};
