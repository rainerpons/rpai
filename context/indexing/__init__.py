"""
Core indexing for RPAI.
"""

from context.indexing.index import index_documents
from context.indexing.store import project_index_exists, delete_project_index, IndexLoadError
from context.indexing.project import build_project_index
from context.indexing.lifecycle import ensure_project_index

__all__ = [
    "index_documents",
    "project_index_exists",
    "delete_project_index",
    "build_project_index",
    "ensure_project_index",
    "IndexLoadError",
]
