import sys

def check_environment():
    print("Checking RPAI environment...")
    
    # 1. Check Python version
    if sys.version_info < (3, 12):
        print("❌ Python 3.12+ is required")
        return False
    print("✅ Python 3.12+ is installed")
    
    # 2. Check dependencies
    try:
        import llama_index.core
        import chromadb
        import langgraph
        import yaml
        print("✅ Dependencies (llama_index, chromadb, langgraph, pyyaml) are installed.")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

    # 3. Check LangGraph initialization
    try:
        from workflows.registry import WORKFLOW_REGISTRY
        for create_graph in WORKFLOW_REGISTRY.values():
            create_graph()
        print("✅ LangGraph workflows initialize correctly.")
    except Exception as e:
        print(f"❌ LangGraph initialization failed: {e}")
        return False

    # 4. Check Chroma initialization
    try:
        # Note: The goal here is dependency-health validation only.
        # Persistence validation will occur once the persistence layer exists.
        # This should eventually migrate to `PersistentClient`.
        _ = chromadb.EphemeralClient()
        print("✅ ChromaDB initializes correctly.")
    except Exception as e:
        print(f"❌ ChromaDB initialization failed: {e}")
        return False
        
    print("\nEnvironment is healthy!")
    return True

if __name__ == "__main__":
    if not check_environment():
        sys.exit(1)
    sys.exit(0)
