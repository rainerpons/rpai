from .implementation_plan import create_graph as create_implementation_plan_graph
from .issue_decomposition import create_graph as create_issue_decomposition_graph

WORKFLOW_REGISTRY = {
    "implementation_plan": create_implementation_plan_graph,
    "issue_decomposition": create_issue_decomposition_graph,
}
