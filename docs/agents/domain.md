# Domain docs

How the engineering skills should consume this repository's domain documentation when exploring the codebase.

canvodpy-extensions shares canvodpy's domain (GNSS-T, sites, files, stores). So its words are canvodpy's: there is no second glossary here.

## Before exploring, read these

- **`canvodpy:GLOSSARY.md`**: the project's words, in canvodpy at the locked commit (`just canvodpy-ref`).
- **`canvodpy:docs/adr/index.md`**: canvodpy's decisions. Read the ones about the area you're about to work in.
- **`docs/adr/`** in this repository, once it exists: decisions that concern only the extensions.
- **`CODING_STANDARDS.md`**: the rules every change follows.
- The **`AGENTS.md`** of every package you change: where things live, invariants, tests.

## Where new terms and decisions go

- **A new term** goes into canvodpy's `GLOSSARY.md`, through a pull request in canvodpy. The extensions never define a word of their own.
- **A decision that concerns only the extensions** (how a package works, what it supports) gets an ADR in this repository's `docs/adr/`, numbered from `0001`, with a row in `docs/adr/index.md`. Create the folder with the first ADR.
- **A decision that changes canvodpy too** (a contract, a public name canvodpy imports) gets its ADR in canvodpy.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in canvodpy's `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/mattpocock-skills:domain-modeling`, and add the term in canvodpy).

## Flag conflicts with an ADR

If your output contradicts an existing ADR, here or in canvodpy, surface it explicitly rather than silently overriding:

> _Contradicts canvodpy ADR-0007 (provenance in log books), but worth reopening because…_
