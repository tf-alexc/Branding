# Letterhead Templates

The `letterhead` skill loads `.dotx` master templates from this folder. They are the source of truth for the skill — no SharePoint sync, no re-upload, no external dependency once they live here.

## Required files

```
Letterhead [Bracknell].dotx
Letterhead [Doncaster].dotx
Letterhead [Houston].dotx
Letterhead [Jersey].dotx
Letterhead [London].dotx
Letterhead [Luton].dotx
Letterhead [Vancouver].dotx
```

Filename must match the pattern `Letterhead [Office].dotx` exactly (square brackets, single space before `[`, `.dotx` extension).

## One-time setup (if any file is missing)

The Anthropic remote execution environment cannot download `.dotx` files from SharePoint directly (the MIME type is blocked by the SharePoint MCP). The templates must be copied in from a local machine that has them synced from SharePoint:

**Source:** [Design / MS Word Templates / Letterheads](https://totalaoc.sharepoint.com/sites/team-design2/Shared%20Documents/Document%20Templates/MS%20Word%20Templates/Letterheads)

From a local CLI session on a Mac with the SharePoint folder synced via OneDrive:

```bash
cd ~/path/to/Branding   # local clone of tf-alexc/Branding

# Adjust the source path to wherever the SharePoint folder is synced locally
SRC="/Users/alexcraiu/Library/CloudStorage/OneDrive-SharedLibraries-TotalAOC/Design - Document Templates/MS Word Templates/Letterheads"

cp "$SRC"/Letterhead*.dotx skills/letterhead/templates/

git add skills/letterhead/templates/*.dotx
git commit -m "Bundle TrustFlight letterhead .dotx templates"
git push
```

After this is done once, the skill is fully self-contained and works from any environment, including Claude Code on the web.

## Updating a template

When SharePoint masters change, re-copy them into this folder and commit. The skill will pick up the new version on the next run.

## Adding a new brand

Create a sub-folder `templates/{Brand}/` (e.g. `templates/Baines Simmons/`) and drop the office `.dotx` files inside. Then update `letterhead.py` to resolve `{brand}/{office}` paths (currently it resolves flat).
