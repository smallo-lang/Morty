from unittest import TestCase

from morty.Parser import Parser, State


class ParserTest(TestCase):
    def test_can_parse_instruction_with_no_operand(self):
        self._parse_and_check_result('end', 'end', ())

    def test_can_parse_instruction_with_one_label_operand(self):
        self._parse_and_check_result(
            'jump start',
            'jump', ((State.IDENTIFIER, 'start'),)
        )

    def test_can_parse_instruction_with_one_int_operand(self):
        self._parse_and_check_result(
            'put 1',
            'put', ((State.INTEGER, 1),)
        )

    def test_can_parse_instruction_with_negative_int(self):
        self._parse_and_check_result(
            'put -2020 year',
            'put', ((State.INTEGER, -2020), (State.IDENTIFIER, 'year'))
        )

    def test_can_parse_instruction_with_one_str_operand(self):
        self._parse_and_check_result(
            'put "I love SmallO"',
            'put', ((State.STRING, 'I love SmallO'),)
        )

    def test_can_parse_instruction_with_newline_in_str(self):
        self._parse_and_check_result(
            r'put "I love SmallO\n"',
            'put', ((State.STRING, 'I love SmallO\n'),)
        )

    def test_can_parse_instruction_with_quote_in_str(self):
        self._parse_and_check_result(
            r'put "He said: \"I love SmallO\""',
            'put', ((State.STRING, 'He said: "I love SmallO"'),)
        )

    def test_can_parse_complex_instruction(self):
        self._parse_and_check_result(
            'add "one" 2 var',
            'add', (
                (State.STRING, 'one'),
                (State.INTEGER, 2),
                (State.IDENTIFIER, 'var')
            )
        )

    def _parse_and_check_result(self, instruction, opcode, operand):
        self.parser = Parser()
        self.parser.parse(instruction)
        self.assertEqual(opcode, self.parser.opcode)
        self.assertEqual(operand, self.parser.operand)
