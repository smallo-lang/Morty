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

        self.OPCODES = {
            'put':  (self._put_, (State.VALUE, State.IDENTIFIER)),
            'add':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'sub':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'mul':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'div':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'mod':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'gth':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'lth':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'geq':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'leq':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'eq':   (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'neq':  (self._nop_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'ini':  (self._ini_, (State.IDENTIFIER,)),
            'ins':  (self._ini_, (State.IDENTIFIER,)),
            'out':  (self._out_, (State.VALUE,)),
            'outl': (self._nop_, (State.VALUE,)),
            'nl':   (self._nop_, tuple()),
            'con':  (self._nop_, (State.VALUE, State.VALUE, State.IDENTIFIER)),
            'sti':  (self._nop_, (State.NOT_INTEGER, State.IDENTIFIER)),
            'not':  (self._nop_, (State.VALUE, State.IDENTIFIER)),
            'and':  (self._nop_, (State.VALUE, State.VALUE, State.IDENTIFIER)),
            'or':   (self._nop_, (State.VALUE, State.VALUE, State.IDENTIFIER)),
            'jump': (self._jump_, (State.IDENTIFIER,)),
            'jmpt': (self._nop_, (State.IDENTIFIER, State.IDENTIFIER)),
            'jmpf': (self._nop_, (State.IDENTIFIER, State.IDENTIFIER)),
            'br':   (self._jump_, (State.IDENTIFIER,)),
            'brt':  (self._nop_, (State.IDENTIFIER, State.IDENTIFIER)),
            'brf':  (self._nop_, (State.IDENTIFIER, State.IDENTIFIER)),
            'back': (self._nop_, tuple()),
            'err':  (self._nop_, (State.NOT_INTEGER, State.NOT_STRING)),
            'end':  (self._end_, tuple()),
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

        info = self.OPCODES.get(instruction.opcode)
        if info is None:
            self._error(f'unknown opcode: {instruction.opcode}')
            return

        opcode_method, operand_types = info
        if len(instruction.operand) != len(operand_types):
            self._error(f'invalid operand length: {line}')
            return

        for operand_item, expected_operand_type in \
                zip(instruction.operand, operand_types):
            operand_type, operand_value = operand_item
            if State.mismatch(operand_type, expected_operand_type):
                self._error(
                    f'invalid operand type {operand_value} ' +
                    f'in instruction {line}\n' +
                    f'expected {State.name(expected_operand_type)}\n' +
                    f'got {State.name(operand_type)}')
                return

        self._record(instruction.operand)
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
    def _nop_(self, _):
        pass

    def _put_(self, instruction):
        value, name = instruction.operand
        value, name = value[1], name[1]
        self._instr(
            Op.PUSH, self._get_literal_as_i32(value),
            Op.POP, self._get_literal_as_i32(name))

    def _ini_(self, instruction):
        name = instruction.operand[0][1]
        self._instr(
            Op.INI,
            Op.POP, self._get_literal_as_i32(name))

    def _out_(self, instruction):
        name = instruction.operand[0][1]
        self._instr(
            Op.PUSH,
            self._get_literal_as_i32(name),
            Op.OUT)

    def _jump_(self, instruction):
        label = instruction.operand[0][1]
        self._instr(
            Op.PUSH,
            self._get_literal_as_i32(label),
            Op.JUMP)

    def _end_(self, _):
        self._instr(Op.END)
