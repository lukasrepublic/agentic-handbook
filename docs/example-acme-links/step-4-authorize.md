# Step 4 — Authorize the acceptance contracts

**Goal.** Freeze and operator-sign each atom's contract. This is the **front-authorization gate** —
the load-bearing v1 safety action. An un-authorized spec can *never* reach `main` (no skip).

## You run

```bash
/foundry:authorize        # auth · create-link · resolve-redirect · dashboard
#   for each atom: displays the scope + the live-seam checkpoints you are signing,
#   gets your explicit per-atom confirmation, then freezes spec_sha256 + contract_sha256.
```

## What to expect

For each atom the gate prints the exact checkpoints — the PASS criteria — and asks you to confirm.
On `--yes` it writes a signed `authorized:` block below a sentinel in the contract:

```yaml
authorized:
  operator_id: op_lukas
  auth_seq: 1
  spec_sha256:     <hash of the spec's normative region>
  contract_sha256: <hash of the contract-proper>
  merge_autonomy_mode: regular
```

An audit-trail entry is recorded. From here the floor and certification verify every change against these frozen
hashes — change the spec after authorizing and the merge is blocked until you **re-authorize**.

> **Why confirm by hand?** The operator's explicit yes — having seen the exact checkpoints — *is*
> the front-funnel authority. The agent never self-confirms.

**Next:** [Step 5 — the money shot](step-5-money-shot.md).
