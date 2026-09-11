from fnmatch import fnmatch
from heuristics.heuristic_base import Heuristic


def get_parts(fact):
    """Extract the components of a PDDL fact by removing parentheses and splitting the string."""
    return fact[1:-1].split()


def match(fact, *args):
    """
    Check if a PDDL fact matches a given pattern.

    - `fact`: The complete fact as a string, e.g., "(at p1 l0)".
    - `args`: The expected pattern (wildcards `*` allowed).
    - Returns `True` if the fact matches the pattern, else `False`.
    """
    parts = get_parts(fact)
    return all(fnmatch(part, arg) for part, arg in zip(parts, args))


class CvrpStripsHeuristic(Heuristic):
    """
    A domain-dependent heuristic for the CVRP (Capacitated Vehicle Routing Problem) domain.

    # Summary
    This heuristic estimates the number of actions needed to deliver all packages to their goal locations, considering vehicle capacities and travel distances.

    # Assumptions
    - Vehicles have limited capacity, represented by size levels (c0, c1, c2, ...).
    - Each package occupies one unit of capacity.
    - Vehicles can carry multiple packages as long as their capacity allows.
    - The road network is undirected (if there is a road from A to B, there is also a road from B to A).
    - Vehicles start at a depot (usually l0) and can return there if needed.

    # Heuristic Initialization
    - Extract the goal locations for each package.
    - Extract the road network (undirected graph) from static facts.
    - Compute all-pairs shortest path distances between locations using Floyd-Warshall.
    - Determine the capacity level of each vehicle from the initial state.
    - Map capacity levels to numeric values (c0=0, c1=1, c2=2, etc.).

    # Step-By-Step Thinking for Computing Heuristic
    1. Identify all packages that still need to be delivered (not at their goal location).
    2. For each vehicle, determine:
       - Its current location.
       - Its current capacity (number of free slots).
       - Which packages it is currently carrying.
    3. For each undelivered package, determine:
       - Its current location (either at a location or inside a vehicle).
       - Its goal location.
    4. Estimate the cost of delivering each package:
       - If the package is at a location and not in a vehicle:
         - It needs to be picked up by some vehicle and transported to its goal.
         - The cost includes: driving the vehicle to the package's location, picking up the package, driving to the goal, and dropping it off.
       - If the package is inside a vehicle:
         - The vehicle must drive to the package's goal location and drop it off.
    5. Account for vehicle capacity constraints:
       - When estimating the number of trips needed, consider that a vehicle can carry multiple packages if capacity allows.
       - Group packages by their current location and goal location to estimate efficient routing.
    6. Compute the total heuristic value as the sum of estimated action costs for all deliveries.
    """

    def __init__(self, task):
        """Initialize the heuristic by extracting static information and computing distances."""
        self.goals = task.goals
        static_facts = task.static

        # Extract road network from static facts
        self.roads = {}
        for fact in static_facts:
            if match(fact, "road", "*", "*"):
                loc1, loc2 = get_parts(fact)[1], get_parts(fact)[2]
                if loc1 not in self.roads:
                    self.roads[loc1] = set()
                if loc2 not in self.roads:
                    self.roads[loc2] = set()
                self.roads[loc1].add(loc2)
                self.roads[loc2].add(loc1)

        # Extract capacity-predecessor relationships to determine capacity levels
        self.capacity_levels = {}
        capacity_preds = []
        for fact in static_facts:
            if match(fact, "capacity-predecessor", "*", "*"):
                s1, s2 = get_parts(fact)[1], get_parts(fact)[2]
                capacity_preds.append((s1, s2))

        # Build capacity level mapping (c0=0, c1=1, c2=2, ...)
        # Find the maximum capacity level
        all_sizes = set()
        for s1, s2 in capacity_preds:
            all_sizes.add(s1)
            all_sizes.add(s2)
        # Sort sizes by their predecessor chain
        sorted_sizes = []
        remaining = set(all_sizes)
        while remaining:
            # Find a size that has no predecessor in remaining (or is c0)
            for size in list(remaining):
                has_pred = any(s2 == size and s1 in remaining for s1, s2 in capacity_preds)
                if not has_pred:
                    sorted_sizes.append(size)
                    remaining.remove(size)
                    break
            else:
                # Fallback: just add any remaining
                sorted_sizes.extend(sorted(remaining))
                break

        # Assign levels based on position in chain
        for i, size in enumerate(sorted_sizes):
            self.capacity_levels[size] = i

        # Extract goal locations for packages
        self.goal_locations = {}
        for goal in self.goals:
            if match(goal, "at", "*", "*"):
                package, location = get_parts(goal)[1], get_parts(goal)[2]
                self.goal_locations[package] = location

        # Compute all-pairs shortest paths using Floyd-Warshall
        all_locations = set(self.roads.keys())
        # Add locations from goals and initial state if not in roads
        for fact in task.initial_state:
            if match(fact, "at", "*", "*"):
                obj, loc = get_parts(fact)[1], get_parts(fact)[2]
                if loc.startswith('l'):
                    all_locations.add(loc)
        for loc in self.goal_locations.values():
            all_locations.add(loc)

        # Initialize distance matrix
        self.dist = {}
        for loc1 in all_locations:
            self.dist[loc1] = {}
            for loc2 in all_locations:
                if loc1 == loc2:
                    self.dist[loc1][loc2] = 0
                elif loc2 in self.roads.get(loc1, set()):
                    self.dist[loc1][loc2] = 1
                else:
                    self.dist[loc1][loc2] = float('inf')

        # Floyd-Warshall
        for k in all_locations:
            for i in all_locations:
                for j in all_locations:
                    if self.dist[i][k] + self.dist[k][j] < self.dist[i][j]:
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]

        # Extract initial vehicle capacities
        self.initial_capacities = {}
        for fact in task.initial_state:
            if match(fact, "capacity", "*", "*"):
                vehicle, size = get_parts(fact)[1], get_parts(fact)[2]
                self.initial_capacities[vehicle] = self.capacity_levels[size]

    def __call__(self, node):
        """Compute an estimate of the minimal number of required actions."""
        state = node.state

        # Extract current state information
        vehicle_locations = {}
        vehicle_capacities = {}
        package_locations = {}  # location or vehicle name
        packages_in_vehicles = {}  # vehicle -> set of packages

        for fact in state:
            parts = get_parts(fact)
            if len(parts) < 3:
                continue
            pred = parts[0]
            if pred == "at":
                obj, loc = parts[1], parts[2]
                if obj.startswith('v'):
                    vehicle_locations[obj] = loc
                elif obj.startswith('p'):
                    package_locations[obj] = loc
            elif pred == "in":
                pkg, veh = parts[1], parts[2]
                package_locations[pkg] = veh
                if veh not in packages_in_vehicles:
                    packages_in_vehicles[veh] = set()
                packages_in_vehicles[veh].add(pkg)
            elif pred == "capacity":
                veh, size = parts[1], parts[2]
                vehicle_capacities[veh] = self.capacity_levels[size]

        # Identify undelivered packages
        undelivered = []
        for pkg, goal_loc in self.goal_locations.items():
            current_loc = package_locations.get(pkg)
            if current_loc is None:
                continue
            # Check if package is at its goal location
            if current_loc == goal_loc:
                continue
            undelivered.append((pkg, current_loc, goal_loc))

        if not undelivered:
            return 0

        total_cost = 0

        # For each undelivered package, estimate delivery cost
        for pkg, current_loc, goal_loc in undelivered:
            # Check if package is in a vehicle
            if current_loc.startswith('v'):
                # Package is in vehicle
                veh = current_loc
                veh_loc = vehicle_locations.get(veh)
                if veh_loc is None:
                    continue
                # Cost to drive to goal and drop off
                if veh_loc != goal_loc:
                    total_cost += self.dist.get(veh_loc, {}).get(goal_loc, float('inf'))
                total_cost += 1  # drop action
            else:
                # Package is at a location
                # Find nearest vehicle that can pick it up
                best_cost = float('inf')
                for veh, veh_loc in vehicle_locations.items():
                    # Check if vehicle has capacity
                    if vehicle_capacities.get(veh, 0) > 0:
                        # Cost: drive to package location, pick up, drive to goal, drop
                        cost = 0
                        if veh_loc != current_loc:
                            cost += self.dist.get(veh_loc, {}).get(current_loc, float('inf'))
                        cost += 1  # pick up
                        if current_loc != goal_loc:
                            cost += self.dist.get(current_loc, {}).get(goal_loc, float('inf'))
                        cost += 1  # drop
                        best_cost = min(best_cost, cost)
                if best_cost != float('inf'):
                    total_cost += best_cost
                else:
                    # No vehicle can pick it up directly; estimate as if vehicle needs to return to depot first
                    # This is a rough estimate
                    total_cost += 2  # minimal estimate

        # Account for vehicle repositioning costs (simplified)
        # For each vehicle not at depot, add cost to return to depot if it has no more packages to deliver
        for veh, veh_loc in vehicle_locations.items():
            # Check if vehicle has any undelivered packages
            has_undelivered = False
            if veh in packages_in_vehicles:
                for pkg in packages_in_vehicles[veh]:
                    if pkg in self.goal_locations:
                        if package_locations.get(pkg) != self.goal_locations[pkg]:
                            has_undelivered = True
                            break
            if not has_undelivered:
                # Vehicle is empty or only has delivered packages
                # Add cost to return to depot (l0) if not already there
                if veh_loc != 'l0':
                    total_cost += self.dist.get(veh_loc, {}).get('l0', 0)

        return total_cost
