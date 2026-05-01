#!/usr/bin/env python3
"""
BSL Course Sheet Filler
Extracts content from an original course PDF and fills the new InDesign-exported template.

Usage:
    python3 fill_course_sheet.py <source_pdf>
    python3 fill_course_sheet.py --all   (process all PDFs in the source folder)
"""

import fitz  # PyMuPDF
import re
import os
import sys

TEMPLATE_PATH = '/Users/alexcraiu/Desktop/Claude Playground/InDesign/BSL Course Sheets/Course - Regulatory Compliance Pathway - Template.pdf'
SOURCE_DIR = '/Users/alexcraiu/Desktop/Documents/Baines Simmons/Course Sheets/CURRENT PDF VERSIONS'
OUTPUT_DIR = '/Users/alexcraiu/Desktop/Claude Playground/InDesign/BSL Course Sheets/Output'
FONTS_DIR     = '/Users/alexcraiu/Desktop/Claude Playground/InDesign/BSL Course Sheets/fonts'
FONT_LIGHT    = os.path.join(FONTS_DIR, 'OpenSans-Light.ttf')
FONT_REGULAR  = os.path.join(FONTS_DIR, 'OpenSans-Regular.ttf')
FONT_SEMIBOLD = os.path.join(FONTS_DIR, 'OpenSans-SemiBold.ttf')
FONT_BOLD     = os.path.join(FONTS_DIR, 'OpenSans-Bold.ttf')

# ── Brand colours (RGB 0–1) ───────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

C_GRAPHITE = hex_to_rgb('#242D41')   # body text
C_SAPPHIRE = hex_to_rgb('#1E5BB5')   # section headings
C_LIGHT    = hex_to_rgb('#E0E7F5')   # title (large heading)
C_WHITE    = (1.0, 1.0, 1.0)         # subtitle
C_AZURE    = hex_to_rgb('#479FF8')   # bullet markers

# ── Template placeholder strings (from template PDF analysis) ─────────────────
T_HEADING   = '[Course Title]'
T_SUBTITLE  = '[Subtitle]'
T_LEVEL     = 'Practitioner'
T_DURATION  = '1 Day'
T_PATHWAY   = 'Regulatory Compliance Pathway'
T_PREREQ    = 'There are no pre-requisites for this course.'

# Overview text box rect on page 1 (x0, y0, x1, y1)
OVERVIEW_RECT = fitz.Rect(36, 157, 579, 740)

# Body block on page 2: overflow from page 1 + "Courses you might also like"
BODY_RECT_P2 = fitz.Rect(36, 66, 579, 655)


# ── Extraction ────────────────────────────────────────────────────────────────

# Contact-info patterns that appear as footers in source PDFs — never include these in output
_CONTACT_PATTERNS = re.compile(
    r'bainessimm|@bainessimm|\+44\s*\(|training@|hello@|visit our website|contact us|contact:|'
    r'\b\d{4,}\s*\d{3,}',  # phone-number-like digit runs
    re.IGNORECASE
)

def _is_contact_text(text):
    """Return True if the text looks like footer/contact info from the source PDF."""
    return bool(_CONTACT_PATTERNS.search(text))


def get_spans(page):
    spans = []
    for b in page.get_text('dict')['blocks']:
        if b['type'] == 0:
            for line in b['lines']:
                for span in line['spans']:
                    spans.append(span)
    return spans


def clean(text):
    return re.sub(r'\s+', ' ', text).strip()


def extract_course_data(pdf_path):
    doc = fitz.open(pdf_path)
    data = {}

    # ── Page 1 ────────────────────────────────────────────────────────────────
    p1_spans = get_spans(doc[0])

    # Pathway: top-right area (x > 300, y < 65), excluding "Level:" line
    pathway_parts = [
        s['text'] for s in p1_spans
        if s['bbox'][0] > 300 and s['bbox'][1] < 65 and 'Level:' not in s['text']
    ]
    data['pathway'] = clean(' '.join(pathway_parts))

    # Level: top-right, contains "Level:"
    for s in p1_spans:
        if 'Level:' in s['text'] and s['bbox'][0] > 300:
            m = re.search(r'Level:\s*(.+)', s['text'])
            if m:
                data['level'] = m.group(1).strip()
            break

    # Duration: text containing "Duration:"
    for s in p1_spans:
        if 'Duration:' in s['text']:
            m = re.search(r'Duration:\s*(.+)', s['text'])
            if m:
                data['duration'] = m.group(1).strip()
            break

    # Title: large text (size >= 16pt) in top-left (x < 400, y < 200)
    title_spans = sorted(
        [s for s in p1_spans if s['size'] >= 16 and s['bbox'][0] < 400 and s['bbox'][1] < 200],
        key=lambda s: (s['bbox'][1], s['bbox'][0])
    )
    if title_spans:
        # Build full combined title text
        full_title = clean(' '.join(s['text'] for s in title_spans))
        # Clean up multiple dashes and extra whitespace
        full_title = re.sub(r'\s*-\s*-\s*', ' - ', full_title)
        full_title = re.sub(r'\s+-\s*$', '', full_title).strip()
        # Normalise en dash / em dash to " - " so the split logic handles them uniformly
        full_title = re.sub(r'\s*[–—]\s*', ' - ', full_title)

        # Split strategy: if " - " appears more than once, split at the second occurrence
        # e.g. "TR10 - MRP Part 145 - Successfully Applying..." → heading / subtitle
        parts = re.split(r'\s+-\s+', full_title)
        if len(parts) >= 3:
            # "TR10", "MRP Part 145", "Successfully Applying..."
            data['heading']  = parts[0] + ' - ' + parts[1]
            data['subtitle'] = ' - '.join(parts[2:])
        elif len(parts) == 2:
            data['heading']  = parts[0]
            data['subtitle'] = parts[1]
        else:
            # No " - " separator: split at first colon if present
            if ':' in full_title:
                idx = full_title.index(':')
                data['heading']  = full_title[:idx].strip()
                data['subtitle'] = full_title[idx+1:].strip()
            else:
                data['heading']  = full_title
                data['subtitle'] = ''

    # Body overview: spans in the middle zone of page 1
    # Exclude: header (y < 200), footer (y > 760), top-right blocks (x > 300, y < 100),
    #          and quote/pull-quote column (x > 380, y < 400)
    body_spans = sorted(
        [s for s in p1_spans
         if 200 <= s['bbox'][1] <= 760
         and not (s['bbox'][0] > 300 and s['bbox'][1] < 100)
         and not (s['bbox'][0] > 380 and s['bbox'][1] < 400)
         and clean(s['text'])],
        key=lambda s: (round(s['bbox'][1] / 5) * 5, s['bbox'][0])
    )

    # For 3-page source PDFs, overview continues on source page 2 before Prerequisites.
    # Offset those spans' y by 1000 so they sort after all page-1 content.
    if len(doc) > 2:
        Y_OFFSET = 1000
        BODY_STOP = {'prerequisites', 'course details', 'faq', 'faqs'}
        for s in sorted(get_spans(doc[1]), key=lambda s: (s['bbox'][1], s['bbox'][0])):
            t = clean(s['text'])
            if not t:
                continue
            if s['bbox'][1] < 200:  # skip page header
                continue
            if t.lower() in BODY_STOP:
                break
            if _is_contact_text(t):  # skip contact footer lines
                continue
            if s['bbox'][0] > 380 and s['bbox'][1] < 400:  # skip quotes
                continue
            offset_s = dict(s)
            offset_s['bbox'] = (s['bbox'][0], s['bbox'][1] + Y_OFFSET,
                                s['bbox'][2], s['bbox'][3] + Y_OFFSET)
            body_spans.append(offset_s)
        body_spans.sort(key=lambda s: (round(s['bbox'][1] / 5) * 5, s['bbox'][0]))

    data['overview'] = _merge_intro_questions(_build_overview(body_spans))

    # ── Remaining pages: locate the right page for each section ─────────────
    # Each section is searched per-page to avoid cross-page y-value mixing.
    pages_spans = [get_spans(doc[i]) for i in range(1, len(doc))]

    def _page_with(keyword):
        """Return spans for the first page (after p1) containing keyword."""
        for spans in pages_spans:
            if any(keyword.lower() in clean(s['text']).lower() for s in spans):
                return spans
        return pages_spans[0] if pages_spans else []

    prereq_spans  = _page_with('Prerequisites')
    details_spans = _page_with('Course format:')
    related_spans = next(           # last page that has "courses you might"
        (spans for spans in reversed(pages_spans)
         if any('courses you might' in clean(s['text']).lower() for s in spans)),
        pages_spans[-1] if pages_spans else []
    )

    # Prerequisites
    in_prereq = False
    prereq_parts = []
    for s in sorted(prereq_spans, key=lambda s: (s['bbox'][1], s['bbox'][0])):
        t = clean(s['text'])
        if not t:
            continue
        if t == 'Prerequisites':
            in_prereq = True
            continue
        if in_prereq:
            if any(h in t for h in ['Course details', 'Course format', 'FAQ', 'FAQs']):
                break
            if _is_contact_text(t):
                break
            prereq_parts.append(t)
    data['prerequisites'] = clean(' '.join(prereq_parts)) or 'There are no pre-requisites for this course.'

    data['course_format']     = _extract_detail(details_spans, 'Course format:')
    data['course_level_desc'] = _extract_detail(details_spans, 'Course level:')
    data['assessment']        = _extract_detail(details_spans, 'Assessment process:')
    data['course_size']       = _extract_detail(details_spans, 'Course size:')
    data['related_courses']   = _extract_related_courses(related_spans)
    data['faqs']              = _extract_faqs(doc)

    doc.close()
    return data


def _extract_faqs(doc):
    """Extract FAQ Q&A pairs from all source pages.
    Returns list of (question_text, answer_text) tuples.
    Q/A prefixes (Q. Q: A. A:) are stripped; standardised Q:/A: applied at render time.
    """
    QA_Q = re.compile(r'^Q[.:]\s+', re.IGNORECASE)
    QA_A = re.compile(r'^A[.:]\s+', re.IGNORECASE)
    # Single-char spans like 's' or "'" that follow "FAQ" heading
    FAQ_HEADING = re.compile(r'^faq', re.IGNORECASE)

    in_faq       = False
    current_type = None   # 'q' or 'a'
    current_text = []
    current_q    = None
    qa_pairs     = []

    def _flush():
        nonlocal current_q
        if current_type == 'q':
            current_q = clean(' '.join(current_text))
        elif current_type == 'a' and current_q:
            qa_pairs.append((current_q, clean(' '.join(current_text))))
            current_q = None

    for pg_idx in range(len(doc)):
        spans = sorted(
            [s for b in doc[pg_idx].get_text('dict')['blocks'] if b['type'] == 0
             for line in b['lines'] for s in line['spans'] if clean(s['text'])],
            key=lambda s: (s['bbox'][1], s['bbox'][0])
        )
        for s in spans:
            t = clean(s['text'])
            if not t or _is_contact_text(t):
                continue
            if 'courses you might' in t.lower():
                break
            if FAQ_HEADING.match(t) or t in ("'", '\u2019', 's'):
                if FAQ_HEADING.match(t):
                    in_faq = True
                continue
            if not in_faq:
                continue
            if QA_Q.match(t):
                _flush()
                current_type = 'q'
                current_text = [QA_Q.sub('', t)]
            elif QA_A.match(t):
                _flush()
                current_type = 'a'
                current_text = [QA_A.sub('', t)]
            elif current_type:
                current_text.append(t)

    _flush()
    return qa_pairs


def _extract_detail(spans, label):
    """Extract the text following a bold label in the course details section."""
    sorted_spans = sorted(spans, key=lambda s: (s['bbox'][1], s['bbox'][0]))
    found = False
    parts = []
    label_lower = label.lower()
    for s in sorted_spans:
        t = clean(s['text'])
        if not t:
            continue
        if label_lower in t.lower():
            # Text may be split across the label span and the following spans
            after = re.split(re.escape(label), t, flags=re.IGNORECASE, maxsplit=1)
            if len(after) > 1 and after[1].strip():
                parts.append(after[1].strip())
            found = True
            continue
        if found:
            # Stop at next label or contact info
            if any(lbl in t.lower() for lbl in ['course format', 'course level', 'assessment process', 'course size', 'courses you might', 'prerequisites', 'faq']):
                break
            if _is_contact_text(t):
                break
            parts.append(t)
    return clean(' '.join(parts))


def _merge_intro_questions(segments):
    """Merge consecutive question paragraphs in the intro (pre-heading) section
    into a single flowing paragraph, removing the spacers between them.
    Questions are detected by ending with '?'.
    """
    first_heading = next(
        (i for i, (t, h) in enumerate(segments) if h is True), len(segments)
    )
    intro, rest = segments[:first_heading], segments[first_heading:]

    merged = []
    i = 0
    while i < len(intro):
        text, kind = intro[i]
        if not text:  # spacer — check if it's between two question paragraphs
            prev = merged[-1][0] if merged else ''
            nxt  = intro[i + 1][0] if i + 1 < len(intro) else ''
            if prev.endswith('?') and nxt.endswith('?'):
                # Absorb spacer and merge next question onto previous
                merged[-1] = (merged[-1][0] + ' ' + nxt, merged[-1][1])
                i += 2
                continue
        merged.append((text, kind))
        i += 1

    return merged + list(rest)


def _build_overview(spans):
    """Reconstruct body text as list of (text, is_heading) tuples.
    Consecutive lines of the same paragraph are joined so word-wrap
    in the template produces natural flow without unnecessary breaks.
    """
    HEADING_PATTERNS = [
        'how will this course benefit',
        'key areas of focus',
        'is this course right for me',
        'this course would also benefit',
    ]

    # Pass 1 — collect source lines with paragraph break markers
    # Note: source font boldness is intentionally ignored — headings detected by pattern only
    raw = []   # (text, new_para)
    prev_y = None
    cur_line, cur_new_para, cur_has_bullet = [], False, False

    for s in spans:
        t = s['text'].rstrip()
        if not t.strip():
            continue
        y = round(s['bbox'][1] / 3) * 3

        if prev_y is not None and abs(y - prev_y) > 6:
            if cur_line or cur_has_bullet:
                text = clean(' '.join(cur_line))
                if cur_has_bullet:
                    text = '• ' + text
                raw.append((text, cur_new_para))
            cur_line, cur_has_bullet = [], False
            cur_new_para = abs(y - prev_y) > 14

        if s.get('font', '') == 'SymbolMT':
            cur_has_bullet = True   # always place at front — SymbolMT order varies per line
        else:
            cur_line.append(t)
        prev_y = y

    if cur_line or cur_has_bullet:
        text = clean(' '.join(cur_line))
        if cur_has_bullet:
            text = '• ' + text
        raw.append((text, cur_new_para))

    # Pass 2 — merge bullet marker with following line; detect headings by pattern
    merged = []   # (text, is_heading, new_para)
    i = 0
    while i < len(raw):
        text, new_para = raw[i]
        if text == '•' and i + 1 < len(raw):
            merged.append(('• ' + raw[i + 1][0], False, new_para))
            i += 2
            continue
        is_heading = any(p in text.lower() for p in HEADING_PATTERNS)
        merged.append((text, is_heading, new_para))
        i += 1

    # Pass 3 — join consecutive body lines into full paragraphs;
    # also reattach bullet continuation lines (source PDF wrapping, new_para=False)
    result = []
    para_words = []
    last_bullet_idx = None   # index into result of the most recent bullet entry

    def flush_para():
        nonlocal last_bullet_idx
        if para_words:
            result.append((' '.join(para_words), False))
            para_words.clear()
        last_bullet_idx = None

    for text, is_heading, new_para in merged:
        if not text:
            flush_para()
            result.append(('', False))
            continue
        if is_heading or text.startswith('•'):
            flush_para()
            last_bullet_idx = len(result)
            result.append((text, is_heading))
            continue
        # Body line: if it immediately follows a bullet (no para break, no buffered words)
        # treat it as a continuation of that bullet rather than a new paragraph
        if last_bullet_idx is not None and not new_para and not para_words:
            prev_text, prev_flag = result[last_bullet_idx]
            result[last_bullet_idx] = (prev_text + ' ' + text, prev_flag)
            continue
        last_bullet_idx = None
        if new_para and para_words:
            flush_para()
            result.append(('', False))
        para_words.append(text)

    flush_para()
    return result


def _extract_related_courses(p2_spans):
    """Extract 'Courses you might also like to consider' as (text, is_heading) segments."""
    sorted_spans = sorted(p2_spans, key=lambda s: (s['bbox'][1], s['bbox'][0]))
    in_section = False
    segments = []
    cur_line, cur_has_bullet = [], False
    prev_y = None

    def flush_line():
        if cur_line or cur_has_bullet:
            text = clean(' '.join(cur_line))
            segments.append(('• ' + text if cur_has_bullet else text, False))
        cur_line.clear()

    for s in sorted_spans:
        t = s['text'].strip()
        if not t:
            continue
        y = round(s['bbox'][1] / 3) * 3

        if 'courses you might' in t.lower():
            flush_line()
            in_section = True
            segments.append(('Courses you might also like to consider', True))
            prev_y = y
            continue

        if not in_section:
            continue

        if _is_contact_text(t):
            break

        if prev_y is not None and abs(y - prev_y) > 6:
            flush_line()
            cur_has_bullet = False

        if s.get('font', '') == 'SymbolMT':
            cur_has_bullet = True
        else:
            cur_line.append(t)
        prev_y = y

    flush_line()

    # Post-process: reattach orphaned continuation lines to the preceding bullet.
    # In the related courses section every entry is either a heading or a bullet,
    # so any non-bullet text that follows a bullet is a wrapped continuation.
    fixed = []
    for text, is_heading in segments:
        if (not is_heading and text and not text.startswith('•')
                and fixed and fixed[-1][0].startswith('•')):
            fixed[-1] = (fixed[-1][0] + ' ' + text, False)
        else:
            fixed.append((text, is_heading))
    return fixed


def _layout_segments(rect, segments):
    """Compute text layout without rendering.
    Returns (layout_items, overflow_segments, final_y).
    final_y is the next-baseline position after all placed content.
    """
    f_body    = fitz.Font(fontfile=FONT_REGULAR)
    f_bold    = fitz.Font(fontfile=FONT_BOLD)
    f_heading = fitz.Font(fontfile=FONT_SEMIBOLD)
    sz_body, sz_head     = 8.5, 14
    lead_body, lead_head = sz_body * 1.35, sz_head * 1.25
    gap_before_head      = 12
    para_space           = 4.5
    width         = rect.x1 - rect.x0
    bullet_indent = 12.0

    DETAIL_LABEL_RE = re.compile(
        r'^(Course format|Course level|Assessment|Course size)(: )(.*)', re.IGNORECASE)
    COURSE_CODE_RE = re.compile(r'^([A-Z]{2,5}[\d_]\S*)\s*(.*)')

    layout = []
    y = rect.y0 + sz_body
    overflow = []
    before_first_heading = True   # body text before the first heading renders in Sapphire
    last_was_heading = False      # suppress para_space immediately after a heading

    for i, (text, is_heading) in enumerate(segments):
        if not text:
            if not last_was_heading:
                y += para_space
            continue

        overflowed = False

        if is_heading is True:
            before_first_heading = False
            last_was_heading = True
            y += gap_before_head
            for line in _word_wrap(text, f_heading, sz_head, width):
                if y > rect.y1:
                    overflowed = True
                    break
                layout.append((rect.x0, y, line, f_heading, sz_head, 'heading'))
                y += lead_head

        elif is_heading == 'faq_q':
            if not last_was_heading:
                y += para_space   # extra breathing room before each new question (skip first)
            last_was_heading = False
            q_label = 'Q'
            colon   = ': '
            q_body  = text[3:] if text.startswith('Q: ') else text
            label_w = f_bold.text_length(q_label, sz_body) + f_body.text_length(colon, sz_body)
            wrapped = _word_wrap(q_body, f_body, sz_body, width - bullet_indent - label_w)
            for j, line in enumerate(wrapped):
                if y > rect.y1:
                    overflowed = True
                    break
                if j == 0:
                    layout.append((rect.x0, y, '•', f_body, sz_body, 'bullet_marker'))
                    layout.append((rect.x0 + bullet_indent, y, q_label, f_bold, sz_body, 'faq'))
                    layout.append((rect.x0 + bullet_indent + f_bold.text_length(q_label, sz_body), y, colon + line, f_body, sz_body, 'faq'))
                else:
                    layout.append((rect.x0 + bullet_indent, y, line, f_body, sz_body, 'faq'))
                y += lead_body

        elif is_heading == 'faq_a':
            last_was_heading = False
            a_label = 'A'
            colon   = ': '
            a_body  = text[3:] if text.startswith('A: ') else text
            label_w = f_bold.text_length(a_label, sz_body) + f_body.text_length(colon, sz_body)
            wrapped = _word_wrap(a_body, f_body, sz_body, width - bullet_indent - label_w)
            for j, line in enumerate(wrapped):
                if y > rect.y1:
                    overflowed = True
                    break
                if j == 0:
                    layout.append((rect.x0 + bullet_indent, y, a_label, f_bold, sz_body, 'faq'))
                    layout.append((rect.x0 + bullet_indent + f_bold.text_length(a_label, sz_body), y, colon + line, f_body, sz_body, 'faq'))
                else:
                    layout.append((rect.x0 + bullet_indent, y, line, f_body, sz_body, 'faq'))
                y += lead_body

        elif text.startswith('• '):
            last_was_heading = False
            bullet_text = text[2:]
            cm = COURSE_CODE_RE.match(bullet_text)
            if cm:
                course_code = cm.group(1)
                rest        = cm.group(2)
                code_w  = f_bold.text_length(course_code, sz_body)
                space_w = f_body.text_length(' ', sz_body)
                rest_lines = _word_wrap(rest, f_body, sz_body,
                                        width - bullet_indent - code_w - space_w) if rest else []
                if y > rect.y1:
                    overflowed = True
                else:
                    layout.append((rect.x0, y, '•', f_body, sz_body, 'bullet_marker'))
                    layout.append((rect.x0 + bullet_indent, y, course_code, f_bold, sz_body, 'related_title'))
                    if rest_lines:
                        layout.append((rect.x0 + bullet_indent + code_w + space_w, y,
                                       rest_lines[0], f_body, sz_body, 'related_desc'))
                    y += lead_body
                    for rline in rest_lines[1:]:
                        if y > rect.y1:
                            overflowed = True
                            break
                        layout.append((rect.x0 + bullet_indent, y, rline, f_body, sz_body, 'related_desc'))
                        y += lead_body
            else:
                wrapped = _word_wrap(bullet_text, f_body, sz_body, width - bullet_indent)
                for j, line in enumerate(wrapped):
                    if y > rect.y1:
                        overflowed = True
                        break
                    if j == 0:
                        layout.append((rect.x0, y, '•', f_body, sz_body, 'bullet_marker'))
                    layout.append((rect.x0 + bullet_indent, y, line, f_body, sz_body, 'bullet_text'))
                    y += lead_body

        else:
            last_was_heading = False
            dm = DETAIL_LABEL_RE.match(text)
            if dm:
                label   = dm.group(1) + dm.group(2)
                value   = dm.group(3)
                label_w = f_bold.text_length(label, sz_body)
                val_lines = _word_wrap(value, f_body, sz_body, width - label_w)
                for j, vline in enumerate(val_lines):
                    if y > rect.y1:
                        overflowed = True
                        break
                    if j == 0:
                        layout.append((rect.x0, y, label, f_bold, sz_body, 'detail_label'))
                        layout.append((rect.x0 + label_w, y, vline, f_body, sz_body, 'detail_value'))
                    else:
                        layout.append((rect.x0, y, vline, f_body, sz_body, 'detail_value'))
                    y += lead_body
            else:
                kind = 'intro' if before_first_heading else 'body'
                for line in _word_wrap(text, f_body, sz_body, width):
                    if y > rect.y1:
                        overflowed = True
                        break
                    layout.append((rect.x0, y, line, f_body, sz_body, kind))
                    y += lead_body

        if overflowed:
            overflow = list(segments[i:])
            break

    return layout, overflow, y


def _render_overview_text(page, rect, segments):
    """Render overview segments — assumes rect already cleared by batch redaction.
    Three TextWriter passes: Graphite (body + bullet text), Sapphire (headings),
    Azure (bullet marker '•' only). Bullet text is indented past the marker.
    Course detail labels and related course codes are rendered in Bold Graphite.
    Returns (overflow_segments, final_y).
    """
    layout, overflow, final_y = _layout_segments(rect, segments)

    pass_map = [
        (C_GRAPHITE, {'body', 'bullet_text', 'detail_label', 'detail_value', 'related_title', 'related_desc', 'faq'}),
        (C_SAPPHIRE, {'heading', 'intro'}),
        (C_AZURE,    {'bullet_marker'}),
    ]
    for color, kinds in pass_map:
        tw = fitz.TextWriter(page.rect)
        for x, ly, text, font, size, kind in layout:
            if kind in kinds:
                tw.append((x, ly), text, font=font, fontsize=size)
        tw.write_text(page, color=color)

    return overflow, final_y


# ── Template filling ──────────────────────────────────────────────────────────

def _word_wrap(text, font, fontsize, max_width):
    """Wrap text to fit within max_width, return list of lines.
    If the final line would be a single orphan word, merge it onto the
    previous line (allowed to slightly exceed max_width on the right).
    """
    words = text.split()
    lines, current = [], []
    for word in words:
        test = ' '.join(current + [word])
        if font.text_length(test, fontsize) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    # Avoid single-word orphan on last line — merge onto previous line
    if len(lines) >= 2 and len(lines[-1].split()) == 1:
        lines[-2] = lines[-2] + ' ' + lines[-1]
        lines.pop()
    return lines or ['']


def render_overview(page, rect, segments):
    """Render mixed-style overview: (text, is_heading) segments into rect.
    Two-pass render: body (Graphite) then headings (Sapphire), using separate
    TextWriters since write_text only accepts one colour per writer.
    """
    f_body    = fitz.Font(fontfile=FONT_REGULAR)
    f_heading = fitz.Font(fontfile=FONT_REGULAR)
    sz_body, sz_head     = 8.5, 14
    lead_body, lead_head = sz_body * 1.35, sz_head * 1.5
    gap_before_head      = sz_body * 1.2
    width = rect.x1 - rect.x0

    _clear_rect(page, rect)

    def _render_pass(target_heading, color):
        tw   = fitz.TextWriter(page.rect)
        y    = rect.y0 + sz_body
        done = False
        for text, is_heading in segments:
            if done:
                break
            if not text:
                y += lead_body * 0.5
                continue
            if is_heading:
                y += gap_before_head
            font = f_heading if is_heading else f_body
            size = sz_head   if is_heading else sz_body
            lead = lead_head if is_heading else lead_body
            for line in _word_wrap(text, font, size, width):
                if y > rect.y1:
                    done = True
                    break
                if is_heading == target_heading:
                    tw.append((rect.x0, y), line, font=font, fontsize=size)
                y += lead
        tw.write_text(page, color=color)   # always reached

    _render_pass(False, C_GRAPHITE)   # body text
    _render_pass(True,  C_SAPPHIRE)   # section headings


def _clear_rect(page, rect):
    """Remove text in rect with no fill, preserving vector background graphics."""
    page.add_redact_annot(rect, fill=())
    page.apply_redactions(images=0, graphics=0)


def replace_text(page, old_text, new_text, fontsize=11, font_path=None, color=C_GRAPHITE):
    """Find a text string on a page, remove it, insert replacement."""
    rects = page.search_for(old_text)
    if not rects:
        print(f'  [warn] Could not find: {repr(old_text[:60])}')
        return
    font = fitz.Font(fontfile=font_path)
    for rect in rects:
        _clear_rect(page, rect)
        tw = fitz.TextWriter(page.rect)
        tw.append((rect.x0, rect.y1 - 1), new_text, font=font, fontsize=fontsize)
        tw.write_text(page, color=color)


def replace_textbox(page, rect, new_text, fontsize=8.5, font_path=None, color=C_GRAPHITE):
    """Remove text in rect and fill with wrapped text."""
    font = fitz.Font(fontfile=font_path)
    _clear_rect(page, rect)
    tw = fitz.TextWriter(page.rect)
    overflow = tw.fill_textbox(rect, new_text, font=font, fontsize=fontsize, align=fitz.TEXT_ALIGN_LEFT)
    tw.write_text(page, color=color)
    if overflow:
        print(f'  [warn] Text overflowed in rect {rect}: {len(overflow)} chars dropped')


def fill_template(course_data, output_path):
    doc = fitz.open(TEMPLATE_PATH)
    d   = course_data
    p1  = doc[0]
    p2  = doc[1]

    print(f'  Heading:  {d.get("heading")}')
    print(f'  Subtitle: {d.get("subtitle")}')
    print(f'  Level:    {d.get("level")}')
    print(f'  Duration: {d.get("duration")}')

    duration = ' '.join(w.capitalize() for w in d.get('duration', T_DURATION).split())

    # ── Page 1: batch all redactions, apply once, then write ─────────────────
    # Collect (search_text, replacement, fontsize, font_path, color)
    p1_fields = [
        (T_HEADING,  d.get('heading',  T_HEADING),  24,   FONT_LIGHT,   C_LIGHT),
        (T_SUBTITLE, d.get('subtitle', T_SUBTITLE), 12,   FONT_REGULAR, C_WHITE),
        (T_LEVEL,    d.get('level',    T_LEVEL),    8.5,  FONT_BOLD,    C_WHITE),
        (T_DURATION, duration,                      8.5,  FONT_BOLD,    C_WHITE),
    ]

    p1_writes = []  # (rect, new_text, fontsize, font_path, color)
    for old, new, sz, fp, col in p1_fields:
        rects = p1.search_for(old)
        if not rects:
            print(f'  [warn] Not found: {repr(old)}')
            continue
        for rect in rects:
            p1.add_redact_annot(rect, fill=())
            p1_writes.append((rect, new, sz, fp, col))

    p1.add_redact_annot(OVERVIEW_RECT, fill=())
    p1.apply_redactions(images=0, graphics=0)   # single call for page 1

    for rect, new_text, fontsize, font_path, color in p1_writes:
        font = fitz.Font(fontfile=font_path)
        tw   = fitz.TextWriter(p1.rect)
        # Use font ascender for accurate baseline — avoids the ~5pt drift from rect.y1 - 1
        baseline_y = rect.y0 + font.ascender * fontsize
        if font_path == FONT_LIGHT:
            # Course code (first word) in SemiBold; remainder in Light
            parts  = new_text.split(' ', 1)
            code   = parts[0]
            rest   = parts[1] if len(parts) > 1 else ''
            f_semi = fitz.Font(fontfile=FONT_SEMIBOLD)
            code_str = code + (' ' if rest else '')
            tw.append((rect.x0, baseline_y), code_str, font=f_semi, fontsize=fontsize)
            if rest:
                x_rest = rect.x0 + f_semi.text_length(code_str, fontsize)
                tw.append((x_rest, baseline_y), rest, font=font, fontsize=fontsize)
        else:
            tw.append((rect.x0, baseline_y), new_text, font=font, fontsize=fontsize)
        tw.write_text(p1, color=color)

    # ── Build Course Details segments — always rendered first on page 1 ─────────
    detail_lines = []
    for label, key in [
        ('Course format',     'course_format'),
        ('Course level',      'course_level_desc'),
        ('Assessment',        'assessment'),
        ('Course size',       'course_size'),
    ]:
        val = d.get(key, '')
        if val:
            detail_lines.append(f'{label}: {val}')

    course_details_segments = []
    if detail_lines:
        course_details_segments.append(('Course details', True))
        for line in detail_lines:
            course_details_segments.append((line, False))
        course_details_segments.append(('', False))   # spacer before overview

    # Split overview at first heading: intro (Sapphire) → Course Details → rest
    overview = d.get('overview', [])
    first_head = next((i for i, (t, h) in enumerate(overview) if h is True), len(overview))
    intro_segments  = overview[:first_head]
    body_segments   = overview[first_head:]

    # Trim trailing spacers from intro so Course Details sits cleanly after it
    while intro_segments and not intro_segments[-1][0]:
        intro_segments.pop()
    if intro_segments:
        intro_segments.append(('', False))   # single spacer before Course Details

    p1_segments = intro_segments + course_details_segments + body_segments
    overflow, p1_final_y = _render_overview_text(p1, OVERVIEW_RECT, p1_segments)

    # ── Try fitting Prerequisites onto page 1 if space allows ────────────────
    prereq = d.get('prerequisites', '')
    prereq_on_p1 = False
    if prereq and not overflow:
        sz_body = 8.5
        # Sub-rect starting where overview ended (y0 adjusted so first baseline = p1_final_y)
        sub_rect = fitz.Rect(OVERVIEW_RECT.x0, p1_final_y - sz_body, OVERVIEW_RECT.x1, OVERVIEW_RECT.y1)
        prereq_segments = [('Prerequisites', True), (prereq, False)]
        _, prereq_overflow, _ = _layout_segments(sub_rect, prereq_segments)
        if not prereq_overflow:
            _render_overview_text(p1, sub_rect, prereq_segments)
            prereq_on_p1 = True
            print('  Prerequisites: rendered on page 1')

    # ── Page 2: body block ────────────────────────────────────────────────────
    # Order: overflow from p1 → prerequisites (if not on p1) → related courses → FAQs
    # Course details is always on page 1 — never repeated on page 2.
    p2_segments = list(overflow)

    def _append_section(heading, body_text):
        if not body_text:
            return
        if p2_segments:
            p2_segments.append(('', False))
        p2_segments.append((heading, True))
        p2_segments.append((body_text, False))

    if not prereq_on_p1:
        _append_section('Prerequisites', prereq)

    related = d.get('related_courses', [])
    if related:
        if p2_segments:
            p2_segments.append(('', False))
        p2_segments.extend(related)

    faqs = d.get('faqs', [])
    if faqs:
        if p2_segments:
            p2_segments.append(('', False))
        p2_segments.append(('FAQ', True))
        for q_text, a_text in faqs:
            p2_segments.append(('Q: ' + q_text, 'faq_q'))
            p2_segments.append(('A: ' + a_text, 'faq_a'))

    if p2_segments:
        p2.add_redact_annot(BODY_RECT_P2, fill=())
        p2.apply_redactions(images=0, graphics=0)
        _render_overview_text(p2, BODY_RECT_P2, p2_segments)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc.save(output_path)
    print(f'  Saved: {output_path}')
    doc.close()


# ── Main ──────────────────────────────────────────────────────────────────────

def process(source_pdf, open_after=False):
    print(f'\nProcessing: {os.path.basename(source_pdf)}')
    data = extract_course_data(source_pdf)
    heading  = data.get('heading', 'output')
    subtitle = data.get('subtitle', '')
    code     = heading.split()[0]
    title_rest = heading[len(code):].strip().lstrip('- ').strip()
    full_title = f'{title_rest} - {subtitle}' if (title_rest and subtitle) else (title_rest or subtitle)
    safe_title = re.sub(r'[/\\:*?"<>|]', ' ', full_title).strip()
    safe_title = re.sub(r'\s{2,}', ' ', safe_title)
    safe_code  = re.sub(r'[/\\:*?"<>|]', ' ', code).strip()
    filename   = f'{safe_code} - {safe_title}.pdf' if safe_title else f'{safe_code}.pdf'
    output_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(output_path):
        print(f'[skip] Already exists: {os.path.basename(output_path)}')
        if open_after:
            os.system(f'open "{source_pdf}"')
            os.system(f'open "{output_path}"')
        return
    fill_template(data, output_path)
    if open_after:
        os.system(f'open "{source_pdf}"')
        os.system(f'open "{output_path}"')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 fill_course_sheet.py <source.pdf>')
        print('       python3 fill_course_sheet.py --all')
        sys.exit(1)

    if sys.argv[1] == '--all':
        pdfs = [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.pdf')]
        for pdf in sorted(pdfs):
            process(pdf)
    else:
        process(sys.argv[1], open_after=True)
