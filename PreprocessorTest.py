from unittest import TestCase

from Preprocessor import Preprocessor
from Op import Op
import make
from make import i32


class PreprocessorTest(TestCase):
    def setUp(self) -> None:
        self.pre = Preprocessor()

    def test_works_for_empty_code(self):
        self._assert_results_match(
            inp=[],
            mem=[],
            ins=make.ins()
        )

    def test_works_for_multiple_instructions(self):
        self._assert_results_match(
            inp=['ini n', 'out n'],
            mem=[0],
            ins=make.ins(Op.INI, Op.POP, i32(0),
                 Op.PUSH, i32(0), Op.OUT)
        )

    def test_works_for_label_and_instruction(self):
        self._assert_results_match(
            inp=['jump exit', 'exit:'],
            mem=[6],
            ins=make.ins(Op.PUSH, i32(0), Op.JUMP)
        )

    """ Destructive tests. """
    def test_sets_err_flag_on_duplicate_labels(self):
        self.pre.process(['start:', 'end', 'start:', 'add 1 2 s', 'back'])
        self._assert_err_flag_set()

    def test_catches_invalid_labels(self):
        self.pre.process(['1invalid:'])
        self._assert_err_flag_set()

    """ Opcode-Related tests. """
    def test_put_(self):
        self._assert_results_match(
            inp=['put 1 a', 'put a b'],
            mem=[1, 0, 0],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.POP, i32(1),
                Op.PUSH, i32(1),
                Op.POP, i32(2))
        )

    """ Utility methods. """
    def _assert_results_match(self, inp, mem, ins):
        self.pre.process(inp)
        self.assertEqual(mem, self.pre.memory)
        self.assertEqual(ins, self.pre.instructions)

    def _assert_err_flag_set(self):
        self.assertTrue(self.pre.err)

    def _assert_err_flag_not_set(self):
        self.assertFalse(self.pre.err)

    """
    def test_works_for_good_code(self):
        self.pre.process([
            'inn age',
            'lth age 18 b',
            'jmpf b exit',
            'out "You are a minor"',
            'exit:',
            'end',
        ])
        self.assertEqual([
            'inn age',
            'lth age 18 b',
            'jmpf b exit',
            'out "You are a minor"',
            'end',
        ], self.pre.instructions)
        self.assertEqual({'exit': 4}, self.pre.labels)
        self._assert_err_flag_not_set()
    """
