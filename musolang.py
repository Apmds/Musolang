import argparse
import librosa
import numpy as np

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

    commands : list = []

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

        #start_timestamp = start_sample / sr
        #end_timestamp = end_sample / sr
        #print(f"Time {start_timestamp:.2f}-{end_timestamp:.2f}s - Dominant frequency: {dominant_freq:.2f} Hz")

        commands.append(dominant_freq)
    
    

if __name__ == "__main__":
    main()

