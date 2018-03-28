from compiler.program import Serializable

instructions = [
    'add',
    'sub',
    'mul',
    'orr',
    'xor',
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

str2id = {instructions[i]: i for i in range(len(instructions))}

default_arg_size = 5


def get_argument(word, idx, arg_size=default_arg_size):
    return (word >> (idx * arg_size)) & ((1 << arg_size) - 1)


def get_word(args, arg_size=default_arg_size, need_check=True):
    if need_check:
        for arg in args:
            assert 0 <= arg < (1 << arg_size)

    word = 0
    offset = 0
    for arg in args:
        word += (arg << (arg_size * offset))
        offset += 1

    return word


class OnlyRegistersInstruction(Serializable):
    @staticmethod
    def basic_size():
        return 1

    def get_id(self):
        return self.instruction_id

    def __init__(self, num_arguments=-1, instruction_id=-1):
        self.instruction_id = instruction_id
        self.num_arguments = num_arguments
        self.registers = []

    def size(self):
        return 1

    def serialize(self):
        assert len(self.registers) == self.num_arguments
        return [get_word([self.instruction_id, self.num_arguments] + self.registers)]

    def deserialize(self, word):
        assert len(word) == 1
        word = word[0]
        self.instruction_id = get_argument(word, 0)
        self.num_arguments = get_argument(word, 1)

        self.registers = [get_argument(word, idx) for idx in range(2, self.num_arguments + 2)]


class AddrInstruction(Serializable):
    @staticmethod
    def basic_size():
        return 1

    def get_id(self):
        return str2id['addr']

    def __init__(self, label=-1, r=-1):
        self.label = label
        self.r = r

    def size(self):
        return 1

    def serialize(self):
        assert self.r != -1
        assert self.label != -1
        instruction_id = str2id['addr']

        return [get_word([instruction_id, self.r, self.label], need_check=False)]

    def deserialize(self, word):
        assert len(word) == 1
        word = word[0]

        instruction_id = get_argument(word, 0)
        assert instruction_id == str2id['addr']

        self.r = get_argument(word, 1)
        self.label = (word >> (2 * default_arg_size))  # !!!


class OnlyLabelInstruction(Serializable):
    @staticmethod
    def basic_size():
        return 1

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

        return [get_word([self.instruction_id, self.label], need_check=False)]

    def deserialize(self, word):
        assert len(word) == 1
        word = word[0]

        self.instruction_id = get_argument(word, 0)
        self.label = (word >> default_arg_size)


class SyscallInstruction(Serializable):
    @staticmethod
    def basic_size():
        return 1

    def get_id(self):
        return str2id['syscall']

    def size(self):
        return 1

    def serialize(self):
        return [get_word([str2id['syscall']])]

    def deserialize(self, binary):
        pass


class RetInstruction(Serializable):
    @staticmethod
    def basic_size():
        return 1

    def get_id(self):
        return str2id['ret']

    def size(self):
        return 1

    def serialize(self):
        return [get_word([str2id['ret']])]

    def deserialize(self, binary):
        pass


class DataInstruction(Serializable):
    @staticmethod
    def basic_size():
        return 2

    def get_id(self):
        return self.instruction_id

    def __init__(self, instruction_id=-1, label=-1, data=()):
        self.label = label
        self.data = data
        self.data_size = len(data)
        self.instruction_id = instruction_id

    def size(self):
        return self.data_size + 2

    def set_data(self, data):
        self.data = data
        self.data_size = len(data)

    def serialize(self):
        assert self.label != -1
        assert self.instruction_id != -1
        assert self.data
        return [get_word([self.instruction_id, self.label]), self.data_size] + self.data

    def deserialize(self, binary):
        assert len(binary) == DataInstruction.basic_size()
        word = binary[0]

        self.instruction_id = get_argument(word, 0)

        self.label = (word >> default_arg_size)
        self.data_size = binary[1]


id2class = [OnlyRegistersInstruction] * 15 + \
           [AddrInstruction] + \
           4 * [OnlyLabelInstruction] + \
           2 * [DataInstruction] + \
           [RetInstruction, SyscallInstruction]

assert len(id2class) == len(str2id)


def str_to_register(s):
    return int(s[1:])


def str_to_words(s):
    words = []
    for i in range(0, len(s), 4):
        words.append(get_word(list(map(ord, s[i:i + 4])), arg_size=8))

    return words


def create_instruction(name):
    if name not in str2id:
        return None

    if str2id['add'] <= str2id[name] <= str2id['and']:
        return OnlyRegistersInstruction(num_arguments=3, instruction_id=str2id[name])

    if str2id['neg'] <= str2id[name] <= str2id['pop']:
        return OnlyRegistersInstruction(num_arguments=1, instruction_id=str2id[name])

    if str2id['mov'] <= str2id[name] <= str2id['str']:
        return OnlyRegistersInstruction(num_arguments=2, instruction_id=str2id[name])

    if str2id[name] == str2id['addr']:
        return AddrInstruction()

    if str2id['je'] <= str2id[name] <= str2id['call']:
        return OnlyLabelInstruction(instruction_id=str2id[name])

    if str2id[name] == str2id['ret']:
        return RetInstruction()

    if str2id[name] == str2id['syscall']:
        return SyscallInstruction()

    assert str2id[name] == str2id['dd'] or str2id[name] == str2id['db']

    return DataInstruction(str2id[name])


def create_on_registers_instruction(name, args):
    instruction = OnlyRegistersInstruction(3, str2id[name])
    registers = list(map(str_to_register, args))

    instruction.registers = registers
    return instruction


def create_only_label_instruction(name, args, label_encoder):
    assert len(args) == 1
    label_id = label_encoder.get_id(args[0])
    instruction = OnlyLabelInstruction(str2id[name], label_id)
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
