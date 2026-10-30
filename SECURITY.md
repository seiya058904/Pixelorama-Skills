# Security boundaries

This package supplies instructions and an optional read-only diagnostic. It does not enforce a sandbox or harden third-party software.

At Pixelorama-MCP revision `56fd8aa94c0905591bd2515fe9823eb70d4496d2`, the bridge listens on loopback, accepts commands without request authentication, advertises permissive CORS, and exposes dynamic GDScript execution. These are source-review observations, not a reproduced exploit or an assurance about every release or bundled binary. A local endpoint is still a privileged control surface.

Before enabling it, disclose this risk and obtain explicit approval. Do not forward or expose it. Do not disable browser/network safeguards. Prefer an authenticated bridge for shared or untrusted environments. Disabling `eval_gdscript` in the agent is defense in depth only; another caller could bypass that client. The skill does not patch or endorse the upstream security design.

Local transport and local inference are different. Screenshots, project details and prompts returned to a cloud agent may be processed by its provider. Respect private-artwork restrictions. No telemetry is implemented by this package, but it cannot speak for the editor, agent, extensions, or provider.

Keep user projects, installation records and diagnostic outputs out of public commits. Never commit API keys, local paths containing personal information, app configuration, downloaded binaries, or generated test artwork by accident. Limit output writes to authorized paths and preserve originals/undo history.

The doctor accepts literal loopback HTTP endpoints only, does not follow redirects, bypasses proxy environment settings, and limits response size and applies a socket timeout. It makes no mutations. Passing health checks does not establish authentication, trust, MCP connectivity, or artistic correctness.

For a suspected vulnerability, report sanitized reproduction steps to the relevant maintainer. Do not post credentials or private artwork in a public issue. No private disclosure channel is configured by this package.
