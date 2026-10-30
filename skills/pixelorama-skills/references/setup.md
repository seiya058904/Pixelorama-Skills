# Setup and recovery

Read only when installation, connectivity, or recovery is needed. Default bridge: [abidoo22/Pixelorama-MCP](https://github.com/abidoo22/Pixelorama-MCP/tree/56fd8aa94c0905591bd2515fe9823eb70d4496d2). Reuse a working alternative rather than installing a second bridge. The reviewed upstream revision is `56fd8aa94c0905591bd2515fe9823eb70d4496d2`; it is a reference point, not a promise of compatibility or security.

## 1. Inspect the host

Confirm where Pixelorama runs, which shell/OS the agent controls, and whether that same host exposes the client's MCP tools. On Windows, prefer a native Windows Node process for a native Pixelorama app. WSL, containers, SSH sessions, and cloud agents can have different loopback networks and path formats; do not solve this by opening port 7373 to a LAN or the internet.

Check `node --version`, `npm --version`, `git --version`, existing Pixelorama installs, and the client's registered MCPs. For new installs, use a maintained Node.js LTS satisfying the upstream package requirements; the upstream documented minimum of 18 is not a recommendation to install an obsolete runtime.

Optional read-only diagnostic, using the absolute path of this skill:

```sh
python "<SKILL_DIR>/scripts/doctor.py"
```

It checks local executables and GET `/health` on literal loopback only. It installs nothing, changes no settings, and does not prove MCP/editor operation. Python is optional: use the checks below without installing it solely for this helper. On Windows, `py -3` may be the available interpreter.

## 2. Install only missing components

Use an approved, persistent, user-owned directory outside unrelated repositories. Inspect any existing target; never overwrite it. For a fresh installation, review the upstream package manifests and lifecycle scripts, choose a specific revision, and record it. The commands below deliberately pin the reviewed revision:

```sh
git clone https://github.com/abidoo22/Pixelorama-MCP.git "<INSTALL_DIR>/Pixelorama-MCP"
cd "<INSTALL_DIR>/Pixelorama-MCP"
git checkout --detach 56fd8aa94c0905591bd2515fe9823eb70d4496d2
cd mcp-server
npm ci --ignore-scripts
npm run typecheck
npm run build
```

Replace placeholders with actual OS-native paths; run each command only after the previous one succeeds. If a dependency genuinely requires an install script, inspect it and seek any necessary authorization before running it. Do not automatically run `npm audit fix`, upgrade dependencies, or switch to another version to hide errors.

If Pixelorama is absent, obtain a stable build from its [official releases](https://github.com/Orama-Interactive/Pixelorama/releases). Inspect published checksums when supplied. Do not require elevation or install Godot unless necessary. The editor and bundled bridge normally do not require a separate Godot installation; rebuilding the `.pck` does.

## 3. Enable the bridge deliberately

At the reviewed revision, `pixelorama-plugin/Main.gd` binds to `127.0.0.1:7373`, accepts `/command` without request authentication, and advertises permissive CORS. Dynamic GDScript is an additional privileged endpoint. **Disclose this before first activation and obtain explicit approval for this risk** unless already granted. No approval: finish safe preparation and leave the extension disabled. A localhost check, skill instruction, or client tool denylist is not authentication.

Use a trusted dedicated session; never tunnel, forward, or publicly bind this endpoint. A properly authenticated bridge is preferable for untrusted/shared environments. This skill does not patch the server. Do not claim all data remains local: model-side image inspection follows the configured provider's data path.

In Pixelorama: **Edit → Preferences → Extensions → Add Extension**, choose `pixelorama-plugin/PixMcpBridge.pck`, enable it, and restart only after unsaved work has been saved. Perform these actions through authorized GUI tools when available; otherwise give the user only these missing actions. Do not blindly rewrite the app's configuration or bypass extension quarantine.

Record the app version, extension API version, server commit, and `.pck` SHA-256. A bundled binary is not proven to match source just because it is in the same checkout. Verify the resulting capabilities; investigate or explicitly rebuild a mismatched plugin using upstream instructions.

```sh
curl --noproxy "*" --max-time 5 --fail http://127.0.0.1:7373/health
```

On Windows PowerShell, use `curl.exe` rather than an ambiguous alias. Expect `status: ok` and `server: pix-mcp-bridge`; examine the reported versions. Do not send mutations to an unexpected process on that port.

## 4. Register MCP for the actual client

Use the built **absolute** `mcp-server/dist/index.js` path. Registration is client-specific; merge only the intended entry and preserve other settings. Prefer project-scoped installation when the user has not requested global changes; choose the CLI's documented scope. Check the installed CLI's help before changing configuration.

Codex CLI, after confirming the intended configuration scope:

```sh
codex mcp add pixelorama -- node "<ABSOLUTE_INDEX_JS>"
codex mcp list
```

Claude Code, explicit personal scope when requested:

```sh
claude mcp add --scope user --transport stdio pixelorama -- node "<ABSOLUTE_INDEX_JS>"
claude mcp list
```

Other MCP clients: use their documented local **stdio** entry, with `command` set to `node` (or its absolute executable path) and one argument containing the absolute entrypoint path. Do not paste Claude's JSON schema into an incompatible client. Where supported, disable `eval_gdscript` in client tool settings as defense in depth—not as a bridge security fix. Reload only when necessary; a newly registered MCP may require a new session.

## 5. Prove readiness

Separate four gates: dependencies/build; bridge health; a real MCP read; a real editor round trip. Do not stop at `mcp list`. In a new 16×16 test project, draw a 4×4 rectangle in one batch, capture it, save a new `.pxo`, export a PNG, and verify file dimensions and the reopened project. Preserve the user's previous active project and unsaved work. Keep test outputs in a named folder; do not delete them without approval.

Record exact versions and evidence locally, outside the shared skill; omit secrets and personal paths from public reports. Reuse a verified setup on later tasks rather than reinstalling. Revalidate after a version/configuration change. Upstream `npm test` at the reviewed revision is a placeholder, not an integration test.

## Recovery

| Symptom | Next safe action |
| --- | --- |
| Connection refused | Check the editor, extension state, and port owner; do not kill an unknown process. |
| Health succeeds, MCP fails | Check client entrypoint, runtime, MCP stderr, and actual tool discovery. |
| Commands hang | Check dialogs, paused/minimized editor state, logs, and versions. Inspect state before retrying mutations. |
| API/schema mismatch | Compare the running plugin with the pinned source; do not assume advertised version ranges prove compatibility. |
| Missing host access | Prepare assets/configuration and report the exact missing capability; never substitute the cloud machine for the user's desktop. |

Official client references: [Codex MCP](https://developers.openai.com/codex/mcp), [Claude Code MCP](https://code.claude.com/docs/en/mcp).
