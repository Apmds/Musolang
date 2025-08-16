from __future__ import annotations
import sys 
import argparse
import librosa
import numpy as np
from enum import Enum

# Action frequencies
FREQ_IMMEDIATE = 50
FREQ_PRINT = 110
FREQ_ADD = 140
FREQ_SUB = 170
FREQ_MULT = 220
FREQ_DIV = 260
FREQ_CYCLE_TYPE = 310
FREQ_STR_DEF = 390
FREQ_INPUT = 500
FREQ_FUNC_DEF = 600
FREQ_FUNC_EXEC = 660
FREQ_VAR_INIT = 700

# Frequency required arguments
FREQ_ARGS = {
    FREQ_IMMEDIATE: 2,
    FREQ_PRINT: 1,
    FREQ_ADD: 3,
    FREQ_SUB: 3,
    FREQ_MULT: 3,
    FREQ_DIV: 3,
    FREQ_CYCLE_TYPE: 1,
    FREQ_STR_DEF: 1,
    FREQ_INPUT: 1,
    FREQ_FUNC_DEF: 1,
    FREQ_FUNC_EXEC: 1,
    FREQ_VAR_INIT: 1,
}

class VariableType(Enum):
    NUMBER = "number"
    STRING = "string"
    FUNCTION = "funtion"

class Action:
    '''Represents one of the action frequencies and their argument data'''
    def __init__(self, frequency : Frequency, arguments : list[Frequency], req_arguments : int):
        self.frequency = frequency
        self.req_arguments = req_arguments
        self.arguments = arguments
    
    def parse_arguments(self, symbol_table : dict[Frequency, Variable], ignore_undefined : bool = True):
        '''Parses the arguments list based on the current state of the symbol table'''
        
        # Set arguments as only the needed ones
        new_args = []
        for arg in self.arguments:
            # In normal frequencies, the only arguments are the required ones
            if len(new_args) >= self.req_arguments and not self.frequency.is_encasing():
                break

            # Handle undefined args
            if (not arg in symbol_table) and ignore_undefined:
                continue
         
            new_args.append(arg)
        
        self.arguments = new_args

        if not self.is_valid():
            print(f"{self.frequency} Hz action has {len(self.arguments)} arguments, when {self.req_arguments} are required.", file=sys.stderr)

    def is_valid(self) -> bool:
        return len(self.arguments) >= self.req_arguments

    def __str__(self):
        return f"Action: {self.frequency} Hz, {self.req_arguments} arguments required, {self.arguments}"

    def __repr__(self):
        return str(self)

class Frequency:
    '''Represents an audio's frequency'''
    def __init__(self, freq : np.float64, timestamp_start : float, timestamp_end : float):
        self.value = freq
        self.timestamp_start = timestamp_start
        self.timestamp_end = timestamp_end
    
    def is_action_frequency(self) -> bool:
        '''Returns True if this is a recognized action frequency'''
        return self.value == FREQ_IMMEDIATE or \
           self.value == FREQ_PRINT or \
           self.value == FREQ_ADD or \
           self.value == FREQ_SUB or \
           self.value == FREQ_MULT or \
           self.value == FREQ_DIV or \
           self.value == FREQ_CYCLE_TYPE or \
           self.value == FREQ_STR_DEF or \
           self.value == FREQ_INPUT or \
           self.value == FREQ_FUNC_DEF or \
           self.value == FREQ_FUNC_EXEC or \
           self.value == FREQ_VAR_INIT
    
    def is_encasing(self) -> bool:
        '''Returns True if this is an encasing frequency'''
        return self.value == FREQ_STR_DEF or \
               self.value == FREQ_FUNC_DEF
    
    def __eq__(self, other):
        if isinstance(other, Frequency):
            return self.value == other.value
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f"{self.value} ({self.timestamp_start:.2f}-{self.timestamp_end:.2f}s)"

class Variable:
    '''Represents an initialized variable'''
    def __init__(self, frequency : Frequency, var_type : VariableType, value : str | np.float64 | list[Action]):
        self.frequency = frequency
        self.type = var_type
        self.value = value
    

    def is_valid(self) -> bool:
        return (self.type == VariableType.NUMBER and type(self.value) == np.float64) or \
               (self.type == VariableType.STRING and type(self.value) == str) or \
               (self.type == VariableType.FUNCTION and isinstance(self.value, list) and all(isinstance(v, Action) for v in self.value))

def print_undefined(var : Variable):
    '''Prints the "undefined variable" error'''
    print(f"Variable {var.frequency} is not defined!", file=sys.stderr)


def execute_immediate(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_IMMEDIATE action'''
    arg_store = action.arguments[0]
    arg_val = action.arguments[1]

    if not arg_store in symbol_table:
        print_undefined(arg_store)
        exit(1)

    if symbol_table[arg_store].type != VariableType.NUMBER:
        print(f"Cannot store a {VariableType.NUMBER} value on a {symbol_table[arg_store].type} variable (variable {arg_store})", file=sys.stderr)
        exit(1)
    
    symbol_table[arg_store].value = arg_val.value

def execute_print(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_PRINT action'''
    arg0 = action.arguments[0]
    if symbol_table[arg0].type == VariableType.FUNCTION:
        print(f"Cannot print a function (variable {arg0})", file=sys.stderr)
        exit(1)
    
    print(symbol_table[arg0].value)

def execute_add(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_ADD action'''
    arg_store = action.arguments[0]
    arg_left = action.arguments[1]
    arg_right = action.arguments[2]

    # All types must be equal
    if symbol_table[arg_store].type != symbol_table[arg_left].type or \
        symbol_table[arg_store].type != symbol_table[arg_right].type:
        print(f"Addition between types {symbol_table[arg_left].type} and {symbol_table[arg_right].type} cannot be stored in {symbol_table[arg_store].type} variable.", file=sys.stderr)
        exit(1)

    # Cannot add functions
    if symbol_table[arg_store].type == VariableType.FUNCTION or \
        symbol_table[arg_left].type == VariableType.FUNCTION or \
        symbol_table[arg_right].type == VariableType.FUNCTION:
        print(f"Addition action is not supported between types {symbol_table[arg_left].type} and {symbol_table[arg_right].type}.", file=sys.stderr)
        exit(1)
    
    # Strings can be added (concatenated) as well
    symbol_table[arg_store].value = symbol_table[arg_left].value + symbol_table[arg_right].value

def execute_sub(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_SUB action'''
    arg_store = action.arguments[0]
    arg_left = action.arguments[1]
    arg_right = action.arguments[2]

    # Can only work with numbers
    if symbol_table[arg_store].type != VariableType.NUMBER or \
        symbol_table[arg_left].type != VariableType.NUMBER or \
        symbol_table[arg_right].type != VariableType.NUMBER:
        print(f"Subtraction action is not supported between types {symbol_table[arg_left].type} and {symbol_table[arg_right].type}.", file=sys.stderr)
        exit(1)
    
    symbol_table[arg_store].value = symbol_table[arg_left].value - symbol_table[arg_right].value

def execute_mult(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_MULT action'''
    arg_store = action.arguments[0]
    arg_left = action.arguments[1]
    arg_right = action.arguments[2]

    # Can only work with numbers
    if symbol_table[arg_store].type != VariableType.NUMBER or \
        symbol_table[arg_left].type != VariableType.NUMBER or \
        symbol_table[arg_right].type != VariableType.NUMBER:
        print(f"Multiplication action is not supported between types {symbol_table[arg_left].type} and {symbol_table[arg_right].type}.", file=sys.stderr)
        exit(1)
    
    symbol_table[arg_store].value = symbol_table[arg_left].value * symbol_table[arg_right].value

def execute_div(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_DIV action'''
    arg_store = action.arguments[0]
    arg_left = action.arguments[1]
    arg_right = action.arguments[2]

    # Can only work with numbers
    if symbol_table[arg_store].type != VariableType.NUMBER or \
        symbol_table[arg_left].type != VariableType.NUMBER or \
        symbol_table[arg_right].type != VariableType.NUMBER:
        print(f"Division action is not supported between types {symbol_table[arg_left].type} and {symbol_table[arg_right].type}.", file=sys.stderr)
        exit(1)
    
    if arg_right == 0:
        print(f"Cannot divide by 0.", file=sys.stderr)
        exit(1)
    
    symbol_table[arg_store].value = symbol_table[arg_left].value / symbol_table[arg_right].value

def execute_cycle_type(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_CYCLE_TYPE action'''
    arg0 = action.arguments[0]

    match symbol_table[arg0].type:
        case VariableType.NUMBER: # Convert to string
            symbol_table[arg0].type = VariableType.STRING
            symbol_table[arg0].value = str(symbol_table[arg0].value)
        case VariableType.STRING: # Try to convert to number
            symbol_table[arg0].type = VariableType.NUMBER
            try:
                symbol_table[arg0].value = str(symbol_table[arg0].value)
            except ValueError:
                print(f"Cannot convert \"{symbol_table[arg0].value}\" to {VariableType.NUMBER}.", file=sys.stderr)
                exit(1)

        case _: # Error
            print(f"Type {symbol_table[arg0].type} cannot be used in cycle type action.", file=sys.stderr)
            exit(1)

def execute_str_def(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_STR_DEF action'''

def execute_input(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_INPUT action'''
    arg0 = action.arguments[0]

    if symbol_table[arg0].type != VariableType.STRING:
        print(f"Input instruction must store the value in a {VariableType.STRING} variable, got {symbol_table[arg0].type}.", file=sys.stderr)
        exit(1)
    
    symbol_table[arg0].value = input()

def execute_func_def(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_FUNC_DEF action'''

def execute_func_exec(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_FUNC_EXEC action'''

def execute_var_init(action : Action, symbol_table : dict[Frequency, Action]):
    '''Executes the FREQ_VAR_INIT action'''
    arg0 = action.arguments[0]
    # Cannot define a variable twice
    if arg0 in symbol_table:
        print(f"Variable {arg0} was defined twice!", file=sys.stderr)
        exit(1)
    
    symbol_table[arg0] = Variable(arg0, VariableType.NUMBER, 0)

def main():
    parser = argparse.ArgumentParser(
        prog="musolang.py",
        description="An interpreter that executes music."
    )
    parser.add_argument("filename", help="audio file to be executed")
    parser.add_argument("-i", "--interval", type=float, default=1, help="size of time intervals where commands are read (in seconds)")

    args = parser.parse_args()

    file_path = args.filename
    chunk_duration = args.interval

    # Load audio file
    y, sr = librosa.load(file_path, sr=None)

    # Set chunk size in seconds
    chunk_samples = int(chunk_duration * sr)

    frequencies : list[Frequency] = []

    # Loop through audio in chunks
    for start_sample in range(0, len(y), chunk_samples):
        end_sample = start_sample + chunk_samples
        chunk = y[start_sample:end_sample]

        # Skip if chunk is empty (happens at end of file)
        if len(chunk) == 0:
            continue

        # FFT
        fft_result = np.fft.fft(chunk)
        fft_magnitude = np.abs(fft_result)[:len(fft_result)//2]
        freqs = np.fft.fftfreq(len(chunk), d=1/sr)[:len(chunk)//2]

        # Find dominant frequency
        dominant_freq = freqs[np.argmax(fft_magnitude)]

        start_timestamp = start_sample / sr
        end_timestamp = end_sample / sr
        #print(f"Time {start_timestamp:.2f}-{end_timestamp:.2f}s - Dominant frequency: {dominant_freq:.2f} Hz")

        frequencies.append(Frequency(dominant_freq, start_timestamp, end_timestamp))
    
    # Parse the frequencies as actions
    actions : list[Action] = []
    
    i : int = 0
    while i < len(frequencies):
        freq = frequencies[i]
        if freq.is_action_frequency():
            args : list[np.float64] = []
            i += 1
            while i < len(frequencies):
                arg = frequencies[i]
                if arg.is_action_frequency() and not freq.is_encasing():
                    break

                if freq == arg and freq.is_encasing():
                    i += 1
                    break
                    
                args.append(arg)
                i += 1
            
            actions.append(Action(freq, args, FREQ_ARGS[freq.value]))
        else:
            i += 1

    symbol_table : dict[Frequency, Variable] = {}

    #print(*actions, sep="\n")

    for action in actions:
        ignore_undefined = not action.frequency.is_encasing() and not action.frequency.value == FREQ_VAR_INIT and not action.frequency.value == FREQ_IMMEDIATE
        action.parse_arguments(symbol_table, ignore_undefined=ignore_undefined)

        #print(symbol_table)
        #print(action)
        if not action.is_valid():
            exit(1)

        # Match statement is gay and doesn't work here
        if action.frequency.value == FREQ_IMMEDIATE:
            execute_immediate(action, symbol_table)
        
        elif action.frequency.value == FREQ_PRINT:
            execute_print(action, symbol_table)    
        
        elif action.frequency.value == FREQ_ADD:
            execute_add(action, symbol_table)

        elif action.frequency.value == FREQ_SUB:
            execute_sub(action, symbol_table)

        elif action.frequency.value == FREQ_MULT:
            execute_mult(action, symbol_table)

        elif action.frequency.value == FREQ_DIV:
            execute_div(action, symbol_table)

        elif action.frequency.value == FREQ_CYCLE_TYPE:
            execute_cycle_type(action, symbol_table)

        elif action.frequency.value == FREQ_STR_DEF:
            execute_str_def(action, symbol_table)

        elif action.frequency.value == FREQ_INPUT:
            execute_input(action, symbol_table)

        elif action.frequency.value == FREQ_FUNC_DEF:
            execute_func_def(action, symbol_table)

        elif action.frequency.value == FREQ_FUNC_EXEC:
            execute_func_exec(action, symbol_table)
        
        elif action.frequency.value == FREQ_VAR_INIT:
            execute_var_init(action, symbol_table)
            


if __name__ == "__main__":
    main()

