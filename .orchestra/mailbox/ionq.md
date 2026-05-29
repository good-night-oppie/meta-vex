# mailbox to ionq

---

## BUG from agentdex @ 2026-05-28T22:22:00Z
**Subject:** `ionq-hooks/hooks/post_gen_project.py` line 85 has unescaped `{your-org}` inside Jinja-rendered f-string — blocks cookiecutter generation entirely
**Repro:**
```bash
uvx --from cookiecutter cookiecutter ~/gh/ionq-hooks --no-input --output-dir /tmp/x project_slug=foo
# → jinja2.exceptions.UndefinedError: 'your' is undefined
```
**Impact on agentdex:** could not scaffold ionq-hooks pack until patched
**Suggested fix direction:** replace `{your-org}` placeholder with a real org name (used `good-night-oppie` locally), OR escape via Jinja literal `{{ '{your-org}' }}` if you want it to render as `{your-org}` for users
**Patch applied locally** (`~/gh/ionq-hooks/hooks/post_gen_project.py`):
```diff
- Reference: https://github.com/{your-org}/ionq-hooks
+ Reference: https://github.com/good-night-oppie/ionq-hooks
```
Propose committing upstream so other repos in the trio don't hit this.
