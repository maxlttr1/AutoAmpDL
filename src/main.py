from dependencies import check_dependencies
from logic import arg_parser

def main() -> None:
    check_dependencies()
    try:
        arg_parser()
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C).")

if __name__ == "__main__":
    main()
