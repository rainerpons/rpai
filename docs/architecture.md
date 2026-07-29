# RPAI Architecture

This document describes the implemented architectural boundaries, dependency direction, and design patterns in RPAI. Planned subsystems are intentionally excluded until their requirements and implementations are concrete.

## Project Context Pipeline

The current project-context subsystem turns a configured local repository into persistent, queryable context:

`project config → local repository → documents → index → query → relevant context`

1. `core.config` loads project configuration and resolves the configured local repository.
2. `core.ingestion` discovers supported files and represents their contents as internal `Document` objects with repository-relative metadata.
3. `core.indexing` chunks and embeds those documents and persists their retrieval representation.
4. Chroma stores project-specific vectors on disk so the index can be reopened across process lifetimes.
5. `core.retrieval` reconnects to the persisted vector store, performs semantic retrieval, and returns internal `RetrievalResult` objects with source metadata.

LlamaIndex provides indexing, chunking, embedding, and vector-store integration. Chroma owns persistent vector storage. RPAI keeps its own application boundaries around those libraries so external abstractions do not define the rest of the codebase.

## Dependency Direction

- Higher-level and user-facing CLI tools depend on `core` behavior.
- `core` contains application and domain behavior and must not depend on user-facing tooling.
- `doctor` may depend on `core`, but `core` must not depend on `doctor`.
- Retrieval depends on shared embedding configuration and indexing storage infrastructure, but remains separate from the indexing process itself.

## Core (`core`)

- **`core.config`**: Loads project configuration and resolves values the application consumes.
- **`core.ingestion`**: Turns supported project sources into internal `Document` objects.
- **`core.indexing`**: Turns documents into persistent, project-isolated retrieval representations.
- **`core.embeddings`**: Owns shared embedding model configuration used by indexing and retrieval.
- **`core.retrieval`**: Queries a project's persisted index and returns internal `RetrievalResult` objects without exposing LlamaIndex retrieval types to callers.

### Ingestion Components (`core.ingestion`)

Ingestion keeps file-system responsibilities separate and independently testable:

- **Discovery** determines candidate source files.
- **Reading** obtains supported file content.
- **Orchestration** coordinates discovery and reading to produce documents.

### Persistent State

Persistent application state lives under `state/` and is separated by the technology responsible for it. Chroma vector data is stored beneath `state/chroma/` using deterministic project-specific directories, keeping indexes for different local repositories isolated.

## Doctor (`doctor`)

`doctor` is a user-facing validation boundary. It verifies that a configured project can be used by RPAI and presents actionable validation failures without moving validation concerns into the core project-context pipeline.

## Design Patterns in Use

This section records design patterns that are visible in the implemented codebase. Architectural principles such as separation of concerns and dependency direction are documented elsewhere in this file rather than classified as design patterns.

### Data Transfer Object

`core.ingestion.models.Document` and `core.retrieval.models.RetrievalResult` provide application-owned data structures at subsystem boundaries. They keep repository content, retrieval results, and metadata independent from LlamaIndex-specific document and node types.

### Facade

Small application-facing functions hide integration details behind focused interfaces. For example, indexing and retrieval callers interact with `get_storage_context` rather than constructing Chroma clients, collections, vector stores, docstores, and LlamaIndex storage contexts themselves.

### Pipeline

The project-context subsystem is organized as a unidirectional processing pipeline. Configuration feeds ingestion, ingestion produces documents, indexing persists their retrieval representation, and retrieval queries that persisted representation for relevant context. Each stage has a distinct input, output, and responsibility.

## Future Architecture

Workflow orchestration, GitHub-based project context, and other agentic capabilities are future subsystems. Their architecture and design patterns should be documented here when they are implemented rather than represented by speculative packages or placeholder abstractions.
