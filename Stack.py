class Stack:
    def __init__(self):
        self.mem = []

    def __len__(self):
        return len(self.mem)

    def __str__(self):
        return str(self.mem)

    def __repr__(self):
        return str(self)

    def push(self, item):
        self.mem.append(item)

    def pop(self):
        return self.mem.pop(-1)

    def peek(self):
        return self.mem[-1]

    def empty(self):
        return len(self.mem) == 0

    def clear(self):
        self.mem = []
