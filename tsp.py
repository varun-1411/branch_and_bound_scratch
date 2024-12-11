import os
import numpy as np
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import time
from branch_and_bound import branch_and_bound

def solve_tsp(n, c, results, file,output_file=None, time_limit=120):
    """
    Solve the traveling salesman problem with Gurobi

    Parameters:
    n (int): Number of nodes
    c (list of lists): Cost matrix
    output_file (str): Name of the output file
    time_limit (int): Time limit in seconds

    Returns:
    None
    """
    # add time limit
    if time_limit is not None:
        gp.setParam("TimeLimit", time_limit)
    

    m = gp.Model("tsp")
    # Suppress the output (initial Gurobi information)
    m.setParam('OutputFlag', 0)
    x = m.addVars(n, n, vtype=GRB.BINARY, name="x")
    u = m.addVars(n, vtype=GRB.CONTINUOUS, name="u")
    m.setObjective(gp.quicksum(c[i][j] * x[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE)

    # Add constraints
    m.addConstrs((gp.quicksum(x[i, j] for j in range(n)) == 1 for i in range(n)), name="out")
    m.addConstrs((gp.quicksum(x[j, i] for j in range(n)) == 1 for i in range(n)), name="in")
    # m.addConstrs((u[i] - u[j] + n * x[i, j] <= n - 1 for i in range(1, n) for j in range(1, n)), name="subtour")
    # Subtour elimination constraints (MTZ formulation)
    # Ensure that u[1] = 1 and u[i] is between 2 and n for nodes 2 to n
    m.addConstr(u[0] == 1, name="u_1_fixed")
    m.addConstrs((u[i] >= 2 for i in range(1, n)), name="u_lower_bound")
    m.addConstrs((u[i] <= n for i in range(1, n)), name="u_upper_bound")

    # Subtour elimination: u[i] - u[j] + n * x[i, j] <= n - 1 for i != j
    m.addConstrs((u[i] - u[j] + n * x[i, j] <= n - 1 for i in range(1, n) for j in range(1, n) if i != j), name="subtour")

    m.optimize()
    total_time = m.Runtime

    best_objective = None
    best_bound = None
    gap = None
    nodes_explored = None

    best_objective = m.objVal if hasattr(m, 'objVal') else None
    best_bound = m.ObjBound if hasattr(m, 'ObjBound') else None
    gap = m.MIPGap * 100 if hasattr(m, 'MIPGap') else None
    nodes_explored = m.NodeCount if hasattr(m, 'NodeCount') else None
    for var in m.getVars():
        var.vtype = GRB.CONTINUOUS  # Convert to continuous
    # Write the modified model with continuous variables to an .lp file
    m.update()  # Ensure the model reflects changes to the variable types
    results.append({
        "File": file,
        "Best Bound": best_bound if best_bound else 'None',
        "Best Objective": best_objective if best_objective else 'None',
        "GAP (%)": gap if gap else 'None',
        "Nodes Explored": nodes_explored if nodes_explored else 'None',
        "Time Taken (seconds)": total_time
    })
    m.write(output_file)
    # Return None if no optimal solution is found
    return None



def solve_tsp_cw_mcf(n, c,results, file,output_file=None, time_limit=120):
    """
    Solve the Traveling Salesman Problem using the Claus and Wong multi-commodity flow formulation.

    Parameters:
    - n: Number of nodes
    - c: Cost matrix (n x n) representing the cost of traveling from node i to node j

    Returns:
    - None
    """
    gp.setParam("TimeLimit", time_limit)
    # Create the Gurobi model
    m = gp.Model("tsp_cw_mcf")
    # Suppress the output (initial Gurobi information)
    m.setParam('OutputFlag', 0)
    # Binary variables x[i, j] to indicate if edge (i, j) is in the tour
    x = m.addVars(n, n, vtype=GRB.BINARY, name="x")

    # Continuous flow variables f[i, j, k] for the flow of commodity k from node i to node j
    f = m.addVars(n, n, n, vtype=GRB.CONTINUOUS, name="f")

    # Set objective: minimize the total cost of the tour
    m.setObjective(gp.quicksum(c[i, j] * x[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE)

    # Constraint 1: sum(x[i, j]) over j = sum(x[j, i]) over i = 1 for all i
    m.addConstrs((gp.quicksum(x[i, j] for j in range(n) if i != j) == 1 for i in range(n)), name="out_degree")
    m.addConstrs((gp.quicksum(x[j, i] for j in range(n) if i != j) == 1 for i in range(n)), name="in_degree")

    # Constraint 2: sum(f[1, j, k]) over j = 1 for all k in range(2, n)
    m.addConstrs((gp.quicksum(f[0, j, k] for j in range(n)) == 1 for k in range(1, n)), name="flow_out_1")

    # Constraint 3: sum(f[j, 1, k]) over j = 0 for all k in range(2, n)
    m.addConstrs((gp.quicksum(f[j, 0, k] for j in range(n)) == 0 for k in range(1, n)), name="flow_in_1")

    # Constraint 4: sum(f[k, j, k]) over j = 0 for all k in range(2, n)
    m.addConstrs((gp.quicksum(f[k, j, k] for j in range(n)) == 0 for k in range(1, n)), name="no_self_flow")

    # Constraint 5: sum(f[j, k, k]) over j = 1 for all k in range(2, n)
    m.addConstrs((gp.quicksum(f[j, k, k] for j in range(n)) == 1 for k in range(1, n)), name="self_flow_out")

    # Constraint 6: sum(f[i, j, k]) over j - sum(f[j, i, k]) over j = 0 for all i, k in 2 to n and i != k
    m.addConstrs((
        gp.quicksum(f[i, j, k] for j in range(n) if i != j) - gp.quicksum(f[j, i, k] for j in range(n) if i != j) == 0 
        for i in range(1, n) for k in range(1, n) if i != k), name="flow_conservation")

    # Constraint 7: f[i, j, k] <= x[i, j] for all i, j, k in 1 to n
    m.addConstrs((f[i, j, k] <= x[i, j] for i in range(n) for j in range(n) for k in range(n) if i != j), name="flow_link")

    best_objective = None
    best_bound = None
    gap = None
    nodes_explored = None
    m.optimize()
    total_time = m.Runtime
    best_objective = m.objVal if hasattr(m, 'objVal') else None
    best_bound = m.ObjBound if hasattr(m, 'ObjBound') else None
    gap = m.MIPGap * 100 if hasattr(m, 'MIPGap') else None
    nodes_explored = m.NodeCount if hasattr(m, 'NodeCount') else None
    for var in m.getVars():
        var.vtype = GRB.CONTINUOUS  # Convert to continuous
    # Write the modified model with continuous variables to an .lp file
    m.update()  # Ensure the model reflects changes to the variable types
    results.append({
        "File": file,
        "Best Bound": best_bound if best_bound else 'None',
        "Best Objective": best_objective if best_objective else 'None',
        "GAP (%)": gap if gap else 'None',
        "Nodes Explored": nodes_explored if nodes_explored else 'None',
        "Time Taken (seconds)": total_time
    })
    m.write(output_file)
    return None

def read_atsp_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        n = int(lines[3].split()[1])
        c = []
        # convert the lines to a list of integers then to a numpy 2d array
        for i in range(7, len(lines)-1):
            temp = list(map(int, lines[i].split()))
            # print(temp)
            c.extend(temp)
        c = np.array(c).reshape((n,n))
        # print(c)
    return n, c


res_dir = 'results'
os.makedirs(res_dir, exist_ok=True)

output_dir_mtz = 'lp_files_mtz'
os.makedirs(output_dir_mtz, exist_ok=True)

output_dir_mcf = 'lp_files_cw_mcf'
os.makedirs(output_dir_mcf, exist_ok=True)


results = []
for root, dirs, files in os.walk("ATSP"):
        for file in files:

                # print(f"----------------{file}----------------")
                # print(file)
                n, c = read_atsp_file(os.path.join(root, file))
                # time limit is set to 120 seconds
                # print("MTZ Formulation")
                solve_tsp(n, c, results,file, output_file=os.path.join(output_dir_mtz, file + '.lp'), time_limit=120)
                # print()
df = pd.DataFrame(results)
df.to_csv(os.path.join(res_dir, 'gurobi_atsp_mtz.csv'), index=False)

results = []
for root, dirs, files in os.walk("ATSP"):
        for file in files:

                # print(f"----------------{file}----------------")
                # print(file)
                n, c = read_atsp_file(os.path.join(root, file))
                if not (file.startswith('rbg')):
                    # print("cw_mcf Formulation")
                    solve_tsp_cw_mcf(n, c,results, file, output_file=os.path.join(output_dir_mcf, file + '.lp'), time_limit=120)
                    print()

df = pd.DataFrame(results)
df.to_csv(os.path.join(res_dir, 'gurobi_atsp_mcf.csv'), index=False)



output_dir_mcf = 'lp_files_cw_mcf'
os.makedirs(output_dir_mcf, exist_ok=True)
results = []
for root, dirs, files in os.walk("ATSP"):
    sorted_files = sorted(files)
    for file in sorted_files:
        if not (file.startswith('rbg') or file.startswith('ftv170')):
    # for file in files:
        # Process each file
        # print(f"Processing file: {file}")
            model = gp.read(os.path.join(output_dir_mcf, f"{file}.lp"))
            model.setParam('OutputFlag', 0)

            best_lp_relaxation, best_objective, time_taken, gap, nodes_explored = branch_and_bound(model, time_limit=120)
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
df.to_csv(os.path.join(res_dir, 'custom_atsp_mcf.csv'), index=False)



output_dir_mtz = 'lp_files_mtz'
os.makedirs(output_dir_mtz, exist_ok=True)

results = []
for root, dirs, files in os.walk("ATSP"):
    sorted_files = sorted(files)
    for file in sorted_files:
        model = gp.read(os.path.join(output_dir_mtz, f"{file}.lp"))
        model.setParam('OutputFlag', 0)

        best_lp_relaxation, best_objective, time_taken, gap, nodes_explored = branch_and_bound(model)

        # Print LaTeX row for each file
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
df.to_csv(os.path.join(res_dir, 'custom_atsp_mtz.csv'), index=False)


