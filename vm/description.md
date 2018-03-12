# Assembler specification

## Registers:
There are 32 general-purpose 32bit registers, called r0 ... r31

fp == r29
sp == r30
ip == r31

## Section .text

### Commands:
- add r0, r1, r2
- sub r0, r1, r2
- mul r0, r1, r2
- orr r0, r1, r2
- and r0, r1, r2


- neg r0
- inc r0
- dec r0


- push r1
- pop r1


- mov r0, r1
- cmp r0, r1
- ldr r0, r0
- str r0, r0


- addr r1, label
- je label
- jne label
- jng label
- jnz label
- call label


- syscall

## Section .data
### Commands:
- db "smth", 1, 2, 3, 0
- dd 0x12345678


## System calls
Expected system call id in r0
- 1 write (in: r1 - file handle, in: r2 - output address, in: r3 - (maximum) number of bytes)
- 2 read  (in: r1 - file handle, in: r2 - input address, in: r3 - (maximum) number of bytes)
- 3 alloc (in: r1 - number of bytes, in: r2 - start address)

