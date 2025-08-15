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
    NUMBER = 1
    STRING = 2
    FUNCTION = 3

class Action:
    '''Represents one of the action frequencies and their argument data'''
    def __init__(self, frequency : np.float64, arguments : list[np.float64], req_arguments : int):
        self.frequency = frequency
        self.req_arguments = req_arguments
        self.arguments = arguments
    
    def __str__(self):
        return f"Action: {self.frequency} Hz, {self.req_arguments} arguments required, {self.arguments}"

    def __repr__(self):
        return str(self)
    

class Variable:
    '''Represents an initialized variable'''
    def __init__(self, frequency : np.float64, var_type : VariableType, value : str | float):
        self.frequency = frequency
        self.type = var_type
        self.value = value
    

    def is_valid(self) -> bool:
        return (self.type == VariableType.NUMBER and type(self.value) == float) or \
               (self.type == VariableType.STRING and type(self.value) == str)

def is_action_frequency(freq) -> bool:
    '''Returns True if freq is a recognized action frequency'''
    return freq == FREQ_IMMEDIATE or \
           freq == FREQ_PRINT or \
           freq == FREQ_ADD or \
           freq == FREQ_SUB or \
           freq == FREQ_MULT or \
           freq == FREQ_DIV or \
           freq == FREQ_CYCLE_TYPE or \
           freq == FREQ_STR_DEF or \
           freq == FREQ_INPUT or \
           freq == FREQ_FUNC_DEF or \
           freq == FREQ_FUNC_EXEC or \
           freq == FREQ_VAR_INIT

def is_encasing_frequency(freq) -> bool:
    '''Returns True if freq is an encasing frequency'''
    return freq == FREQ_STR_DEF or \
           freq == FREQ_FUNC_DEF

def main():
    parser = argparse.ArgumentParser(
        prog="musolang.py",
        description="An interpreter that executes music."
    )
    parser.add_argument("filename", help="audio file to be executed")
    parser.add_argument("-i", "--interval", type=float, default=0.1, help="size of time intervals where commands are read (in seconds)")

    args = parser.parse_args()

    file_path = args.filename
    chunk_duration = args.interval

    # Load audio file
    y, sr = librosa.load(file_path, sr=None)

    # Set chunk size in seconds
    chunk_samples = int(chunk_duration * sr)

    frequencies : list[np.float64] = []

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
        print(f"Time {start_timestamp:.2f}-{end_timestamp:.2f}s - Dominant frequency: {dominant_freq:.2f} Hz")

        frequencies.append(dominant_freq)
    
    # Parse the frequencies as actions
    actions : list[Action] = []
    
    i : int = 0
    while i < len(frequencies):
        freq = frequencies[i]
        if is_action_frequency(freq):
            args : list[np.float64] = []
            i += 1
            while i < len(frequencies):
                arg = frequencies[i]
                if is_action_frequency(arg) and not is_encasing_frequency(freq):
                    break

                if freq == arg and is_encasing_frequency(freq):
                    i += 1
                    break
                    
                args.append(arg)
                i += 1
            
            actions.append(Action(freq, args, FREQ_ARGS[freq]))
        else:
            i += 1

    print(*actions, sep="\n")



if __name__ == "__main__":
    main()

