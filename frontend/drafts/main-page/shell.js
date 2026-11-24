// Shared helpers for the main-page mocks.

// The signature mark: an orange (CV) and a blue (job) disc whose overlap grows with the fit.
// 0 = the discs just touch; 100 = they sit on top of each other (all brown). null = no score: two empty rings.
function overlap(score, r) {
  const gap = 2 * r;                                  // centre distance at score 0 (touching)
  const d = score == null ? gap : gap * (1 - Math.max(0, Math.min(100, score)) / 100);
  const w = 2 * r + gap + 2, h = 2 * r + 2;
  const cx1 = r + 1 + (gap - d) / 2, cx2 = cx1 + d, cy = r + 1;
  const label = score == null ? 'no score yet' : `fit ${score} of 100`;
  if (score == null) {
    return `<svg class="ov" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${label}">
      <circle cx="${cx1}" cy="${cy}" r="${r - 0.75}" fill="none" stroke="#c9c3b4" stroke-width="1.5" stroke-dasharray="3 2.5"/>
      <circle cx="${cx2}" cy="${cy}" r="${r - 0.75}" fill="none" stroke="#c9c3b4" stroke-width="1.5" stroke-dasharray="3 2.5"/></svg>`;
  }
  return `<svg class="ov" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${label}">
    <circle cx="${cx1}" cy="${cy}" r="${r}" fill="#ff7a1a"/>
    <circle cx="${cx2}" cy="${cy}" r="${r}" fill="#2f5bea" style="mix-blend-mode:multiply"/></svg>`;
}

// Score bands (PRODUCT.md, since 2026-11-24): weak < 50, partial 50–70, strong above. Always shown as words next to the number.
function band(score) { return score > 70 ? 'Strong fit' : score >= 50 ? 'Partial fit' : 'Weak fit'; }

// Small legend dots: 'fit' = brown overlap chip, 'job' = blue ring (a skill only the job has), 'cv' = orange.
function dot(kind) {
  if (kind === 'fit') return `<svg width="16" height="12" viewBox="0 0 16 12" style="isolation:isolate"><circle cx="5.5" cy="6" r="5" fill="#ff7a1a"/><circle cx="10.5" cy="6" r="5" fill="#2f5bea" style="mix-blend-mode:multiply"/></svg>`;
  if (kind === 'job') return `<svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="4.75" fill="none" stroke="#2f5bea" stroke-width="2"/></svg>`;
  // neutral marks for the CV review groups (orange and blue keep their CV / job meaning elsewhere)
  if (kind === 'half') return `<svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="4.75" fill="none" stroke="#14141a" stroke-width="1.5"/><path d="M6 1.25a4.75 4.75 0 0 1 0 9.5z" fill="#14141a"/></svg>`;
  if (kind === 'ring') return `<svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="4.75" fill="none" stroke="#55534c" stroke-width="1.5"/></svg>`;
  return `<svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5.5" fill="#ff7a1a"/></svg>`;
}

// Source values shown in plain English (FE_NOTES: "Fără" = no experience required; "Middle" = mid-level)
function levelName(v) { return v === 'Fără' ? 'No experience' : v === 'Middle' ? 'Mid-level' : (v || 'Not given'); }

// The You button in the top bar: a small mark plus the CV state.
function youBadge(text, hasCv) {
  const m = document.getElementById('youMark'), s = document.getElementById('youState');
  if (m) m.innerHTML = hasCv ? overlap(62, 7) : overlap(null, 7);
  if (s) s.textContent = text;
}
