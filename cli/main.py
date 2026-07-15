import argparse
import sys
from doctor.project import validate_project

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

def main() -> int:
    parser = argparse.ArgumentParser(description="RPAI CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    doctor_parser = subparsers.add_parser("doctor", help="Run diagnostic checks")
    doctor_parser.add_argument("--project", required=True, help="Path to the project configuration YAML file")
    
    args = parser.parse_args()
    
    if args.command == "doctor":
        return handle_doctor(args)
        
    return EXIT_FAILURE

if __name__ == "__main__":
    sys.exit(main())
