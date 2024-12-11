import os
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from  branch_and_bound import branch_and_bound
import pandas as pd
import time
import traceback

# Helper function to extract 100 elements from multiple lines (12 per line)
def extract_full_row(start_idx, lines_needed, lines):
    elements = []
    for i in range(lines_needed):
        line_elements = list(map(int, lines[start_idx + i].split()))
        elements.extend(line_elements)
    return elements


def read_gap_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
        # Read the first line which contains m and n
        m, n = map(int, lines[0].split())

        lines_reqd = n // 12 + 1
        # Initialize lists to hold the resources and costs
        costs = []
        resources = []
        capacity_constraints = []

        # Extract costs (first m rows of 100 elements each)
        cost_start_idx = 1
        for i in range(m):
            costs.append(extract_full_row(cost_start_idx + i * lines_reqd, lines_reqd, lines))

        # Extract resources (next m rows of 100 elements each)
        resource_start_idx = cost_start_idx + m * (lines_reqd)
        for i in range(m):
            resources.append(extract_full_row(resource_start_idx + i * lines_reqd, lines_reqd, lines))

        # Extract the final capacity constraint values
        capacity_start_idx = resource_start_idx + m * (lines_reqd)
        capacity_constraints = list(map(int, ' '.join(lines[capacity_start_idx:]).split()))

        # Convert lists to numpy arrays (optional)
        costs = np.array(costs)
        resources = np.array(resources)
        capacity_constraints = np.array(capacity_constraints)


        return m, n, costs, resources, capacity_constraints


def solve_gap(resource_matrix, cost_matrix, capacity, m, n, results, file, output_file="model.lp" ):
    # Create a new model
    model = gp.Model("GAP")

    # Suppress the output (initial Gurobi information)
    model.setParam('OutputFlag', 0)
    gp.setParam("TimeLimit", 120)

    # Create variables (continuous instead of binary)
    x = model.addVars(m, n, vtype=GRB.BINARY, name="x")

    # Set objective (minimize cost)
    model.setObjective(sum(cost_matrix[i][j] * x[i, j] for i in range(m) for j in range(n)), GRB.MINIMIZE)

    # Each task is assigned to exactly one resource (relaxed to continuous)
    model.addConstrs((x.sum('*', j) == 1 for j in range(n)), name="task")

    # Capacity constraints (keeping them as constraints)
    model.addConstrs((sum(resource_matrix[i][j] * x[i, j] for j in range(n)) <= capacity[i] for i in range(m)),
                     name="capacity")

    # Optimize model
    model.optimize()
    total_time = model.Runtime

    best_objective = None
    best_bound = None
    gap = None
    nodes_explored = None
    # If model is solved to optimality or with an integer solution, extract GAP and node count
    if model.status == GRB.OPTIMAL or model.status == GRB.SUBOPTIMAL:
        best_objective = model.objVal
        best_bound = model.ObjBound
        gap = model.MIPGap * 100  # MIPGap is a percentage
        nodes_explored = model.NodeCount

    # After solving, convert variables from binary to continuous and ensure bounds
    for var in model.getVars():
        var.vtype = GRB.CONTINUOUS  # Convert to continuous
    # Write the modified model with continuous variables to an .lp file
    model.update()  # Ensure the model reflects changes to the variable types
    model.write(output_file)

    results.append({
        "File": file,
        "Best Bound": best_bound if best_bound is not None else 'None',
        "Best Objective": best_objective if best_objective is not None else 'None',
        "GAP (%)": gap if gap is not None else 'None',
        "Nodes Explored": nodes_explored if nodes_explored is not None else 'None',
        "Time Taken (seconds)": total_time
    })

    # return model




output_dir = 'lp_files_gap'
os.makedirs(output_dir, exist_ok=True)

res_dir = 'results'
os.makedirs(res_dir, exist_ok=True)

#
results = []
for root, dirs, files in os.walk("GAP"):
    for file in sorted(files):
        # if file.startswith("a05"):
        #     print(f"File: {file}")
            m, n, cost_matrix, resource_matrix, capacity = read_gap_file(os.path.join(root, file))
            # print(f"m = {m}, n = {n}")
            solve_gap(resource_matrix, cost_matrix, capacity, m, n,results,file, os.path.join(output_dir, f"{file}.lp"))
            # model = solve_gap(resource_matrix, cost_matrix, capacity, m, n, os.path.join(output_dir, f"{file}.lp"))
            print()
df = pd.DataFrame(results)
df.to_csv(os.path.join(res_dir, 'gurobi_gap.csv'), index=False)

# Branch and bound

results = []
for root, dirs, files in os.walk("GAP"):
    sorted_files = sorted(files)
    for file in sorted_files:
        # if file.startswith("a05"):
            model = gp.read(os.path.join(output_dir, f"{file}.lp"))
            model.setParam('OutputFlag', 0)


            best_lp_relaxation, best_objective, time_taken, gap, nodes_explored = branch_and_bound(model,time_limit=120, tolerance=1e-10)
            results.append({
                "File": file,
                "LP Relaxation": best_lp_relaxation if best_lp_relaxation != float('inf') else 'inf',
                "Best Objective": best_objective if best_objective is not None else 'None',
                "Nodes Explored": nodes_explored,
                "Gap (%)": gap if gap != float('inf') else 'inf',
                "Time Taken (seconds)": time_taken if time_taken is not None else 0
            })

            # Convert the results list into a pandas DataFrame
df = pd.DataFrame(results)
# Save the DataFrame to a CSV file
df.to_csv(os.path.join(res_dir, 'custom_gap.csv'), index=False)

