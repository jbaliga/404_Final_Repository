import pyaudio
import threading
import time
import cv2

#from EC_FUNCTION import *
from ENV_CORRECT import *

frames = []

def vrCollect():
    counter = 0
    while True:
        record_system_audio() #bit of overlap when writting
        if counter == 0:
            appendAudio(["out.wav"], vrWav)
            counter += 1
        else:
            appendAudio([vrWav, "out.wav"], vrWav)
        
        if (audioDurationMS(vrWav) > 20 * 1000):
            clipAudio(vrWav, vrWav, (audioDurationMS(vrWav) - (20 * 1000)), audioDurationMS(vrWav))

        #print("vrIteration")
        key = cv2.waitKey(0)
        #print(key)  # Print the key code
        if key == ord("q"):
            break

def micCollect():
    global frames
    #global numpyFrames

    while True:
        micData = (stream.read(CHUNK))
        frames.append(np.frombuffer(micData, dtype=np.float64))
        #numpyFrames = np.hstack(frames)
        #print("frames lots " + str(len(frames)))

        if (len(frames) > (20 * RATE)): #(20 * int(RATE / CHUNK * 1))): #removing too much?
            frames = [(len(frames) - 1 - (20 * RATE)), (len(frames) - 1)]
            print("frames woo " + str(len(frames)))

        #print("micIteration")
        key = cv2.waitKey(0)
        #print(key)  # Print the key code
        if key == ord("q"):
            break

#environmental correction while setup
lat = None #get from latency while

p = pyaudio.PyAudio()
stream = p.open(format = pyaudio.paFloat32, channels = 1, rate = RATE, input = True, frames_per_buffer = CHUNK) #output=False

output_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, output=True, frames_per_buffer= CHUNK)

print(sc.default_speaker().name)
# clear/declare vrWav file so there are no onsets
silent_audio = AudioSegment.silent(duration=1000)
silent_audio.export("vrWav.wav", format="wav")
vrWav = 'vrWav.wav'

thread1 = threading.Thread(target=vrCollect)
thread2 = threading.Thread(target=micCollect)
thread1.start()
thread2.start()

print("post threads")

#'''
recordData, srRecord = librosa.load(vrWav)
print(librosa.onset.onset_detect(y=recordData, sr=srRecord))
while (len(librosa.onset.onset_detect(y=recordData, sr=srRecord)) < 2):
    time.sleep(0.1)
    recordData, srRecord = librosa.load(vrWav)
    #print("in while")
print(librosa.onset.onset_detect(y=recordData, sr=srRecord))

#latency calculation 
'''
while (lat == None):       
    lat = latency(np.hstack(frames), librosa.load(vrWav)[0], RATE)
print("this is lat" + str(lat))
#sf.write("check.wav", numpyFrames, RATE)
'''
lat = 0
#clip either the front of vr or mic audio
#clipAudio(vrWav, vrWav, (lat * 1000), audioDurationMS(vrWave)) #endTimeMS = starttime + chunk size
#clip frames
ecRun = "ecRun.wav"
while True:
    clipAudio(vrWav, ecRun, (audioDurationMS(vrWav) - lat - 1), (audioDurationMS(vrWav) - lat))
    inversedAudio, audioIncrease = environmentalCorrection(ecRun, np.hstack(frames[(len(frames) - 1 - (int(RATE / CHUNK * 1))) : (len(frames) - 1)])) #most recent second of frames [end - (int(RATE / CHUNK * 1)), end], audio [end - 1 second - latency, end - latency]
    output_stream.write(inversedAudio)

    key = cv2.waitKey(0)
    print(key)  # Print the key code
    if key == ord("q"):
        break

print("uhh hello")
thread1.join()
thread2.join()
print("Hello!!!")
stream.stop_stream()
stream.close()
output_stream.stop_stream()
output_stream.close()
p.terminate()

#chop old audio from threads
#ouput stream for inverse
#correct timing for environmental correction
#change Audio increase for Jaiden output -> 