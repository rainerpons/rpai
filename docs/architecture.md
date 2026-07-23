# Architecture and Responsibility Boundaries

The RPAI architecture is cleanly separated by responsibility to ensure modularity and ease of testing. The current boundaries for local repository ingestion are defined as follows:

## Configuration (`core.config`)
Solely responsible for defining the contract of a project configuration. It handles loading the YAML configuration files and resolving underlying fields (such as `local_repository`) into concrete, validated paths. It enforces the presence, type, and existence of these paths and raises standard Python exceptions when validation fails.

## Doctor (`doctor.project`)
Solely responsible for surfacing user-facing validation errors. It acts purely as a translator between lower-level exceptions raised by `core.config` and the `ValidationError` interface presented to the user.

## Discovery (`core.ingestion.discovery`)
Solely responsible for filesystem traversal. It guarantees a deterministic traversal order and explicitly excludes metadata folders (like `.git` and `__pycache__`). It operates independently of repository validation and does not concern itself with whether the discovered files are text or binary.

## Reading (`core.ingestion.reader`)
Solely responsible for opening files and attempting UTF-8 decoding. It treats decoding failures as the boundary for unsupported or binary file types, gracefully skipping them while allowing genuine I/O errors to propagate.

## Ingestion (`core.ingestion.local_repo`)
The orchestrator of the local ingestion process. It uses `core.config` to fetch and validate the repository boundary, loops through the paths provided by `discovery`, streams those paths through the `reader`, and bundles the successfully read text files into `Document` objects.
