import argparse
import numpy as np
import re
from scipy.io.wavfile import write

def add_tone(start_time, freq, tone_duration, output, sample_rate, amplitude=0.5):
    '''Adds a tone to output'''

    t = np.linspace(0, tone_duration, int(sample_rate * tone_duration), False)
    tone = amplitude * np.sin(2 * np.pi * freq * t)
    start_index = int(start_time * sample_rate)
    end_index = start_index + len(tone)
    output[start_index:end_index] += tone

def main():
    parser = argparse.ArgumentParser(
        prog="wavgen.py",
        description="Generates a .wav file based on a file of frequencies and timestamps."
    )
    parser.add_argument("freqs", help="file with audio data. Each line is either empty or contains one or more frequencies.")
    parser.add_argument("-i", "--interval", type=float, help="Time that each frequency lasts.", default=1)
    parser.add_argument("-o", "--output", help="Name of output file", default="tones.wav")
    parser.add_argument("-s", "--sample", type=int, help="Outputs sample rate in Hz.", default=44100)

    args = parser.parse_args()

    # Settings
    sample_rate = args.sample
    interval = args.interval

    file_duration : float = 0
    with open(args.freqs, "r") as file:
        for line in file:
            # Ignore empty lines
            if len(line.strip()) == 0:
                continue

            file_duration += interval * len(re.split(" +", line))
    output = np.zeros(int(sample_rate * file_duration))  # silent base track

    start_time = 0.0

    with open(args.freqs, "r") as file:

        for i, line in enumerate(file):
            # Ignore empty lines
            if len(line.strip()) == 0:
                continue
            
            for val in re.split(" +", line):
                try:
                    freq = float(val)

                    # Add tones at specific times
                    add_tone(start_time=start_time, freq=freq, tone_duration=interval, output=output, sample_rate=sample_rate)
                    start_time += interval

                except ValueError:
                    print(f"Wrong line formatting in line {i}: Line must only contain one or more numbers.")
                    exit(1)

    # Normalize to avoid clipping
    output = output / np.max(np.abs(output))

    # Save as .wav
    write(args.output, sample_rate, (output * 32767).astype(np.int16))


if __name__ == "__main__":
    main()