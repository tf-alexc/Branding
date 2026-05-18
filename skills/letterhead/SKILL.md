---
name: letterhead
description: Generate a 1-2 page TrustFlight letterhead from the office-specific master templates bundled inside this skill. Simplified counterpart to word-brand for short branded letters. Use this skill when the user asks for a letter, letterhead, branded letter, signed letter, or formal correspondence on TrustFlight stationery.
---

# TrustFlight Letterhead Skill

**Script:** `~/.claude/skills/letterhead/letterhead.py`
**Bundled templates:** `~/.claude/skills/letterhead/templates/Letterhead [Office].docx` (or `.dotx`)
**Templates source of truth (SharePoint):** [Design / MS Word Templates / Letterheads](https://totalaoc.sharepoint.com/sites/team-design2/Shared%20Documents/Document%20Templates/MS%20Word%20Templates/Letterheads)
**Dependency:** `python-docx` (already installed)

The script opens the office-specific master (`.docx` preferred, `.dotx` accepted as a fallback) from the bundled `templates/` folder, inheriting the letterhead header/footer (logo, address bar, contact details, page layout), clears the placeholder body, and rebuilds it from a JSON spec. Output saves as `.docx`. No external uploads or re-downloads needed: every office template ships with the skill.

---

## Required user inputs

Before running, the user must specify **both** a brand/company and an office. If either is missing, ask before generating.

| Field | Allowed values |
|---|---|
| **Brand / company** | `TrustFlight`, `Baines Simmons`, `Kenyon`, `Redline` |
| **Office** | `Bracknell`, `Doncaster`, `Houston`, `Vancouver`, `London`, `Luton`, `Jersey` |

Current template coverage: **only `TrustFlight` has office letterheads bundled.** If the user picks Baines Simmons, Kenyon, or Redline, stop and tell them no letterhead template exists for that brand yet, then ask whether to fall back to TrustFlight.

---

## Length rules

- Target **1 page**. Up to **2 pages** is acceptable.
- If the body looks like it will overflow 2 pages, trim or summarise before generating, then flag this to the user.

---

## Brand styling reference (inherited from the `.dotx`)

| Element | Spec |
|---|---|
| Body font | Open Sans, 8.5pt, Graphite `#242D41` |
| Date | Open Sans, 8.5pt, Graphite `#242D41` |
| Recipient block (name through phone) | Open Sans, 8.5pt, Graphite, single line spacing, no inter-paragraph gap |
| Sign-off + signer title | Open Sans, 8.5pt, Graphite `#242D41` |
| Signer name only | Open Sans, 8.5pt, **Sapphire** `#1E5BB5`, bold |
| Header (logo + office address) | Pre-built in template, do not modify |
| Footer (page number / strapline) | Pre-built in template, do not modify |

Never use em dashes (brand rule). Use commas, colons, or rewrite.

---

## Process

1. **Confirm brand + office** with the user. Ask if missing.
2. **Draft the letter content** (date, recipient, salutation, body paragraphs, sign-off, signer).
3. **Write a temp JSON file** (e.g. `/tmp/letterhead_data.json`) with the spec below.
4. **Run the script:**
   ```bash
   python3 ~/.claude/skills/letterhead/letterhead.py /tmp/letterhead_data.json
   ```
5. The script saves to `output_path` as `.docx`. Default location: `/Users/alexcraiu/Desktop/Claude Playground/Letterheads/`.

---

## JSON Spec

```json
{
  "brand": "TrustFlight",
  "office": "Vancouver",
  "output_path": "/Users/alexcraiu/Desktop/Claude Playground/Letterheads/Letter - Acme Aviation.docx",
  "date": "31 March 2026",
  "recipient": {
    "name": "John Doe",
    "title": "Director of Operations",
    "company": "Acme Aviation",
    "address": ["123 Main Street", "Suite 400", "Vancouver, BC, V6B 1A1"],
    "email": "john.doe@acmeaviation.com",
    "phone": "+1 (604) 555 0182"
  },
  "subject": "Re: Maintenance contract renewal",
  "salutation": "Dear John,",
  "body": [
    "Thank you for your continued partnership with TrustFlight over the past year.",
    "We are pleased to confirm the renewal of your maintenance contract for the coming term, with the updated scope discussed in our meeting last week.",
    "Please review the attached terms and return a signed copy at your earliest convenience."
  ],
  "signoff": "Kind regards,",
  "signer": {
    "name": "Alex Craiu",
    "title": "Branding & Visual Designer"
  }
}
```

### Optional fields

- `date` — omit to auto-fill today's date in `DD Month YYYY` format (e.g. `18 May 2026`).
- `subject` — omit to skip the "Re:" line.
- `recipient.title`, `recipient.company`, `recipient.email`, `recipient.phone` — any can be omitted; missing lines are skipped cleanly.
- `recipient.address` — accepts a list of address parts (joined with `, ` on a single line) or a pre-joined string. The recipient block renders as: name (bold), `title, company` (joined on one line), single-line address, email, phone — all tight, no inter-paragraph gap.
- `salutation` — defaults to `Dear Sir/Madam,` if omitted.
- `signoff` — defaults to `Kind regards,` if omitted. Rendered in Graphite. Only the signer's name appears in Sapphire; the signer's title stays in Graphite.

---

## File naming

Suggested output filename: `Letter - [Recipient or Topic].docx`. Always save under `/Users/alexcraiu/Desktop/Claude Playground/Letterheads/` unless the user specifies otherwise. Create the folder if it doesn't exist.

---

## Templates directory

```
skills/letterhead/templates/
├── Letterhead [Bracknell].docx
├── Letterhead [Doncaster].docx
├── Letterhead [Houston].docx
├── Letterhead [Jersey].docx
├── Letterhead [London].docx
├── Letterhead [Luton].docx
└── Letterhead [Vancouver].docx
```

`.docx` is preferred. The script will also accept `.dotx` if that's what's present — same file format under the hood, only the MIME flag differs. Either works. These ship with the skill: see `templates/README.md` for the one-time setup if any are missing.

---

## Adding a new office or brand

1. Drop the new template into `skills/letterhead/templates/` with filename pattern `Letterhead [Office].docx` (or `.dotx`). Commit it.
2. Add the office to the allowed list in this SKILL.md.
3. For a new brand, create `templates/{Brand}/Letterhead [Office].docx` and update `letterhead.py` to resolve `{brand}/{office}` paths.
