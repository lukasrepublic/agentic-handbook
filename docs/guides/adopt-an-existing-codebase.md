# Adopt an existing codebase

> **Prerequisite: team mode.** This guide uses the shared GitHub Project and team surfaces. Enable it first with `/foundry:team-mode enable` (script `scripts/foundry_operating_mode.py enable-team`; pending: lands with gn-17). Single-operator mode is the default and needs none of it; see "Operating modes" in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md).

Bring a repository that has never used Foundry under the shared operating model while keeping what
it already has: its CI, branch protections, docs, architecture and work in flight. You do not extract
or authorize a specification for every capability before your first change.

Definitions live in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md) and
[`../github-planning-surface.md`](../github-planning-surface.md). Checked against the foundry base
tree `origin/atom/subtract`; the release pin is pending: lands with gn-06.

## Starting conditions

- A codebase on GitHub with its own CI and, ideally, branch protection already in place.
- No `.claude/foundry-*.json` files. If they exist, use
  [upgrade-and-migrate.md](upgrade-and-migrate.md).
- The prerequisites of [start-a-new-project.md](start-a-new-project.md) (Claude Code, `python3`,
  node 22 or newer, `gh`).

## Actor and permissions

- **Project adoption owner**: reads the existing repository settings, creates the shared Project
  and labels, decides which existing issues become tasks. Needs admin read on the repository.
- **Operator**: authenticates `gh` as themselves. Adoption changes no protection rule and no
  permission; anything that would is a human decision below.

## Steps

1. **Inventory before changing anything.** Record, in one issue or a short note, what exists:

   ```bash
   gh api repos/<owner>/<repo>/branches/main/protection
   ls .github/workflows
   gh issue list --state open --limit 200
   ls docs
   ```

   Note the required checks, who may merge, the existing docs and ADRs, and open work. These stay
   as they are.

2. **Scaffold beside the code, not over it.** The workspace is a separate repository that hosts
   your code repository as a gitignored sibling (see [the control plane guide](../control-plane.md)).
   Preview first:

   ```bash
   npx create-agentic-workspace --dir my-workspace --dry-run
   npx create-agentic-workspace --dir my-workspace
   ```

   To add the pieces into a folder that already has files instead, use `--existing`: nothing already
   there is overwritten.

3. **Install and wire**, from the workspace root:

   ```bash
   claude plugin marketplace add lukasrepublic/agentic-foundry
   claude plugin install foundry@agentic-foundry
   ```

   ```text
   /foundry:init
   /foundry:doctor
   ```

4. **Declare the code repository**: clone it into the workspace as a gitignored sibling, add its
   `repos{}` entry, and keep its own CI and protections as the merge floor
   ([step 4 of the control plane guide](../control-plane.md#step-4--bring-in-your-first-code-repo)).

5. **Create the shared Project and labels** by hand ([planning surface](../github-planning-surface.md)).
   Move existing issues in only as you touch them; do not bulk-import the backlog.

6. **Do one real change using existing knowledge.** Write a task whose Context links the existing
   docs and ADRs, with a Done-means command from the repository's own test suite:

   ```bash
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" start <issue-number>
   ```

   ```text
   /foundry:dispatch <issue-number>
   ```

   Specification extraction is opt-in per change; the default path needs the task, its Done means and
   the links to what is already written.

## Expected results

- The repository's CI, protections, history and docs are unchanged; the workspace sits beside them.
- One shared Project, the first real change merged through your existing required checks, and its
  issue closed `completed` after the accepting human agreed.
- Differences from a new project: an inventory exists, existing issues were imported selectively, and
  no spec was authorized wholesale.

## Outstanding human decisions

- Which open issues become tasks, and who owns each.
- Whether any existing branch protection should change (never done by this procedure).
- Which existing documents are the current source for each topic; see
  [find-and-maintain-knowledge.md](find-and-maintain-knowledge.md).

## If it fails

- The Done-means command cannot run locally: fix the command in the issue, or have the operator read
  and start the ticket with `--trust-author` when the issue author lacks write access.
- The wizard would touch a file you maintain: stop, run `--dry-run`, and keep your file; an edited
  managed file is reported as drifted and left byte-identical.
- Anything else: [diagnose-and-recover.md](diagnose-and-recover.md).
