# Step 1 — Install + scaffold from the template

**Goal.** Stand up the workspace (this template) with the Foundry factory wired in and green,
then scaffold the Acme Links app it will build.

## You run

```bash
# 1. Use this template (the workspace = the WHAT), then wire the factory (the HOW):
claude plugin marketplace add lukasrepublic/agentic-foundry
claude plugin install foundry@agentic-foundry
/foundry:doctor                      # → DOCTOR-GREEN (the gate is live + fail-closed)

# 2. Scaffold the app repo — Next.js App Router + Drizzle + Better Auth + the design system:
cp .env.example .env                 # set DATABASE_URL + BETTER_AUTH_SECRET
make install                         # npm install
make db-push                         # create the schema in your dev DB
make dev                             # http://localhost:3000  — the "app-exercise binding"
```

## What to expect

- `/foundry:doctor` prints `DOCTOR-GREEN` — gate self-tests pass, the operator registry resolves,
  every probe is green (manifest, hooks, skills, profile lock, operator registry). If it's
`DOCTOR-RED`, fix the named probe before continuing.
- `make dev` serves a design-system-styled landing page at `localhost:3000`. The build is clean
  (`next build` compiles + typechecks).

The four features are **not** built here — they ship as governed checkpoints in steps 5–6.
This step is the *sprint-0 foundation*: the app skeleton, the DB schema (`src/db/schema.ts`), and
the design tokens.

## Checkpoint

```bash
git checkout step-1   # the scaffold, building + serving
```

**Next:** [Step 2 — author specs + the adversarial audit](step-2-specs.md).
