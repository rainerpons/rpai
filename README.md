# RPAI

An opinionated agentic software engineering workflow.

## Overview

RPAI is designed around a consistent development process that can be applied across multiple repositories, technology stacks, and engineering domains.

## Requirements

* Python 3.12+

## Recommended Tooling

* `uv` for development and dependency management. While the project uses standard Python packaging and remains installable via ordinary tooling, examples and scripts may utilize `uv`.

## Architecture

RPAI is designed as a foundational infrastructure for personal AI engineering, employing explicit structures and concepts rather than generic components.

### CLI-First Philosophy
Interaction is intended to be via a dedicated CLI (e.g., `rpai doctor`), routing input through workflow runners rather than direct module execution.

### Configuration-Driven Project Onboarding
Support for multiple projects is achieved entirely via configuration (`projects/*.yaml`) rather than custom code. Environmental configuration is strictly separated from project configuration.

### Source Precedence Strategy
Retrieval logic prioritizes the engineer's active reality over historical records:
1. Local Working Tree
2. Local Commits
3. GitHub (Canonical Source)

### Persistent State Layout
Application state is segregated explicitly by technology under the `state/` directory (e.g., Chroma vectors, LangGraph checkpoints, caches) to preserve long-term operational memory across sessions.

### Design Patterns in Use
* **Adapter Pattern**: Abstractions for data ingestion (e.g., `retrieval/adapters/github_adapter.py` and `retrieval/adapters/local_adapter.py`) isolate source differences from the retrieval router.
* **Registry Pattern**: Workflows are registered explicitly via a static dictionary (`workflows/registry.py`) without dynamic reflection or complex plugins.
