# Source review

Reviewed on **2026-10-30**. This is provenance, not a compatibility certification.

| Source | What was checked |
| --- | --- |
| [Pixelorama-MCP `56fd8aa9`](https://github.com/abidoo22/Pixelorama-MCP/tree/56fd8aa94c0905591bd2515fe9823eb70d4496d2) | README, tool reference, setup material, server/client architecture, bridge request handling and dynamic script capability. |
| [Bridge Main.gd](https://github.com/abidoo22/Pixelorama-MCP/blob/56fd8aa94c0905591bd2515fe9823eb70d4496d2/pixelorama-plugin/Main.gd) | Loopback binding, request handling, CORS, lack of request authentication in reviewed code. |
| [Package manifest](https://github.com/abidoo22/Pixelorama-MCP/blob/56fd8aa94c0905591bd2515fe9823eb70d4496d2/mcp-server/package.json) | Build/typecheck scripts and placeholder test command. |
| [License](https://github.com/abidoo22/Pixelorama-MCP/blob/56fd8aa94c0905591bd2515fe9823eb70d4496d2/LICENSE) | MIT; pix-MCP Contributors attribution. |
| [Pixelorama stable v1.2.3](https://github.com/Orama-Interactive/Pixelorama/releases/tag/v1.2.3) | Official release metadata; not a verified runtime combination in this environment. |
| [Agent Skills specification](https://agentskills.io/specification) | Portable frontmatter, directory naming and progressive loading. |
| [Codex skills](https://developers.openai.com/codex/skills) | `.agents/skills` locations and skill discovery. |
| [Codex MCP](https://developers.openai.com/codex/mcp) | Local stdio registration and client-side tool restrictions. |
| [Claude Code skills](https://code.claude.com/docs/en/skills) | `.claude/skills` locations. |
| [Claude Code MCP](https://code.claude.com/docs/en/mcp) | Explicit scope and stdio command syntax. |

Gallery URLs are pinned to the same upstream source revision. No measured latency, tool-count benchmark, artist-quality claim, Windows certification, or claim of fully local model inference is copied from upstream marketing.

Re-check current documentation before changing installation instructions. A new upstream version should trigger source review and the editor smoke test, not an automatic dependency bump. Record tested app/plugin/client/runtime versions separately from declared version compatibility.

CI checkout action is pinned to `11d5960a326750d5838078e36cf38b85af677262`, resolved from the official `actions/checkout` v4 tag during this review. Publication command syntax was checked against the official [GitHub CLI create](https://cli.github.com/manual/gh_repo_create), [API](https://cli.github.com/manual/gh_api), and [edit](https://cli.github.com/manual/gh_repo_edit) documentation.
