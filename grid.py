class Grid:
    def __init__(self, width, height, size):
        self.size = size
        self.cols = int(width // size) + 1
        self.rows = int(height // size) + 1
        self.cells = {}

    def clear(self):
        """Empties the grid for each frame"""
        self.cells.clear()

    def _cell_index(self, x, y):
        """Calculates the cell co-ordinate from position"""
        return (int(x // self.size), int(y // self.size))

    def insert(self, position, i):
        """Inserts a particles position and index into a cell for querying"""
        index = self._cell_index(*position)
        if index not in self.cells: self.cells[index] = []
        self.cells[index].append((position, i))

    def query(self, rect):
        """Query points within a rectangular area"""
        x, y, w, h = rect
        results = []

        for column in range(int(x // self.size), int((x + w) // self.size) + 1):
            for row in range(int(y // self.size), int((y + h) // self.size) + 1):
                cell = self.cells.get((column, row), [])
                for position, index in cell:
                    if x <= position[0] < x + w and y <= position[1] < y + h:
                        results.append((position, index))
        return results