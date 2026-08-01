from workflow.context import Context


def build_prompt(task: str, context: Context) -> str:
    parts = []
    parts.append("Task:")
    parts.append(task)
    parts.append("")
    parts.append("Project context:")
    parts.append("")
    
    if not context.entries:
        parts.append("No project context was retrieved.")
    else:
        for i, entry in enumerate(context.entries):
            parts.append(f"[Source: {entry.source}]")
            parts.append(entry.content)
            if i < len(context.entries) - 1:
                parts.append("")
                
    return "\n".join(parts)
