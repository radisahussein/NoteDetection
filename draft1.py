#-------------------------------------------------#
'''
FINAL PROJECT ANALYSIS OF ALGORITHM
SEMESTER 3 2020-2021


GROUP MEMBERS:

- Radisa Hussein Rachmadi - 2301891752
- Rayhan Ali Darmawan - 
- Rainamira Azzahra - 
- Patrick Alvin - 

'''

import numpy as np
import pyaudio

#---------------INITIALIZING VALUES---------------#

# Initializing values for the range of the note detection

lowestNote = 36
highestNote = 84

# Initializing values for sampling and FFT

samplingFrequency = 22050
sampleFrameSize = 2048
framesPerFFT = 16

#---------------DERIVED QUANTITIES---------------#

samplesPerFFT = sampleFrameSize*framesPerFFT
frequencyStep = float(samplingFrequency) / samplesPerFFT

#---------------LIST OF NOTE NAMES---------------#

noteNames = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

#---------------CONVERSION FUNCTIONS---------------#

'''
The formula for conversion are based on:
https://newt.phys.unsw.edu.au/jw/notes.html
'''

def frequencyToNumber(f):

    #Function to convert frequency to number

    return 12*np.log2(f/440.0) + 69


def numberToFrequency(n):

    #Function to convert number to frequency

    return 2.0**((n-69)/12.0) * 440 


#---------------GET NOTE NAME FUNCTION---------------#

def getNoteName(n):

    #Function to get the note name based on n
    
    return noteNames[n % 12] + str(n/12 - 1)


#---------------MAIN FUNCTION---------------#

def noteToFFT(n):

    #Converting note to FFT

    return numberToFrequency(n)/frequencyStep

# To get the min and max index in FFT of the notes
minIndex = max(0,int(np.floor(noteToFFT(lowestNote-1))))
maxIndex = min(samplesPerFFT, int(np.ceil(noteToFFT(highestNote+1))))

# Allocating space for FFT process
temp = np.zeros(samplesPerFFT, dtype=np.float32)
numberOfFrames = 0

# Initializing pyaudio
stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                channels=1,rate=samplingFrequency,
                                input=True,
                                frames_per_buffer=sampleFrameSize)

#Starting Stream
stream.start_stream()


#Hanning Window Function
window = 0.5 * (1 - np.cos(np.linspace(0,2*np.pi, samplesPerFFT, False)))

print('Sampling Frequency:',samplingFrequency, "Hz")
print('Max Resolution:', frequencyStep,"Hz\n")


while stream.is_active():

    # Shifting the data down and the new data in
    temp[:-sampleFrameSize] = temp[sampleFrameSize:]
    temp[-sampleFrameSize:] = np.frombuffer(stream.read(sampleFrameSize), np.int16)

    # Run the FFT on the windowed buffer
    fft = np.fft.rfft(temp * window)

    # Obtain frequency
    freq = (np.abs(fft[minIndex:maxIndex]).argmax() + minIndex) * frequencyStep

    #Get the note number and nearest note
    n = frequencyToNumber(freq)
    n0 = int(round(n))

    numberOfFrames += 1

    if numberOfFrames >= framesPerFFT:
        print ('Frequency: {:7.2f} Hz   |   Note: {:>3s} {:+.2f}'.format(freq,getNoteName(n0), n-n0))