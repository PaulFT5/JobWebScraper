// word label so the level isn't shown by color alone
export function scoreLabel(score: number): string {
    if (score < 40) return 'Weak match';
    if (score <= 70) return 'Partial match';
    return 'Strong match';
}

export type ScoreTheme ={ badge: string; bar: string; ring: string; text: string };

// shared score colors: red < 40, amber up to 70, emerald above
export function scoreTheme(score: number): ScoreTheme {
    if (score < 40) {
        return {
            badge: 'border-red-300 bg-red-50 text-red-700',
            bar: 'bg-red-500',
            ring: 'stroke-red-500',
            text: 'text-red-600'
        };
    }
    if (score <= 70) {
        return {
            badge: 'border-amber-300 bg-amber-50 text-amber-700',
            bar: 'bg-amber-500',
            ring: 'stroke-amber-500',
            text: 'text-amber-600'
        };
    }
    return {
        badge: 'border-emerald-300 bg-emerald-50 text-emerald-700',
        bar: 'bg-emerald-500',
        ring: 'stroke-emerald-500',
        text: 'text-emerald-600'
    };
}
