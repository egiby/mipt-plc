import sys

from compiler.program import Program
from compiler.instructions import create_instruction, str_to_words
from vm.vm import VirtualMachine


def parse_args(argv):
    args = []
    return args


def main(args):
    program = Program()

    db = create_instruction('db')
    db.set_data(str_to_words('N:\n'))
    db_label = program.add_data_instruction(db)

    db_addr = create_instruction('addr')
    db_addr.label = db_label
    db_addr.r = 1

    dd = create_instruction('dd')
    dd.set_data([0])
    dd_label = program.add_data_instruction(dd)

    dd_addr = create_instruction('addr')
    dd_addr.label = dd_label
    dd_addr.r = 1

    xor0 = create_instruction('xor')
    xor0.registers = [0, 0, 0]

    xor2 = create_instruction('xor')
    xor2.registers = [2, 0, 0]

    inc0 = create_instruction('inc')
    inc0.registers = [0]

    inc2 = create_instruction('inc')
    inc2.registers = [2]

    dec0 = create_instruction('dec')
    dec0.registers = [0]

    program.add_instruction(xor0)
    program.add_instruction(inc0)  # r0 = 1
    program.add_instruction(db_addr)  # r1 = db_label

    program.add_instruction(inc2)
    program.add_instruction(inc2)
    program.add_instruction(inc2)  # r2 = 3

    program.add_instruction(create_instruction('syscall'))  # print start message

    program.add_instruction(inc0)  # r0 = 2
    program.add_instruction(dd_addr)  # r1 = dd_label

    program.add_instruction(create_instruction('syscall'))  # input N

    # something interesting...

    cmp = create_instruction('cmp')
    cmp.registers = [0, 0]
    program.add_instruction(cmp)

    je = create_instruction('je')
    je.label = program.get_last_address() + 1 + 20  # skip fib description
    program.add_instruction(je)

    # fib: in r0, our r1
    fib_label = program.get_last_address()
    call_fib = create_instruction('call')
    call_fib.label = fib_label

    program.add_instruction(xor2)  # fib 1
    program.add_instruction(inc2)  # fib 2
    program.add_instruction(inc2)  # fib 3

    cmp = create_instruction('cmp')
    cmp.registers = [2, 0]
    program.add_instruction(cmp)  # fib 4

    jng = create_instruction('jng')
    jng.label = program.get_last_address() + 1 + 2
    program.add_instruction(jng)  # fib 5 if 2 >= r0 skip next two instructions

    mov01 = create_instruction('mov')
    mov01.registers = [1, 0]

    mov13 = create_instruction('mov')
    mov13.registers = [3, 1]

    add113 = create_instruction('add')
    add113.registers = [1, 1, 3]

    program.add_instruction(mov01)  # fib 6 return 0 or 1
    program.add_instruction(create_instruction('ret'))  # fib 7 end function

    push0 = create_instruction('push')
    push0.registers = [0]
    pop0 = create_instruction('pop')
    pop0.registers = [0]

    push3 = create_instruction('push')
    push3.registers = [3]
    pop3 = create_instruction('pop')
    pop3.registers = [3]

    program.add_instruction(dec0)  # fib 8
    program.add_instruction(push0)  # fib 9 save r0
    program.add_instruction(call_fib)  # fib 10 recursive call for n - 1
    program.add_instruction(pop0)  # fib 11

    program.add_instruction(mov13)  # fib 12 r3 = r1 == fib(n - 1)
    program.add_instruction(dec0)  # fib 13

    program.add_instruction(push3)  # fib 14 save r3
    program.add_instruction(push0)  # fib 15 save r0
    program.add_instruction(call_fib)  # fib 16 recursive call for n - 2
    program.add_instruction(pop0)  # fib 17
    program.add_instruction(pop3)  # fib 18

    program.add_instruction(add113)  # fib 19 r1 += r3
    program.add_instruction(create_instruction('ret'))  # fib 20
    # fib ends

    ldr = create_instruction('ldr')
    ldr.registers = [0, 1]  # r1 still has dd_label
    program.add_instruction(ldr)  # store n to r0

    push1 = create_instruction('push')
    push1.registers = [1]

    pop1 = create_instruction('pop')
    pop1.registers = [1]

    program.add_instruction(push1)  # save r1
    program.add_instruction(call_fib)
    program.add_instruction(mov13)  # r3 = fib(n)
    program.add_instruction(pop0)  # r1 = dd_label

    store = create_instruction('str')
    store.registers = [3, 1]
    program.add_instruction(store)  # dd = r3

    program.add_instruction(xor0)
    program.add_instruction(inc0)
    program.add_instruction(inc0)
    program.add_instruction(inc0)
    program.add_instruction(create_instruction('syscall'))  # output fib(n)

    binary = program.serialize()
    print(binary)

    vm = VirtualMachine(binary, memory_size=100)

    vm.run()


if __name__ == '__main__':
    main(parse_args(sys.argv))
