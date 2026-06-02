import sys
import argparse
import arcade
from src.parser.map_parser import MapParser
from src.models.data_map import DataMap
from src.algo.graph import Graph
from src.algo.reservation_table import ReservationTable
from src.algo.pathfinding import PathFinder
from src.gui.visualizer import FlyInVisualizer


def display_terminal(drone_paths: dict[int, list[str]],
                     drone_turn: dict[int, int]) -> None:

    max_turn: int = max(len(path) for path in drone_paths.values())
    drone_moved: dict[int, int] = {}
    print()
    for turn in range(1, max_turn):
        line_output: list[str] = []
        for drone_id, path in drone_paths.items():
            if turn < len(path):
                current_node: str = path[turn]
                prev_node: str = path[turn - 1]
                if current_node != prev_node:
                    line_output.append(f"D{drone_id}-{current_node}")
                    drone_moved[turn] = drone_moved.get(turn, 0) + 1
        if line_output:
            print(" ".join(line_output))
    sum_turn: int = sum(turn for turn in drone_turn.values())
    print(f"\nThe average number of turns per drone {sum_turn/drone_id}\n")
    for turn_index, count in drone_moved.items():
        print(f"Number of drones moved at the turn {turn_index} is {count}")


def compute_drone_paths(
        data_map: DataMap,
        graph: Graph,
        table: ReservationTable) -> dict[int, list[str]]:
    """calcul paths for each drone using the pathfinder.

    The function solves for a path and reserves the
    route in the reservation table. It returns a mapping
    from drone id to list of zone/link names representing the path.

    Args:
        data_map: Parsed map and drone count.
        graph: Graph built from the parsed map.
        table: Reservation table to reserve turns and links.

    Returns:
        Mapping of drone id to route (list of location strings).
    """

    remaining_drones = data_map.nb_drones
    drone_id = 1
    drone_paths: dict[int, list[str]] = {}
    drone_turn: dict[int, int] = {}

    while remaining_drones > 0:
        solver = PathFinder(graph, table)
        path = solver.solve()
        drone_paths[drone_id] = path

        for turn, location in enumerate(path):
            table.reserve(turn, location)
            if "-" in location:
                table.reserve(turn + 1, location)

            if turn > 0 and path[turn - 1] != location:
                prev_location = path[turn - 1]
                if "-" not in prev_location + location:
                    route = (f"{min(prev_location, location)}-"
                             f"{max(prev_location, location)}")
                    table.reserve(turn, route)

        table.park(path)
        remaining_drones -= 1
        drone_id += 1
        drone_turn[drone_id] = (len(path) - 1)

    display_terminal(drone_paths, drone_turn)

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
