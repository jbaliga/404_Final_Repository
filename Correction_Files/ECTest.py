#import pyaudio

#from EC_FUNCTION import *
from Correction_Files.ENV_CORRECT import *

micClip = 'micClip.wav'
m4atowav('MusAm.m4a', micClip)

inData, srIn = librosa.load('clippedAudio.wav')
lat = latency(librosa.load(micClip)[0], inData, RATE)
print("latency is " + str(lat))
#displayWav('clippedAudio.wav')
#displayWav(micClip)
displayWavLines('clippedAudio.wav')
displayWavLines(micClip)
clipAudio(micClip, micClip, (lat * 1000), (lat * 1000 + audioDurationMS('clippedAudio.wav')))
displayWavLines(micClip)
plt.show()

#print(audioDurationMS('clippedAudio.wav'))
#print(audioDurationMS(micClip))

micData, srData = librosa.load(micClip)
inversedAudio, ambientAudio, audioIncrease = environmentalCorrection('clippedAudio.wav', micClip)

print((ambientAudio + inversedAudio))

print("Audio % Increase Matrix")
print(audioIncrease)
print()
print("Average % Increase" + str(averageS(audioIncrease)))

audioTemp= AudioSegment.from_wav('clippedAudio.wav')
antiAudio = AudioSegment(data=inversedAudio.tobytes(), sample_width=audioTemp.sample_width, frame_rate=audioTemp.frame_rate, channels=audioTemp.channels)
inversed = 'inversed.wav'
antiAudio.export(inversed, format="wav")