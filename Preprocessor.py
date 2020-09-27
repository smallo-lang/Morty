import re

from Parser import Parser, State
from Op import Op
from make import i32


class Preprocessor:
    def __init__(self):
        self.memory = []
        self.instructions = b''
        self.literals = {}
        self.memory_counter = 0
        self.labels = set()
        self.err = ''

        self.INFO = {
            'put': (self._put_, 2),
            'add': 3,
            'sub': 3,
            'mul': 3,
            'div': 3,
            'mod': 3,
            'gth': 3,
            'lth': 3,
            'geq': 3,
            'leq': 3,
            'eq': 3,
            'neq': 3,
            'ini': (self._ini_, 1),
            'ins': 1,
            'out': (self._out_, 1),
            'outl': 1,
            'nl': 0,
            'con': 3,
            'sti': 2,
            'not': 2,
            'and': 3,
            'or': 3,
            'jump': (self._jump_, 1),
            'jmpt': 2,
            'jmpf': 2,
            'br': 1,
            'brt': 2,
            'brf': 2,
            'back': 0,
            'err': 2,
            'end': (self._end_, 0),
        }

    def process(self, code):
        code.append('end')
        for line in code:
            if self.err:
                break

            if self._is_label(line):
                self._check_and_add_label(line)
            else:
                self._check_and_add_instruction(line)

    def _error(self, msg):
        self.err = msg

    def _check_and_add_label(self, line):
        label = self._parse_label_name(line)

        if not self._is_valid_label(label):
            self._error(f'invalid label: {label}')
        elif label in self.labels:
            self._error(f'duplicate labels detected: {line}')
        else:
            self.labels.add(label)
            self._record_literal_if_not_known(label, is_id=True)
            self._set_memory_for_literal(label, len(self.instructions))

    def _record_literal_if_not_known(self, literal, is_id=False):
        if literal not in self.literals:
            self.memory.append(0 if is_id else literal)
            self.literals[literal] = self.memory_counter
            self.memory_counter += 1

    def _set_memory_for_literal(self, literal, value):
        self.memory[self._get_literal(literal)] = value

    def _get_literal(self, name):
        return self.literals[name]

    def _get_literal_as_i32(self, name):
        return i32(self._get_literal(name))

    def _check_and_add_instruction(self, line):
        instruction = Parser()
        instruction.parse(line)
        if instruction.err():
            self._error(f'failed to parse instruction: {line}')
            return

        info = self.INFO.get(instruction.opcode)
        if info is None:
            self._error(f'unknown opcode: {instruction.opcode}')
            return

        opcode_method, expected_operand_length = info
        if len(instruction.operand) != expected_operand_length:
            self._error(f'invalid operand length: {line}')
            return

        opcode_method(instruction)

    def _record(self, operand):
        for state, value in operand:
            if state == State.IDENTIFIER:
                self._record_literal_if_not_known(value, is_id=True)
            else:
                self._record_literal_if_not_known(value)

    def _instr(self, *bts):
        for each in bts:
            self.instructions += each

    @staticmethod
    def _is_label(line):
        return line[-1] == ':'

    @staticmethod
    def _is_valid_label(label):
        return bool(re.search('^[_a-zA-Z][_a-zA-Z0-9]*$', label))

    @staticmethod
    def _parse_label_name(line):
        return line[:-1]

    """ Opcode-Specific Methods. """
    def _put_(self, instruction):
        value, name = instruction.operand
        if name[0] != State.IDENTIFIER:
            self._error(f'[put] expected a name instead of {name[0]}')

        self._record(instruction.operand)
        value, name = value[1], name[1]
        self._instr(
            Op.PUSH, self._get_literal_as_i32(value),
            Op.POP, self._get_literal_as_i32(name))

    def _ini_(self, instruction):
        name = instruction.operand[0][1]
        if instruction.operand[0][0] != State.IDENTIFIER:
            self._error(f'[ini] expected a name instead of {name}')
            return

        self._record(instruction.operand)
        self._instr(
            Op.INI,
            Op.POP, self._get_literal_as_i32(name))

    def _out_(self, instruction):
        name = instruction.operand[0][1]
        if instruction.operand[0][0] != State.IDENTIFIER:
            self._error(f'[out] expected a name instead of {name}')
            return

        self._record(instruction.operand)
        self._instr(
            Op.PUSH,
            self._get_literal_as_i32(name),
            Op.OUT)

    def _jump_(self, instruction):
        label = instruction.operand[0][1]
        if instruction.operand[0][0] != State.IDENTIFIER:
            self._error(f'[jump] expected a label instead of {label}')
            return

        self._record(instruction.operand)
        self._instr(
            Op.PUSH,
            self._get_literal_as_i32(label),
            Op.JUMP)

    def _end_(self, _):
        self._instr(Op.END)
