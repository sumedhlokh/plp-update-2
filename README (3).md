# Maze Solver Robot - Top 3 Routes

A robot explores a maze and finds the **top 3 shortest paths** from
start to goal, ranked best-first, like route options on a map app.

It works by trying every possible route with backtracking, saving
every complete route it finds, then sorting them by length.

Built in **C++** (main project) with a **Streamlit** web demo (Python port).

## Concepts covered

| Concept | Where |
|---|---|
| Abstract class | `Robot` (`solve`, `getTopPaths` have no implementation there) |
| Child class | `SmartRobot` |
| Encapsulation | `Maze` keeps its grid and goal private |
| Stack | the current path: push when stepping forward, pop when backtracking |

## Project structure

```
maze-solver/
├── maze_solver.cpp      C++ project (main submission)
├── app.py               Streamlit demo (Python)
├── requirements.txt
└── README.md
```

## Run the C++ version

```
g++ -std=c++11 maze_solver.cpp -o maze_solver
./maze_solver
```

## Run the Streamlit demo

```
pip install -r requirements.txt
streamlit run app.py
```

Pick a maze from the dropdown, or paste your own in the text box
(use `#` for wall, `.` for open floor, `S` for start, `G` for goal).
The app shows the top 3 shortest routes side by side, each with its
length and how many cells the robot had to check overall.

## Live demo

Add your Streamlit Cloud link here after deploying.

## How it works

1. Step into a cell and push it onto the current path.
2. Try every direction (up, right, down, left) from there, one at a
   time, going deeper with each try.
3. If the goal is reached, save this complete route.
4. Either way, pop that cell off the path afterwards (backtrack) and
   un-mark it as visited, so other routes can reuse it.
5. Repeat until every possible path has been explored.
6. Sort every complete route by length and keep the shortest 3.

**Note:** this checks every path, so it guarantees the best answers,
but is slow on large mazes (keep maze size to about 20x20 or
smaller). Real systems like Google Maps use smarter algorithms (such
as Dijkstra's algorithm or A*) that skip checking most roads, so
they stay fast on huge maps.
