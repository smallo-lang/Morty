from unittest import TestCase

from morty.Preprocessor import Preprocessor
from morty.Op import Op
from morty import make
from morty.make import i32


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

    def test_con_(self):
        self._assert_results_match(
            inp=['con "hello" world message'],
            mem=['hello', None, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.CON,
                Op.POP, i32(2))
        )

    def test_sti_(self):
        self._assert_results_match(
            inp=['sti "42" magic'],
            mem=['42', None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.STI,
                Op.POP, i32(1))
        )

    def test_not_(self):
        self._assert_results_match(
            inp=['not 42 false'],
            mem=[42, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.NOT,
                Op.POP, i32(1))
        )

    def test_and_(self):
        self._assert_results_match(
            inp=['and 0 1 false'],
            mem=[0, 1, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.AND,
                Op.POP, i32(2))
        )

    def test_or_(self):
        self._assert_results_match(
            inp=['or 0 1 true'],
            mem=[0, 1, None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.PUSH, i32(1),
                Op.OR,
                Op.POP, i32(2))
        )

    def test_jump_(self):
        self._assert_results_match(
            inp=['jump main'],
            mem=[None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.JUMP)
        )

    def test_jmpt_(self):
        self._assert_results_match(
            inp=['jmpt true main'],
            mem=[None, None],
            ins=make.ins(
                Op.PUSH, i32(1),
                Op.PUSH, i32(0),
                Op.JMPT)
        )

    def test_jmpf_(self):
        self._assert_results_match(
            inp=['jmpf false main'],
            mem=[None, None],
            ins=make.ins(
                Op.PUSH, i32(1),
                Op.PUSH, i32(0),
                Op.JMPF)
        )

    def test_br_(self):
        self._assert_results_match(
            inp=['br func'],
            mem=[None],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.BR)
        )

    def test_brt_(self):
        self._assert_results_match(
            inp=['brt true func'],
            mem=[None, None],
            ins=make.ins(
                Op.PUSH, i32(1),
                Op.PUSH, i32(0),
                Op.BRT)
        )

    def test_brf_(self):
        self._assert_results_match(
            inp=['brf false func'],
            mem=[None, None],
            ins=make.ins(
                Op.PUSH, i32(1),
                Op.PUSH, i32(0),
                Op.BRF)
        )

    def test_back_(self):
        self._assert_results_match(
            inp=['back'],
            mem=[],
            ins=make.ins(Op.BACK)
        )

    def test_err(self):
        self._assert_results_match(
            inp=['err "piss off" 404'],
            mem=['piss off', 404],
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.OUT,
                Op.PUSH, i32(1),
                Op.ERR)
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

    def test_works_for_good_code(self):
        self._assert_results_match(
            inp=[
                'jump main',
                'func:',
                'out "Input your age: "',
                'ini age',
                'out "You are "',
                'out age',
                'out " years old -- that\'s cool!"',
                'back',
                'main:',
                'br func',
            ],
            # 0. main 1. func  2            3. age
            mem=[37, 6, 'Input your age: ', None,
                 'You are ', ' years old -- that\'s cool!'],
            #    4           5
            ins=make.ins(
                Op.PUSH, i32(0),
                Op.JUMP,
                Op.PUSH, i32(2),
                Op.OUT,
                Op.INI,
                Op.POP, i32(3),
                Op.PUSH, i32(4),
                Op.OUT,
                Op.PUSH, i32(3),
                Op.OUT,
                Op.PUSH, i32(5),
                Op.OUT,
                Op.BACK,
                Op.PUSH, i32(1),
                Op.BR)
        )
