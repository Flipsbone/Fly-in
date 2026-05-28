import sys
import argparse
import arcade
from src.parser.map_parser import MapParser
from src.models.data_map import DataMap
from src.algo.graph import Graph
from src.algo.reservation_table import ReservationTable
from src.algo.pathfinding import PathFinder
from src.gui.visualizer import FlyInVisualizer


def compute_drone_paths(
        data_map: DataMap,
        graph: Graph,
        table: ReservationTable) -> dict[int, list[str]]:

    remaining_drones = data_map.nb_drones
    drone_id = 1
    drone_paths: dict[int, list[str]] = {}

    while remaining_drones > 0:
        solver = PathFinder(graph, table)
        path = solver.solve()
        drone_paths[drone_id] = path

        text: list[str] = []
        for turn, location in enumerate(path):
            table.reserve(turn, location)
            if "-" in location:
                table.reserve(turn + 1, location)
            text.append(f"D{drone_id}-{location} Turn={turn}")

            if turn > 0 and path[turn - 1] != location:
                prev_location = path[turn - 1]
                if "-" not in prev_location + location:
                    route = (f"{min(prev_location, location)}-"
                             f"{max(prev_location, location)}")
                    table.reserve(turn, route)

        print(f"--- Drone {drone_id} ---")
        print(f"Path found in {len(path) - 1} steps.")
        print(" ".join(text))

        remaining_drones -= 1
        drone_id += 1
    return drone_paths


def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser()
    parser.add_argument("map_path")
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    try:
        with open(args.map_path, "r") as map_file:
            parse = MapParser()
            data_map = parse.parse_map(map_file)

        graph = Graph(data_map)
        table = ReservationTable()
        checker = PathFinder(graph, table)
        if not checker.is_one_solution():
            print("No path found.", file=sys.stderr)
            return 1
        drone_paths = compute_drone_paths(data_map, graph, table)

        window = FlyInVisualizer(graph, drone_paths)
        window.setup()
        arcade.run()

    except PermissionError as e:
        print(f"Permission Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File '{args.map_path}' not found.", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    main()
