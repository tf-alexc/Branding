# Letterhead Templates

The `letterhead` skill loads master templates from this folder. They are the source of truth for the skill: no SharePoint sync, no re-upload, no external dependency once they live here.

## Required files

```
Letterhead [Bracknell].docx
Letterhead [Doncaster].docx
Letterhead [Houston].docx
Letterhead [Jersey].docx
Letterhead [London].docx
Letterhead [Luton].docx
Letterhead [Vancouver].docx
```

Filename must match the pattern `Letterhead [Office].docx` exactly (square brackets, single space before `[`).

`.dotx` is also accepted as a fallback if that's what you have on hand — same OOXML format, only the MIME flag differs. The script checks `.docx` first, then `.dotx`. Prefer `.docx` for convenience and tool compatibility.

## One-time setup (if any file is missing)

The Anthropic remote execution environment cannot download Word template binaries from SharePoint directly (the SharePoint MCP returns extracted text for `.docx` and blocks `.dotx` entirely). The templates must be copied in from a local machine that has them synced from SharePoint.

**Source:** [Design / MS Word Templates / Letterheads](https://totalaoc.sharepoint.com/sites/team-design2/Shared%20Documents/Document%20Templates/MS%20Word%20Templates/Letterheads)

From a local CLI session on a Mac with the SharePoint folder synced via OneDrive:

```bash
cd ~/path/to/Branding   # local clone of tf-alexc/Branding

# Adjust the source path to wherever the SharePoint folder is synced locally
SRC="/Users/alexcraiu/Library/CloudStorage/OneDrive-SharedLibraries-TotalAOC/Design - Document Templates/MS Word Templates/Letterheads"

# Easiest: open each .dotx in Word once and save it as .docx into this folder,
# OR just copy the .dotx files directly — the script accepts both.
cp "$SRC"/Letterhead*.dotx skills/letterhead/templates/

git add skills/letterhead/templates/*.docx skills/letterhead/templates/*.dotx 2>/dev/null
git commit -m "Bundle TrustFlight letterhead templates"
git push
```

After this is done once, the skill is fully self-contained and works from any environment, including Claude Code on the web.

## Updating a template

When SharePoint masters change, re-copy them into this folder and commit. The skill will pick up the new version on the next run.

## Adding a new brand

Create a sub-folder `templates/{Brand}/` (e.g. `templates/Baines Simmons/`) and drop the office templates inside. Then update `letterhead.py` to resolve `{brand}/{office}` paths (currently it resolves flat).
