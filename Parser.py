from string import ascii_lowercase as LOWERCASE


class State:
    FINISH = 0
    ERROR = 1
    START = 2
    OPCODE = 3
    DUMP = 4
    IDENTIFIER = 5
    INTEGER = 6
    STRING = 7

    """ Additional semantic states for the Preprocessor. """
    VALUE = 8   # IDENTIFIER / INTEGER / STRING
    NOT_INTEGER = 9
    NOT_STRING = 10

    """ States translated back as strings. """
    NAME = ['finish', 'error', 'start', 'opcode', 'dump',
            'identifier', 'integer', 'string', 'value',
            'not integer', 'not string']

    @staticmethod
    def name(state):
        return State.NAME[state]

    @staticmethod
    def mismatch(got, expected):
        if expected == State.VALUE:
            return False
        elif expected == State.NOT_INTEGER:
            return got == State.INTEGER
        elif expected == State.NOT_STRING:
            return got == State.STRING
        else:
            return got != expected


class Parser:
    def __init__(self):
        self.ender = ';'
        self.instruction = ''
        self.opcode = ''
        self.operand = ()

        self._index = 0
        self._state = State.START
        self._buf = ''
        self._curs = ''

        self.STATES = {
            State.START: self._start_,
            State.OPCODE: self._opcode_,
            State.DUMP: self._dump_,
            State.IDENTIFIER: self._identifier_,
            State.INTEGER: self._integer_,
            State.STRING: self._string_,
        }

        self.ESCAPE_SEQUENCES = {
            r'\n': '\n',
            r'\t': '\t',
            r'\r': '\r',
            r'\"': '"',
        }

    def parse(self, instruction):
        self.instruction = instruction + self.ender
        while self._state not in (State.ERROR, State.FINISH):
            self.next()

    def next(self):
        self._curs = self.instruction[self._index]
        self.STATES[self._state]()

    def err(self):
        return self._state == State.ERROR

    def _shift(self):
        self._index += 1

    def _buf_curs(self):
        self._buf += self._curs
        self._shift()

    def _clear_buf(self):
        self._buf = ''

    def _set_opcode(self):
        self.opcode = self._buf
        self._shift()

    def _add_operand(self):
        value = self._buf

        if self._state == State.INTEGER:
            value = int(value)
        elif self._state == State.STRING:
            for esc, seq in self.ESCAPE_SEQUENCES.items():
                value = value.replace(esc, seq)

        self.operand += ((self._state, value),)
        self._shift()

    def _start_(self):
        if self._curs.isalpha() and self._curs in LOWERCASE:
            self._buf_curs()
            self._state = State.OPCODE
        else:
            self._state = State.ERROR

    def _opcode_(self):
        if self._curs == self.ender:
            self._set_opcode()
            self._state = State.FINISH
        elif self._curs in LOWERCASE:
            self._buf_curs()
            return
        elif self._curs.isspace():
            self._set_opcode()
            self._state = State.DUMP
        else:
            self._state = State.ERROR

    def _dump_(self):
        self._clear_buf()

        if self._curs == self.ender:
            self._state = State.FINISH
        elif self._curs.isspace():
            self._buf_curs()
            return
        elif self._curs.isidentifier():
            self._buf_curs()
            self._state = State.IDENTIFIER
        elif self._curs == '-' or self._curs.isdecimal():
            self._buf_curs()
            self._state = State.INTEGER
        elif self._curs == '"':
            self._shift()
            self._state = State.STRING
        else:
            self._state = State.ERROR

    def _identifier_(self):
        if self._curs == self.ender:
            self._add_operand()
            self._state = State.FINISH
        elif self._curs.isspace():
            self._add_operand()
            self._state = State.DUMP
        elif (self._buf + self._curs).isidentifier():
            self._buf_curs()
            return
        else:
            self._state = State.ERROR

    def _integer_(self):
        if self._curs == self.ender:
            self._add_operand()
            self._state = State.FINISH
        elif self._curs.isspace():
            self._add_operand()
            self._state = State.DUMP
        elif self._curs.isdecimal():
            self._buf_curs()
            return
        else:
            self._state = State.ERROR

    def _string_(self):
        if self._curs == '"' and self._buf[-1] != '\\':
            self._add_operand()
            self._state = State.DUMP
        else:
            self._buf_curs()
            return
