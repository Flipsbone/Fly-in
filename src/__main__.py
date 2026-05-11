import sys
import argparse
from src.parser.map_parser import parse_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_path")
    args = parser.parse_args()
    try:
        with open(args.map_path, "r") as map_file:
            my_network = parse_map(map_file)
    except PermissionError as e:
        print(f"Permission Error: {e}.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File '{args.map_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except (ValueError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
