import sys

def check_environment():
    print("Checking RPAI environment...")
    
    # 1. Check Python version
    if sys.version_info < (3, 12):
        print("❌ Python version must be >= 3.12")
        return False
    print("✅ Python version is >= 3.12")
    
    # 2. Check dependencies
    try:
        import llama_index.core
        import chromadb
        import langgraph
        import yaml
        import dotenv
        print("✅ Dependencies (llama_index, chromadb, langgraph, pyyaml, python-dotenv) are installed.")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

    # 3. Check LangGraph initialization
    try:
        from workflows.implementation_plan import create_graph
        graph = create_graph()
        print("✅ LangGraph workflows initialize correctly.")
    except Exception as e:
        print(f"❌ LangGraph initialization failed: {e}")
        return False

    # 4. Check Chroma initialization
    try:
        client = chromadb.EphemeralClient()
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
