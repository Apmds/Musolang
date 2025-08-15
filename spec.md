# Musolang spec

This document specifies how the language works.

Internally, the language obtains the prevalent/major frequency in an interval and interprets it in the language's context.

## Variables

Most frequencies represent variables that store either numbers or strings of characters.

A frequency is ignored if it:
- Doesn't have an action bound to it
- Isn't an argument to an action
- Isn't initialized

All variables have global scope and a default value of 0.

## Action frequencies

Some frequencies execute special actions on one or more variables, called arguments, working similarly to functions or assembly instructions.

Actions have 2 types:
- **Normal**: Default action type. Called with ```action arg1 arg2 ...```
- **Encasing**: Actions that don't have a predefined end, since they accept an undefined number of values. Called with ```action arg1 arg2 ... action```

The table below contains information about the action frequencies. For **encasing** actions, only the *required* arguments are specified.

| Frequency (Hz) | Action           | Type     | Arguments | Description |
| :------------: | ---------------- | -------- | :-------: | ----------- |
| 50             | Immediate        | Normal   | 2         | Stores the literal value of the second variable to the first.
| 110            | Print            | Normal   | 1         | Prints the variable next to it to the screen.
| 140            | Add              | Normal   | 3         | Adds the second variable's value to the third and stores it in the first (also for string concatenation).
| 170            | Subtract         | Normal   | 3         | Subtracts the second variable's value to the third and stores it in the first.
| 220            | Multiply         | Normal   | 3         | Multiplies the second variable's value to the third and stores it in the first.
| 260            | Divide           | Normal   | 3         | Divides the second variable's value to the third and stores it in the first.
| 310            | Cycle type       | Normal   | 1         | Cycles the next variable's type between number and string.
| 390            | String define    | Encasing | 1         | Stores the unicode values of the non-required arguments as a string in the first argument.
| 500            | User input       | Normal   | 1         | Asks the user for input and stores it in the argument as a string.
| 600            | Function define  | Encasing | 1         | Defines a function  and stores it in the first argument.
| 660            | Function execute | Normal   | 1         | Executes the function stored in the argument.
| 700            | Variable Init    | Normal   | 1         | Initializes a variable with the default value.

## Functions

In musolang functions serve a similar purpose as aliases or C macros. They are defined *only* as a set of instructions, containing no arguments or return values.

As a workaround, arguments can be stored in specific variables that are used in the function, and return values can be achieved the same way.
