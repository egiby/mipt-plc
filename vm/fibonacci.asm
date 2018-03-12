        global  main
        extern  printf

        section .text
main:
        push    r3                     ; we have to save this since we use it

        mov     r1, 90                 ; r1 will countdown to 0
        xor     r0, r0                ; r0 will hold the current number
        xor     r3, r3                ; r3 will hold the next number
        inc     r3                     ; r3 is originally 1
print:
        ; We need to call printf, but we are using r0, r3, and r1.  printf
        ; may destroy r0 and r1 so we will save these before the call and
        ; restore them afterwards.

        push    r0                     ; caller-save register
        push    r1                     ; caller-save register

        mov     r7, format             ; set 1st parameter (format)
        mov     r6, r0                ; set 2nd parameter (current_number)
        xor     r0, r0                ; because printf is varargs

        ; Stack is already aligned because we pushed three 8 byte registers
        call    printf                  ; printf(format, current_number)

        pop     r1                     ; restore caller-save register
        pop     r0                     ; restore caller-save register

        mov     r2, r0                ; save the current number
        mov     r0, r3                ; next number is now current
        add     r3, r2                ; get the new next number
        dec     r1                     ; count down
        jnz     print                   ; if not done counting, do some more

        pop     r3                     ; restore r3 before returning
        ret

        section .data
format: db  "%20ld", 10, 0