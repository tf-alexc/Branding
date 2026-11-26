// The Graphics Generator holiday post (LinkedIn Single, 1200x1600), as reusable parts.
window.W = {
  // A design-system SVG shown only as an image.
  svg(kit, name, cls) {
    return '<img class="' + cls + '" alt="" src="data:image/svg+xml,' + encodeURIComponent(kit.module(name)) + '">';
  },
  // R34 title tiers: 150 / 124 / 100 / 80 / 62px, picked from the title length (two rows max).
  titlePx(title) {
    const t = String(title || '').trim().toUpperCase(), words = t.split(/\s+/);
    const half = Math.max(Math.ceil(t.length / 2), ...words.map((w) => w.length));
    const perLine = t.length <= 18 ? t.length : half;
    const want = Math.max(56, Math.min(150, Math.floor(1080 / (0.66 * Math.max(perLine, 1)))));
    return [150, 124, 100, 80, 62].find((s) => s <= want) || 62;
  },
};