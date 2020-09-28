from unittest import TestCase

from .Preprocessor import Preprocessor
from .Op import Op
from . import make
from .make import i32


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
            mem=[None],
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

    def test_sets_err_flag_on_unknown_opcode(self):
        self.pre.process(['outln "hello world"'])
        self._assert_err_flag_set()

    def test_sets_err_flag_on_invalid_operand_length(self):
        self.pre.process(['put 1'])
        self._assert_err_flag_set()
        self.pre = Preprocessor()
        self.pre.process(['end 1'])
        self._assert_err_flag_set()

    def test_sets_err_flag_on_invalid_operand_type(self):
        self.pre.process(['put 1 1'])
        self._assert_err_flag_set()

    """ Opcode-related tests. """
    def test_put_(self):
        self._assert_results_match(
            inp=['put 1 a', 'put a b'],
            mem=[1, None, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.POP, i32(1),
                Op.PUSH, i32(1),
                Op.POP, i32(2))
        )

    def test_add_(self):
        self._assert_results_match(
            inp=['add 1 a b'],
            mem=[1, None, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.ADD,
                Op.POP, i32(2))
        )

    def test_sub_(self):
        self._assert_results_match(
            inp=['sub a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.SUB,
                Op.POP, i32(2))
        )

    def test_mul_(self):
        self._assert_results_match(
            inp=['mul a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.MUL,
                Op.POP, i32(2))
        )

    def test_div_(self):
        self._assert_results_match(
            inp=['div a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.DIV,
                Op.POP, i32(2))
        )

    def test_mod_(self):
        self._assert_results_match(
            inp=['mod a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.MOD,
                Op.POP, i32(2))
        )

    def test_gth_(self):
        self._assert_results_match(
            inp=['gth a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.GTH,
                Op.POP, i32(2))
        )

    def test_lth_(self):
        self._assert_results_match(
            inp=['lth a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.LTH,
                Op.POP, i32(2))
        )

    def test_geq_(self):
        self._assert_results_match(
            inp=['geq a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.GEQ,
                Op.POP, i32(2))
        )

    def test_leq_(self):
        self._assert_results_match(
            inp=['leq a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.LEQ,
                Op.POP, i32(2))
        )

    def test_eq_(self):
        self._assert_results_match(
            inp=['eq a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.EQ,
                Op.POP, i32(2))
        )

    def test_neq_(self):
        self._assert_results_match(
            inp=['neq a 2 b'],
            mem=[None, 2, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.NEQ,
                Op.POP, i32(2))
        )

    def test_ini_(self):
        self._assert_results_match(
            inp=['ini age'],
            mem=[None],
            ins=make.ins(
                Op.INI,
                Op.POP, i32(0))
        )

    def test_ins_(self):
        self._assert_results_match(
            inp=['ins name'],
            mem=[None],
            ins=make.ins(
                Op.INS,
                Op.POP, i32(0))
        )

    def test_out_(self):
        self._assert_results_match(
            inp=['out age'],
            mem=[None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.OUT)
        )

    def test_outl_(self):
        self._assert_results_match(
            inp=['outl age'],
            mem=[None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.OUT,
                Op.NL)
        )

    def test_nl_(self):
        self._assert_results_match(
            inp=['nl'],
            mem=[],
            ins=make.ins(Op.NL)
        )

    def test_jump_(self):
        self._assert_results_match(
            inp=['jump main'],
            mem=[None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.JUMP)
        )

    def test_end_(self):
        self._assert_results_match(
            inp=['end'],
            mem=[],
            ins=make.ins(Op.END)
        )

    """ Utility methods. """
    def _assert_results_match(self, inp, mem, ins):
        self.pre.process(inp)
        self._assert_err_flag_not_set()
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
