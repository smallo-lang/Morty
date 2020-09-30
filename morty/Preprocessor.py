import re

from .Parser import Parser, State
from .Op import Op
from .make import i32


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
            'add':  (self._add_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'sub':  (self._sub_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'mul':  (self._mul_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'div':  (self._div_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'mod':  (self._mod_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'gth':  (self._gth_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'lth':  (self._lth_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'geq':  (self._geq_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'leq':  (self._leq_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'eq':   (self._eq_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'neq':  (self._neq_, (State.NOT_STRING, State.NOT_STRING, State.IDENTIFIER)),
            'ini':  (self._ini_, (State.IDENTIFIER,)),
            'ins':  (self._ins_, (State.IDENTIFIER,)),
            'out':  (self._out_, (State.VALUE,)),
            'outl': (self._outl_, (State.VALUE,)),
            'nl':   (self._nl_, tuple()),
            'con':  (self._con_, (State.VALUE, State.VALUE, State.IDENTIFIER)),
            'sti':  (self._sti_, (State.NOT_INTEGER, State.IDENTIFIER)),
            'not':  (self._not_, (State.VALUE, State.IDENTIFIER)),
            'and':  (self._and_, (State.VALUE, State.VALUE, State.IDENTIFIER)),
            'or':   (self._or_, (State.VALUE, State.VALUE, State.IDENTIFIER)),
            'jump': (self._jump_, (State.IDENTIFIER,)),
            'jmpt': (self._jmpt_, (State.IDENTIFIER, State.IDENTIFIER)),
            'jmpf': (self._jmpf_, (State.IDENTIFIER, State.IDENTIFIER)),
            'br':   (self._br_, (State.IDENTIFIER,)),
            'brt':  (self._brt_, (State.IDENTIFIER, State.IDENTIFIER)),
            'brf':  (self._brf_, (State.IDENTIFIER, State.IDENTIFIER)),
            'back': (self._back_, tuple()),
            'err':  (self._err_, (State.NOT_INTEGER, State.NOT_STRING)),
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
            self.memory.append(None if is_id else literal)
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
        opcode_method(self._unpack(instruction.operand))

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

    @staticmethod
    def _unpack(operand):
        return tuple([value for _, value in operand])

    """ Abstracting common opcode practices. """
    def _unary_operation(self, operand, operation):
        x, y = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(x),
            operation,
            Op.POP, self._get_literal_as_i32(y))

    def _binary_operation(self, operand, operation):
        x, y, z = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(x),
            Op.PUSH, self._get_literal_as_i32(y),
            operation,
            Op.POP, self._get_literal_as_i32(z))

    """ Opcode-specific methods. """
    def _nop_(self, _):
        pass

    def _put_(self, operand):
        value, name = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(value),
            Op.POP, self._get_literal_as_i32(name))

    def _add_(self, operand):
        self._binary_operation(operand, Op.ADD)

    def _sub_(self, operand):
        self._binary_operation(operand, Op.SUB)

    def _mul_(self, operand):
        self._binary_operation(operand, Op.MUL)

    def _div_(self, operand):
        self._binary_operation(operand, Op.DIV)

    def _mod_(self, operand):
        self._binary_operation(operand, Op.MOD)

    def _gth_(self, operand):
        self._binary_operation(operand, Op.GTH)

    def _lth_(self, operand):
        self._binary_operation(operand, Op.LTH)

    def _geq_(self, operand):
        self._binary_operation(operand, Op.GEQ)

    def _leq_(self, operand):
        self._binary_operation(operand, Op.LEQ)

    def _eq_(self, operand):
        self._binary_operation(operand, Op.EQ)

    def _neq_(self, operand):
        self._binary_operation(operand, Op.NEQ)

    def _ini_(self, operand):
        name = operand[0]
        self._instr(
            Op.INI,
            Op.POP, self._get_literal_as_i32(name))

    def _ins_(self, operand):
        name = operand[0]
        self._instr(
            Op.INS,
            Op.POP, self._get_literal_as_i32(name))

    def _out_(self, operand):
        name = operand[0]
        self._instr(
            Op.PUSH, self._get_literal_as_i32(name),
            Op.OUT)

    def _outl_(self, operand):
        name = operand[0]
        self._instr(
            Op.PUSH, self._get_literal_as_i32(name),
            Op.OUT,
            Op.NL)

    def _nl_(self, _):
        self._instr(Op.NL)

    def _con_(self, operand):
        self._binary_operation(operand, Op.CON)

    def _sti_(self, operand):
        self._unary_operation(operand, Op.STI)

    def _not_(self, operand):
        self._unary_operation(operand, Op.NOT)

    def _and_(self, operand):
        self._binary_operation(operand, Op.AND)

    def _or_(self, operand):
        self._binary_operation(operand, Op.OR)

    def _jump_(self, operand):
        label = operand[0]
        self._instr(
            Op.PUSH, self._get_literal_as_i32(label),
            Op.JUMP)

    def _jmpt_(self, operand):
        boolean, label = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(label),
            Op.PUSH, self._get_literal_as_i32(boolean),
            Op.JMPT)

    def _jmpf_(self, operand):
        boolean, label = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(label),
            Op.PUSH, self._get_literal_as_i32(boolean),
            Op.JMPF)

    def _br_(self, operand):
        label = operand[0]
        self._instr(
            Op.PUSH, self._get_literal_as_i32(label),
            Op.BR)

    def _brt_(self, operand):
        boolean, label = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(label),
            Op.PUSH, self._get_literal_as_i32(boolean),
            Op.BRT)

    def _brf_(self, operand):
        boolean, label = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(label),
            Op.PUSH, self._get_literal_as_i32(boolean),
            Op.BRF)

    def _back_(self, _):
        self._instr(Op.BACK)

    def _err_(self, operand):
        message, error_code = operand
        self._instr(
            Op.PUSH, self._get_literal_as_i32(message),
            Op.OUT,
            Op.PUSH, self._get_literal_as_i32(error_code),
            Op.ERR)

    def _end_(self, _):
        self._instr(Op.END)
