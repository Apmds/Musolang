import argparse
import numpy as np
import csv
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
        description="Generates a .wav file based on a CSV file of frequencies and timestamps."
    )
    parser.add_argument("freqs", help="csv file with audio data. Each row follows this format: <start_time(s)>,<frequency(Hz)>,<duration(s)>")
    parser.add_argument("-i", "--ignore", action="store_true", help="Ignore the first row")
    parser.add_argument("-o", "--output", help="Name of output file", default="tones.wav")
    parser.add_argument("-d", "--duration", type=int, required=True, help="Time duration of file, in seconds")
    parser.add_argument("-s", "--sample", type=int, help="Outputs sample rate in Hz.", default=44100)

    args = parser.parse_args()


    # Settings
    sample_rate = args.sample
    file_duration = args.duration
    output = np.zeros(int(sample_rate * file_duration))  # silent base track

    with open(args.freqs, "r") as csvfile:
        reader = csv.reader(csvfile)

        for i, row in enumerate(reader):
            if i == 0 and args.ignore:
                continue
            
            if len(row) != 3:
                print(f"Wrong row formatting in row {i}: Invalid number of arguments")
                exit(1)
            
            try:
                start_time = float(row[0])
                freq = float(row[1])
                duration = float(row[2])

                # Add tones at specific times
                add_tone(start_time=start_time, freq=freq, tone_duration=duration, output=output, sample_rate=sample_rate)

            except ValueError:
                print(f"Wrong row formatting in row {i}: All row elements must be real numbers.")
                exit(1)

    # Normalize to avoid clipping
    output = output / np.max(np.abs(output))

    # Save as .wav
    write(args.output, sample_rate, (output * 32767).astype(np.int16))


if __name__ == "__main__":
    main()