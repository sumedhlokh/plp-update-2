// ======================================================================
//  Maze Solver Robot - shows the TOP 3 BEST (shortest) paths
//  Explores every possible route through the maze, then ranks the
//  complete routes shortest-first, like route options on a map app.
//
//  Concepts covered: Abstract class, Child class, Encapsulation,
//                     Stack operations (push / pop, via recursion)
//
//  Compile:  g++ -std=c++11 maze_solver.cpp -o maze_solver
//  Run:      ./maze_solver        (or maze_solver.exe on Windows)
// ======================================================================
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

struct Position { int row, col; };

// ---------------- MAZE : holds the map (Encapsulation) ----------------
class Maze {
private:
    vector<string> grid;      // private: map data hidden from outside
    Position goal;

public:
    Maze(vector<string> g) {
        grid = g;
        for (int r = 0; r < (int)grid.size(); r++)
            for (int c = 0; c < (int)grid[r].size(); c++)
                if (grid[r][c] == 'G') goal = {r, c};
    }

    bool isWall(int r, int c) {
        if (r < 0 || c < 0 || r >= (int)grid.size() || c >= (int)grid[0].size())
            return true;                    // outside the maze = treat as wall
        return grid[r][c] == '#';
    }

    bool isGoal(Position p) {
        return p.row == goal.row && p.col == goal.col;
    }

    Position getStart() {
        for (int r = 0; r < (int)grid.size(); r++)
            for (int c = 0; c < (int)grid[r].size(); c++)
                if (grid[r][c] == 'S') return {r, c};
        return {0, 0};
    }

    int rows() { return grid.size(); }
    int cols() { return grid[0].size(); }

    // label lets us mark route 1, 2, 3 with different characters
    void display(vector<Position> path, char label) {
        vector<string> copy = grid;
        for (auto p : path)
            if (copy[p.row][p.col] == '.') copy[p.row][p.col] = label;
        for (auto row : copy) cout << row << "\n";
    }
};

// ---------------- ROBOT : abstract class ----------------
class Robot {
protected:
    Maze* maze;
    Position pos;
    int cellsChecked = 0;     // how much work the robot did

    Position nextCell(Position p, int dir) {
        if (dir == 0) return {p.row - 1, p.col};   // UP
        if (dir == 1) return {p.row, p.col + 1};   // RIGHT
        if (dir == 2) return {p.row + 1, p.col};   // DOWN
        return {p.row, p.col - 1};                 // LEFT
    }

public:
    Robot(Maze* m) { maze = m; pos = m->getStart(); }
    virtual ~Robot() {}

    virtual void solve() = 0;                            // pure virtual: HOW to search
    virtual vector<vector<Position>> getTopPaths(int k) = 0;  // pure virtual: ranked answers

    int getCellsChecked() { return cellsChecked; }
};

// ======================================================================
//  SmartRobot (child class)
//  Explores EVERY possible path from S to G using backtracking, keeps
//  every complete route found, then ranks them shortest-first.
// ======================================================================
class SmartRobot : public Robot {
private:
    vector<vector<bool>> visited;
    vector<Position> currentPath;        // the path being built now (acts as a stack)
    vector<vector<Position>> allPaths;   // every complete route found

    // Tries every direction from the last cell in currentPath.
    // Calling itself (recursion) behaves like a stack: each call waits
    // for the deeper call to finish before it continues.
    void explore() {
        Position current = currentPath.back();

        if (maze->isGoal(current)) {
            allPaths.push_back(currentPath);   // save a copy of this complete route
            return;
        }

        for (int dir = 0; dir < 4; dir++) {
            Position n = nextCell(current, dir);
            cellsChecked++;
            if (!maze->isWall(n.row, n.col) && !visited[n.row][n.col]) {
                visited[n.row][n.col] = true;
                currentPath.push_back(n);        // PUSH: step into this cell
                explore();                        // go deeper, try all of ITS options
                currentPath.pop_back();           // POP: undo the step (backtrack)
                visited[n.row][n.col] = false;    // un-mark, so other routes can reuse it
            }
        }
    }

public:
    SmartRobot(Maze* m) : Robot(m) {
        visited.assign(m->rows(), vector<bool>(m->cols(), false));
    }

    void solve() override {
        currentPath.push_back(pos);
        visited[pos.row][pos.col] = true;
        explore();

        // Rank every route found, shortest first (like map apps rank routes)
        sort(allPaths.begin(), allPaths.end(),
             [](const vector<Position>& a, const vector<Position>& b) {
                 return a.size() < b.size();
             });
    }

    vector<vector<Position>> getTopPaths(int k) override {
        vector<vector<Position>> top;
        for (int i = 0; i < (int)allPaths.size() && i < k; i++)
            top.push_back(allPaths[i]);
        return top;
    }
};

// ---------------- MAIN ----------------
int main() {
    vector<string> layout = {
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
        "###########"
    };

    Maze maze(layout);
    SmartRobot robot(&maze);

    robot.solve();
    vector<vector<Position>> top3 = robot.getTopPaths(3);

    cout << "Total cells checked: " << robot.getCellsChecked() << "\n\n";

    if (top3.empty()) {
        cout << "No path found.\n";
        return 0;
    }

    char labels[3] = {'1', '2', '3'};
    for (int i = 0; i < (int)top3.size(); i++) {
        cout << "Route " << (i + 1) << "  (length: " << top3[i].size() << " cells)\n";
        maze.display(top3[i], labels[i]);
        cout << "\n";
    }

    return 0;
}
