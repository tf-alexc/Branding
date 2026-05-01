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

Clone this repo into your Claude Code skills directory:

```bash
# If you don't have a skills directory yet
mkdir -p ~/.claude/skills

# Clone directly into the skills directory
git clone <repo-url> ~/.claude/skills

# Or if ~/.claude/skills already exists with content
cd ~/.claude/skills
git init
git remote add origin <repo-url>
git pull origin main
```

## Using a Skill

In any Claude Code session, type:

```
/brand-framework
```

Claude will load the full Brand Framework and Brand Guidelines into context.

## Keeping Up to Date

```bash
cd ~/.claude/skills
git pull
```

## Contributing

Brand or skill updates should go through Alex Craiu (alex.craiu@trustflight.com) for brand-related content, or the relevant content owner.
