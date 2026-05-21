import sys
import argparse
from src.parser.map_parser import MapParser
from src.algo.graph import Graph
from src.algo.reservation_table import ReservationTable
from src.algo.PathFinding import PathFinder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("map_path")
    args = parser.parse_args()

    try:
        with open(args.map_path, "r") as map_file:
            parse = MapParser()
            data_map = parse.parse_map(map_file)

        graph = Graph(data_map)
        table = ReservationTable()

        checker = PathFinder(graph, table)
        if not checker.is_one_solution():
            print("No path found.", file=sys.stderr)
            sys.exit(1)

        remaining_drones = data_map.nb_drones
        drone_id = 1

        while remaining_drones > 0:
            solver = PathFinder(graph, table)
            path = solver.solve()

            text = []
            for turn, location in enumerate(path):
                table.reserve(turn, location)
                text.append(f"D{drone_id}-{location} Turn={turn}")

            print(f"--- Drone {drone_id} ---")
            print(f"Path found in {len(path) - 1} steps.")
            print(" ".join(text))

            remaining_drones -= 1
            drone_id += 1

    except PermissionError as e:
        print(f"Permission Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File '{args.map_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except (ValueError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
