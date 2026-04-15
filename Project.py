import tkinter as tk
import heapq
from collections import deque
import random

CELL = 40
ROWS = 10
COLS = 15

class Node:
    def __init__(self, r, c):
        self.r = r
        self.c = c

    def __eq__(self, other):
        return self.r == other.r and self.c == other.c

    def __hash__(self):
        return hash((self.r, self.c))

    def __lt__(self, other):
        return False


def heuristic(a, b):
    return abs(a.r - b.r) + abs(a.c - b.c)

# ---------------- BFS ----------------
def bfs(grid, start, goal):
    queue = deque([start])
    visited = {start}
    parent = {}
    nodes = 0

    while queue:
        current = queue.popleft()
        nodes += 1

        if current == goal:
            path = []
            temp = current
            while temp in parent:
                path.append(temp)
                temp = parent[temp]
            path.append(start)
            return path[::-1], nodes

        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = current.r+dr, current.c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and grid[nr][nc] != 0:
                neighbor = Node(nr,nc)
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

    return [], nodes


# ---------------- A* (FIXED) ----------------
def astar(grid, start, goal):
    pq = []
    heapq.heappush(pq, (0, start))
    parent = {}
    g = {start: 0}
    nodes = 0

    while pq:
        _, current = heapq.heappop(pq)
        nodes += 1

        if current == goal:
            cost = g[current]  # ✅ FIXED

            path = []
            temp = current
            while temp in parent:
                path.append(temp)
                temp = parent[temp]
            path.append(start)

            return path[::-1], cost, nodes

        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = current.r+dr, current.c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and grid[nr][nc] != 0:
                neighbor = Node(nr,nc)
                temp_cost = g[current] + grid[nr][nc]

                if neighbor not in g or temp_cost < g[neighbor]:
                    g[neighbor] = temp_cost
                    f = temp_cost + heuristic(neighbor, goal)
                    heapq.heappush(pq,(f,neighbor))
                    parent[neighbor] = current

    return [], 0, nodes


# ---------------- GUI ----------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🚑 Smart Emergency Route System ")
        self.root.configure(bg="#ecf0f1")

        self.canvas = tk.Canvas(root, width=COLS*CELL, height=ROWS*CELL, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=5, padx=10, pady=10)

        self.grid = [[random.choice([1,2,3]) for _ in range(COLS)] for _ in range(ROWS)]

        self.start = None
        self.goal = None
        self.current_path = []
        self.ambulance = None

        self.canvas.bind("<Button-1>", self.click)

        tk.Button(root, text="Run BFS", width=12, bg="#3498db", fg="white",
                  command=self.run_bfs).grid(row=1,column=0)

        tk.Button(root, text="Run A*", width=12, bg="#2ecc71", fg="white",
                  command=self.run_astar).grid(row=1,column=1)

        tk.Button(root, text="Block Road", width=12, bg="#e74c3c", fg="white",
                  command=self.block).grid(row=1,column=2)

        tk.Button(root, text="Reset", width=12, bg="#34495e", fg="white",
                  command=self.reset).grid(row=1,column=3)

        self.stats = tk.Label(root, text="", font=("Arial", 11, "bold"), bg="#ecf0f1")
        self.stats.grid(row=2,column=0,columnspan=5)

        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for i in range(ROWS):
            for j in range(COLS):
                x1,y1 = j*CELL, i*CELL
                x2,y2 = x1+CELL, y1+CELL

                val = self.grid[i][j]
                color = "black" if val==0 else "#2ecc71" if val==1 else "#f1c40f" if val==2 else "#e67e22"

                self.canvas.create_rectangle(x1,y1,x2,y2, fill=color, outline="#bdc3c7")

                if val != 0:
                    self.canvas.create_text(x1+20, y1+20, text=str(val),
                                            fill="black", font=("Arial", 10, "bold"))

        # Path (no blinking)
        for node in self.current_path:
            self.draw_cell(node, "#1abc9c")

        if self.start:
            self.draw_cell(self.start, "#2980b9")
        if self.goal:
            self.draw_cell(self.goal, "#c0392b")

    def draw_cell(self, node, color):
        x1,y1 = node.c*CELL, node.r*CELL
        x2,y2 = x1+CELL, y1+CELL
        self.canvas.create_rectangle(x1,y1,x2,y2, fill=color)

    def click(self, e):
        c = e.x//CELL
        r = e.y//CELL
        node = Node(r,c)

        if not self.start:
            self.start = node
        else:
            self.goal = node

        self.draw()

    def move_ambulance(self, path, i=0):
        if i >= len(path):
            return

        node = path[i]
        x = node.c*CELL + CELL//2
        y = node.r*CELL + CELL//2

        if self.ambulance:
            self.canvas.delete(self.ambulance)

        self.ambulance = self.canvas.create_oval(
            x-8, y-8, x+8, y+8,
            fill="red"
        )

        self.root.after(120, lambda: self.move_ambulance(path, i+1))

    def run_bfs(self):
        if not self.start or not self.goal:
            self.stats.config(text="⚠️ Select Start & Goal")
            return

        path, nodes = bfs(self.grid, self.start, self.goal)
        self.current_path = path
        self.draw()
        self.move_ambulance(path)

        self.stats.config(text=f"BFS → Steps: {len(path)} | Nodes: {nodes}")

    def run_astar(self):
        if not self.start or not self.goal:
            self.stats.config(text="⚠️ Select Start & Goal")
            return

        path, cost, nodes = astar(self.grid, self.start, self.goal)
        self.current_path = path
        self.draw()
        self.move_ambulance(path)

        self.stats.config(text=f"A* → Cost: {cost} | Steps: {len(path)} | Nodes: {nodes}")

    def block(self):
        for _ in range(10):
            r = random.randint(0,ROWS-1)
            c = random.randint(0,COLS-1)
            self.grid[r][c] = 0
        self.draw()

    def reset(self):
        self.grid = [[random.choice([1,2,3]) for _ in range(COLS)] for _ in range(ROWS)]
        self.start = None
        self.goal = None
        self.current_path = []
        self.draw()
        self.stats.config(text="Reset Done")


root = tk.Tk()
app = App(root)
root.mainloop()