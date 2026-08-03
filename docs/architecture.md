# RPAI Architecture

This document describes the implemented architectural boundaries, dependency direction, and design patterns in RPAI.

## Package Layout and Subsystems

The codebase is organized into modular subsystems:

*   **`config`**: Loads project configuration and resolves consumes values.
*   **`context`**: Owns the project-context pipeline: discovering files, reading their contents, chunking and indexing them using LlamaIndex and Chroma, and performing semantic retrieval.
*   **`ai`**: Owns inference providers (e.g., Ollama) and client factories.
*   **`memory`**: Provides a provider-independent long-term semantic memory service.
*   **`orchestration`**: Coordinates index state, performs retrieval, builds context, and invokes the AI models to execute user intents/workflows.
*   **`doctor`**: Validates project workspace configurations before runtime.
*   **`cli`**: The user-facing command-line tool.

---

## Dependency Direction

*   Higher-level and user-facing CLI tools depend on `orchestration` and `config` behavior.
*   `orchestration` coordinates `context`, `ai`, and `memory`, but those subsystems do not depend on orchestration.
*   The `memory` subsystem remains provider-independent, hiding third-party client details from application consumers.

---

## Memory Subsystem (`memory`)

The memory subsystem implements long-term semantic storage that is fully independent of any specific backend provider.

*   **`MemoryService`**: An abstract base protocol representing the application-facing memory operations (CRUD: create, retrieve, update, delete).
*   **Mem0**: Reconciles memory storage. Mem0 is the current memory provider, and all code specific to Mem0 remains encapsulated within this package.
*   **Decoupled Relationship**: Callers and workflow components depend only on the `MemoryService` abstraction, ensuring that replacing Mem0 with a different backend does not affect the rest of the application.

---

## Project Context Pipeline

The context subsystem turns a configured local repository into persistent, queryable context:

`project config → local repository → documents → index → query → relevant context`

1. `config` loads project configuration and resolves the local repository.
2. `context.ingestion` discovers supported files and represents their contents as internal `Document` DTOs.
3. `context.indexing` chunks, embeds, and indexes documents into persistent storage context.
4. Chroma stores project-specific vectors on disk so the index can be reopened across process lifetimes.
5. `context.retrieval` performs semantic retrieval and returns internal `RetrievalResult` objects.

---

## Design Patterns in Use

*   **Dependency Inversion**: Workflow orchestration and other packages interact with semantic memory via `MemoryService` rather than importing third-party libraries directly.
*   **Pipeline / Data Flow**: Unidirectional pipeline for turning local files into index vectors and semantic queries.
*   **Data Transfer Objects (DTOs)**: `Document` and `RetrievalResult` prevent external library types (like LlamaIndex documents/nodes) from leaking throughout the application.
*   **Factory Pattern**: `create_memory_service` and `create_language_model` construct instances from project configuration dicts dynamically.
