# RPAI Architecture

This document defines the stable architectural boundaries and dependency directions for RPAI.

## Dependency Direction
* Higher-level and user-facing workflows depend on `core` behavior.
* `core` contains application and domain behavior and must not depend on user-facing tooling.
* `doctor` may depend on `core`, but `core` should not depend on `doctor`.

## Core (`core`)
* **`core.config`**: Owns loading and resolving project configurations into values the application can consume.
* **`core.ingestion`**: Turns supported project sources into RPAI `Document` objects.
* **`core.indexing`**: Turns `Document` objects into persistent, project-isolated retrieval representations.
  * Chroma owns persistent vector storage.
  * LlamaIndex owns generic chunking/indexing/embedding/vector-store integration.
* **`core.embeddings`**: Owns shared embedding models and configurations used by indexing and retrieval.
* **`core.retrieval`**: Owns retrieving relevant context from a project's index, returning internal `RetrievalResult` objects without leaking LlamaIndex abstractions. Depends on `core.embeddings` and `core.indexing` storage but decoupled from the indexing process itself.

## Ingestion Components (`core.ingestion`)
Ingestion components should remain independently testable and avoid taking on each other's responsibilities:
* **Discovery**: Determines candidate source files.
* **Reading**: Obtains supported file content.
* **Orchestration**: Coordinates discovery and reading to produce documents.

## Doctor (`doctor`)
Validates that a project can be used by RPAI and presents actionable validation failures to the user.
