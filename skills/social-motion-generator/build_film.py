#!/usr/bin/env python3
"""Build every document a social motion film needs, from a short JSON spec.

Two steps (see SKILL.md):

  python3 build_film.py prepare spec.json --ds <design-system project dir> --out <work dir>
      Crops and saves the raster images to <out>/upload/ (upload these to the film),
      and writes the film's modules to <out>/docs/.

  python3 build_film.py assets <out> --blobs blobs.json
      blobs.json maps each uploaded file name to its blob id ("plate-clean.jpg": "3e44...").
      Writes the assets docs and <out>/writes.json: a ready-made `writes` array for one
      ArtifactData batch. The scene and the final scenes.json are written after it:
      <out>/docs/scene.json and <out>/docs/scenes-final.json.

Needs Python 3 with Pillow and numpy. No network access: everything comes from the
design system download (--ds) and the files named in the spec.
"""
import argparse, json, os, re, shutil, sys
from html import escape
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

BRANDS = {
    'trustflight': {'label': 'TrustFlight', 'url': 'TRUSTFLIGHT.COM',
                    'white': 'logos/trustflight-logo-horizontal-white.svg',
                    'dark': 'logos/trustflight-logo-horizontal-midnight.svg'},
    'kenyon': {'label': 'Kenyon', 'url': 'KENYONINTERNATIONAL.COM',
               'white': 'logos/kenyon-120-logo-white.svg',
               'dark': 'logos/kenyon-120-logo-rgb.svg'},
    'bainessimmons': {'label': 'Baines Simmons', 'url': 'BAINESSIMMONS.COM',
                      'white': 'logos/baines-logo-white.svg',
                      'dark': 'logos/baines-logo-midnight.svg'},
    'redline': {'label': 'Redline', 'url': 'TRUSTREDLINE.CO.UK',
                'white': 'logos/redline-logo-white.svg',
                'dark': 'logos/redline-logo-midnight.svg'},
}
PALETTE = [["#031022", "#03D4FF", "#FFFFFF", "#1E5BB5"]]
FONTS = {"display": {"family": "Titillium Web", "or": "instrument-sans", "weights": [300, 400, 700]},
         "sans": {"family": "Open Sans", "or": "instrument-sans", "weights": [400, 700]}}


def js(s):
    """Text for a single-quoted JS string that becomes HTML: HTML-escape, then JS-escape."""
    return escape(str(s), quote=False).replace('\\', '\\\\').replace("'", "\\'")


def svg_text(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<metadata>.*?</metadata>', '', s, flags=re.S)   # C2PA blocks are large
    return re.sub(r'<\?xml[^>]*\?>', '', s).strip()


def cover(src, dst, w, h, q):
    im = Image.open(src).convert('RGB')
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((l, t, l + w, t + h))
    im.save(dst, 'JPEG', quality=q)
    return im


def tab_is_dark(im):
    a = np.asarray(im.crop((0, 0, 600, 220))).astype(float) / 255
    return (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]).mean() < 0.55


def scenes_doc(look, dur, sid, name, desc, stage):
    return {"v": 1, "stage": stage, "lang": "en", "look": look, "palettes": PALETTE, "theirs": 1,
            "width": 1200, "height": 1600, "fps": 30, "background": "#031022", "fonts": FONTS,
            "scenes": [{"id": sid, "name": name, "dur": dur, "desc": desc}]}


def film_name(kind, spec, name):
    """Naming convention: '<Type> - <Brand(s)> - <holiday or tradeshow name>'."""
    keys = spec.get('brands') or [spec['brand']]
    labels = 'All' if set(keys) >= set(BRANDS) else ', '.join(BRANDS[k]['label'] for k in keys)
    return spec.get('film_title') or f"{kind} - {labels} - {name}"


def employee(ds, name):
    for e in json.load(open(os.path.join(ds, 'assets/portraits/employees.json'))):
        if e['name'].lower() == name.lower():
            return e
    sys.exit(f'Not in employees.json: {name}. Ask for their photo and title, and give "portrait" and "title" in the spec.')


# ---------------------------------------------------------------- tradeshow

def tradeshow(spec, ds, out, up, docs):
    brand = BRANDS[spec['brand']]
    mode = spec.get('mode', 'attending').lower()
    shutil.copy(os.path.join(HERE, 'assets/plate-clean.jpg'), up)
    shutil.copy(os.path.join(HERE, 'assets/plate-lines.webp'), up)
    if spec.get('photo'):
        cover(spec['photo'], os.path.join(up, 'city.jpg'), 1200, 1600, 78)
    im = Image.open(spec['event_logo']).convert('RGBA')
    im = im.crop(im.getbbox())
    if im.height < 300:
        im = im.resize((round(im.width * 300 / im.height), 300), Image.LANCZOS)
    if im.width > 2000:
        im = im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS)
    im.save(os.path.join(up, 'event-logo.png'))

    people = []
    for i, p in enumerate(spec.get('people', [])[:6]):
        e = employee(ds, p['name']) if not p.get('portrait') else {}
        slug = re.sub(r'[^a-z0-9]+', '-', p['name'].lower()).strip('-')
        src = p.get('portrait') or os.path.join(ds, e.get('portraitWindow') or e['portrait'])
        Image.open(src).convert('RGB').save(os.path.join(up, slug + '.jpg'), 'JPEG', quality=86)
        people.append({'file': slug + '.jpg', 'name': p['name'], 'title': p.get('title') or e['title'],
                       'brand': p.get('brand') or e.get('brand') or brand['label']})
    n = len(people)
    layout = {1: 'ts-solo', 2: 'ts-cols', 3: 'ts-cols ts-cols3'}.get(n, '')

    mods = {'brand-logo.txt': svg_text(os.path.join(ds, 'assets', brand['white'])),
            'icon-date.txt': svg_text(os.path.join(ds, 'assets/icons/icon-date.svg')),
            'icon-location.txt': svg_text(os.path.join(ds, 'assets/icons/icon-location.svg'))}
    pills = []
    if spec.get('dates'):
        pills.append(('icon-date.txt', '', spec['dates'].upper()))
    if spec.get('location'):
        flag = spec.get('flag')
        if flag:
            mods[f'flag-{flag}.txt'] = svg_text(os.path.join(ds, f'assets/icons/flags/{flag}.svg'))
            pills.append((f'flag-{flag}.txt', 'ts-flag', spec['location'].upper()))
        else:
            pills.append(('icon-location.txt', '', spec['location'].upper()))
    if spec.get('venue'):
        pills.append(('icon-location.txt', '', spec['venue'].upper()))
    if mode == 'exhibiting' and spec.get('booth'):
        mods['icon-booth.txt'] = svg_text(os.path.join(ds, 'assets/icons/icon-booth.svg'))
        b = re.sub(r'^booth\s*', '', str(spec['booth']), flags=re.I)
        pills.append(('icon-booth.txt', '', 'BOOTH ' + (b if b.startswith('#') else '#' + b)))

    title = spec['title']
    px = spec.get('title_px') or min(92, int(2040 / (0.52 * max(len(title), 1))))
    t_style = '' if px >= 92 else f' style="font-size:{px}px"'
    l_style = ' style="filter:brightness(0) invert(1)"' if spec.get('event_logo_white') else ''

    p_lines = ''.join(f"          W.person(kit, 'post-p{i+1}', '{p['file']}', '{js(p['name'])}', '{js(p['title'])}', '{js(p['brand'])}') +\n"
                      for i, p in enumerate(people))
    pill_lines = ''.join(f"        W.pill(kit, 'post-pill{i+1}', '{m}', '{c}', '{js(t)}') +\n" for i, (m, c, t) in enumerate(pills))
    p_sel = ', '.join(f"'.post-p{i+1}'" for i in range(n))
    pill_sel = ', '.join(f"'.post-pill{i+1}'" for i in range(len(pills)))
    who_move = "'translateY(' + lerp(22, 0, w).toFixed(1) + 'px)'" if n in (2, 3) else "'translateX(' + lerp(28, 0, w).toFixed(1) + 'px)'"
    frame_origin = "      p.frame.style.transformOrigin = '50% 100%';\n" if n in (2, 3) else ''

    scene = f"""const {{ seg, lerp, eo, eio, eob, TextFx }} = kit;
kit.scene('post', {{
  async init(kit) {{
    kit.stage.append(kit.h('<div class="ground">' +
      W.backdrop(kit, 'post-back') +
      W.svg(kit, 'brand-logo.txt', 'ts-brand post-brand') +
      '<div class="ts-col post-col">' +
        '<img class="ts-evlogo post-evlogo"{l_style} alt="" src="' + kit.assets.url('event-logo.png') + '">' +
        '<div class="ts-tag post-tag">{mode.upper()}</div>' +
        '<div class="ts-title post-title"{t_style}>{js(title)}</div>' +
        '<div class="ts-people {layout} post-people">' +
{p_lines}        '</div>' +
      '</div>' +
      '<div class="ts-pills post-pills">' +
{pill_lines}      '</div>' +
      '<div class="ts-url post-url">{brand['url']}</div>' +
      '<div class="ts-strip post-strip"></div>' +
    '</div>'));
    const q = (s) => kit.stage.querySelector(s);
    Object.assign(this, {{
      back: q('.post-back'), brand: q('.post-brand'), evlogo: q('.post-evlogo'), tag: q('.post-tag'), title: q('.post-title'),
      url: q('.post-url'), strip: q('.post-strip'),
      people: [{p_sel}].map((s) => ({{ frame: q(s + ' .ts-frame'), who: q(s + ' .ts-who') }})),
      col: q('.post-col'), pillRow: q('.post-pills'),
      pills: [{pill_sel}].map(q),
    }});
    await W.fit(this.col, this.pillRow);
  }},
  render(t) {{
    // Backdrop settles at a constant rate for the whole film, so it never stops moving.
    this.back.style.transform = 'scale(' + lerp(1.15, 1.0, seg(t, 0, 10)).toFixed(4) + ')';
    if (!this.lines) this.lines = this.back.querySelector('.ts-lines');
    W.lines(this.lines, t);
    // Brand furniture: logo, URL, Sapphire-to-Electric strip.
    const b = eo(seg(t, -0.6, 0.4));
    this.brand.style.opacity = b;
    this.brand.style.transform = 'translateY(' + lerp(-14, 0, b).toFixed(1) + 'px)';
    this.strip.style.transform = 'scaleX(' + eio(seg(t, -0.3, 1.0)).toFixed(4) + ')';
    this.url.style.opacity = eo(seg(t, 0.2, 0.9));
    // Event logo, then the tag, then the title word by word.
    const l = eo(seg(t, -0.3, 0.7));
    this.evlogo.style.opacity = l;
    this.evlogo.style.transform = 'translateY(' + lerp(34, 0, l).toFixed(1) + 'px)';
    const g = seg(t, 0.6, 1.3);
    this.tag.style.opacity = eo(seg(t, 0.6, 1.0));
    this.tag.style.transformOrigin = '0px 33px';
    this.tag.style.transform = 'scale(' + lerp(0.86, 1, eob(g, 1.6)).toFixed(4) + ')';
    TextFx.fadeFromRight(this.title, t, 1.0, {{ dx: 30, dur: 0.6 }});
    // People: frame pops in, then name and role follow.
    this.people.forEach((p, i) => {{
      const t0 = 1.9 + i * 0.35, f = seg(t, t0, t0 + 0.6), w = eo(seg(t, t0 + 0.15, t0 + 0.7));
      p.frame.style.opacity = eo(seg(t, t0, t0 + 0.3));
{frame_origin}      p.frame.style.transform = 'scale(' + lerp(0.7, 1, eob(f, 1.6)).toFixed(4) + ')';
      p.who.style.opacity = w;
      p.who.style.transform = {who_move};
    }});
    // Event detail pills rise into place along the bottom.
    this.pills.forEach((el, i) => {{
      const t0 = 2.9 + i * 0.25, k = eo(seg(t, t0, t0 + 0.6));
      el.style.opacity = k;
      el.style.transform = 'translateY(' + lerp(26, 0, k).toFixed(1) + 'px)';
    }});
  }},
}});
"""
    names = ', '.join(p['name'] for p in people) or 'no people'
    desc = (f"The {brand['label']} tradeshow post builds up: {title} logo, {mode.upper()} tag, title, {names}, "
            f"then the {', '.join(t for _, _, t in pills)} pills, and holds while the background zooms and the lines sway.")
    look = "Graphics Generator tradeshow post: the LinkedIn Standard tradeshow layout from the TrustFlight design system, built up with simple fades and eased slides. plain"
    return dict(css=open(os.path.join(HERE, 'templates/tradeshow-base.css')).read(),
                shared=open(os.path.join(HERE, 'templates/tradeshow-shared.js')).read(),
                mods=mods, scene_id='post', scene=scene,
                scenes=lambda st: scenes_doc(look, 10, 'post', 'Attending post' if mode == 'attending' else 'Exhibiting post', desc, st),
                title=film_name('Tradeshow', spec, title))


# ---------------------------------------------------------------- holiday

def holiday(spec, ds, out, up, docs):
    brand = BRANDS[spec['brand']]
    # Holiday options: 'single-slide' (was 'base') and 'multi-slide' (was 'complex'). Old names still work.
    raw = re.sub(r'[\s_]+', '-', str(spec.get('option', 'single-slide')).strip().lower())
    option = 'multi' if raw in ('multi-slide', 'multi', 'multislide', 'complex') else 'single'
    im = cover(spec['photo'], os.path.join(up, 'photo.jpg'), 1200, 1600, 84)
    dark = tab_is_dark(im)
    mods = {'brand-logo.txt': svg_text(os.path.join(ds, 'assets', brand['white' if dark else 'dark']))}
    flag_imgs = ''
    for f in spec.get('flags', []):
        mods[f'flag-{f}.txt'] = svg_text(os.path.join(ds, f'assets/imagery/holiday/flag-{f}.svg'))
        flag_imgs += f" + W.svg(kit, 'flag-{f}.txt', 'holiday-flag')"
    flags_html = (f"        '<div class=\"hd-flags holiday-flags\">'{flag_imgs} + '</div>' +\n" if flag_imgs
                  else "        '<div class=\"hd-flags holiday-flags\" style=\"display:none\"></div>' +\n")
    title, sub = spec['title'], spec.get('subtitle', 'Celebrating')
    tab_cls = 'hd-tab holiday-tab' + ('' if dark else ' hd-light')
    complex_html = complex_q = complex_init = complex_render = ''
    dur = 10
    if option == 'multi':
        dur = 19
        complex_html = (f"      '<div class=\"hd-warm holiday-m1\"><div class=\"hd-warm-line holiday-m1line\">{js(spec['message'])}</div></div>' +\n"
                        f"      '<div class=\"hd-msg holiday-m2\"><div class=\"hd-title holiday-m2title\">{js(spec.get('closing') or 'Happy ' + title + '!')}</div></div>' +\n")
        complex_q = " block: q('.holiday-block'), m1: q('.holiday-m1'), m1line: q('.holiday-m1line'), m2: q('.holiday-m2'), m2title: q('.holiday-m2title'),"
        complex_init = "\n    this.m2title.style.fontSize = W.titlePx(this.m2title.textContent) + 'px';"
        complex_render = """    // Multi-slide: the holiday block fades out at 6 s.
    const out = ei(seg(t, 6.0, 6.7));
    this.block.style.opacity = 1 - out;
    this.block.style.transform = 'translateY(' + lerp(0, -30, out).toFixed(1) + 'px)';
    // Beat 2: a warm, centred thank-you, word by word; it holds, then lifts away.
    const o1 = ei(seg(t, 13.0, 13.6));
    TextFx.fadeFromRight(this.m1line, t, 7.0, { stagger: 0.09, dur: 0.6, dx: 30 });
    this.m1.style.opacity = t < 6.9 ? 0 : 1 - o1;
    this.m1.style.transform = 'translateY(calc(-50% + ' + lerp(0, -30, o1).toFixed(1) + 'px))';
    // Beat 3: "Happy [holiday]!" lands and holds to the end.
    const m = eo(seg(t, 14.0, 15.0));
    this.m2.style.opacity = m;
    this.m2.style.transform = 'translateY(calc(-50% + ' + lerp(12, 0, m).toFixed(1) + 'px)) scale(' + lerp(0.985, 1, m).toFixed(4) + ')';
"""
    scene = f"""const {{ seg, lerp, eo, ei, eio, eob, TextFx }} = kit;
kit.scene('holiday', {{
  init(kit) {{
    kit.stage.append(kit.h('<div class="ground">' +
      '<img class="hd-photo holiday-photo" alt="" src="' + kit.assets.url('photo.jpg') + '">' +
      '<div class="hd-fade"></div>' +
      '<div class="{tab_cls}"><div class="hd-tab-line holiday-tabline"></div>' + W.svg(kit, 'brand-logo.txt', 'hd-logo holiday-logo') + '</div>' +
      '<div class="hd-block holiday-block">' +
{flags_html}        '<div class="hd-subrow"><div class="hd-rule hd-rule-l holiday-rl"></div><div class="hd-sub holiday-sub">{js(sub)}</div><div class="hd-rule hd-rule-r holiday-rr"></div></div>' +
        '<div class="hd-title holiday-title">{js(title)}</div>' +
      '</div>' +
{complex_html}      '<div class="hd-url holiday-url">{brand['url']}</div>' +
    '</div>'));
    const q = (s) => kit.stage.querySelector(s);
    Object.assign(this, {{ photo: q('.holiday-photo'), tabline: q('.holiday-tabline'), logo: q('.holiday-logo'), flags: q('.holiday-flags'),{complex_q}
      rl: q('.holiday-rl'), rr: q('.holiday-rr'), sub: q('.holiday-sub'), title: q('.holiday-title'), url: q('.holiday-url') }});
    this.title.style.fontSize = W.titlePx(this.title.textContent) + 'px';{complex_init}
  }},
  render(t) {{
    // Photo keeps moving for the whole film: a steady zoom out with a slow rise.
    const k = seg(t, 0, {dur});
    this.photo.style.transform = 'translateY(' + lerp(40, 0, k).toFixed(1) + 'px) scale(' + lerp(1.15, 1.0, k).toFixed(4) + ')';
    // Logo tab: outline and logo fade in.
    const g = eo(seg(t, -0.6, 0.4));
    this.logo.style.opacity = g;
    this.logo.style.transform = 'translateY(' + lerp(-14, 0, g).toFixed(1) + 'px)';
    this.tabline.style.opacity = eo(seg(t, -0.3, 0.7));
    // Flag pops in.
    const f = seg(t, 0.7, 1.3);
    this.flags.style.opacity = eo(seg(t, 0.7, 1.0));
    this.flags.style.transform = 'scale(' + lerp(0.8, 1, eob(f, 1.6)).toFixed(4) + ')';
    // Rules grow outward from the subtitle; the subtitle fades in as its tracking tightens.
    const r = eio(seg(t, 1.2, 2.0));
    this.rl.style.transform = 'scaleX(' + r.toFixed(4) + ')';
    this.rr.style.transform = 'scaleX(' + r.toFixed(4) + ')';
    const s = eo(seg(t, 1.3, 2.0));
    this.sub.style.opacity = s;
    this.sub.style.letterSpacing = lerp(0.3, 0.12, s).toFixed(4) + 'em';
    // Title rises a little and settles.
    const ti = eo(seg(t, 2.0, 3.0));
    this.title.style.opacity = ti;
    this.title.style.transform = 'translateY(' + lerp(12, 0, ti).toFixed(1) + 'px) scale(' + lerp(0.985, 1, ti).toFixed(4) + ')';
    // URL is static: it fades in with the brand logo and never moves.
    this.url.style.opacity = g;
{complex_render}  }},
}});
"""
    look = f"Graphics Generator holiday post ({'multi-slide, with a thank-you slide and a closing slide' if option == 'multi' else 'single slide'}): the LinkedIn Single holiday layout from the TrustFlight design system, built up with simple fades over a slowly moving photo. plain"
    desc = f"The {brand['label']} {title} post builds over the photo: logo tab and URL, flag, {sub.upper()} between two rules, {title.upper()}"
    desc += (f"; at 6 s it fades out for \"{spec['message']}\", then \"{spec.get('closing') or 'Happy ' + title + '!'}\" holds to the end." if option == 'multi' else ", then holds.")
    return dict(css=open(os.path.join(HERE, 'templates/holiday-base.css')).read(),
                shared=open(os.path.join(HERE, 'templates/holiday-shared.js')).read(),
                mods=mods, scene_id='holiday', scene=scene,
                scenes=lambda st: scenes_doc(look, dur, 'holiday', 'Holiday post', desc, st),
                title=film_name('Holiday', spec, title))


# ---------------------------------------------------------------- steps

def prepare(a):
    spec = json.load(open(a.spec))
    out = os.path.abspath(a.out)
    up, docs = os.path.join(out, 'upload'), os.path.join(out, 'docs')
    os.makedirs(up, exist_ok=True); os.makedirs(docs, exist_ok=True)
    ds = os.path.abspath(a.ds)
    for k in [spec['brand']] + list(spec.get('brands') or []):
        if k not in BRANDS:
            sys.exit('brand must be one of ' + ', '.join(BRANDS))
    r = {'tradeshow': tradeshow, 'holiday': holiday}[spec['kind']](spec, ds, out, up, docs)
    w = [('film', 'meta', {'v': 1, 'title': r['title']}),
         ('modules', 'scenes.json', {'kind': 'json', 'text': json.dumps(r['scenes']('rough'), ensure_ascii=False)}),
         ('modules', 'base.css', {'kind': 'css', 'text': r['css']}),
         ('modules', 'shared.js', {'kind': 'js', 'text': r['shared']})]
    w += [('modules', k, {'kind': 'text', 'text': v}) for k, v in r['mods'].items()]
    w.append(('film', 'script', {'code': 'window.CUT = kit.scenes();'}))
    plan = []
    for col, doc, data in w:
        p = os.path.join(docs, f'{col}__{doc}.json')
        json.dump(data, open(p, 'w'), ensure_ascii=False)
        plan.append({'op': 'set', 'collection': col, 'doc_id': doc, 'file_path': p})
    json.dump({'kind': 'js', 'text': r['scene']}, open(os.path.join(docs, 'scene.json'), 'w'), ensure_ascii=False)
    json.dump({'kind': 'json', 'text': json.dumps(r['scenes']('final'), ensure_ascii=False)}, open(os.path.join(docs, 'scenes-final.json'), 'w'), ensure_ascii=False)
    json.dump({'plan': plan, 'scene_id': r['scene_id'], 'title': r['title']}, open(os.path.join(out, 'plan.json'), 'w'))
    print('Film title:', r['title'])
    print('Upload these files to the film (Artifact publish, asset: true, file_paths):')
    for f in sorted(os.listdir(up)):
        print(' ', os.path.join(up, f))


def assets(a):
    out = os.path.abspath(a.out)
    plan = json.load(open(os.path.join(out, 'plan.json')))
    blobs = json.load(open(a.blobs))
    mime = {'jpg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
    writes = list(plan['plan'])
    for f in sorted(os.listdir(os.path.join(out, 'upload'))):
        if f not in blobs:
            sys.exit(f'No blob id for {f}')
        w, h = Image.open(os.path.join(out, 'upload', f)).size
        p = os.path.join(out, 'docs', f'assets__{f}.json')
        json.dump({'ref': '/_blob/' + blobs[f].split('/')[-1], 'mime': mime[f.rsplit('.', 1)[1]], 'w': w, 'h': h}, open(p, 'w'))
        writes.insert(-1, {'op': 'set', 'collection': 'assets', 'doc_id': f, 'file_path': p})
    json.dump(writes, open(os.path.join(out, 'writes.json'), 'w'), indent=1)
    print('Batch writes:', os.path.join(out, 'writes.json'))
    print(f"Then: set modules/scene-{plan['scene_id']}.js from", os.path.join(out, 'docs/scene.json'))
    print('Last: set modules/scenes.json (if_version from the batch) from', os.path.join(out, 'docs/scenes-final.json'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p1 = sp.add_parser('prepare'); p1.add_argument('spec'); p1.add_argument('--ds', required=True); p1.add_argument('--out', required=True)
    p2 = sp.add_parser('assets'); p2.add_argument('out'); p2.add_argument('--blobs', required=True)
    a = ap.parse_args()
    {'prepare': prepare, 'assets': assets}[a.cmd](a)
