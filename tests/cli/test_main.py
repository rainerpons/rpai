import pytest
from unittest.mock import patch, MagicMock

from cli.main import handle_run, EXIT_SUCCESS, EXIT_FAILURE


@patch("cli.main.load_project_config")
@patch("cli.main.load_language_model_config")
@patch("cli.main.create_language_model")
@patch("cli.main.execute_task")
def test_handle_run_success(mock_execute_task, mock_create_language_model, mock_load_language_model_config, mock_load_project_config, capsys):
    mock_args = MagicMock()
    mock_args.project = "project.yaml"
    mock_args.task = "My task"
    
    mock_project_config = {"project": "config"}
    mock_load_project_config.return_value = mock_project_config
    
    mock_lm_config = MagicMock()
    mock_load_language_model_config.return_value = mock_lm_config
    
    mock_language_model = MagicMock()
    mock_create_language_model.return_value = mock_language_model
    
    mock_result = MagicMock()
    mock_result.output = "Generated workflow result text"
    mock_execute_task.return_value = mock_result
    
    result = handle_run(mock_args)
    
    assert result == EXIT_SUCCESS
    
    mock_load_project_config.assert_called_once_with("project.yaml")
    mock_load_language_model_config.assert_called_once_with(mock_project_config)
    mock_create_language_model.assert_called_once_with(mock_lm_config)
    mock_execute_task.assert_called_once_with("My task", mock_project_config, mock_language_model)
    
    captured = capsys.readouterr()
    assert "Generated workflow result text\n" in captured.out
    assert captured.err == ""


@patch("cli.main.load_project_config")
def test_handle_run_failure(mock_load_project_config, capsys):
    mock_args = MagicMock()
    mock_args.project = "project.yaml"
    mock_args.task = "My task"
    
    mock_load_project_config.side_effect = Exception("Configuration error")
    
    result = handle_run(mock_args)
    
    assert result == EXIT_FAILURE
    
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Error: Configuration error\n" in captured.err
