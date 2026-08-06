# Ubiquitous Language

The following terms define the core vocabulary used in the workflow and language model execution layer:

*   **Task**: The plain-text user intent or instruction.
*   **Context**: The retrieved, project-specific information used to inform the model about the repository.
*   **Provider**: The external service or infrastructure responsible for actual inference (e.g., OpenAI).
*   **LanguageModel**: The protocol defining the interface for language models to participate in workflow execution, completely decoupled from provider-specific types.
*   **TaskResult**: The RPAI-owned object containing the final generated output and any relevant execution metadata, ensuring callers do not depend on provider responses.
