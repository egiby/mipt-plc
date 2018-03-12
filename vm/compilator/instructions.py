from compilator.program import Serializable


str_ids = {
    'add': 0,
    'sub': 1,
    'mul': 2,
    'orr': 3,
    'and': 4,

    'neg': 5,
    'inc': 6,
    'dec': 7,

    'push': 8,
    'pop': 9,

    'mov': 10,
    'cmp': 11,
    'ldr': 12,
    'str': 13,

    'addr': 14,
    'je': 15,
    'jne': 16,
    'jng': 17,
    'jnz': 18,
    'call': 19,

    'syscall': 31
}


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
    def __init__(self, num_arguments, instruction_id=-1):
        self.instruction_id = instruction_id
        self.num_arguments = num_arguments
        self.registers = []

    def serialize(self):
        return get_word([self.instruction_id, *self.registers])

    def deserialize(self, word):
        self.instruction_id = get_argument(word, 0)

        self.registers = [get_argument(word, idx) for idx in range(1, self.num_arguments)]


class AddrInstruction(Serializable):
    def __init__(self):
        self.label = -1
        self.r = -1

    def serialize(self):
        assert self.r != -1
        assert self.label != -1
        instruction_id = str_ids['addr']

        return get_word([instruction_id, self.r, self.label])

    def deserialize(self, word):
        instruction_id = get_argument(word, 0)
        assert instruction_id == str_ids['addr']

        self.r = get_argument(word, 1)
        self.label = (word >> (2 * arg_size))  # !!!


class OnlyLabelInstruction(Serializable):
    def __init__(self, instruction_id=-1):
        self.label = -1
        self.instruction_id = instruction_id

    def serialize(self):
        assert self.label != -1
        assert self.instruction_id != -1

        return get_word([self.instruction_id, self.label])

    def deserialize(self, word):
        self.instruction_id = get_argument(word, 0)
        self.label = (word >> arg_size)
