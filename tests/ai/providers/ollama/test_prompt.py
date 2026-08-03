from orchestration.context import Context, ContextEntry
from ai.providers.ollama.prompt import build_prompt


def test_build_prompt_empty_context():
    task = "What is the project architecture?"
    context = Context()
    
    prompt = build_prompt(task, context)
    
    expected = (
        "Task:\n"
        "What is the project architecture?\n"
        "\n"
        "Project context:\n"
        "\n"
        "No project context was retrieved."
    )
    assert prompt == expected


def test_build_prompt_one_context_entry():
    task = "Fix the bug."
    context = Context(entries=(ContextEntry(source="main.py", content="print('hello')"),))
    
    prompt = build_prompt(task, context)
    
    expected = (
        "Task:\n"
        "Fix the bug.\n"
        "\n"
        "Project context:\n"
        "\n"
        "[Source: main.py]\n"
        "print('hello')"
    )
    assert prompt == expected


def test_build_prompt_multiple_context_entries():
    task = "Add tests."
    context = Context(entries=(
        ContextEntry(source="main.py", content="def add(a, b): return a + b"),
        ContextEntry(source="test_main.py", content="def test_add(): pass"),
    ))
    
    prompt = build_prompt(task, context)
    
    expected = (
        "Task:\n"
        "Add tests.\n"
        "\n"
        "Project context:\n"
        "\n"
        "[Source: main.py]\n"
        "def add(a, b): return a + b\n"
        "\n"
        "[Source: test_main.py]\n"
        "def test_add(): pass"
    )
    assert prompt == expected


def test_build_prompt_preserves_task_exactly():
    task = "  Task with spaces\nand newlines.  "
    context = Context()
    
    prompt = build_prompt(task, context)
    
    expected = (
        "Task:\n"
        "  Task with spaces\nand newlines.  \n"
        "\n"
        "Project context:\n"
        "\n"
        "No project context was retrieved."
    )
    assert prompt == expected
