# `lp` - Loops

One feature noticably missing from ASM is a conditional loop. TGL provides this module with a few simple preset loops.

Using loops will:

1. Spare you the hassle of writing multiple insturctions just to get a loop going
2. Result in more readable assembly

## About loops

Each loop has a starting tag where you define the loop and an ending tag to end it.

E.g.

```
! lp for rax, 0, 10, 1
  ; HERE LOOP BODY
! lp endfor
```

The loop will require a register as a control variable. This register is not saved and it is assumed that you will choose a register you do not need to touch.

Now the loops supported in `lp` module:

## `for`

```
for REG, START, END, CHANGE

register REG - The control register for the loop
int START - The initial value of the register (The lower end of the range)
int END - The upper end of the range (Exclusive)
int CHANGE - Some integer to add to the register
```

A simple for loop. Syntax is similar to the standard for loop.

The closing tag is `endfor`

Example usage:

`Echo numbers 5,4,3,2,1`

```
! lp for r8, 5, 0, -1
  ; Here echo the ASCII value
! lp endfor
```

## `unt`

```
unt REG, FINAL

register REG - The control register for the loop
int FINAL - Loop will continue until REG reaches FINAL value
```

A do..until loop. It will continue executing until `REG` is equal to the `FINAL` value.

You are responsible for the necessary changes to `REG`.

The closing tag is `endunt`

Example usage:

`Go through a NULL-terminated string until it reaches NULL`

```
! unt r8b, 0
  ; Load the character into r8b
! endunt
```
