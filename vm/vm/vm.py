from compiler.program import Program


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
        self.set_register_value(self.sp, self.code_size + memory_size)

    def set_register_value(self, r, value):
        self.memory[self.register_addrs[r]] = value

    def get_register_value(self, r):
        return self.memory[self.register_addrs[r]]

    def inc_register(self, r):
        self.memory[self.register_addrs[r]] += 1

    def dec_register(self, r):
        self.memory[self.register_addrs[r]] -= 1

    def set_stack_top(self, value):
        self.memory[self.get_register_value(self.sp)] = value

    def get_stack_top(self):
        return self.memory[self.get_register_value(self.sp)]

    def _eval_arithmetic_operation(self, instruction, operation):
        r1, *args = instruction.registers

        self.set_register_value(r1, operation(args))

    def _eval_push(self, r):
        self.set_stack_top(self.get_register_value(r))
        self.dec_register(self.sp)

    def _eval_pop(self, r):
        self.set_register_value(r, self.get_stack_top())
        self.inc_register(self.sp)

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
        addr = self.label_encoder.id2address[label]
        self.set_register_value(r1, addr)

    def _eval_jump(self, label, predicate):
        result = self.get_register_value(self.cmp)
        if predicate(result):
            addr = self.label_encoder.id2address[label]
            self.set_register_value(self.ip, addr)  # BAD MAGIC

    def _eval_call(self, label):
        self._eval_push(self.ip)
        addr = self.label_encoder.id2address[label]
        self.set_register_value(self.ip, addr)

    def _eval_ret(self):
        self._eval_pop(self.ip)

    def _eval(self, instruction):
        pass

    def run(self):
        while self.ip < self.code_size:
            instruction = self.get_current_instruction()
            self._eval(instruction)

    def get_current_instruction(self):
        pass