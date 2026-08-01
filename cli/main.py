import argparse
import sys
from doctor.project import validate_project
from core.config import load_project_config
from providers.config import load_language_model_config
from providers.factory import create_language_model
from workflow.orchestration import execute_task

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def handle_doctor(args: argparse.Namespace) -> int:
    result = validate_project(args.project)
    
    if not result.success:
        if result.message:
            print(f"Error: {result.message}", file=sys.stderr)
        return EXIT_FAILURE
        
    if result.message:
        print(result.message)
        
    return EXIT_SUCCESS

def handle_run(args: argparse.Namespace) -> int:
    try:
        project_config = load_project_config(args.project)
        lm_config = load_language_model_config(project_config)
        language_model = create_language_model(lm_config)
        result = execute_task(args.task, project_config, language_model)
        print(result.output)
        return EXIT_SUCCESS
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_FAILURE

def main() -> int:
    parser = argparse.ArgumentParser(description="RPAI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    doctor_parser = subparsers.add_parser("doctor", help="Run diagnostic checks")
    doctor_parser.add_argument("--project", required=True, help="Path to the project configuration YAML file")
    doctor_parser.set_defaults(handler=handle_doctor)
    
    run_parser = subparsers.add_parser("run", help="Run a workflow task")
    run_parser.add_argument("--project", required=True, help="Path to the project configuration YAML file")
    run_parser.add_argument("--task", required=True, help="Task description")
    run_parser.set_defaults(handler=handle_run)
    
    args = parser.parse_args()
    return args.handler(args)

if __name__ == "__main__":
    sys.exit(main())
