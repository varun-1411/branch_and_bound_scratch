# 🚀 **Branch and Bound for Combinatorial Optimization Problems**

## **Overview**

This project implements **Branch and Bound (B&B)** algorithms for solving key combinatorial optimization problems using Gurobi. It includes problem formulations, benchmark dataset experiments, and performance evaluation.

The problems addressed include:
1. **Generalized Assignment Problem (GAP)** with a minimization objective.
2. **Uncapacitated Facility Location (UFL)**:
   - Weaker/Compact formulation.
   - Extended formulation.
3. **Asymmetric Traveling Salesman Problem (ATSP)**:
   - Multi-commodity flow (MCF) formulation.
   - Miller-Tucker-Zemlin (MTZ) formulation.

---

## 📊 **Project Structure**

The repository is organized as follows:

```plaintext
root/
│
├── data/                     # Contains the benchmark datasets (GAP, UFL, ATSP)
│   ├── GAP/                  # GAP dataset
│   ├── UFL/                  # UFL dataset
│   └── ATSP/                 # ATSP dataset
│
├── lp_files/                 # Exported .lp files for each problem instance
│
├── src/                      # Code for model formulation and B&B implementation
│   ├── gap_solver.py         # Generalized Assignment Problem solver
│   ├── ufl_solver.py         # Uncapacitated Facility Location solver
│   ├── atsp_mcf_solver.py    # ATSP solver (MCF formulation)
│   ├── atsp_mtz_solver.py    # ATSP solver (MTZ formulation)
│   ├── branch_and_bound.py   # Generic Branch and Bound implementation
│   └── utils/                # Helper functions (e.g., file I/O, preprocessing)
│

```

---

## 🛠️ **Problem Descriptions**

### 1. **Generalized Assignment Problem (GAP)**  
The GAP involves assigning tasks to agents with a given cost and resource capacity constraints.  
- **Dataset**: [OR Library](http://people.brunel.ac.uk/~mastjjb/jeb/orlib/gapinfo.html)

### 2. **Uncapacitated Facility Location (UFL)**  
UFL aims to determine the locations of facilities to minimize the cost of opening facilities and serving clients.  
- **Dataset**: [OR Library](http://people.brunel.ac.uk/~mastjjb/jeb/orlib/uncapinfo.html)

### 3. **Asymmetric Traveling Salesman Problem (ATSP)**  
The ATSP finds the shortest route for a salesman visiting a set of cities with asymmetric travel costs.  
- **Formulations**:
   - **MTZ**: Miller-Tucker-Zemlin formulation.
   - **MCF**: Multi-commodity flow formulation.  
- **Dataset**: [TSPLIB95](http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp95.pdf)  



| File      | LP Relaxation | Best Objective | Nodes Explored | Gap (%) | Time Taken (s) |
|-----------|---------------|----------------|----------------|---------|----------------|
| a05100    | 1698.00       | 1698.00        | 83             | 0.0     | 0.19           |
| a05200    | 3235.00       | 3235.00        | 17             | 0.0     | 0.06           |



| File      | LP Relaxation | Best Objective | Nodes Explored | Gap (%) | Time Taken (s) |
|-----------|---------------|----------------|----------------|---------|----------------|
| br17.atsp | 39.0          | 39.0           | 99             | 0.0     | 3.10           |



| File      | LP Relaxation | Best Objective | Nodes Explored | Gap (%) | Time Taken (s) |
|-----------|---------------|----------------|----------------|---------|----------------|
| br17.atsp | 2.11          | 10169.0        | 53388          | 99.97%  | 120.00         |



| File      | LP Relaxation | Best Objective | Nodes Explored | Gap (%) | Time Taken (s) |
|-----------|---------------|----------------|----------------|---------|----------------|
| ufl1      | 1742.0        | 1742.0         | 159            | 0.0     | 5.13           |

---

## 🚀 **Features**
- **Modeling**: Formulates problems as integer programs.
- **Solver**: Uses Gurobi to solve and export LP files.
- **Branch and Bound**: Implements a custom B&B algorithm.
- **Benchmarking**: Compares performance on publicly available datasets.

---

## 📊 **Performance Results**

### **Generalized Assignment Problem (GAP)**

| File      | LP Relaxation | Best Objective | Nodes Explored | Gap (%) | Time Taken (seconds) |
|-----------|---------------|----------------|----------------|---------|----------------------|
| a05100    | 1698.00       | 1698.00        | 83             | 0.0     | 0.19                 |
| a05200    | 3235.00       | 3235.00        | 17             | 0.0     | 0.06                 |
| a10100    | 1360.00       | 1360.00        | 447            | 0.0     | 1.31                 |
| a10200    | 2623.00       | 2623.00        | 9              | 0.0     | 0.04                 |
| a20100    | 1158.00       | 1158.00        | 949            | 0.0     | 4.33                 |
| a20200    | 2339.00       | 2339.00        | 6327           | 0.0     | 54.04                |
| b05100    | 1831.33       | 1943.00        | 46021          | 5.75    | 120.00               |
| b05200    | 3547.41       | 3849.00        | 17368          | 7.84    | 120.01               |
| b10100    | 1400.67       | 1539.00        | 19180          | 8.99    | 120.01               |
| b10200    | 2815.05       | 3866.00        | 3546           | 27.18   | 120.03               |
| b20100    | 1155.18       | 1452.00        | 6083           | 20.44   | 120.02               |
| b20200    | 2331.14       | 2825.00        | 2325           | 17.48   | 120.00               |

### **ATSP Results**

#### **MCF Formulation**

| File         | LP Relaxation  | Best Objective | Nodes Explored | Gap (%)           | Time Taken (seconds) |
|--------------|----------------|----------------|----------------|-------------------|----------------------|
| br17.atsp    | 39.0           | 39.0           | 99             | 0.0%              | 3.10                 |
| ft53.atsp    | 6905.0         | 6905.0         | 1              | 0.0%              | 12.23                |
| ft70.atsp    | 38652.5        | inf            | 3              | inf%              | 120.02               |
| ftv33.atsp   | 1286.0         | 1286.0         | 1              | 0.0%              | 1.64                 |
| ftv35.atsp   | 1457.33        | 1487.0         | 79             | 1.99%             | 120.00               |
| ftv38.atsp   | 1514.33        | 1560.0         | 51             | 2.93%             | 120.00               |
| ftv44.atsp   | 1584.875       | inf            | 25             | inf%              | 120.02               |
| ftv47.atsp   | 1748.61        | inf            | 20             | inf%              | 120.00               |
| ftv55.atsp   | 1584.0         | inf            | 9              | inf%              | 120.03               |
| ftv64.atsp   | 1807.5         | inf            | 4              | inf%              | 120.07               |
| ftv70.atsp   | 1909.0         | inf            | 3              | inf%              | 120.01               |
| kro124p.atsp | inf            | inf            | 1              | inf%              | 120.04               |
| p43.atsp     | 5611.0         | inf            | 65             | inf%              | 120.01               |
| ry48p.atsp   | 14289.33       | inf            | 17             | inf%              | 120.07               |

#### **MTZ Formulation**

| File         | LP Relaxation  | Best Objective | Nodes Explored | Gap (%)           | Time Taken (seconds) |
|--------------|----------------|----------------|----------------|-------------------|----------------------|
| br17.atsp    | 2.11         | 10169.0        | 53388          | 99.97%          | 120.00             |
| ft53.atsp    | 5935.29      | 13795.0        | 3632           | 56.97%          | 120.02             |
| ft70.atsp    | 37987.26     | 47055.0        | 1743           | 19.27%          | 120.01             |
| ftv170.atsp  | 2631.47      | inf            | 354            | inf%              | 120.05           |
| ftv33.atsp   | 1187.00      | 1654.0         | 22021          | 28.23%          | 120.00             |
| ftv35.atsp   | 1377.11      | 1740.0         | 19623          | 20.85%          | 120.00             |
| ftv38.atsp   | 1434.33      | 2045.0         | 16109          | 29.86%          | 120.00             |
| ftv44.atsp   | 1523.34      | 2729.0         | 7991           | 44.17%          | 120.00             |
| ftv47.atsp   | 1655.73      | 2831.0         | 7943           | 41.51%          | 120.00             |
| ftv55.atsp   | 1438.23      | inf            | 1619           | inf%              | 120.12           |
| ftv64.atsp   | 1722.85      | 4018.0         | 1869           | 57.12%          | 120.07             |
| ftv70.atsp   | 1769.37      | 2720.0         | 3706           | 34.94%          | 120.008            |
| kro124p.atsp | 34008.51     | inf            | 959            | inf%              | 120.01           |
| p43.atsp     | 0.0            | inf            | 2969           | inf%              | 120.02         |
| rbg323.atsp  | 0.0            | 0.0            | 1              | 0.0%              | 0.70           |
| rbg358.atsp  | 0.0            | 0.0            | 1              | 0.0%              | 0.93           |
| rbg403.atsp  | 0.0            | 0.0            | 1              | 0.0%              | 1.188          |
| rbg443.atsp  | 0.0            | 0.0            | 1              | 0.0%              | 1.39           |
| ry48p.atsp   | 12563.70     | inf            | 1953           | inf%              | 120.05           |

### **UFL Results**
# UFL with weaker formulation

| File        | LP Relaxation | Best Objective | Nodes Explored | Gap (%) | Time Taken (seconds) |
|-------------|---------------|----------------|----------------|---------|----------------------|
| cap101.txt  | 659341.15      | 811617.06      | 59273          | 18.76   | 120.00               |
| cap102.txt  | 664015.90      | 860886.75      | 59664          | 22.87   | 120.00               |
| cap103.txt  | 668503.01      | 894008.14      | 59103          | 25.22   | 120.00               |
| cap104.txt  | 674734.59      | 928941.75      | 59330          | 27.37   | 120.00               |
| cap131.txt  | 631421.45      | 851002.88      | 36323          | 25.80   | 120.00               |
| cap132.txt  | 636321.45      | 893595.76      | 36608          | 28.79   | 120.00               |
| cap133.txt  | 641221.45      | 923595.76      | 33937          | 30.57   | 120.00               |
| cap134.txt  | 648426.30      | 957305.86      | 36116          | 32.27   | 120.00               |
| cap71.txt   | 932615.75      | 932615.75      | 8635           | 0.00    | 14.26                |
| cap72.txt   | 977799.40      | 977799.40      | 9595           | 0.00    | 15.63                |
| cap73.txt   | 1010641.45     | 1010641.45     | 8053           | 0.00    | 13.87                |
| cap74.txt   | 1034976.98     | 1034976.98     | 4235           | 0.00    | 7.52                 |
| capa.txt    | 4801483.12     | 19534785.73    | 974            | 75.42   | 120.07               |
| capb.txt    | 3668833.37     | 14668820.85    | 1003           | 74.99   | 120.01               |
| capc.txt    | 3300869.23     | 13620036.27    | 1003           | 75.76   | 120.02               |


# UFL with stronger formulation

| File                 | LP Relaxation   | Best Objective   | Nodes Explored | Gap (%) | Time Taken (seconds) |
|----------------------|-----------------|-------------------|----------------|---------|----------------------|
| cap101.txt           | 796648.44       | 796648.44         | 1              | 0.00    | 0.00                 |
| cap102.txt           | 854704.20       | 854704.20         | 1              | 0.00    | 0.01                 |
| cap103.txt           | 893782.11       | 893782.11         | 1              | 0.00    | 0.01                 |
| cap104.txt           | 928941.75       | 928941.75         | 1              | 0.00    | 0.00                 |
| cap131.txt           | 793439.56       | 793439.56         | 1              | 0.00    | 0.01                 |
| cap132.txt           | 851495.33       | 851495.33         | 1              | 0.00    | 0.01                 |
| cap133.txt           | 893076.71       | 893076.71         | 1              | 0.00    | 0.01                 |
| cap134.txt           | 928941.75       | 928941.75         | 1              | 0.00    | 0.01                 |
| cap71.txt            | 932615.75       | 932615.75         | 1              | 0.00    | 0.00                 |
| cap72.txt            | 977799.40       | 977799.40         | 1              | 0.00    | 0.00                 |
| cap73.txt            | 1010641.45      | 1010641.45        | 1              | 0.00    | 0.00                 |
| cap74.txt            | 1034976.98      | 1034976.98        | 1              | 0.00    | 0.00                 |
| capa.txt             | 17156454.48     | 17156454.48       | 1              | 0.00    | 1.03                 |
| capb.txt             | 12979071.58     | 12979071.58       | 1              | 0.00    | 1.17                 |
| capc.txt             | 11505594.33     | 11505594.33       | 11             | 0.00    | 9.85                 |




