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
import wave
import os
#---------------INITIALIZING VALUES---------------#

# Initializing values for the range of the note detection

lowestNote = 36
highestNote = 84

# Initializing values for sampling and FFT

samplingFrequency = 22050
sampleFrameSize = 2048
framesPerFFT = 32

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


def noteToFFT(n):

    #Converting note to FFT

    return numberToFrequency(n)/frequencyStep

#---------------GET NOTE NAME FUNCTION---------------#

def getNoteName(n):

    #Function to get the note name based on n
    
    return noteNames[n % 12] + str(n/12 - 1)

#---------------MAIN FUNCTIONS---------------#

#Function for live detection, stops whenever the user wants
def liveDetection(lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep,duration):

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

    print('\nSampling Frequency:',samplingFrequency, "Hz")
    print('Max Resolution:', frequencyStep,"Hz\n")

    for i in range(0,int(samplingFrequency / sampleFrameSize * duration)):

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

        #Default note when no sound is played or heard by device
        defaultNote = "A#2"

        if numberOfFrames >= framesPerFFT:
            if defaultNote not in getNoteName(n0):
                print ('Frequency: {:7.2f} Hz   |   Note: {:>3s} {:+.2f}'.format(freq,getNoteName(n0), n-n0))

    print("FINISH STREAM")
    stream.stop_stream()
    stream.close()

#Function for recording audio files
def recordNotes(samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep,duration,filename):

    #Initialize Path
    path = 'C:/Users/radis/OneDrive/Desktop/Github/Binus/Final Project/AoA SEM3/FinalProjectAA/recordings/'


    # Initializing pyaudio
    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                    channels=1,rate=samplingFrequency,
                                    input=True,
                                    frames_per_buffer=sampleFrameSize)

    #Starting Stream
    stream.start_stream()

    #Hanning Window Function
    window = 0.5 * (1 - np.cos(np.linspace(0,2*np.pi, samplesPerFFT, False)))
    
    print("----------Now Recording----------\n")

    frames = []
    for i in range (int(samplingFrequency / sampleFrameSize * duration)):
        data = stream.read(sampleFrameSize)
        frames.append(data)
    
    print("----------Finished Recording----------")

    #End stream
    stream.stop_stream()
    stream.close()
    
    #Writing frames to filename
    wf = wave.open(path+filename,"wb")
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(samplingFrequency)
    wf.writeframes(b"".join(frames))
    wf.close()
    
#Function to view audio files recorded and saved by the user
def history(lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep):
    
    #Initialize an array to store all the files
    files = []

    #Path to the audio files
    path = 'C:/Users/radis/OneDrive/Desktop/Github/Binus/Final Project/AoA SEM3/FinalProjectAA/recordings/'

    #Finding files with the .wav extension
    for f in os.listdir(path):
        if f.endswith('.wav'):
            files.append(f)

    #For menu
    print("")
    filecount = 1
    for i in files:
        print(filecount,")",i)
        filecount += 1
    
    print("---------------OPEN FILE---------------")
    filechoice = int(input("Select File (0 to exit this page): "))
    print("---------------------------------------")

    if filechoice < filecount+1:
        if filechoice == 0:
            mainProgram()

        for i in files:
            if files.index(i)+1 == filechoice:
                selectFile(i,lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep)
    else:
        print("Selection doesn't exist!")
        history()

#Function to get notes and frequency of a saved audio file
def analyzeFile(file,lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep):

    #path
    path = "C:/Users/radis/OneDrive/Desktop/Github/Binus/Final Project/AoA SEM3/FinalProjectAA/recordings/"

    #read file
    fileread = wave.open(path+file,'r')

    # To get the min and max index in FFT of the notes
    minIndex = max(0,int(np.floor(noteToFFT(lowestNote-1))))
    maxIndex = min(samplesPerFFT, int(np.ceil(noteToFFT(highestNote+1))))

    # Allocating space for FFT process
    temp = np.zeros(samplesPerFFT, dtype=np.float32)
    numberOfFrames = 0

    #Hanning Window Function
    window = 0.5 * (1 - np.cos(np.linspace(0,2*np.pi, samplesPerFFT, False)))

    #get duration of file
    duration = (fileread.getnframes() / fileread.getframerate())
    print(duration)

    print('Sampling Frequency:',samplingFrequency, "Hz")
    print('Max Resolution:', frequencyStep,"Hz\n")

    for i in range(0,int(samplingFrequency / sampleFrameSize * duration)):

        # Shifting the data down and the new data in
        temp[:-sampleFrameSize] = temp[sampleFrameSize:]
        temp[-sampleFrameSize:] = np.frombuffer(fileread.readframes(sampleFrameSize), np.int16)

        # Run the FFT on the windowed buffer
        fft = np.fft.rfft(temp * window)

        # Obtain frequency
        freq = (np.abs(fft[minIndex:maxIndex]).argmax() + minIndex) * frequencyStep

        #Get the note number and nearest note
        n = frequencyToNumber(freq)
        n0 = int(round(n))

        numberOfFrames += 1

        #Default note when no sound is played or heard by device
        defaultNote = "A#2"

        #Print note names and frequency
        if numberOfFrames >= framesPerFFT:
            if defaultNote not in getNoteName(n0):
                print ('Frequency: {:7.2f} Hz   |   Note: {:>3s} {:+.2f}'.format(freq,getNoteName(n0), n-n0))
    
    selectFile(file,lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep)


def selectFile(f,lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep):

    #path
    path = "C:/Users/radis/OneDrive/Desktop/Github/Binus/Final Project/AoA SEM3/FinalProjectAA/recordings/"

    #Menu for selected audio file
    print("\nFile",f,"selected:\n")
    print("1. Play")
    print("2. Delete")
    print("3. Analyze")
    print("4. Exit")
    print("------------------------------")

    selectChoice = int(input("What to do: "))

    while True:
        if selectChoice == 1:
            
            file = wave.open(path+f, 'rb')

            p = pyaudio.PyAudio()

            stream = p.open(format = pyaudio.paInt16,
                            channels = 1, rate=samplingFrequency,
                            output=True)
            
            data = file.readframes(1024)
            
            print("---------------PLAYING FILE---------------")

            while data:
                stream.write(data)
                data = file.readframes(1024)
            print("---------------END---------------")

            stream.stop_stream()
            stream.close()
            p.terminate()
            selectFile(f,lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep)

        #Deletes the selected file 
        if selectChoice == 2:
            os.remove("C:/Users/radis/OneDrive/Desktop/Github/Binus/Final Project/AoA SEM3/FinalProjectAA/recordings/"+f)
            print("\nFile Deleted!")
            history(lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep)
        
        if selectChoice == 3:
            analyzeFile(f,lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep)

        if selectChoice == 4:
            history(lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep)


#---------------MAIN PROGRAM---------------#

def mainProgram():
    print("---------------NOTE DETECTOR PROGRAM---------------")
    print("1. Live Recording")
    print("2. Record")
    print("3. History")
    print("4. Exit")
    print("---------------------------------------------------")

    selection = input("Choice: ")
    

    while True:

        if selection == '1':
            duration = int(input("Duration: "))
            liveDetection(lowestNote,highestNote,samplesPerFFT,samplingFrequency,sampleFrameSize,frequencyStep,duration)
            mainProgram()

        elif selection == '2':
            duration = int(input("Record Duration: "))
            inputfile = input("Save File as: ")
            filename = inputfile + '.wav'

            if os.path.isfile("C:/Users/radis/OneDrive/Desktop/Github/Binus/Final Project/AoA SEM3/FinalProjectAA/recordings/"+filename):
                print("File name already exists!")
            else:
                recordNotes(samplesPerFFT,samplingFrequency,sampleFrameSize,frequencyStep,duration,filename)

            mainProgram()
        
        elif selection == '3':
            history(lowestNote, highestNote, samplesPerFFT, samplingFrequency, sampleFrameSize, frequencyStep)
            mainProgram()
            

        elif selection == '4':
            exit()
        
        else:
            print("\nSelection does not exist!\n")
            mainProgram()

mainProgram()
