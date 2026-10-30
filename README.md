<div align="center">

<img src="assets/banner.svg" alt="Pixelorama Skills — Describe. Draw. Refine." width="100%">

# Pixelorama Skills

**One portable skill. An editable pixel-art workflow.**

[![Agent Skills](https://img.shields.io/badge/format-Agent_Skills-9cafff?style=flat-square)](https://agentskills.io)
[![MCP](https://img.shields.io/badge/bridge-Pixelorama_MCP-75d6b0?style=flat-square)](https://github.com/abidoo22/Pixelorama-MCP)
[![MIT](https://img.shields.io/badge/license-MIT-eecb89?style=flat-square)](LICENSE)

[English](README.md) · [简体中文](README.zh-CN.md) · [Read the skill](skills/pixelorama-skills/SKILL.md) · [Setup](skills/pixelorama-skills/references/setup.md)

</div>

Turn a drawing brief into a repeatable workflow for **Codex, Claude Code, and other Agent Skills + MCP clients**: detect the environment, connect Pixelorama, draw in batches, inspect the result, refine it, and deliver an editable project.

Pixelorama supplies the editor. [Pixelorama-MCP](https://github.com/abidoo22/Pixelorama-MCP) supplies the tools. **This repository teaches the agent how to use them well.** No editor fork, model API, or background service is bundled.

> Independent community project. Not affiliated with or endorsed by Orama Interactive, the Pixelorama-MCP maintainers, OpenAI, or Anthropic. The skill guides behavior; it does not guarantee artistic quality or grant tool access.

## What the workflow can help you make

| Create | Refine | Deliver |
| --- | --- | --- |
| Sprites, icons, props, pixel UI | Silhouettes, palette, edges, readable details | Editable `.pxo` + transparent PNG |
| Idle loops and short character animations | Anchors, frame consistency, timing | Spritesheets, PNG frames, supported animation formats |
| Tilesets and repeating scenes | Seams, transitions, coherent style | Tile sheets; optional supported Godot resources |

Capabilities depend on the connected bridge and model. The skill does not manufacture missing tools, semantic layers, or animation consistency from a flat image.

## See the upstream possibilities

These are **examples published by Pixelorama-MCP**, linked from the reviewed upstream revision with attribution. They illustrate the underlying toolchain—not results reproduced or certified with this skill. Images remain hosted upstream.

<table>
<tr>
<td width="50%" align="center"><a href="https://github.com/abidoo22/Pixelorama-MCP/tree/56fd8aa94c0905591bd2515fe9823eb70d4496d2"><img src="https://raw.githubusercontent.com/abidoo22/Pixelorama-MCP/56fd8aa94c0905591bd2515fe9823eb70d4496d2/docs/examples/showcase_cyberpunk_banner.gif" alt="Upstream example: animated cyberpunk city" width="100%"></a><br><b>Animated worlds</b><br><sub>Upstream Pixelorama-MCP example</sub></td>
<td width="50%" align="center"><a href="https://github.com/abidoo22/Pixelorama-MCP/tree/56fd8aa94c0905591bd2515fe9823eb70d4496d2"><img src="https://raw.githubusercontent.com/abidoo22/Pixelorama-MCP/56fd8aa94c0905591bd2515fe9823eb70d4496d2/docs/examples/showcase_astral_banner.gif" alt="Upstream example: floating island animation" width="100%"></a><br><b>Looping scenes</b><br><sub>Upstream Pixelorama-MCP example</sub></td>
</tr><tr>
<td width="50%" align="center"><a href="https://github.com/abidoo22/Pixelorama-MCP/tree/56fd8aa94c0905591bd2515fe9823eb70d4496d2"><img src="https://raw.githubusercontent.com/abidoo22/Pixelorama-MCP/56fd8aa94c0905591bd2515fe9823eb70d4496d2/docs/examples/dungeon_tileset_4x.png" alt="Upstream example: dungeon tiles and props" width="100%"></a><br><b>Tiles and game assets</b><br><sub>Upstream Pixelorama-MCP example</sub></td>
<td width="50%" align="center"><a href="https://github.com/abidoo22/Pixelorama-MCP/tree/56fd8aa94c0905591bd2515fe9823eb70d4496d2"><img src="https://raw.githubusercontent.com/abidoo22/Pixelorama-MCP/56fd8aa94c0905591bd2515fe9823eb70d4496d2/docs/examples/dialog_box_2x.png" alt="Upstream example: retro dialogue box" width="100%"></a><br><b>Pixel interfaces</b><br><sub>Upstream Pixelorama-MCP example</sub></td>
</tr>
</table>

Artwork credit: **pix-MCP Contributors / the upstream project**. See [source and notices](THIRD_PARTY_NOTICES.md). The banner above is decorative repository artwork, not a generated Pixelorama sample.

## Quick start

Copy **only** the complete `skills/pixelorama-skills/` folder into your client's skills directory. Keep `references/`, the optional `scripts/doctor.py`, and `LICENSE` together with `SKILL.md`.

| Client | Personal installation | Project installation |
| --- | --- | --- |
| Codex | `~/.agents/skills/pixelorama-skills/` | `.agents/skills/pixelorama-skills/` |
| Claude Code | `~/.claude/skills/pixelorama-skills/` | `.claude/skills/pixelorama-skills/` |
| Other Agent Skills clients | Use the client's documented directory | Use the client's documented directory |

On Windows, `~` means your user home directory. Install into a new directory; do not silently overwrite an existing skill. Replace the older `pixelorama-art` installation deliberately so duplicate copies do not compete.

Then ask your agent:

> Use pixelorama-skills to create a 32×32 cream-colored cat with a dark brown outline and a six-frame idle loop. Set up Pixelorama-MCP first if needed and authorized. Inspect and improve the result, then save the editable project and export a transparent spritesheet with timing information.

The agent can follow the setup procedure when it has authorized access to the host. It may still need you to approve installation or enable the editor extension. **Installing this skill alone neither installs Pixelorama nor registers MCP.** If the skill is not discovered, reload the client as its documentation requires.

## A small skill, a complete loop

```text
Your brief
   ↓
Pixelorama Skills  →  detect · protect · plan
   ↓
Agent + MCP        →  batch draw · inspect · refine
   ↓
Pixelorama         →  editable layers and animation frames
   ↓
Verified outputs   →  .pxo + the assets your project needs
```

The core instructions stay small. [Setup](skills/pixelorama-skills/references/setup.md) is loaded only when needed; [drawing guidance](skills/pixelorama-skills/references/drawing.md) adds composition, palette, animation, tileset, and export checks. The optional read-only doctor checks prerequisites and loopback health without installing anything.

| Prompt | What the agent should check |
| --- | --- |
| “Make eight 32×32 potion icons in one style.” | Shared palette, lighting, scale, padding and transparent exports. |
| “Animate this slime without changing its design.” | A protected source, stable anchors, all short-loop frames and loop transition. |
| “Turn this terrain into a seamless 16×16 tileset.” | Grid, 3×3 repeat, boundaries and transitions. |
| “Change only the cloak on this character.” | Exact target layer/region; unrelated pixels and timing preserved. |

## Runtime and privacy

Live control needs Pixelorama, a compatible local bridge, Node.js, and an agent with MCP access to that host. The bridge runs locally, but canvas screenshots may still be sent to the agent's configured model provider. No paid image API is required by this skill; agent subscriptions or provider usage may have their own costs.

The reviewed upstream bridge has an **unauthenticated loopback HTTP endpoint**. First activation requires informed approval. Do not expose or tunnel it, and do not assume that client-side tool restrictions secure it. `eval_gdscript` is not used by default. See [Security](SECURITY.md) before enabling the bridge.

## Validation, not marketing

Repository checks cover the skill's structure, local links, source references, diagnostic behavior, and reproducible packaging. They are **not** an art-quality benchmark or proof of desktop compatibility. Actual MCP/editor drawing, Windows installation, and artistic quality require the documented [smoke test](docs/SMOKE_TEST.md).

See the exact scope and results in [Validation](docs/VALIDATION.md), and the pinned documentation sources in [Upstream review](docs/UPSTREAM.md).

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/package.py --out dist
```

Python 3.10+ is needed only for these maintenance tools and the optional doctor, not to read/use the skill itself. The `dist/` files are generated, not committed. The included GitHub Actions workflow runs repository checks when published; it does not run a desktop editor.

## Repository map

```text
skills/pixelorama-skills/   The installable skill; copy this folder
  SKILL.md                 Compact core workflow
  references/              Setup and drawing guidance
  scripts/doctor.py        Optional, read-only environment check
assets/                    Decorative README banner
scripts/                   Validation, packaging, cloud publishing helper
tests/                     Standard-library unit tests
docs/                      Evidence, smoke test and publishing guide
```

## Credits and license

Built around [Pixelorama](https://github.com/Orama-Interactive/Pixelorama), [Pixelorama-MCP](https://github.com/abidoo22/Pixelorama-MCP), and the [Agent Skills specification](https://agentskills.io/specification). The upstream README inspired this project's gallery and presentation; the operational guidance is maintained separately.

Our instructions and helper code are [MIT licensed](LICENSE). Upstream projects and artwork retain their own notices. [Third-party notices](THIRD_PARTY_NOTICES.md) · [Changelog](CHANGELOG.md)
