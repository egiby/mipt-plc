from compiler.program import Serializable

instructions = [
    'add',
    'sub',
    'mul',
    'orr',
    'and',

    'neg',
    'inc',
    'dec',

    'push',
    'pop',

    'mov',
    'cmp',
    'ldr',
    'str',

    'addr',
    'je',
    'jne',
    'jng',
    'call',

    'db',
    'dd',

    'ret',
    'syscall'
]

_str2id = {instructions[i]: i for i in range(len(instructions))}

arg_size = 5


def get_argument(word, idx):
    return (word >> (idx * arg_size)) & ((1 << arg_size) - 1)


def get_word(args):
    for arg in args:
        assert 0 <= arg < (1 << arg_size)

    word = 0
    offset = 0
    for arg in args:
        word += (arg << (arg_size * offset))
        offset += 1

    return word


class OnlyRegistersInstruction(Serializable):
    def get_id(self):
        return self.instruction_id

    def __init__(self, num_arguments, instruction_id=-1):
        self.instruction_id = instruction_id
        self.num_arguments = num_arguments
        self.registers = []

    def size(self):
        return 1

    def serialize(self):
        return [get_word([self.instruction_id, *self.registers])]

    def deserialize(self, word):
        assert len(word) == 1
        word = word[0]
        self.instruction_id = get_argument(word, 0)

        self.registers = [get_argument(word, idx) for idx in range(1, self.num_arguments)]


class AddrInstruction(Serializable):
    def get_id(self):
        return _str2id['addr']

    def __init__(self, label=-1, r=-1):
        self.label = label
        self.r = r

    def size(self):
        return 1

    def serialize(self):
        assert self.r != -1
        assert self.label != -1
        instruction_id = _str2id['addr']

        return [get_word([instruction_id, self.r, self.label])]

    def deserialize(self, word):
        assert len(word) == 1
        word = word[0]

        instruction_id = get_argument(word, 0)
        assert instruction_id == _str2id['addr']

        self.r = get_argument(word, 1)
        self.label = (word >> (2 * arg_size))  # !!!


class OnlyLabelInstruction(Serializable):
    def get_id(self):
        return self.instruction_id

    def __init__(self, instruction_id=-1, label=-1):
        self.label = label
        self.instruction_id = instruction_id

    def size(self):
        return 1

    def serialize(self):
        assert self.label != -1
        assert self.instruction_id != -1

        return [get_word([self.instruction_id, self.label])]

    def deserialize(self, word):
        assert len(word) == 1
        word = word[0]

        self.instruction_id = get_argument(word, 0)
        self.label = (word >> arg_size)


class SyscallInstruction(Serializable):
    def get_id(self):
        return _str2id['syscall']

    def size(self):
        return 1

    def serialize(self):
        return [get_word([_str2id['syscall']])]

    def deserialize(self, binary):
        pass


class DataInstruction(Serializable):
    def get_id(self):
        return self.instruction_id

    def __init__(self, instruction_id=-1, label=-1, data=()):
        self.label = label
        self.data = data
        self.instruction_id = instruction_id

    def size(self):
        return len(self.data) + 2

    def serialize(self):
        assert self.label != -1
        assert self.instruction_id != -1
        assert self.data
        return [get_word([self.instruction_id, self.label]), len(self.data)] + self.data

    def deserialize(self, binary):
        assert len(binary) >= 2
        word = binary[0]

        self.instruction_id = get_argument(word, 0)

        self.label = (word >> arg_size)
        size = binary[1]
        assert size + 2 == len(binary)

        self.data = binary[2:]


def str_to_register(s):
    return int(s[1:])


def create_on_registers_instruction(name, args):
    instruction = OnlyRegistersInstruction(3, _str2id[name])
    registers = list(map(str_to_register, args))

    instruction.registers = registers
    return instruction


def create_only_label_instruction(name, args, label_encoder):
    assert len(args) == 1
    label_id = label_encoder.get_id(args[0])
    instruction = OnlyLabelInstruction(_str2id[name], label_id)
    return instruction


def create_addr_instruction(args, label_encoder):
    assert len(args) == 2
    r = str_to_register(args[0])
    label_id = label_encoder.get_id(args[1])

    instruction = AddrInstruction(label_id, r)
    return instruction


def create_syscall_instruction():
    return SyscallInstruction()


def create_data_instruction(name, args):
    data = []
    if name == 'dd':
        data = [int(args[0], 16)]
    elif name == 'db':
        pass
    else:
        assert False
