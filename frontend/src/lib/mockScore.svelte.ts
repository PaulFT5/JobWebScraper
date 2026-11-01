// TEMPORARY: a mock match score to preview score colors (circle, card badge and bar) before the matcher exists.
// Delete together with MockScoreSwitch.svelte; ScoreCard and JobPanel then go back to no score.
export const mockScore = $state({ value: null as number | null });
