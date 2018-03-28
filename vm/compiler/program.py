import pickle

word_size = 4
byte_order = 'big'


class Serializable:
    def get_id(self):
        raise NotImplementedError()

    @staticmethod
    def basic_size():
        raise NotImplementedError()

    def size(self):
        raise NotImplementedError()

    def serialize(self):
        raise NotImplementedError()

    def deserialize(self, binary):
        raise NotImplementedError()


class LabelEncoder:
    def __init__(self):
        self.labels = []
        self.label2id = {}
        self.id2address = {}

    def add_label(self, label, address):
        # TODO: check that label is unique
        self.labels.append(label)
        self.label2id[label] = len(self.labels) - 1
        self.id2address[self.label2id[label]] = address

    def get_id(self, label):
        return self.label2id[label]

    def get_label(self, label_id):
        return self.labels[label_id]


class Program(Serializable):
    def get_id(self):
        return

    def size(self):
        return

    def __init__(self):
        self.instructions = []
        self.label_encoder = LabelEncoder()
        self.data = []
        self.address = 0

    def get_last_address(self):
        return self.address

    def add_instruction(self, instruction):
        self.instructions.append(instruction)
        self.address += instruction.size()

    def add_data_instruction(self, instruction, label=''):
        address = self.get_last_address() + instruction.basic_size()
        if label:
            self.label_encoder.add_label(label, address)

        instruction.label = address
        self.add_instruction(instruction)

        return instruction.label

    def serialize(self):
        bin_data = []

        for line in self.instructions:
            words = line.serialize()
            for word in words:
                bin_data.append(word.to_bytes(word_size, byte_order))

        bin_data.append(pickle.dumps(self.label_encoder))
        binary = b''.join(bin_data)

        return (len(bin_data) - 1).to_bytes(word_size, byte_order) + binary

    def deserialize(self, binary):
        size = int.from_bytes(binary[:word_size], byte_order)

        self.data = [0] * size
        for i in range(size):
            self.data[i] = int.from_bytes(binary[word_size * (i + 1):word_size * (i + 2)], byte_order)

        self.label_encoder = pickle.loads(binary[word_size * (size + 1):])
