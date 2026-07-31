import os
import site

# Workaround to allow llama-index's 'workflows' package to be loaded
# alongside our local 'workflows' package by merging their paths.
_site_packages = site.getsitepackages()
if hasattr(site, 'getusersitepackages'):
    _site_packages.append(site.getusersitepackages())

for sp in _site_packages:
    sp_workflows = os.path.join(sp, 'workflows')
    if os.path.isdir(sp_workflows) and sp_workflows not in __path__:
        __path__.append(sp_workflows)

from workflows.language_model import LanguageModel
from workflows.models import WorkflowResult
from workflows.orchestration import execute_task

__all__ = ["LanguageModel", "WorkflowResult", "execute_task"]
