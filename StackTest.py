from unittest import TestCase

from Stack import Stack


class StackTest(TestCase):
    def setUp(self) -> None:
        self.stack = Stack()

    def test_push_increases_length(self):
        self.stack.push(0)
        self.assertEqual(1, len(self.stack))

    def test_two_push_pop(self):
        self.stack.push(1)
        self.stack.push(2)
        two, one = self.stack.pop(), self.stack.pop()
        self.assertEqual(0, len(self.stack))
        self.assertEqual(2, two)
        self.assertEqual(1, one)

    def test_peek(self):
        self.stack.push(1)
        self.stack.push(2)
        two = self.stack.peek()
        self.assertEqual(2, two)

    def test_empty(self):
        self.assertEqual(True, self.stack.empty())
        self.stack.push(1)
        self.assertEqual(False, self.stack.empty())
        self.stack.pop()
        self.assertEqual(True, self.stack.empty())

    def test_clear(self):
        self.stack.push(1)
        self.stack.clear()
        self.assertEqual(True, self.stack.empty())
