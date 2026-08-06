# RPAI Architecture

This document describes the implemented architectural boundaries, dependency direction, and design patterns in RPAI.

## Package Layout and Subsystems

The codebase is organized into modular subsystems:

*   **`config`**: Loads project configuration and resolves values consumed by the application.
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

The memory subsystem provides a provider-independent interface for long-term semantic memory.

* **`MemoryService`**: The application-facing memory abstraction (Protocol) defining the operations supported by semantic memory providers.
* **`MemoryEntry`**: The application-owned dataclass representing a retrieved memory item.
* **`ProviderResponseError`**: The application-owned exception raised when provider responses are malformed or unsupported.
* **Encapsulated Providers**: Provider implementations (such as Mem0) are implementation details contained entirely within the `memory` subsystem. No provider-specific response types, exceptions, or data structures cross the subsystem boundary.
* **Provider Adaptation**: The memory subsystem adapts provider responses into application-owned models before exposing them to the rest of the application. Any invalid or unsupported provider responses are translated into `ProviderResponseError` exceptions instead of leaking provider behavior across subsystem boundaries.
* **Factory**: Constructs the configured memory provider via the package-level `memory` API.

Callers depend on `MemoryService` and `MemoryEntry`, not on Mem0 or another concrete provider, allowing the implementation to change without affecting the rest of the application.

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

*   **Dependency Inversion**: Orchestration and other consumers depend on the `MemoryService` abstraction rather than a concrete memory provider.
*   **Pipeline / Data Flow**: Unidirectional pipeline for turning local files into index vectors and semantic queries.
*   **Data Transfer Objects (DTOs)**: `Document` and `RetrievalResult` prevent external library types (like LlamaIndex documents/nodes) from leaking throughout the application.
*   **Factory Pattern**: Factory functions construct configured application services while hiding concrete provider implementations from callers.
