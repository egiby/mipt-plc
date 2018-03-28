import sys

from compiler.program import Program, word_size, byte_order
from compiler.instructions import str2id, id2class, get_argument

from operator import add, sub, mul, or_, and_, xor


maxint = 2 ** 32
byte = 8


class VirtualMachine:
    def __init__(self, binary_code, memory_size=2 ** 16):
        program = Program()
        program.deserialize(binary_code)

        self.code_size = len(program.data)
        self.memory = program.data + [0] * (memory_size + 32)
        self.label_encoder = program.label_encoder
        self.register_addrs = list(range(len(self.memory) - 32, len(self.memory)))

        self.ip = 31
        self.sp = 30
        self.fp = 29
        self.cmp = 28

        self.set_register_value(self.ip, 0)  # first code instruction
        self.set_register_value(self.sp, self.code_size + memory_size - 1)

    def set_register_value(self, r, value):
        self.memory[self.register_addrs[r]] = value

    def get_register_value(self, r):
        return self.memory[self.register_addrs[r]]

    def inc_register(self, r, delta=1):
        self.memory[self.register_addrs[r]] += delta

    def dec_register(self, r, delta=1):
        self.memory[self.register_addrs[r]] -= delta

    def set_stack_top(self, value):
        self.memory[self.get_register_value(self.sp)] = value

    def get_stack_top(self):
        return self.memory[self.get_register_value(self.sp)]

    def _eval_arithmetic_operation(self, instruction, operation):
        r1, *args = instruction.registers

        self.set_register_value(r1, operation(*list(map(self.get_register_value, args))))

    def _eval_neg(self, r):
        old = self.get_register_value(r)
        self.set_register_value(r, (maxint - 1) ^ old)

    def _eval_push(self, r):
        self.set_stack_top(self.get_register_value(r))
        self.dec_register(self.sp)

    def _eval_pop(self, r):
        self.inc_register(self.sp)
        self.set_register_value(r, self.get_stack_top())

    def _eval_mov(self, r1, r2):
        self.set_register_value(r1, self.get_register_value(r2))

    def _eval_cmp(self, r1, r2):
        r1_value = self.get_register_value(r1)
        r2_value = self.get_register_value(r2)
        result = 0
        if r1_value < r2_value:
            result = -1
        elif r1_value > r2_value:
            result = 1
        self.set_register_value(self.cmp, result)

    def _eval_ldr(self, r1, r2):
        addr = self.get_register_value(r2)
        self.set_register_value(r1, self.memory[addr])

    def _eval_str(self, r1, r2):
        addr = self.get_register_value(r2)
        self.memory[addr] = self.get_register_value(r1)

    def _eval_addr(self, r1, label):
        addr = label
        self.set_register_value(r1, addr)

    def _eval_jump(self, label, predicate, size):
        result = self.get_register_value(self.cmp)
        if predicate(result):
            addr = label
            self.set_register_value(self.ip, addr)
        else:
            self.inc_register(self.ip, size)

    def _eval_call(self, label, size):
        self.inc_register(self.ip, size)
        self._eval_push(self.ip)

        addr = label
        self.set_register_value(self.ip, addr)

    def _eval_ret(self):
        self._eval_pop(self.ip)

    def _eval_write(self, addr, size):
        for byte_idx in range(size):
            word_idx = addr + byte_idx // word_size
            offset = byte_idx % word_size
            word = int.to_bytes(self.memory[word_idx], word_size, byte_order)[::-1]
            sys.stdout.write(chr(word[offset]))

    def _eval_syscall(self):
        syscall_id = self.get_register_value(0)
        if syscall_id == 1:  # write
            addr = self.get_register_value(1)
            size = self.get_register_value(2)
            self._eval_write(addr, size)
        elif syscall_id == 2:  # readint
            value = int(input())
            addr = self.get_register_value(1)
            self.memory[addr] = value
        elif syscall_id == 3:  # writeint
            addr = self.get_register_value(1)
            print(self.memory[addr])
        else:
            raise ValueError('unexpected syscall id')

    def _eval(self, instruction):
        if instruction.get_id() == str2id['add']:
            self._eval_arithmetic_operation(instruction, add)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['sub']:
            self._eval_arithmetic_operation(instruction, sub)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['mul']:
            self._eval_arithmetic_operation(instruction, mul)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['orr']:
            self._eval_arithmetic_operation(instruction, or_)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['xor']:
            self._eval_arithmetic_operation(instruction, xor)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['and']:
            self._eval_arithmetic_operation(instruction, and_)
            self.inc_register(self.ip, instruction.size())

        elif instruction.get_id() == str2id['neg']:
            self._eval_neg(instruction.registers[0])
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['inc']:
            self.inc_register(instruction.registers[0])
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['dec']:
            self.dec_register(instruction.registers[0])
            self.inc_register(self.ip, instruction.size())

        elif instruction.get_id() == str2id['push']:
            self._eval_push(instruction.registers[0])
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['pop']:
            self._eval_pop(instruction.registers[0])
            self.inc_register(self.ip, instruction.size())

        elif instruction.get_id() == str2id['mov']:
            self._eval_mov(*instruction.registers)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['cmp']:
            self._eval_cmp(*instruction.registers)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['ldr']:
            self._eval_ldr(*instruction.registers)
            self.inc_register(self.ip, instruction.size())
        elif instruction.get_id() == str2id['str']:
            self._eval_str(*instruction.registers)
            self.inc_register(self.ip, instruction.size())

        elif instruction.get_id() == str2id['addr']:
            self._eval_addr(instruction.r, instruction.label)
            self.inc_register(self.ip, instruction.size())

        elif instruction.get_id() == str2id['je']:
            self._eval_jump(instruction.label, lambda x: x == 0, instruction.size())
        elif instruction.get_id() == str2id['jne']:
            self._eval_jump(instruction.label, lambda x: x != 0, instruction.size())
        elif instruction.get_id() == str2id['jng']:
            self._eval_jump(instruction.label, lambda x: x <= 0, instruction.size())

        elif instruction.get_id() == str2id['call']:
            self._eval_call(instruction.label, instruction.size())

        elif instruction.get_id() == str2id['ret']:
            self._eval_ret()

        elif instruction.get_id() == str2id['syscall']:
            self._eval_syscall()
            self.inc_register(self.ip, instruction.size())

        else:
            # just ignore
            self.inc_register(self.ip, instruction.size())

    def run(self):
        while self.get_register_value(self.ip) < self.code_size:
            instruction = self.get_current_instruction()
            self._eval(instruction)

    def get_current_instruction(self):
        ip = self.get_register_value(self.ip)
        word = self.memory[ip]
        type_id = get_argument(word, 0)

        instruction_class = id2class[type_id]
        instance = instruction_class()

        instance.deserialize(self.memory[ip:ip + instruction_class.basic_size()])
        return instance
