// The Graphics Generator tradeshow post (LinkedIn Standard, 1200x1600), as reusable parts.
window.W = {
  // A design-system SVG shown only as an image.
  svg(kit, name, cls) {
    return '<img class="' + cls + '" alt="" src="data:image/svg+xml,' + encodeURIComponent(kit.module(name)) + '">';
  },
  // Course plate (wavy lines split onto their own layer so they can move) + venue/city photo at 20% opacity, 4px blur (R27).
  backdrop(kit, cls) {
    return '<div class="ts-layer ' + cls + '"><div class="ts-plate" style="background-image:url(' + kit.assets.url('plate-clean.jpg') + ')"></div>' +
      '<img class="ts-lines ' + cls + '-lines" alt="" src="' + kit.assets.url('plate-lines.webp') + '">' +
      (kit.assets.has('city.jpg') ? '<img class="ts-photo" alt="" src="' + kit.assets.url('city.jpg') + '">' : '') + '</div>';
  },
  // R11: shrink the content column (from its top-left) so it ends 56px above the pill row. Measured once, after fonts load.
  async fit(col, pills) {
    try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (e) {}
    const room = pills.offsetTop - 56 - col.offsetTop, h = col.offsetHeight;
    const s = h > room && h > 0 ? room / h : 1;
    col.style.transformOrigin = '0 0';
    col.style.transform = s < 1 ? 'scale(' + s.toFixed(4) + ')' : '';
  },
  // Continuous drift of the wavy lines: a slow sway and a gentle swell from the bottom edge.
  lines(el, t) {
    const p = 2 * Math.PI;
    el.style.transform = 'translate(' + (26 * Math.sin(p * t / 5)).toFixed(2) + 'px,' + (14 * Math.sin(p * t / 4 + 1)).toFixed(2) + 'px) scaleY(' + (1 + 0.06 * Math.sin(p * t / 4.5 + 0.5)).toFixed(4) + ') skewX(' + (2 * Math.sin(p * t / 6)).toFixed(3) + 'deg)';
  },
  // One attendee: window-crop portrait in the Electric pill frame, name, title, brand (R25).
  person(kit, cls, file, name, role, brand) {
    return '<div class="ts-person ' + cls + '"><div class="ts-frame"><img alt="" src="' + kit.assets.url(file) + '"></div>' +
      '<div class="ts-who"><div class="ts-name">' + name + '</div><div class="ts-role">' + role + '</div><div class="ts-role">' + brand + '</div></div></div>';
  },
  // A Dark Blue detail pill with its icon (R20, R26).
  pill(kit, cls, iconModule, iconCls, text) {
    return '<div class="ts-pill ' + cls + '">' + W.svg(kit, iconModule, iconCls) + '<span>' + text + '</span></div>';
  },
};