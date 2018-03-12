import pickle

word_size = 4
byte_order = 'big'


class Serializable:
    def serialize(self):
        """
        :return:
        """
        raise NotImplementedError()

    def deserialize(self, binary):
        raise NotImplementedError()


class LabelEncoder:
    def __init__(self):
        self.labels = []
        self.label2id = {}
        self.label2address = {}

    def add_label(self, label):
        # TODO: check that label is unique
        self.labels.append(label)
        self.label2id[label] = len(self.labels) - 1

    def get_label(self, label_id):
        return self.labels[label_id]


class Program(Serializable):
    def __init__(self):
        self.data = []
        self.label_encoder = LabelEncoder()

    def serialize(self):
        bin_data = [len(self.data).to_bytes(word_size, byte_order)]
        for word in self.data:
            bin_data.append(word.serialize().to_bytes(word_size, byte_order))

        bin_data.append(pickle.dumps(self.label_encoder))
        return b''.join(bin_data)

    def deserialize(self, binary):
        size = int.from_bytes(binary[:word_size], byte_order)

        self.data = [0] * size
        for i in range(size):
            self.data[i] = int.from_bytes(binary[word_size * (i + 1):word_size * (i + 2)], byte_order)

        self.label_encoder = pickle.loads(binary[word_size * (size + 1):])
