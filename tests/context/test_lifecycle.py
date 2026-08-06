import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from context.indexing.lifecycle import ensure_project_index

@patch("context.indexing.lifecycle.build_project_index")
@patch("context.indexing.lifecycle.project_index_exists")
def test_ensure_missing_index(mock_exists, mock_build):
    mock_exists.return_value = False
    progress = MagicMock()
    
    ensure_project_index({"name": "test"}, state_dir=Path("/state"), on_progress=progress)
    
    mock_build.assert_called_once_with({"name": "test"}, state_dir=Path("/state"))
    progress.assert_any_call("Creating project index...")
    progress.assert_any_call("Project index created.")

@patch("context.indexing.lifecycle.build_project_index")
@patch("context.indexing.lifecycle.project_index_exists")
def test_ensure_existing_index(mock_exists, mock_build):
    mock_exists.return_value = True
    progress = MagicMock()
    
    ensure_project_index({"name": "test"}, state_dir=Path("/state"), on_progress=progress)
    
    mock_build.assert_not_called()
    progress.assert_not_called()

@patch("context.indexing.lifecycle.build_project_index")
@patch("context.indexing.lifecycle.project_index_exists")
def test_ensure_index_no_progress(mock_exists, mock_build):
    mock_exists.return_value = False
    
    ensure_project_index({"name": "test"}, state_dir=Path("/state"))
    
    mock_build.assert_called_once()

@patch("context.indexing.lifecycle.build_project_index")
@patch("context.indexing.lifecycle.project_index_exists")
def test_ensure_index_build_failure(mock_exists, mock_build):
    mock_exists.return_value = False
    mock_build.side_effect = RuntimeError("build failed")
    
    with pytest.raises(RuntimeError, match="build failed"):
        ensure_project_index({"name": "test"}, state_dir=Path("/state"))
        
    mock_build.assert_called_once()
