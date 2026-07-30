# RPAI

An app for agentic software engineering workflows.

## Overview

RPAI provides reusable project context to AI-assisted engineering tools without requiring the same repository context to be supplied repeatedly. Its current project-context subsystem loads project configuration, ingests source files, creates embeddings, persists a vector index, and performs semantic retrieval against that index.

The project emphasizes explicit architectural boundaries, configuration-driven behavior, persistent local state, and independently testable components. It is designed to support multiple software projects and technology stacks while keeping project-specific knowledge isolated.

## Current Capabilities

- Configuration-driven project onboarding with YAML.
- Local repository discovery and text ingestion.
- Document chunking and embeddings through LlamaIndex.
- Persistent vector storage with Chroma.
- Semantic retrieval with repository-relative source metadata.
- Project-isolated persisted state.
- CLI-based project validation through `rpai doctor`.
- Automated unit and end-to-end testing with pytest.

## Project Context Pipeline

The implemented project-context subsystem follows a straightforward data flow:

`project config → local repository → documents → index → query → relevant context`

Project configuration identifies a local repository. Supported repository content is ingested into internal documents, chunked and embedded, and persisted in a project-specific Chroma vector store. Retrieval reconnects to that persisted index and returns relevant context with source metadata that can be traced back to repository-relative files.

## Technology

RPAI is built with Python 3.12+ and uses LlamaIndex for indexing and retrieval integration, Chroma for persistent vector storage, Hugging Face embedding models, PyYAML for project configuration, and pytest for automated testing.

## Usage

Validate a project configuration with the `doctor` command:

```shell
rpai doctor --project projects/example.yaml
```

## Development

`uv` is the recommended tool for local development and dependency management. The project uses standard Python packaging and remains installable through other compatible tooling.

## Architecture

The project keeps configuration, ingestion, indexing, embeddings, retrieval, and user-facing tooling behind explicit boundaries. Persistent state is separated by technology under `state/`, with project-specific vector data isolated within the Chroma state hierarchy.

See `docs/architecture.md` for the detailed component boundaries, dependency direction, and design patterns used by the current implementation.

Future capabilities such as workflow orchestration and GitHub integration are intentionally outside the completed project-context subsystem and will be introduced as their requirements become concrete.
