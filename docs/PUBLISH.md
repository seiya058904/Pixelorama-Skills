# Publish from an authenticated cloud workspace

The repository is prepared for `seiya058904/Pixelorama-Skills`, public visibility. `.github/repository.json` records the intended About description, homepage and topics; GitHub does not apply this file automatically.

The preparation environment did not provide GitHub write operations or an authenticated GitHub CLI. **No remote repository, commit, About update, tag, or release was created by preparing these files.**

Use a cloud coding workspace with Git, Python 3.10+, and a GitHub CLI already authenticated to the intended account. No copy needs to be installed on the user's Windows PC. Do not paste tokens into the chat or commit them.

After reviewing the content and authorization, run from the repository root:

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/publish.py --execute
```

Without `--execute`, the helper prints its plan and makes no remote changes. Execution verifies the authenticated login and refuses an existing Git worktree or existing destination repository, so it cannot overwrite unrelated work. It creates the public repo, commits explicit project files using the account's GitHub noreply identity, pushes `main`, and applies the About description/homepage/topics. No force-push, history rewrite, automatic tag/release, or recursive cleanup is used.

If a partial failure occurs, the helper stops and prints the failed phase. Inspect the exact local/remote state; do not re-run destructively. A published repository must be read back and its GitHub Actions run checked before claiming completion. Creating a GitHub release is a separate optional action, not required to distribute the repository's source.
