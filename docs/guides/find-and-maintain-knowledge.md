# Find and maintain project knowledge

Locate the current requirement, architecture decision, security assessment or runbook for a task;
tell accepted history from an active instruction; and update or supersede a document so that one
current source remains. The rule behind this is in
[`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md): one document per decision, with one current
version, either a Git file or an issue artifact and never both maintained in parallel.

Checked against the foundry base tree `origin/atom/subtract`; the release pin is pending: lands with gn-06.

## Starting conditions

- You have a task or question that depends on existing knowledge.
- Your session is at the workspace root, so the hosted repositories and the workspace's own `docs/`
  resolve.

## Actor and permissions

- **Any operator** reads everything they are permitted to read.
- **The document's owner**, or the named accepting owner on a document task, accepts a change. A
  security-relevant change also needs the separate-context security review the floor requires.

## Steps

1. **Start from the task.** Open the task's Context links; they name the current source. If a link is
   missing, that is a defect in the task: add it.

2. **Search by kind.** Typical homes:

   ```bash
   ls docs/architecture docs/runbooks
   git grep -n "<topic>" -- docs ':!docs/example-acme-links'
   gh issue list --search "<topic>" --state all
   ```

   Requirements live in the issue's acceptance criteria (and any opt-in spec); architecture in
   `docs/architecture/`; security assessments and runbooks in their own documents linked from the work.

3. **Separate accepted history from active instruction.** Active: the working agreement, current docs
   and open issues. History: closed issues, frozen contracts, old specs and release records. History
   keeps its bytes. Read it for context and never follow it as an instruction without finding the
   active document that confirms it.

4. **Check currency before relying on a document.** Look at its last accepted revision
   (`git log -3 --format='%h %ad %s' -- <path>`) and at any `Superseded by` note. If two documents
   say different things, the newer accepted one wins and the other is marked as superseded.

5. **Update in place** when the decision is the same: edit the document on a branch, open one PR,
   link the issue that motivated it, and get the owner's acceptance. Paper is written only when the
   ticket allows it (`Paper allowed`).

6. **Supersede** when the decision changes: write the new document, add a first line `Supersedes:
   <old path>` to it and `Superseded by: <new path>` to the old one (the old file otherwise keeps its
   content), and update every Context link that pointed at the old one.

## Expected results

- Exactly one current document answers each question, and the task links to it.
- A superseded document points forward; nothing active points to it.
- The change is a reviewed PR with an accepting human, recorded on the issue.

## Outstanding human decisions

- Which document is the current source when two disagree.
- Whether knowledge lives in Git or as an issue artifact: pick one, in writing.
- Acceptance of the document change and, where relevant, its security review.

## If it fails

- No current document exists: open a document task ([work-each-day.md](work-each-day.md), Example B)
  rather than inventing the answer.
- Two documents conflict and nobody can say which wins: escalate to the planning owner on the issue; do
  not edit history to settle it.
- A document is out of date after an upgrade: see the preserved-instructions entry in
  [diagnose-and-recover.md](diagnose-and-recover.md).
