import argparse
import sys
from cli.project_validator import validate_project

def main():
    parser = argparse.ArgumentParser(description="RPAI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    doctor_parser = subparsers.add_parser("doctor", help="Run diagnostic checks")
    doctor_parser.add_argument("--project", required=True, help="Path to the project configuration YAML file")
    
    args = parser.parse_args()
    
    if args.command == "doctor":
        result = validate_project(args.project)
        if result.success:
            if result.message:
                print(result.message)
            sys.exit(0)
        else:
            if result.message:
                print(f"Error: {result.message}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
