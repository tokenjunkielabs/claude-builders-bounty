# Bounty #2 — production Next.js 15 + SQLite `CLAUDE.md`

This submission provides an opinionated root-level `CLAUDE.md` for a greenfield SaaS built with Next.js 15 App Router and SQLite.

## Use it

1. Copy `bounty-2/CLAUDE.md` to the root of a new Next.js 15 repository as `CLAUDE.md`.
2. Use pnpm and the exact stack named in the file: TypeScript strict mode, Drizzle ORM, `better-sqlite3`, Zod, Tailwind, Vitest, and Playwright.
3. Start Claude Code from the repository root and give it a product task; the contract supplies the architecture and routine defaults without a setup interview.

## What is fixed by the contract

- A concrete App Router folder and feature layout.
- File, symbol, SQL, action, and query naming conventions.
- Node-only SQLite deployment constraints and connection PRAGMAs.
- Reviewed forward-only Drizzle migrations, safe backfills, and expand/contract rules.
- Server Component, Server Action, Route Handler, caching, and revalidation boundaries.
- Authentication, tenant authorization, Zod validation, typed action results, and secret handling.
- Required development/database scripts and commands.
- Approved implementation patterns and a reasoned anti-pattern table.
- A change workflow and definition of done that tell Claude when to infer defaults and when a real owner decision is required.

## Greenfield acceptance exercise

After copying the file, use this representative request:

> Add authenticated workspaces and a create-project form. A project belongs to one workspace, names are required and at most 120 characters, and the project list should update after creation.

The contract gives Claude enough information to proceed without asking how to structure the feature. A conforming implementation will:

- place routes under `src/app/(app)` and business code under `src/features/projects`;
- add `workspaces`, membership, and `projects` tables using plural snake_case SQL names and tenant foreign keys;
- generate a forward Drizzle migration and indexes;
- use a Node Server Component for the project list;
- use a Server Action with session loading, Zod validation, workspace authorization, a tenant-scoped write, and narrow cache invalidation;
- isolate any interactive form state in a leaf Client Component;
- avoid an internal API round trip, floating-point money, broad cache invalidation, and production schema push.

Those decisions come directly from `CLAUDE.md`; only actual product ambiguities such as invitation policy or billing behavior warrant an owner question.

## Acceptance mapping

| Bounty requirement | Delivered in |
|---|---|
| Project structure | Sections 2 and 15 |
| Naming conventions | Section 3 and database naming in Section 6 |
| DB migration rules | Section 7 |
| Development commands | Sections 11 and 12 |
| Patterns to follow | Sections 4–6 and 13 |
| Anti-patterns to avoid, with reasons | Sections 14 and the rationale attached throughout |
| Opinionated rather than generic | Fixed stack, deployment model, data types, folder ownership, caching, authorization, and migration policy |
| Usable on a greenfield project | Root-copy instructions plus complete operating contract and acceptance exercise |
