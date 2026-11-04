# Join an existing team

> **Prerequisite: team mode.** The team you join runs in team mode; the shared Project, inbox and requests below exist only there. Enable it first with `/foundry:team-mode enable` (script `scripts/foundry_operating_mode.py enable-team`). Single-operator mode is the default and needs none of it; see "Operating modes" in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md).

You are a new engineer on a project that already has a workspace, a shared GitHub Project and a
working agreement. You set up your own access and environment, reuse everything shared, and prove it
with one real task and one request/handoff exchange. You do not recreate the Project, rerun a
migration, or receive anyone's credentials.

Definitions: [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md),
[`../github-planning-surface.md`](../github-planning-surface.md). Checked against the foundry base
tree `origin/atom/subtract`; the release pin is pending: lands with gn-06.

## Starting conditions

- The project adoption owner has added you to the GitHub organization, the planning repository, the
  shared Project and the code repositories you will work in.
- The workspace repository exists and is already wired (`.claude/foundry-operators.json`,
  `repos{}`, working agreement).

## Actor and permissions

- **What the adoption owner supplies:** the workspace repository URL, the Project's owner and
  number, the repository keys and their clone URLs, the labels in use, and an entry for you in
  `.claude/foundry-operators.json` (your GitHub login mapped to an operator id).
- **What you configure privately:** your own `gh` login and scopes, your own git identity, your own
  local clones. Nothing is copied from a colleague.

## Steps

1. **Clone the workspace and enter it:**

   ```bash
   git clone git@github.com:<owner>/<workspace>.git
   cd <workspace>
   ```

2. **Authenticate as yourself** (a credential step, done by you only):

   ```bash
   gh auth login
   gh auth refresh -s read:project -s project
   ```

3. **Install the plugin from the marketplace the workspace names**, then open the session at the
   workspace root:

   ```bash
   claude plugin marketplace add lukasrepublic/agentic-foundry
   claude plugin install foundry@agentic-foundry
   claude
   ```

4. **Bring in the code repositories** the manifest declares, as gitignored siblings:

   ```text
   /foundry:repos sync
   /foundry:repos status
   ```

5. **Verify identity, versions and repository binding:**

   ```text
   /foundry:doctor
   ```

   Confirm that your login appears in `.claude/foundry-operators.json`, and that the plugin version
   your session loads matches what your colleagues run (ask in the planning repository, not in a
   private chat).

6. **Check access to the shared scope:**

   ```bash
   gh project list --owner <owner>
   gh issue list --assignee @me
   gh issue list --label request --assignee @me
   ```

   The inbox-coverage check and the usage-collection check are pending: lands with gn-09 and
   pending: lands with gn-05 respectively. Until they ship, the three commands above are the check
   that you can read your own queue and your own requests.

7. **Take one owned task.** Ask the planning owner to assign you a Ready task, then follow
   [work-each-day.md](work-each-day.md).

8. **Exchange one real request and handoff** with an existing operator: open a request issue from
   the request form, assign it to them, and mark your task blocked by it; later, receive one and
   answer it. Record a handoff comment on your task when you stop (see
   [diagnose-and-recover.md](diagnose-and-recover.md)).

## Expected results

- You see the same Project and views as everyone else, and your personal view lists only your tasks.
- `/foundry:doctor` is green and your first owned task reaches Review with linked evidence.
- A colleague can read your request and handoff from GitHub alone.
- No shared task was duplicated and no migration was rerun.

## Outstanding human decisions

- Which Ready task is yours first, and who accepts it (the planning owner).
- Which repositories you are scoped to work in.
- Any access still missing: requested from the adoption owner, never worked around.

## If it fails

- `gh project list` shows nothing: you lack the `read:project` scope or Project membership. Run the
  refresh yourself, then ask the owner to check your membership.
- Your login is not in the operator registry: ask the owner to add it in a reviewed commit; do not edit
  someone else's entry.
- `/foundry:repos status` reports a dangling or missing clone: clone it where the manifest says.
- Different plugin versions across the team: update your own machine and say so in the planning
  repository. See [diagnose-and-recover.md](diagnose-and-recover.md).
