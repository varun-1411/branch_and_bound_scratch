
from gurobipy import GRB
import time
import traceback

import time
from gurobipy import GRB


def branch_and_bound(model, tolerance=1e-6, time_limit=120):
    """
    Branch and bound using iterative DFS.
    Parameters:
        model: The Gurobi model object (with the continuous relaxation)
        tolerance: The tolerance level for deciding whether a variable is "close" to 0 or 1 (default: 1e-6)
        time_limit: The maximum time allowed for the branch-and-bound process (in seconds)
    Returns:
        best_lp_relaxation: The best LP relaxation value (lower bound from continuous relaxation)
        best_ip_solution: The best integer programming (IP) solution found, if any.
        time_taken: Time taken by the branch-and-bound process.
        mip_gap: The MIP gap if the optimal solution is not found, otherwise 0.
        nodes_explored: Number of nodes explored during the search.
    """
    best_solution = None
    best_objective = float('inf')
    best_bound = float('inf')
    nodes_explored = 0
    start_time = time.time()

    stack = [(id(model), model)]
    active_nodes = {}
    active_int_nodes = {}

    while stack and time.time() - start_time < time_limit:
        _, current_model = stack.pop()
        current_id = id(current_model)
        nodes_explored += 1

        # Set the remaining time limit for this branch
        current_model.Params.TimeLimit = max(time_limit - (time.time() - start_time), 0)

        # Solve the relaxed model
        current_model.optimize()
        if current_model.status != GRB.OPTIMAL :
            # print('infeasible')
            active_nodes = {node_id: obj for node_id, obj in active_nodes.items()
                            if any(node_id == stack_id for stack_id, _ in stack)} #   Remove the current node from active nodes
            continue  # Skip infeasible or time limit reached nodes

        obj_val = current_model.objVal

        if obj_val >= best_objective:
            active_nodes = {node_id: obj for node_id, obj in active_nodes.items()
                            if any(node_id == stack_id for stack_id, _ in stack)}  # Remove the current node from active nodes
            continue  # Prune this branch

        active_nodes[current_id] = obj_val
        # Check if the solution is integral
        fractional_var = choose_branching_variable(current_model, tolerance)

        if fractional_var is None:
            # Found an integer solution
            if obj_val < best_objective:
                best_solution = current_model.copy()
                best_objective = obj_val
                active_int_nodes[current_id] = obj_val
        else:
            # Branch on the fractional variable
            var_name = fractional_var.varName

            # Right branch: var >= ceil(var.x)
            model_right = current_model.copy()
            model_right.getVarByName(var_name).lb = int(fractional_var.x) + 1
            stack.append((current_id, model_right)) # Parent id and model
            # Left branch: var <= floor(var.x)
            model_left = current_model.copy()
            model_left.getVarByName(var_name).ub = int(fractional_var.x)
            stack.append((current_id, model_left))

        active_nodes = {node_id: obj for node_id, obj in active_nodes.items()
                        if any(node_id == stack_id for stack_id, _ in stack)}  # Remove the node if both of its children are explored

    time_taken = time.time() - start_time
    # best bound is equal to minimum of active nodes and active int nodes
    best_bound = min(min(active_int_nodes.values(), default=best_bound),
                     min(active_nodes.values(), default=best_bound))

    # print(best_bound,best_objective)
    if best_objective == float('inf'):
        gap = float('inf')
    else:
        gap = 0.0 if best_objective == best_bound else (best_objective - best_bound) / abs(best_objective) * 100
    return best_bound, best_objective, time_taken, gap, nodes_explored


def choose_branching_variable(model, tolerance=1e-6):
    """
    Choose the variable with the value closest to 0.5 for branching in the Gurobi model.

    Args:
        model (gurobipy.Model): The Gurobi model from which to choose the branching variable.
        tolerance (float): A small tolerance to avoid selecting variables that are already integer.

    Returns:
        gurobipy.Var or None: First fractional variable, or None if no fractional variable is found.
    """
    fractional_vars = []

    # Collect variables that are fractional (not close to integer values)
    for var in model.getVars():
        if tolerance < var.x < 1 - tolerance:
            fractional_vars.append((var, abs(var.x - 0.5)))
            return fractional_vars[0][0]

    # If no fractional variables are found, return None
    if not fractional_vars:
        return None



