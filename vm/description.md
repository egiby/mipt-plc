# Assembler specification

## Registers:
There are 32 general-purpose 32bit registers, called r0 ... r31
Behaviour of overflow in register is undefined

r28 is used for result of comparison
fp == r29
sp == r30
ip == r31

there is no callee-safe guarantee for registers


## Commands:
- add r0, r1, r2
- sub r0, r1, r2
- mul r0, r1, r2
- orr r0, r1, r2
- xor r0, r1, r2
- and r0, r1, r2


- neg r0
- inc r0
- dec r0


- push r1
- pop r1


- mov r0, r1
- cmp r0, r1
- ldr r0, r1
- str r0, r1


- addr r1, label


- je label
- jne label
- jng label


- call label


- db "smth", 13
- dd 0x12345678


- ret
- syscall


## System calls
Expected system call id in r0
- 1 write (in: r1 - output address, in: r2 - number of bytes)
- 2 readint (in: r1 - input address)
- 3 writeint (in: r1 - output address)