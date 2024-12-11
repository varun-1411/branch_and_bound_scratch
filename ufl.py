
import os
import numpy as np
import gurobipy as gp
from gurobipy import GRB
import time
from branch_and_bound import branch_and_bound
import pandas as pd

# Helper function to extract 100 elements from multiple lines (12 per line)
def extract_full_row(start_idx, lines_needed, lines):
    elements = []
    for i in range(lines_needed):
        line_elements = list(map(float, lines[start_idx + i].split()))
        elements.extend(line_elements)
    return elements


# Helper function to extract 100 elements from a single line
def read_ufl_file(filename):

    """
    n - number of clients
    m - number of facilities
    fixed_cost - fixed cost of opening a facility
    cost_matrix - cost of connecting a client to a facility
    """
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        # print(lines)
        fixed_cost = []
        cost_matrix = []
        m, n = map(int, lines[0].split())
        # print(n, m)

        lines_reqd = m // 7 + 1
        # print(lines_reqd)

        fixed_cost_start_index = 1
        fixed_cost_end_index = m + 1
        init_cost_matrix_start_index = fixed_cost_end_index + 1

        # fixed cost
        for i in range(fixed_cost_start_index, fixed_cost_end_index):
            fixed_cost.append(float(lines[i].split()[1]))
        
        # cost matrix
        for i in range(n):
            cost_matrix_start_index = init_cost_matrix_start_index + i * (lines_reqd + 1)
            cost_matrix.append(extract_full_row(cost_matrix_start_index, lines_reqd, lines))
        # print(cost_matrix)
        
        return n, m, fixed_cost, cost_matrix    


# Helper function to solve the UFL problem
def solve_ufl_weak(n, m, fixed_cost, cost_matrix, results, file,  output_file):
    # Create a new model
    gp.setParam("TimeLimit", 120)
    model = gp.Model("ufl")
    model.setParam('OutputFlag', 0)

    # Create variables
    y = model.addVars(m, vtype=GRB.BINARY, name="y")
    x = model.addVars(n, m, vtype=GRB.BINARY, name="x")

    # Set objective
    model.setObjective(gp.quicksum(fixed_cost[j] * y[j] for j in range(m)) + gp.quicksum(cost_matrix[i][j] * x[i, j] for i in range(n) for j in range(m)), GRB.MINIMIZE)

    # Add constraints
    model.addConstrs((x.sum(i, '*') == 1 for i in range(n)), name="c1")
    model.addConstrs((sum(x[i, j] for i in range(n)) <= (n)  * y[j] for j in range(m)), name="c2")
    model.optimize()
    total_time = model.Runtime

    best_objective = None
    best_bound = None
    gap = None
    nodes_explored = None

    # if model.status == GRB.OPTIMAL or model.status == GRB.SUBOPTIMAL:
    best_objective = model.objVal if hasattr(model, 'objVal') else None
    best_bound = model.ObjBound if hasattr(model, 'ObjBound') else None
    gap = model.MIPGap * 100 if hasattr(model, 'MIPGap') else None
    nodes_explored = model.NodeCount if hasattr(model, 'NodeCount') else None

    for var in model.getVars():
        var.vtype = GRB.CONTINUOUS  # Convert to continuous
    # Write the modified model with continuous variables to an .lp file
    model.update()  # Ensure the model reflects changes to the variable types

    results.append({
        "File": file,
        "Best Objective": best_objective if best_objective is not None else 'None',
        "Best Bound": best_bound if best_bound is not None else 'None',
        "GAP (%)": gap if gap is not None else 'None',
        "Nodes Explored": nodes_explored if nodes_explored is not None else 'None',
        "Time Taken (seconds)": total_time
    })
    model.write(output_file)
    # return model

# Helper function to solve the UFL problem
def solve_ufl_strong(n, m, fixed_cost, cost_matrix, results, file, output_file):
    # Create a new model
    gp.setParam("TimeLimit", 120)
    model = gp.Model("ufl")
    model.setParam('OutputFlag', 0)

    # Create variables
    y = model.addVars(m, vtype=GRB.BINARY, name="y")
    x = model.addVars(n, m, vtype=GRB.BINARY, name="x")

    # Set objective
    model.setObjective(gp.quicksum(fixed_cost[j] * y[j] for j in range(m)) + gp.quicksum(cost_matrix[i][j] * x[i, j] for i in range(n) for j in range(m)), GRB.MINIMIZE)

    # Add constraints
    model.addConstrs((x.sum(i, '*') == 1 for i in range(n)), name="c1")
    model.addConstrs((x[i, j] <= y[j] for i in range(n) for j in range(m)), name="c2")
    model.optimize()
    total_time = model.Runtime

    best_objective = None
    best_bound = None
    gap = None
    nodes_explored = None

    best_objective = model.objVal if hasattr(model, 'objVal') else None
    best_bound = model.ObjBound if hasattr(model, 'ObjBound') else None
    gap = model.MIPGap * 100 if hasattr(model, 'MIPGap') else None
    nodes_explored = model.NodeCount if hasattr(model, 'NodeCount') else None
    for var in model.getVars():
        var.vtype = GRB.CONTINUOUS  # Convert to continuous
    # Write the modified model with continuous variables to an .lp file
    model.update()  # Ensure the model reflects changes to the variable types
    results.append({
        "File": file,
        "Best Objective": best_objective if best_objective is not None else 'None',
        "Best Bound": best_bound if best_bound is not None else 'None',
        "GAP (%)": gap if gap is not None else 'None',
        "Nodes Explored": nodes_explored if nodes_explored is not None else 'None',
        "Time Taken (seconds)": total_time
    })
    model.write(output_file)
    # return model

# results_directory
res_dir = 'results'
os.makedirs(res_dir, exist_ok=True)

# Create output directory
output_dir_str = 'lp_files_UFL_Strong'
os.makedirs(output_dir_str, exist_ok=True)

output_dir_weak = 'lp_files_UFL_Weak'
os.makedirs(output_dir_weak, exist_ok=True)

# stronger formulation
results = []
for root, dirs, files in os.walk("UFL"):
        files = sorted(files)
        for file in files:
                n, m, f, c = read_ufl_file(os.path.join(root, file))
                # print("Stronger formulation")
                solve_ufl_strong(n, m, f, c, results, file, os.path.join(output_dir_str, f"{file}.lp"))
df = pd.DataFrame(results)
df.to_csv(os.path.join(res_dir, 'gurobi_ufl_strong.csv'), index=False)


# weaker formulation
results = []
for root, dirs, files in os.walk("UFL"):
        files = sorted(files)
        for file in files:
            # if file.startswith('capb'):
                n, m, f, c = read_ufl_file(os.path.join(root, file))
                # print("Stronger formulation")
                solve_ufl_weak(n, m, f, c, results, file, os.path.join(output_dir_weak, f"{file}.lp"))
df = pd.DataFrame(results)
df.to_csv(os.path.join(res_dir, 'gurobi_ufl_weak.csv'), index=False)


# print("Branch and Bound solution")

output_dir_weak = 'lp_files_UFL_Weak'
os.makedirs(output_dir_weak, exist_ok=True)
results = []
# weaker formulation
for root, dirs, files in os.walk("UFL"):
    sorted_files = sorted(files)
    for file in sorted_files:
            model = gp.read(os.path.join(output_dir_weak, f"{file}.lp"))
            model.setParam('OutputFlag', 0)
            best_lp_relaxation, best_objective, time_taken, gap, nodes_explored = branch_and_bound(model)
            # Append the results to the list
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
df.to_csv(os.path.join(res_dir, 'custom_ufl_weak.csv'), index=False)


# # Stronger formulation
results = []
for root, dirs, files in os.walk("UFL"):
    sorted_files = sorted(files)
    for file in sorted_files:
        model = gp.read(os.path.join(output_dir_str, f"{file}.lp"))
        model.setParam('OutputFlag', 0)
        best_lp_relaxation, best_objective, time_taken, gap, nodes_explored = branch_and_bound(model)
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
df.to_csv(os.path.join(res_dir, 'custom_ufl_strong.csv'), index=False)