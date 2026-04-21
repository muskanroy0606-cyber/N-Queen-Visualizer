# N-Queens Visual Solver

This is a Python Tkinter-based Visualizer that demonstrates how the **Backtracking algorithm** solves the classic N-Queens problem step by step.

## What is the N-Queens Problem?
The N-Queens problem requires placing $N$ chess queens on an $N \times N$ chessboard such that no two queens threaten each other. This means no two queens can share the same:
- Row
- Column
- Diagonal

## Backtracking Algorithm Explanation
Backtracking is a systematic way of trying out different possible solutions to a problem and discarding them ("backtracking") as soon as we realize they cannot lead to a valid solution. 

In the N-Queens problem:
1. **Start** in the leftmost column (or topmost row).
2. **Place** a queen in the current row/column.
3. **Check** if this placement is *safe*.
   - **Safe:** No conflict found. Move to the next row recursively.
   - **Conflict:** Remove the queen (i.e., backtrack) and try the next space.
4. **Repeat** until all rows contain a queen safely (a valid solution is found).
5. After a solution is found, backtrack again to pursue other possible valid configurations.

By utilizing this approach, we avoid checking every possible permutation (brute-force), making the algorithm much faster in finding valid states.

## Complexity Analysis

### Time Complexity: $O(N!)$
In the worst-case scenario, the backtracking algorithm puts the 1st queen in $N$ possible positions, the 2nd queen in $N-1$ possible positions (skipping same column/diagonals), leading to approximately $O(N!)$ checks. This is significantly faster than the naive brute force approach $O(N^N)$.

### Space Complexity: $O(N)$
We only need a single 1D array of size $N$ to store the board state (e.g., `board[row] = col`), plus memory for the call stack during recursion, which reaches a maximum depth of $N$. Therefore, the space complexity is proportional to $N$.

## Sample Input/Output

### Input
- **Board Size (N):** 4
- **Initial Board:** Empty

### Output
The application calculates *all* valid combinations. For `N = 4`, there are exactly `2` solutions:

**Solution 1:**
- Row 1: Col 2 (zero-indexed: 1)
- Row 2: Col 4 (zero-indexed: 3)
- Row 3: Col 1 (zero-indexed: 0)
- Row 4: Col 3 (zero-indexed: 2)
  *(Represented by array `[1, 3, 0, 2]`)*

**Solution 2:**
- Row 1: Col 3 (zero-indexed: 2)
- Row 2: Col 1 (zero-indexed: 0)
- Row 3: Col 4 (zero-indexed: 3)
- Row 4: Col 2 (zero-indexed: 1)
  *(Represented by array `[2, 0, 3, 1]`)*

## Running the Application
Ensure you have Python installed. The app requires no external libraries.
```bash
python n_queens_visualizer.py
```
- Select your desired $N$.
- Adjust the speed slider to see the step-by-step backtracking process.
- Click `Next Step` for manual progress, or `Auto Solve` to watch it animated!
