from sequence import Sequence


def fibonacci_generator():
    a, b = 1, 1
    while True:
        yield a
        a, b = b, a + b


def main():
    print(Sequence(fibonacci_generator())
          .where(lambda x: x % 3 == 0)
          .select(lambda x: x if x % 2 else x ** 2)
          .take(5)
          .to_list())

    with open('text.txt', 'r') as text:
        print(Sequence(["a b d b  b bs b sb sb sa bsa "])
              .select(lambda line: line.split())
              .flatten()
              .group_by(lambda x: x)
              .select(lambda x: (x[0], len(x[1])))
              .order_by(lambda x: -x[1])
              .take(50)
              .to_list())


if __name__ == '__main__':
    main()
