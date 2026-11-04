# The GitHub planning surface

> **Team mode only.** This page is a prerequisite for team mode, not for the default single-operator
> mode. Enable team mode first with `/foundry:team-mode enable` (script
> `scripts/foundry_operating_mode.py enable-team`); see "Operating modes" in
> [`../OPERATING-MODEL.md`](../OPERATING-MODEL.md). The issue and PR templates below stay as they are
> and are harmless in single-operator mode.

Where the team plans and coordinates: one shared GitHub Project, two issue forms, a PR template and a
few labels. The meanings (states, ownership, completion, requests) are defined once in
[`../OPERATING-MODEL.md`](../OPERATING-MODEL.md); this page is the setup that makes them visible.
Creating the Project, labels and views is operator setup, done by hand on your own repositories.

## What ships in this template

| File | Purpose |
|---|---|
| `.github/ISSUE_TEMPLATE/task.yml` | A task: What, Why, Owner, Target repo key, Acceptance criteria, Done means, Context links, Work type. |
| `.github/ISSUE_TEMPLATE/request.yml` | A request to another operator. Applies the `request` label. |
| `.github/ISSUE_TEMPLATE/config.yml` | Turns off blank issues so work arrives through a form. Edit its link to point at your repository. |
| `.github/PULL_REQUEST_TEMPLATE.md` | Linked issue, evidence links, outstanding human decision, and when `Closes #n` is allowed. |

The task form renders its Done-means field as a `### Done means` heading followed by a fenced
block, which is the shape the ticket reader (`foundry-ticket.py`) parses and runs. The command is
optional for a document outcome; then the acceptance criteria name the accepting owner.

Form `required` flags are enforced by GitHub only on public repositories. On a private repository
they are a prompt, so treat the form as guidance there.

## One shared Project per workspace

Create one Project (owned by the same user or organization as the planning repository) and share it
with every operator. A joining operator reuses it; nobody creates a second one.

**Status** holds exactly the five states of the working agreement, in this order:
`Backlog`, `Ready`, `In progress`, `Review`, `Done`. A blocker is not a sixth state; it is the native
"blocked by" relationship.

Suggested fields:

| Field | Type | Use |
|---|---|---|
| Priority | single select | Orders Ready work and competing blockers. |
| Target date | date | The date or iteration for a request or task. Keep the first target when rescheduling. |
| Work type | single select | `code`, `architecture`, `security`, `operations`, `document`. |
| Outcome owner | text or person | The accepting human, where it differs from the assignee. |

### Four views

| View | Filter | Answers |
|---|---|---|
| team | all items, grouped by Status | What is the state of the whole plan? |
| personal | `assignee:@me` | What is mine? |
| blocked | `is:blocked` | What cannot proceed, and on what? |
| review | `status:Review` | What awaits review or acceptance? |

## Labels, and what is not available

Issue types and custom issue fields are organization features. On a user-owned repository they do not
exist, so this setup uses labels and Project fields instead. The meanings do not change.

| Label | Meaning |
|---|---|
| `request` | An action needed from another operator. Applied by the request form. |
| `work:code`, `work:architecture`, `work:security`, `work:operations`, `work:document` | The work type, when you want it on the issue as well as in the Project. Applied by hand. |
| `repo:<key>` | The target repository, where you want to filter by it. `<key>` is a `repos{}` key. |
| `status:backlog`, `status:ready`, `status:in-progress`, `status:review`, `status:done` | Pilot fallback only, for an operator whose token cannot read the Project yet. The Project `Status` field is the state; the deck never writes these labels when the field is readable. |

Create the labels yourself; nothing here creates them for you. An expedited exception to the capacity
limit is also a visible label plus a one-line comment, as the working agreement says.

## Project automation: switch the built-in workflows off

GitHub Projects ships two built-in workflows that are ON by default: **item closed → Done** and
**pull request merged → Done**. Left on, they mark a `not_planned` or `duplicate` closure as Done and
mark a merge as Done while a human decision is still outstanding — exactly what the working
agreement forbids. Open the Project → Workflows and disable both (keep *item added → Backlog* and
*auto-add* if you use them). Done is set by the accepting human, not by automation.

## Requests and blockers

Open a request from `request.yml`, assign it to the target operator, and mark your own task blocked by
it (the issue sidebar, or `gh issue edit <your-task> --add-blocked-by <request>`; `gh issue create --blocked-by <n>` is for a NEW issue that is blocked by `n`). Add an issue to the Project with
`gh issue edit <n> --add-project "<project title>"`.

## Credentials: one set per operator

Each operator authenticates `gh` with their own account and never shares or copies a token or login
with a colleague. Reading and updating the Project needs the `read:project` scope to read and the
`project` scope to write; the operator adds them with `gh auth refresh -s read:project -s project`
and runs that command themselves. Attribution of every event depends on each person acting as
themselves.

## Repository mapping

The `target repo key` on a task is a key of `repos{}` in
[`.claude/foundry-project.json`](../.claude/foundry-project.json); see
[`control-plane.md`](control-plane.md) §3 for adding one. That mapping decides which local checkout a
task is worked in. A task whose key does not resolve is not eligible for dispatch.

## Proposal: a `github_scope` block

A workspace may eventually name its planning surface in `.claude/foundry-project.json`. This is a
proposal; nothing reads it yet and it is not in the shipped file.

```jsonc
"github_scope": {
  "owner": "acme",                 // user or organization that owns the Project
  "planning_repo": "acme-handbook",
  "project_number": 1,             // the shared Project
  "operators": { "alice-login": "op_alice", "bob-login": "op_bob" }  // GitHub login -> operator id
}
```

The `operators` map mirrors the `github` field already in `.claude/foundry-operators.json`.
