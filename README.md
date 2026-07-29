# RPAI

An opinionated agentic software engineering workflow.

## Overview

RPAI is designed around a consistent development process that can be applied across multiple repositories, technology stacks, and engineering domains.

## Requirements

* Python 3.12+

## Usage

You can validate a project configuration using the `doctor` command:

```shell
rpai doctor --project projects/example.yaml
```
## Recommended Tooling

* `uv` for development and dependency management. While the project uses standard Python packaging and remains installable via ordinary tooling, examples and scripts may utilize `uv`.

## Architecture

RPAI is designed as a foundational infrastructure for personal AI engineering, employing explicit structures and concepts rather than generic components.

### CLI-First Philosophy
Interaction is intended to be via a dedicated CLI (e.g., `rpai doctor`), routing input through high-level orchestration layers rather than direct module execution.

### Configuration-Driven Project Onboarding
Support for multiple projects is achieved entirely via configuration (`projects/*.yaml`) rather than custom code. Environmental configuration is strictly separated from project configuration.

### Persistent State Layout
Application state is segregated explicitly by technology under the `state/` directory (e.g., Chroma vectors, caches) to preserve long-term operational memory across sessions.

### Project-Context Subsystem
The core of RPAI operates as a coherent data pipeline that continuously transforms an engineer's active reality into queryable context:

`project config → local repository → documents → index → query → relevant context`

*Note: Future capabilities such as workflow orchestration and GitHub integration are planned but are intentionally separated from the core project-context subsystem.*
