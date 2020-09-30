from unittest import TestCase
import os

from morty.Loader import Loader


class LoaderTest(TestCase):
    def setUp(self) -> None:
        self._write_to_test_file('')
        self.loader = Loader()

    def tearDown(self) -> None:
        os.remove('test.so')

    def test_cleans_lines_around_clean_line(self):
        self._write_to_test_file('\t\nini n\n   \n')
        self._load()
        self._assert_code_equals(['ini n'])

    def test_cleans_comment(self):
        self._write_to_test_file('\t\nini n @ comment\n   \n')
        self._load()
        self._assert_code_equals(['ini n'])

    def test_can_include_files(self):
        self._write_to_test_file(
            """
            >"examples/lib/factorial.so"
              jump adder
            """
        )
        self._load()
        self._assert_code_equals([
            'factorial:',
            'lth n 1 b',
            'jmpt b factorial_back',
            'put n f',
            'factorial_while:',
            'gth n 1 b',
            'jmpf b factorial_back',
            'sub n 1 n',
            'mul f n f',
            'jump factorial_while',
            'factorial_back:',
            'back',
            'jump adder',
        ])

    def test_includes_multiple_files(self):
        self._write_to_test_file(
            """
            >"examples/lib/factorial.so"
            >"examples/theory/infinite.so"
              jump adder
            """
        )
        self._load()
        self._assert_code_equals([
            'factorial:',
            'lth n 1 b',
            'jmpt b factorial_back',
            'put n f',
            'factorial_while:',
            'gth n 1 b',
            'jmpf b factorial_back',
            'sub n 1 n',
            'mul f n f',
            'jump factorial_while',
            'factorial_back:',
            'back',
            'start:',
            'out "I love pizza!"',
            'jump start',
            'jump adder',
        ])

    def test_includes_in_depth(self):
        self._write_to_file('one.so', 'ini a')
        self._write_to_file('two.so', '>"one.so"\nini b')
        self._write_to_test_file('>"two.so"\n ini c')
        self._load()
        self._assert_code_equals([
            'ini a',
            'ini b',
            'ini c',
        ])
        os.remove('one.so')
        os.remove('two.so')

    """ Destructive tests. """
    def test_sets_err_flag_on_nonexistent_include(self):
        self._write_to_test_file('>"non-existent.so"')
        self._load()
        self._assert_err_flag_set()

    def test_catches_empty_include_statements(self):
        self._write_to_test_file('>')
        self._load()
        self._assert_err_flag_set()

    def test_catches_include_statements_with_empty_path(self):
        self._write_to_test_file('>""')
        self._load()
        self._assert_err_flag_set()

    def test_ignores_known_includes(self):
        self._write_to_test_file('>"one.so"\nout "hello world"')
        self._write_to_file('one.so', '>"test.so"\n out "bye world"')
        self._load()
        self._assert_code_equals([
            'out "bye world"',
            'out "hello world"',
        ])
        os.remove('one.so')

    """ Utility methods. """
    @staticmethod
    def _write_to_file(path, string):
        with open(path, 'w') as file:
            file.write(string)

    def _load(self):
        self.loader.load('test.so')

    def _write_to_test_file(self, string):
        self._write_to_file('test.so', string)

    def _assert_code_equals(self, expect):
        self.assertEqual(expect, self.loader.code)

    def _assert_err_flag_set(self):
        self.assertTrue(self.loader.err)
