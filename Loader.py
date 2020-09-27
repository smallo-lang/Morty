from pathlib import Path
import re

from Stack import Stack


class Loader:
    def __init__(self):
        self.current = Stack()
        self.code = []
        self.err = ''
        self.included = set()

    def load(self, src):
        self.include(Path(src).absolute())

    def include(self, path):
        if path in self.included:
            return

        self.included.add(path)
        self.current.push(path)

        if not path.exists():
            self.err = f'path {path} does not exist'
            return

        if not path.is_file():
            self.err = f'path {path} is not a file'
            return

        for line in self._read_lines(path):
            if self.err:
                return

            clean_line = self._clean_line(line)

            if not clean_line:
                continue
            elif self._is_include(clean_line):
                if self._is_valid_include(clean_line):
                    self.include(self._include_path(clean_line))
                else:
                    self.err = f'invalid include {clean_line} in {path}'
            else:
                self.code.append(clean_line)

        self.current.pop()

    @ staticmethod
    def _read_lines(src):
        with open(src) as file:
            return file.readlines()

    @staticmethod
    def _clean_line(line):
        return line.split('@')[0].strip()

    @staticmethod
    def _is_include(line):
        return line[0] == '>'

    @staticmethod
    def _is_valid_include(line):
        return bool(re.search('>".+"', line))

    def _include_path(self, line):
        path = Path(line[2:-1])
        current = self.current.peek()
        return path if path.is_absolute() else current.parent / path
