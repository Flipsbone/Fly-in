import sys
import argparse
from src.parser.map_parser import MapParser
from src.algo.graph import Graph
from src.algo.reservation_table import ReservationTable


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_path")
    args = parser.parse_args()
    try:
        with open(args.map_path, "r") as map_file:
            parse = MapParser()
            my_network = parse.parse_map(map_file)
            graph = Graph(my_network)
            solution = graph.is_one_solution()
            if solution:
                drones = my_network.nb_drones
                table = ReservationTable()
                while drones:
                    solve = graph.solve(table)
                    for i, node in enumerate(solve):
                        table.reserve(i, node)
                    print(table.reservation)
                    print(solve)
                    drones -= 1
                else:
                    print("No path found.", file=sys.stderr)
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
