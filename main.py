from enum import Enum
from math import log2, floor


class NodeType(Enum):
    STATE = 1
    CONDITION = 2
    DECISION = 3


class Node:
    def __init__(self, data: str, node_type: NodeType):
        self.data = data
        self.type = node_type
        self.next = None
        self.next_else = None
        self.visited_state = False
        self.id = 0


def find_states(root, states):
    if root is None or root.visited_state:
        return
    root.visited_state = True

    if root.type == NodeType.STATE:
        states.append(root)

    if root.type == NodeType.CONDITION:
        find_states(root.next_else, states)

    find_states(root.next, states)


def parse_state(node: Node):
    node.data = node.data.strip()
    if node.type == NodeType.CONDITION:
        return (f'if ({node.data}) begin\n' + parse_next(node.next)
                + 'end else begin\n' + parse_next(node.next_else) + 'end\n')
    return ((node.data + '\n').replace('\n', ';\n') if node.data else '') + parse_next(node.next)


def parse_next(next_node: Node):
    if next_node.type == NodeType.STATE:
        return f'n_state = {next_node.id};\n'
    return parse_state(next_node)


forbidden_names = ['begin', 'end', 'if', 'else', 'p_state', 'n_state', 'clock', 'reset']
forbidden_tokens = [';', '//', '"']


def check_input(input_list):
    if input_list is None:
        return []

    for input_name in input_list:
        if input_name in forbidden_names:
            raise ValueError(f'{input_name} is a forbidden name')
        for token in forbidden_tokens:
            if token in input_name:
                raise ValueError(f'{input_name} contains a forbidden character "{token}"')

    return input_list


# Like cmake but for verilog :)
def vmake(root: Node, output_list=None, input_list=None, inout_list=None,
          async_reset=False, negedge_reset=False, negedge_clock=False):
    output_list = check_input(output_list)
    input_list = check_input(input_list)
    inout_list = check_input(inout_list)

    code = 'module main(\n'
    for output_name in output_list:
        code += f'\toutput reg {output_name},\n'
    for inout_name in inout_list:
        code += f'\tinout {inout_name},\n'
    for input_name in input_list:
        code += f'\tinput {input_name},\n'

    code += f'\tinput clock,\n\tinput reset\n);\n'

    states = []
    find_states(root, states)
    for i, state in enumerate(states):
        state.id = i

    code += f'reg [{floor(log2(len(states)))}:0] p_state, n_state;\n\n'

    code += 'always @(p_state'
    for input_name in input_list:
        code += f' or {input_name.split(" ")[-1]}'  # wire [3:0] my_input -> or my_input
    code += ') begin\n'

    code += 'case (p_state)\n'

    for i, state in enumerate(states):
        code += f'{i}: begin\n'
        code += parse_state(state)
        code += 'end\n'

    code += 'endcase\n'

    trigger = lambda negedge: f'{"neg" if negedge else "pos"}edge'
    code += f'always @({trigger(negedge_clock)} clock{("or " + trigger(negedge_reset)) if async_reset else ""}) begin\n'
    code += f'\tif ({"~" if negedge_reset else ""}reset) p_state = 0;\n'
    code += f'\telse p_state = n_state;\nend\n'

    code += 'endmodule\n'
    return code


def rename_verilog(data):
    return data.replace('$display', 'verilog_display').replace('<=', '=')
    # TODO: Add other verilog functions like $time


def verilog_display(data, *args):
    print(data.format(*args))


def simulate_one_cycle(node: Node, input_dict: dict = None, output_dict: dict = None):
    if output_dict is None:
        output_dict = {}
    output_list = check_input(output_dict.keys())

    if input_dict is None:
        input_dict = {}
    check_input(input_dict.keys())

    for input_name in input_dict:
        exec(f'{input_name} = {input_dict[input_name]}')
    for output_name in output_list:
        exec(f'{output_name} = {output_dict[output_name]}')

    if node.type != NodeType.STATE:
        raise ValueError('Root node must be a state')

    node.data = rename_verilog(node.data)
    exec(node.data)
    node = node.next

    while node.type != NodeType.STATE:
        if node.type == NodeType.CONDITION:
            if eval(node.data):
                node = node.next
            else:
                node = node.next_else
        else:
            node.data = rename_verilog(node.data)
            exec(node.data)
            node = node.next

    for output_name in output_list:
        try:
            output_dict[output_name] = eval(output_name)
        except NameError:
            pass
    return node, output_dict


def update_inputs(input_dict: dict, output_dict: dict, node: Node):
    # Provided by the upper module (tester)
    return input_dict


def simulate(root: Node, cycles=1, input_dict: dict = None, output_list: list = None):
    node = root
    if output_list is None:
        output_list = []
    output_dict = dict.fromkeys(output_list, 0)
    for i in range(cycles):
        node, output_dict = simulate_one_cycle(node, input_dict, output_dict)
        print(output_dict)
        input_dict = update_inputs(input_dict, output_dict, node)
