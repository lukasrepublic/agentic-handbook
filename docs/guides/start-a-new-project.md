# Start a new project

> **Prerequisite: team mode.** The shared GitHub setup and Project queue below apply only in team mode. Enable it first with `/foundry:team-mode enable` (script `scripts/foundry_operating_mode.py enable-team`; pending: lands with gn-17). Single-operator mode is the default and needs none of it; see "Operating modes" in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md).

From an empty folder to your first accepted task. The meanings of the five states, ownership and
acceptance are defined once in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md); the shared
GitHub setup is in [`../github-planning-surface.md`](../github-planning-surface.md). This guide
links to both and does not restate them.

Checked against the foundry base tree `origin/atom/subtract`. The release pin for this guide is
pending: lands with gn-06. Until then no version is named here; the install step takes the
marketplace's current release.

## Starting conditions

- You have Claude Code, `python3` with the foundry runtime dependencies, node 22 or newer, `git`
  and the GitHub CLI `gh`.
- You own (or administer) a GitHub account or organization where the planning repository and the
  Project will live, and you can create repositories there.
- Nothing is installed yet, or this is a clean machine for the project. For an existing codebase
  use [adopt-an-existing-codebase.md](adopt-an-existing-codebase.md) instead.

## Actor and permissions

Two roles, which may be one person on a solo project:

- **Project adoption owner**: creates the shared planning repository and the one shared GitHub
  Project, creates the labels, and decides who is an operator. Needs admin on the planning
  repository and the `project` scope on their own `gh` login.
- **Individual operator** (each person, for themselves): authenticates `gh` with their own
  account, adds their own scopes, and keeps their own local environment. Credentials are never
  shared or copied between people.

## Steps

1. **Preview, then scaffold the workspace** (the adoption owner, in a terminal, before any Claude
   session exists):

   ```bash
   npx create-agentic-workspace --dir my-workspace --dry-run
   npx create-agentic-workspace --dir my-workspace
   ```

   `--dry-run` prints every file and capability the wizard would write and writes nothing.
   Add `--gh-account <name>` on a machine with several GitHub accounts so commits in this folder
   use the right identity.

2. **Authenticate your own `gh` login** and add the Project scopes yourself (a credential step: you
   run it, nobody runs it for you):

   ```bash
   gh auth login
   gh auth refresh -s read:project -s project
   ```

3. **Create the shared GitHub scope** by hand, following
   [the planning surface](../github-planning-surface.md): the planning repository from this
   template, one Project with the five Status values and the four views, and the labels.

4. **Install the plugin and open the session at the workspace root**:

   ```bash
   cd my-workspace
   claude plugin marketplace add lukasrepublic/agentic-foundry
   claude plugin install foundry@agentic-foundry
   claude
   ```

   Always start Claude Code at the workspace root, never inside a hosted repository (see
   [the session rule](../control-plane.md#2-the-session-rule-always-start-from-the-control-plane)).

5. **Wire and diagnose** inside the session:

   ```text
   /foundry:init
   /foundry:doctor
   ```

   Edit `.claude/foundry-operators.json` so your GitHub login maps to your operator id, and commit it.

6. **Native capability check** (inbox coverage, Project access, repository protections): the
   command is pending: lands with gn-03. Until it ships, confirm by hand that `gh project list --owner <owner>`
   shows the shared Project and that `gh issue list --assignee @me` runs without an access error.

7. **Establish the working agreement and the first minimal collection**: keep
   [`OPERATING-MODEL.md`](../../OPERATING-MODEL.md) as it is or edit it in writing, then add one
   hosted code repository by the steps in [the control plane guide](../control-plane.md#3-setting-up-a-multi-repo-project-step-by-step).

8. **Run one owned task to Done.** Create a task from the issue form, set yourself as owner and
   mark it Ready on the Project. Then:

   ```bash
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" start <issue-number>
   ```

   ```text
   /foundry:dispatch <issue-number>
   ```

   When the worker reports, run the repository's own tests and the Done-means command locally with
   `bash "$CLAUDE_PLUGIN_ROOT/scripts/foundry-test.sh"`, review the PR, and accept the outcome. The
   full daily cycle is in [work-each-day.md](work-each-day.md).

## Expected results

- `my-workspace/` exists with `.claude/settings.json`, the operator registry and the managed files;
  re-running the wizard later reports drift and never overwrites an edited file.
- `/foundry:doctor` reports `DOCTOR-GREEN`.
- Everyone who works on the project sees the same Project, with one Status field of five values.
- Your first task moves Backlog, Ready, In progress, Review, Done on the Project, with the PR and
  the Done-means output linked as evidence. A green installation or a green doctor alone is not
  the journey; the accepted task is.

## Outstanding human decisions

- Who the project adoption owner is, and who the operators are.
- Whether to keep the pilot defaults (two started outcomes per operator, blocker ordering) or
  change them in writing in the working agreement.
- Branch protection and required checks on every code repository (the merge floor is your
  platform's, not the plugin's).
- Sign-off on any release: the operator's own walkthrough, a practice no check asserts.

## If it fails

- Wizard refuses a non-empty folder: re-run with `--existing`, which adds only missing pieces.
- `/foundry:doctor` is red: read the failing probe line; the usual causes are a session opened in a
  hosted repository rather than the workspace root, or a missing `pyyaml`. See
  [diagnose-and-recover.md](diagnose-and-recover.md).
- `gh` reports a missing scope: run the refresh in step 2 yourself.
- A `/foundry:*` verb is not found: the plugin is not enabled in this scope; re-run the install
  in step 4 and start a new session.
