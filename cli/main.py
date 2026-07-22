import argparse
import sys
from doctor.project import validate_project

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def handle_doctor(args: argparse.Namespace) -> int:
    result = validate_project(args.project)
    
    if result.message:
        if result.success:
            print(result.message)
        else:
            print(f"Error: {result.message}", file=sys.stderr)
            
    return EXIT_SUCCESS if result.success else EXIT_FAILURE

def main() -> int:
    parser = argparse.ArgumentParser(description="RPAI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    doctor_parser = subparsers.add_parser("doctor", help="Run diagnostic checks")
    doctor_parser.add_argument("--project", required=True, help="Path to the project configuration YAML file")
    doctor_parser.set_defaults(handler=handle_doctor)
    
    args = parser.parse_args()
    return args.handler(args)

if __name__ == "__main__":
    sys.exit(main())
