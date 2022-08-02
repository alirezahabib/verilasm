from unittest import TestCase
from main import *


class TestVmake(TestCase):
    # Do nothing state machine :)
    def test_do_nothing(self):
        root = Node('', NodeType.STATE)
        root.next = root
        print(vmake(root))

    # Hello world one state machine
    def test_simple_one_state(self):
        root = Node('$display("Hello world!")', NodeType.STATE)
        root.next = root
        print(vmake(root))

    # Hello world negedge and asynchronous clock and reset one state machine
    def test_simple_negedge_async_reset(self):
        root = Node('$display("Hello negedge-low and asynchronous world!")', NodeType.STATE)
        root.next = root
        print(vmake(root, async_reset=True, negedge_reset=True, negedge_clock=True))

    # Test input check on illegal names
    def test_illegal_name_1(self):
        root = Node('', NodeType.STATE)
        root.next = root
        with self.assertRaises(ValueError):
            print(vmake(root, input_list=['p_state']))

    def test_illegal_name_2(self):
        root = Node('', NodeType.STATE)
        root.next = root
        with self.assertRaises(ValueError):
            print(vmake(root, input_list=['my;input']))

    def test_homework_5(self):
        state1 = Node('', NodeType.STATE)
        cond1 = Node('START == 1', NodeType.CONDITION)
        dec1 = Node('R1 <= DIP_A\n'
                    'R2 <= DIP_B\n'
                    'R3 <= DIP_C\n'
                    'SUM <= 0\n'
                    'READY <= 0', NodeType.DECISION)

        state2 = Node('', NodeType.STATE)
        cond2 = Node('R1 > R2', NodeType.CONDITION)
        dec2 = Node('R1 <= R2\n'
                    'R2 <= R1', NodeType.DECISION)

        state3 = Node('', NodeType.STATE)
        cond3 = Node('OR(R1)', NodeType.CONDITION)
        dec3 = Node('SUM <= SUM + R2\n'
                    'R1 <= R1 - 1', NodeType.DECISION)

        state4 = Node('', NodeType.STATE)
        cond4 = Node('SUM < R3', NodeType.CONDITION)
        dec4 = Node('R4 <= SUM\n'
                    'READY <= 1', NodeType.DECISION)
        dec5 = Node('R4 <= R3\n'
                    'READY <= 1', NodeType.DECISION)

        state1.next = cond1
        cond1.next = dec1
        cond1.next_else = state1
        dec1.next = state2
        state2.next = cond2
        cond2.next = dec2
        cond2.next_else = state3
        dec2.next = state3
        state3.next = cond3
        cond3.next = dec3
        dec3.next = state3
        cond3.next_else = state4
        state4.next = cond4
        cond4.next = dec4
        cond4.next_else = dec5
        dec4.next = state1
        dec5.next = state1

        print(vmake(state1,
                    input_list=['[3:0] DIP_A', '[3:0] DIP_B', '[3:0] DIP_C'],
                    output_list=['[3:0] R1', '[3:0] R2', '[3:0] R3', '[3:0] SUM', 'READY']))


class TestSimulate(TestCase):
    # Do nothing state machine :)
    def test_do_nothing(self):
        root = Node('', NodeType.STATE)
        root.next = root
        simulate(root, 10)

    # Hello world one state machine
    def test_simple_one_state(self):
        root = Node('$display("Hello world!")', NodeType.STATE)
        root.next = root
        print(simulate(root, 10))

    # Test input check on illegal names
    def test_illegal_name_1(self):
        root = Node('', NodeType.STATE)
        root.next = root
        with self.assertRaises(ValueError):
            simulate(root, 10, input_dict={'p_state': 0})

    def test_illegal_name_2(self):
        root = Node('', NodeType.STATE)
        root.next = root
        with self.assertRaises(ValueError):
            simulate(root, 10, input_dict={'my;input': 9})

    def test_homework_5(self):
        state1 = Node('', NodeType.STATE)
        cond1 = Node('START == 1', NodeType.CONDITION)
        dec1 = Node('R1 = DIP_A\n'
                    'R2 = DIP_B\n'
                    'R3 = DIP_C\n'
                    'TOTAL = 0\n'
                    'READY = 0', NodeType.DECISION)

        state2 = Node('', NodeType.STATE)
        cond2 = Node('R1 > R2', NodeType.CONDITION)
        dec2 = Node('temp = R1\n'
                    'R1 = R2\n'
                    'R2 = temp', NodeType.DECISION)

        state3 = Node('', NodeType.STATE)
        cond3 = Node('R1', NodeType.CONDITION)
        dec3 = Node('TOTAL = TOTAL + R2\n'
                    'R1 = R1 - 1', NodeType.DECISION)

        state4 = Node('', NodeType.STATE)
        cond4 = Node('TOTAL < R3', NodeType.CONDITION)
        dec4 = Node('R4 = TOTAL\n'
                    'READY = 1', NodeType.DECISION)
        dec5 = Node('R4 = R3\n'
                    'READY = 1', NodeType.DECISION)

        state1.next = cond1
        cond1.next = dec1
        cond1.next_else = state1
        dec1.next = state2
        state2.next = cond2
        cond2.next = dec2
        cond2.next_else = state3
        dec2.next = state3
        state3.next = cond3
        cond3.next = dec3
        dec3.next = state3
        cond3.next_else = state4
        state4.next = cond4
        cond4.next = dec4
        cond4.next_else = dec5
        dec4.next = state1
        dec5.next = state1

        simulate(state1, 20, {'DIP_A': 54, 'DIP_B': 12, 'DIP_C': 37, 'START': 1},
                 ['R1', 'R2', 'R3', 'TOTAL', 'READY', 'R4'])
        print('\n')
        simulate(state1, 23, {'DIP_A': 15, 'DIP_B': 103, 'DIP_C': 2000, 'START': 1},
                 ['R1', 'R2', 'R3', 'TOTAL', 'READY', 'R4'])

    def test_fibonacci(self):
        state0 = Node('b = 1', NodeType.STATE)
        state1 = Node('print(a)', NodeType.STATE)
        state2 = Node('c = b', NodeType.STATE)
        state3 = Node('b = a + b', NodeType.STATE)
        state4 = Node('a = c', NodeType.STATE)

        state0.next = state1
        state1.next = state2
        state2.next = state3
        state3.next = state4
        state4.next = state1

        simulate(state0, 50, None, ['a', 'b', 'c'])
