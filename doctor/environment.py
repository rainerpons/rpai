import sys
from doctor import ValidationResult

def validate_environment() -> ValidationResult:
    messages = ["Checking RPAI environment..."]
    
    # 1. Check Python version
    if sys.version_info < (3, 12):
        messages.append("❌ Python 3.12+ is required")
        return ValidationResult(success=False, message="\n".join(messages))
    messages.append("✅ Python 3.12+ is installed")
    
    # 2. Check dependencies
    try:
        import llama_index.core
        import chromadb
        import langgraph
        import yaml
        messages.append("✅ Dependencies (llama_index, chromadb, langgraph, pyyaml) are installed.")
    except ImportError as e:
        messages.append(f"❌ Missing dependency: {e}")
        return ValidationResult(success=False, message="\n".join(messages))

    # 3. Check LangGraph initialization
    try:
        from workflows.registry import WORKFLOW_REGISTRY
        for create_graph in WORKFLOW_REGISTRY.values():
            create_graph()
        messages.append("✅ LangGraph workflows initialize correctly.")
    except Exception as e:
        messages.append(f"❌ LangGraph initialization failed: {e}")
        return ValidationResult(success=False, message="\n".join(messages))

    # 4. Check Chroma initialization
    try:
        # Note: The goal here is dependency-health validation only.
        # Persistence validation will occur once the persistence layer exists.
        # This should eventually migrate to `PersistentClient`.
        _ = chromadb.EphemeralClient()
        messages.append("✅ ChromaDB initializes correctly.")
    except Exception as e:
        messages.append(f"❌ ChromaDB initialization failed: {e}")
        return ValidationResult(success=False, message="\n".join(messages))
        
    messages.append("\nEnvironment is healthy!")
    return ValidationResult(success=True, message="\n".join(messages))
