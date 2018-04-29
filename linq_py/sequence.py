from collections import defaultdict


def flatten_generator(generator):
    for array in generator:
        for x in array:
            yield x


def take(generator, n):
    for i in range(n):
        yield next(generator)


class Sequence:
    def __init__(self, generator=()):
        self.generator = generator

    def flatten(self):
        return Sequence(flatten_generator(self.generator))

    def select(self, mapper):
        return Sequence(map(mapper, self.generator))

    def where(self, key_filter):
        return Sequence(filter(key_filter, self.generator))

    def take(self, k):
        return Sequence(take(self.generator, k))

    def group_by(self, key_function):
        d = defaultdict(list)

        for x in self.generator:
            d[key_function(x)].append(x)

        return Sequence(d.items())

    def order_by(self, key_function):
        return Sequence(sorted(self.generator, key=key_function))

    def to_list(self):
        return list(self.generator)
