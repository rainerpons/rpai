# RPAI

An opinionated AI software engineering workflow.

## Overview

RPAI is designed around a consistent development process that can be applied across multiple repositories, technology stacks, and engineering domains.

## Architecture

* **Workflows**: LangGraph graphs representing steps like implementation planning and issue decomposition.
* **Retrieval**: Prioritizes local working tree over local commits, and local commits over GitHub.
* **State**: Persistent application state (checkpoints, chroma DB, caches) stored in `state/`.
* **CLI-First**: Intended to be interacted with via commands like `rpai doctor`.
