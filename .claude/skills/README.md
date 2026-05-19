# TrustFlight Claude Code Skills

Shared skills for use with [Claude Code](https://claude.ai/code). These load automatically when you invoke the relevant skill in any Claude Code session.

## Available Skills

| Skill | Description |
|-------|-------------|
| `brand-framework` | TrustFlight Brand Framework + Brand Guidelines — messaging, voice, visual identity, colours, typography, logos, product reference, and communication standards |
| `ppt-design-system` | TrustFlight PowerPoint design system — brand-compliant slide and deck generation using the official master template, colours, fonts, and layouts via PowerPoint MCP |
| `linkedin-ad-generator` | Generate LinkedIn ad JPGs from the Ads - Template.ai Illustrator file — layout selection, caption update, split-colour styling, and export |
| `linkedin-holiday-generator` | Generate LinkedIn holiday post artboards from `Linkedin - Holidays - New.aic` — creates new artboards for all 60 PDF holidays, updates captions, replaces photos, exports JPGs |
| `course-dates-generator` | Generate sub-brand course date PDFs from `Courses Generator - Template.ai` — scrapes a course listing page, creates one artboard per course, exports multi-page PDF for Redline, BSL, or Kenyon |

## Setup

These skills live under `.claude/skills/` in this repo, which Claude Code auto-discovers. No manual install is required:

- **Claude Code on the web:** open this repo in a session and the skills are available automatically.
- **Claude Code CLI / IDE extensions:** clone this repo and open it as your working directory. The repo-local `.claude/skills/` is picked up alongside any skills in `~/.claude/skills/`.
- **Per-user install (optional):** if you want these available outside this repo, copy or symlink the skill folders into `~/.claude/skills/`.

## Using a Skill

In any Claude Code session, type:

```
/brand-framework
```

Claude will load the full Brand Framework and Brand Guidelines into context.

## Keeping Up to Date

`git pull` inside this repo. Skills update for everyone the next time they open a session on the repo.

## Contributing

Brand or skill updates should go through Alex Craiu (alex.craiu@trustflight.com) for brand-related content, or the relevant content owner.
