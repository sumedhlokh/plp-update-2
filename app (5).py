"""
Maze Solver Robot - Streamlit demo
Python port of maze_solver.cpp.

Explores every possible path through a maze using backtracking, then
ranks the complete routes shortest-first and shows the TOP 3 - like
route options on a map app.

Concepts: Abstract class, Child class, Encapsulation, Stack (push/pop)

Run:  streamlit run app.py
"""
import streamlit as st

DIRS = {"UP": (-1, 0), "RIGHT": (0, 1), "DOWN": (1, 0), "LEFT": (0, -1)}

WALL, OPEN, INK = "#1F2F30", "#EAF4F2", "#0F3D3E"
ROUTE_COLORS = ["#F2A541", "#5E8C88", "#C9598B"]   # route 1, 2, 3


# =====================================================
#  MAZE  (Encapsulation: grid and goal are private)
# =====================================================
class Maze:
    def __init__(self, layout):
        self.__grid = [list(row) for row in layout]
        self.__goal = (0, 0)
        for r, row in enumerate(self.__grid):
            for c, ch in enumerate(row):
                if ch == "G":
                    self.__goal = (r, c)

    def is_wall(self, r, c):
        if r < 0 or c < 0 or r >= self.rows() or c >= self.cols():
            return True
        return self.__grid[r][c] == "#"

    def is_goal(self, pos):
        return pos == self.__goal

    def get_start(self):
        for r, row in enumerate(self.__grid):
            for c, ch in enumerate(row):
                if ch == "S":
                    return (r, c)
        return (0, 0)

    def rows(self):
        return len(self.__grid)

    def cols(self):
        return len(self.__grid[0])

    def symbol(self, r, c):
        return self.__grid[r][c]


# =====================================================
#  ROBOT  (Abstract class: cannot be created directly)
# =====================================================
class Robot:
    def __init__(self, maze):
        self._maze = maze
        self._pos = maze.get_start()
        self.cells_checked = 0

    def _next_cell(self, pos, direction):
        dr, dc = DIRS[direction]
        return (pos[0] + dr, pos[1] + dc)

    def solve(self):                    # pure virtual: HOW to search
        raise NotImplementedError

    def get_top_paths(self, k):         # pure virtual: ranked answers
        raise NotImplementedError


# =====================================================
#  SMART ROBOT  (Child class)
#  Explores every path using backtracking, keeps ALL complete
#  routes, then ranks them shortest-first.
# =====================================================
class SmartRobot(Robot):
    def __init__(self, maze):
        super().__init__(maze)
        self.__visited = {self._pos}
        self.__current_path = [self._pos]
        self.__all_paths = []

    def __explore(self):
        current = self.__current_path[-1]

        if self._maze.is_goal(current):
            self.__all_paths.append(list(self.__current_path))   # save this complete route
            return

        for d in ("UP", "RIGHT", "DOWN", "LEFT"):
            n = self._next_cell(current, d)
            self.cells_checked += 1
            if not self._maze.is_wall(n[0], n[1]) and n not in self.__visited:
                self.__visited.add(n)
                self.__current_path.append(n)      # PUSH: step into this cell
                self.__explore()                    # go deeper (recursion = a stack)
                self.__current_path.pop()           # POP: undo the step (backtrack)
                self.__visited.remove(n)            # un-mark, so other routes can reuse it

    def solve(self):
        self.__explore()
        self.__all_paths.sort(key=len)      # rank shortest first, like a map app

    def get_top_paths(self, k):
        return self.__all_paths[:k]


# =====================================================
#  DRAWING HELPERS
# =====================================================
PRESETS = {
    "Maze 1 - small": [
        "#########",
        "#S..#...#",
        "#.#.#.#.#",
        "#.#...#G#",
        "#########",
    ],
    "Maze 2 - multiple routes": [
        "###########",
        "#S........#",
        "#.##.###.##",
        "#....#....#",
        "#.##.#.##.#",
        "#....#....#",
        "##.#####.##",
        "#.........#",
        "#.##.#.##.#",
        "#....#...G#",
        "###########",
    ],
    "Custom (edit below)": [
        "#########",
        "#S......#",
        "#.#####.#",
        "#......G#",
        "#########",
    ],
}

MAX_CELLS = 20 * 20   # safety limit: exhaustive search is slow on big mazes


def parse_layout(text):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return None, "The maze is empty."
    if len({len(ln) for ln in lines}) != 1:
        return None, "All rows must have the same length."
    joined = "".join(lines)
    if set(joined) - set("#.SG"):
        return None, "Use only  #  .  S  G  characters."
    if joined.count("S") != 1 or joined.count("G") != 1:
        return None, "The maze needs exactly one S and one G."
    if len(lines) * len(lines[0]) > MAX_CELLS:
        return None, f"Maze is too big for exhaustive search (max {MAX_CELLS} cells, e.g. 20x20)."
    return lines, None


def cell_html(bg, txt="", fg="#22323A", size=32):
    return (f"<div style='width:{size}px;height:{size}px;background:{bg};color:{fg};display:flex;"
            f"align-items:center;justify-content:center;font-weight:700;"
            f"border-radius:4px;font-size:{max(10, size // 2)}px'>{txt}</div>")


def maze_html(maze, path, color, size=32):
    on_path = set(path)
    rows = []
    for r in range(maze.rows()):
        cells = []
        for c in range(maze.cols()):
            sym = maze.symbol(r, c)
            if sym == "#":
                cells.append(cell_html(WALL, size=size))
            elif sym in "SG":
                cells.append(cell_html(INK, sym if size >= 16 else "", "#FFFFFF", size=size))
            elif (r, c) in on_path:
                cells.append(cell_html(color, size=size))
            else:
                cells.append(cell_html(OPEN, size=size))
        rows.append("<div style='display:flex;gap:2px'>" + "".join(cells) + "</div>")
    return "<div style='display:flex;flex-direction:column;gap:2px'>" + "".join(rows) + "</div>"


# =====================================================
#  STREAMLIT PAGE
# =====================================================
st.set_page_config(page_title="Maze Solver - Top 3 Routes", page_icon="🤖", layout="wide")
st.title("🤖 Maze Solver Robot - Top 3 Routes")
st.caption("Explores every possible route, then ranks the shortest 3 - like route options on a map app.")

with st.sidebar:
    st.header("Settings")
    choice = st.selectbox("Choose a maze", list(PRESETS))
    text = st.text_area(
        "Maze layout (# wall, . open, S start, G goal)",
        "\n".join(PRESETS[choice]),
        height=220,
    )
    st.markdown(f"Max maze size: 20 x 20 (exhaustive search gets slow on bigger maps)")

layout, error = parse_layout(text)
if error:
    st.error(error)
    st.stop()

maze = Maze(layout)
robot = SmartRobot(maze)
robot.solve()
top_paths = robot.get_top_paths(3)

m1, m2 = st.columns(2)
m1.metric("Routes found", "Yes ✅" if top_paths else "No ❌")
m2.metric("Cells checked", robot.cells_checked)

if not top_paths:
    st.warning("No path exists between S and G in this maze.")
else:
    cols = st.columns(len(top_paths))
    for i, (col, path) in enumerate(zip(cols, top_paths)):
        with col:
            st.subheader(f"Route {i + 1}")
            st.caption(f"{len(path)} cells")
            st.markdown(maze_html(maze, path, ROUTE_COLORS[i]), unsafe_allow_html=True)

with st.expander("How does it work?"):
    st.markdown("""
The robot explores the maze using **backtracking** (trying every possible branch):

1. Step into a cell and **push** it onto the current path.
2. Try every direction (up, right, down, left) from there, one at a time, by exploring each recursively.
3. If it reaches `G`, save this complete route.
4. Either way, **pop** that cell off the path afterwards and un-mark it as visited,
   so other routes can reuse it.
5. Repeat until every possible path has been tried.
6. Finally, sort every complete route found by length, and keep the top 3 shortest -
   just like a map app shows a few route options ranked by travel time.

**OOP used:** `Robot` is an abstract class (`solve` and `get_top_paths` are not
implemented there), `SmartRobot` is its child class, `Maze` keeps its grid
private (encapsulation), and the current path is built and undone like a
**stack** (push / pop).
""")
