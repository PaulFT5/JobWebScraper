// Sample data for the Analyzer mock (FE_NOTES L4). Nothing here comes from the API yet;
// every section is replaced by real endpoints once grounding stats and timings exist.

export type Method = 'exact' | 'fuzzy' | 'embedding' | 'unresolved';

export const METHODS: Method[] = ['exact', 'fuzzy', 'embedding', 'unresolved'];

export const METHOD_LABELS: Record<Method, string> = {
    exact: 'Exact',
    fuzzy: 'Fuzzy',
    embedding: 'Embedding',
    unresolved: 'Unresolved'
};

// categorical slots 1–3 (validated); unresolved is a neutral, not a category
export const METHOD_COLORS: Record<Method, string> = {
    exact: '#2a78d6',
    fuzzy: '#eb6834',
    embedding: '#1baf7a',
    unresolved: '#cbd5e1'
};

// ---------- Extraction ----------

export const funnel = [
    { label: 'Jobs scraped', value: 5203 },
    { label: 'With description', value: 5153 },
    { label: 'Skills extracted', value: 3420 },
    { label: 'Extraction failed', value: 13 }
];

export const methodShare: Record<Method, number> = { exact: 6120, fuzzy: 1190, embedding: 2240, unresolved: 3280 };

export const latency: { method: Method; median: number; p95: number }[] = [
    { method: 'exact', median: 0.02, p95: 0.05 },
    { method: 'fuzzy', median: 9.4, p95: 14.8 },
    { method: 'embedding', median: 31, p95: 58 },
    { method: 'unresolved', median: 41, p95: 72 }
];

export const llmTiming = { medianSec: 6.8, p95Sec: 14.2, cacheHitRate: 0.71, skillsPerJob: 8.9 };

// seconds per job extraction, bucketed
export const llmHistogram = [
    { label: '0–3 s', value: 140 },
    { label: '3–6 s', value: 1180 },
    { label: '6–9 s', value: 1320 },
    { label: '9–12 s', value: 520 },
    { label: '12–15 s', value: 190 },
    { label: '> 15 s', value: 70 }
];

export const topUnresolved = [
    { skill: 'Docker', count: 214 },
    { skill: 'Kubernetes', count: 163 },
    { skill: 'CI/CD', count: 152 },
    { skill: 'Microsoft Excel', count: 131 },
    { skill: 'AutoCAD', count: 88 },
    { skill: 'Power BI', count: 76 },
    { skill: 'SAP S/4HANA', count: 41 },
    { skill: 'Legea 98/2016', count: 23 }
];

export type CvSkill = { skill: string; tier: string; method: Method; ms: number };

export const sampleCv: CvSkill[] = [
    { skill: 'Python', tier: 'mid', method: 'exact', ms: 0.03 },
    { skill: 'SQL', tier: 'mid', method: 'exact', ms: 0.02 },
    { skill: 'PostgreSQL', tier: 'junior', method: 'exact', ms: 0.02 },
    { skill: 'MS Exel', tier: 'senior', method: 'fuzzy', ms: 9.8 },
    { skill: 'Git', tier: 'mid', method: 'exact', ms: 0.02 },
    { skill: 'REST APIs', tier: 'junior', method: 'embedding', ms: 34 },
    { skill: 'Data visualisation', tier: 'junior', method: 'embedding', ms: 29 },
    { skill: 'Docker', tier: 'entry', method: 'unresolved', ms: 47 }
];

export const cvTiming = { parseSec: 7.4, groundingMs: 120 };

// ---------- Matching ----------

export const METRICS = [
    { id: 'chamfer', name: 'Directed Chamfer', note: 'Mean of the best CV match per requirement. UI default.', ready: true },
    { id: 'tversky', name: 'Continuous Tversky', note: 'Overlap with α = 0.8 for missing requirements, β = 0.2 for extra skills.', ready: false },
    { id: 'soft_cosine', name: 'Soft Cosine', note: 'Cosine over the union of skills, using skill-to-skill similarity.', ready: false },
    { id: 'hungarian', name: 'Hungarian', note: 'Best one-to-one assignment, divided by the number of requirements.', ready: false }
] as const;

// stable pseudo-similarity so the mock looks the same on every reload
function hash(s: string): number {
    let h = 2166136261;
    for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
    return (h >>> 0) / 4294967295;
}

export function mockSimilarity(requirement: string, cvSkill: string): number {
    const a = requirement.trim().toLowerCase();
    const b = cvSkill.trim().toLowerCase();
    if (a === b) return 1;
    if (a.includes(b) || b.includes(a)) return 0.82;
    const v = hash(a + '|' + b);
    return v > 0.9 ? 0.6 + (v - 0.9) * 3 : v * 0.5;
}

export function mockMethod(skill: string): Method {
    const v = hash(skill.toLowerCase());
    return v < 0.5 ? 'exact' : v < 0.62 ? 'fuzzy' : v < 0.8 ? 'embedding' : 'unresolved';
}

// rough relative offsets so the not-yet-built metrics show as different numbers
export const METRIC_OFFSETS: Record<string, number> = { chamfer: 0, tversky: -6, soft_cosine: 4, hungarian: -11 };

// ---------- Jobs ----------

// the first ad with a scrape date is from 2026-10-05; older rows have no date and are left out of time views
export const FIRST_SCRAPE = '2026-10-05';
export const PERIODS = ['Since first scrape', 'Last 2 weeks', 'Last week'] as const;

export type ConceptRow = { concept: string; jobs: number; share: number; change: number };

const BASE_CONCEPTS: [string, number][] = [
    ['SQL', 412], ['Python (computer programming)', 388], ['JavaScript', 301], ['use Microsoft Office', 296],
    ['project management', 274], ['Java (computer programming)', 251], ['manage budgets', 198], ['accounting', 187],
    ['customer relationship management', 176], ['Git', 164], ['agile project management', 152], ['React', 141],
    ['search engine optimisation', 118], ['AutoCAD', 103], ['negotiate supplier arrangements', 97]
];

// domain changes which concepts lead, period scales the counts
export function topConcepts(domain: string, period: string): ConceptRow[] {
    const scale = period === 'All time' || period === 'Since first scrape' ? 1 : period === 'Last 2 weeks' ? 0.52 : 0.27;
    const total = Math.round(1733 * scale);
    return BASE_CONCEPTS.map(([concept, n]) => {
        const weight = domain === 'All domains' ? 1 : 0.25 + hash(domain + concept) * 1.5;
        const jobs = Math.max(1, Math.round(n * scale * weight));
        return { concept, jobs, share: jobs / total, change: Math.round((hash(concept + period) - 0.45) * 40) };
    });
}

// categorical slots 1–8 in fixed order (validated); a skill keeps its color for as long as it is listed
export const SERIES_COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948'];

export type SkillTrend = {
    concept: string;
    counts: number[]; // jobs per week with this skill
    shares: number[]; // % of the week's analyzed postings
    ranks: (number | null)[]; // 1 = most requested that week, null = outside the top 10
};

export type WeeklySkills = { weeks: string[]; totals: number[]; skills: SkillTrend[] };

const WEEK_STARTS = ['10-05', '10-12', '10-19', '10-26'];

// weeks are Mondays (first-seen date of the ad), starting at FIRST_SCRAPE; skills sorted by share over the period
export function weeklySkills(domain: string, period: string): WeeklySkills {
    const all = WEEK_STARTS.map((w) => '2026-' + w);
    const weeks = period === 'Last 2 weeks' ? all.slice(-2) : period === 'Last week' ? all.slice(-1) : all;

    // analyzed postings per week; dips (e.g. a holiday week) move counts but not shares
    const totals = weeks.map((w) => Math.round(150 * (0.7 + hash('total' + domain + w) * 0.6)));

    const skills = topConcepts(domain, 'All time').map(({ concept, jobs }) => {
        const counts = weeks.map((w, i) => {
            const wave = 0.8 + hash(concept + w) * 0.4;
            const trend = 1 + (hash(concept + domain) - 0.5) * 0.12 * i;
            return Math.min(totals[i], Math.max(0, Math.round(totals[i] * (jobs / 1733) * wave * trend)));
        });
        return { concept, counts, shares: counts.map((c, i) => (c / totals[i]) * 100), ranks: [] as (number | null)[] };
    });

    weeks.forEach((_, i) => {
        const order = [...skills].sort((a, b) => b.counts[i] - a.counts[i]);
        order.forEach((s, r) => s.ranks.push(r < 10 ? r + 1 : null));
    });

    return { weeks, totals, skills: skills.sort((a, b) => periodShare(b, totals) - periodShare(a, totals)) };
}

// share of all postings in the period: summed counts over summed totals, so busy weeks weigh more
export function periodShare(s: SkillTrend, totals: number[]): number {
    const postings = totals.reduce((a, b) => a + b, 0);
    return postings ? (s.counts.reduce((a, b) => a + b, 0) / postings) * 100 : 0;
}

export function weekLabel(week: string): string {
    const [, m, d] = week.split('-');
    return `${Number(d)} ${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][Number(m) - 1]}`;
}

export const LEVELS = ['No experience', 'Entry', 'Mid-level', 'Senior', 'Executive', 'Not specified'];

export function levelMix(domain: string): { level: string; value: number }[] {
    return LEVELS.map((level) => ({ level, value: Math.round(20 + hash(domain + level) * 180) }));
}

// ---------- Most required skills (view 1) ----------

export type TopSkill = { concept: string; jobs: number; share: number; inEsco: boolean };

export type TopSkillFilters = { domain: string; level: string; city: string; period: string };

// skills grounding could not map to ESCO are counted by their cleaned name
const UNRESOLVED_MOCK: [string, number][] = [['Docker', 214], ['CI/CD', 152]];

// 100% = postings with extracted skills that match the filters; each skill counted once per job
export function topSkills(f: TopSkillFilters, top = 10): { postings: number; skills: TopSkill[] } {
    const key = `${f.domain}|${f.level}|${f.city}`;
    const narrow = (f.domain === 'All domains' ? 1 : 0.22) * (f.level === 'all' ? 1 : 0.3) * (f.city === 'All cities' ? 1 : 0.45);
    const scale = f.period === 'Since first scrape' ? 1 : f.period === 'Last 2 weeks' ? 0.52 : 0.27;
    const postings = Math.max(12, Math.round(1733 * narrow * scale));
    const pool: [string, number, boolean][] = [
        ...BASE_CONCEPTS.map(([c, n]): [string, number, boolean] => [c, n, true]),
        ...UNRESOLVED_MOCK.map(([c, n]): [string, number, boolean] => [c, n, false])
    ];
    const skills = pool
        .map(([concept, n, inEsco]) => {
            const weight = key === 'All domains|all|All cities' ? 1 : 0.3 + hash(key + concept) * 1.4;
            const share = Math.min(0.95, (n / 1733) * weight * (0.9 + hash(f.period + concept) * 0.2));
            const jobs = Math.max(1, Math.round(share * postings));
            return { concept, jobs, share: (jobs / postings) * 100, inEsco };
        })
        .sort((a, b) => b.share - a.share)
        .slice(0, top);
    return { postings, skills };
}

// ESCO labels carry a trailing qualifier ("Java (computer programming)"); the UI shows the short name
export function displayName(concept: string): string {
    return concept.replace(/\s*\([^)]*\)\s*$/, '');
}

// ---------- Rank change (slope chart) ----------

export type SlopeRow = { concept: string; start: number; end: number }; // ranks; 11 = outside the top 10

export const SLOPE_OUTSIDE = 11;

// ranks on pooled counts: the first two dated weeks vs the last two
export function slopeData(domain: string): { startLabel: string; endLabel: string; rows: SlopeRow[] } {
    const { weeks, skills } = weeklySkills(domain, 'Since first scrape');
    const span = Math.min(2, Math.floor(weeks.length / 2)) || 1;
    const sum = (v: number[], from: number, to: number) => v.slice(from, to).reduce((x, y) => x + y, 0);
    const rankBy = (pick: (counts: number[]) => number) => {
        const order = [...skills].sort((x, y) => pick(y.counts) - pick(x.counts));
        return new Map(order.map((s, i) => [s.concept, i + 1]));
    };
    const start = rankBy((c) => sum(c, 0, span));
    const end = rankBy((c) => sum(c, weeks.length - span, weeks.length));
    const rows = skills
        .map((s) => ({ concept: s.concept, start: Math.min(start.get(s.concept)!, SLOPE_OUTSIDE), end: Math.min(end.get(s.concept)!, SLOPE_OUTSIDE) }))
        .filter((r) => r.start < SLOPE_OUTSIDE || r.end < SLOPE_OUTSIDE);
    const label = (from: number, to: number) => (to - from === 1 ? weekLabel(weeks[from]) : `${weekLabel(weeks[from])} – ${weekLabel(weeks[to - 1])}`);
    return { startLabel: label(0, span), endLabel: label(weeks.length - span, weeks.length), rows };
}

// ---------- Specificity (scatter) ----------

export type SpecificityPoint = { concept: string; share: number; concentration: number; topDomain: string };

// concentration = share of the skill's postings that fall in its single most common domain
export function specificity(domains: string[]): SpecificityPoint[] {
    return topConcepts('All domains', 'Since first scrape').map((c) => {
        const weights = domains.map((d) => 0.2 + Math.pow(hash('spec' + c.concept + d), 3) * 3);
        const total = weights.reduce((a, b) => a + b, 0);
        const max = Math.max(...weights);
        return {
            concept: c.concept,
            share: c.share * 100,
            concentration: domains.length ? (max / total) * 100 : 0,
            topDomain: domains[weights.indexOf(max)] ?? '—'
        };
    });
}

// ---------- Co-occurrence ----------

// % of the jobs asking for `concept` that also ask for each other skill
export function coOccurrence(concept: string): { concept: string; pct: number }[] {
    return BASE_CONCEPTS.map(([c]) => c)
        .filter((c) => c !== concept)
        .map((c) => ({ concept: c, pct: Math.round(Math.pow(hash('co' + [concept, c].sort().join('|')), 2) * 90 + 3) }))
        .sort((a, b) => b.pct - a.pct)
        .slice(0, 8);
}

// ---------- Category treemap ----------

// hand-made groups for the mock; real groups would come from the ESCO hierarchy (esco/graph.py)
export const CATEGORIES: { name: string; concepts: string[] }[] = [
    { name: 'Software development', concepts: ['Python (computer programming)', 'JavaScript', 'Java (computer programming)', 'Git', 'React'] },
    { name: 'Data & databases', concepts: ['SQL'] },
    { name: 'Business & management', concepts: ['project management', 'agile project management', 'manage budgets', 'negotiate supplier arrangements'] },
    { name: 'Office & finance', concepts: ['use Microsoft Office', 'accounting'] },
    { name: 'Marketing & sales', concepts: ['customer relationship management', 'search engine optimisation'] },
    { name: 'Engineering & design', concepts: ['AutoCAD'] }
];
