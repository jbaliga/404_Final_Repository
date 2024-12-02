#from EC_FUNCTION import *
import numpy as np
import matplotlib.pyplot as plt
#import time
import librosa, librosa.display
from pydub.utils import mediainfo
from pydub import AudioSegment
import soundfile as sf
import copy
#import sounddevice as sd
import soundcard as sc
import soundfile as sf

#mic audio stream setup1
RATE = 44100
CHUNK = 1024 #RATE

def environmentalCorrection(vrAudio, micAudio, speakerAudios=None, rate=RATE):
  dataVR, srVR = librosa.load(vrAudio) #split original audio into data and sample
  dataMic, srMic = librosa.load(micAudio)

  Svr = returnS(dataVR)
  Smic = returnS(dataMic)

  #Separate ambient noise and speaker audio from mic audio file, still comparing original audio -> dataOrig, srOrig; to testAudio -> dataTest, srTest
  ambientS, speakersComS = seperateAmbient(Smic, Svr)

  #pretty sure this shit is wrong
  #get inverse of ambient noise (this will cancel the ambient noise when played)
  amData = inverseSTFT(ambientS, dataVR) #ipd.Audio(amData, rate=srOrig) #this is what the ambient noise sounds like
  #sf.write("reconAm.wav", amData, srVR) #writes ambient sound to .wav
  speakersData = inverseSTFT(speakersComS, dataVR) #ipd.Audio(speakersData, rate=srOrig) #this is what the speakers are outputing

  '''
  inversedAm = "inversedAM.wav"
  noiseCancelation("reconAm.wav", inversedAm) #this noise cancelation audio file is one of the outputs '''
  inversedAm = noiseCancelation(amData)
  #print(len(amData))

  increaseSpeak = None
  #check if speaker magnitudes are proportional to each other vs original -> if not, per speaker, find difference in magnitude compared to expected (percentage should be fine?)
  if (speakerAudios!=None):
    speakerSList = []
    for speaker in speakerAudios:
      speakerSList.append(returnS(speaker))

      speakerPercentContribution = percentContribution(speakerSList, Svr)

      increaseSpeak.append(perIncrease(speakersComS, Svr)) #percent below that the mic is compared to the original audio
  else:
    increaseSpeak = perIncrease(speakersComS, Svr)

  return inversedAm, amData, increaseSpeak #averageS(increaseSpeak)

#################################################################################################################

def m4atowav(inputFile, outputFile):
    sound = AudioSegment.from_file(inputFile)
    sound.export(outputFile, format="wav")

def audioDurationMS(inputFile):
  info = mediainfo(inputFile)
  fileDur = info['duration']
  return float(fileDur) * 1000

OUTPUT_FILE_NAME = "out.wav" 

def record_system_audio(duration=(1/10), samplerate=RATE, channels=1):                         
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=RATE) as mic:
        data = mic.record(numframes=RATE*duration)
        sf.write(file=OUTPUT_FILE_NAME, data=data[:, 0], samplerate=RATE)

def clipAudio(inputFile, outputFile, startTimeMS, endTimeMS):
  audio = AudioSegment.from_wav(inputFile) #load audio
  clippedAudio = audio[startTimeMS:endTimeMS] #clip audio from start to end time
  clippedAudio.export(outputFile, format="wav") #export clipped audio to new .wav file

def appendAudio(inputFiles, outputFile):
  outputAudio = AudioSegment.empty()
  for inputFile in inputFiles:
    audio = AudioSegment.from_wav(inputFile)
    outputAudio += audio
  outputAudio.export(outputFile, format="wav")

def combineAudio(inputFiles, outputFile): #input files should be same length
  outputAudio = AudioSegment.from_wav(inputFiles[0])
  i = 1
  while i < len(inputFiles):
    audio = AudioSegment.from_wav(inputFiles[i])
    outputAudio = outputAudio.overlay(audio, position=0)
    i += 1
  outputAudio.export(outputFile, format="wav") #this is the problem, why what is it doing

def displayWav(inputFile):
  d, s = librosa.load(inputFile)
  plt.figure(figsize=(14, 5))
  librosa.display.waveshow(d, sr=s) #displays magnitude of audio over time
def displayWavLines(inputFile):
  d, s = librosa.load(inputFile)
  onsetFrames = librosa.onset.onset_detect(y=d, sr=s) #built in onset detection fins frames on onsets
  onsetTime = librosa.frames_to_time(onsetFrames) #get times of onsets
  plt.figure(figsize=(14, 5))
  librosa.display.waveshow(d, sr=s)
  plt.vlines(onsetTime, -0.8, 0.79, color='r', alpha=0.8, label='Onset Times')

def onsetDistanceArray(inputArray, outputArray):
  i = 1
  while i < len(inputArray):
    outputArray.append(inputArray[i] - inputArray[i-1])
    i += 1

def findLatencySpot(timeDist, checkArray): #does smaller combo chunk even work lol
  temp = 0
  i = 0
  while i < len(checkArray):
    j = 0
    temp = checkArray[i]
    while round(temp, 6) < round(timeDist, 6):
      j += 1
      temp = checkArray[i+j]
    if round(temp, 6) == round(timeDist, 6):
      return i #
    i += 1
  return None

def latency(dataT, dataO, sr): #(micAudio, origAudio): #latency calculation, only works in background noise is less than desired audio by a significant amount
  #dataO, srO = librosa.load(origAudio) #getting data and sampling rates
  #dataT, srT = librosa.load(micAudio)
  #onset detection
  ofOrig = librosa.onset.onset_detect(y=dataO, sr=sr)#(y=dataO, sr=srO) #built in onset detection finds frames on onsets
  otOrig = librosa.frames_to_time(ofOrig) #get times of onsets
  ofMic = librosa.onset.onset_detect(y=dataT, sr=sr)#(y=dataT, sr=srT) #built in onset detection fins frames on onsets
  otMic = librosa.frames_to_time(ofMic) #get times of onsets
  #find distance between onsets then find matching onsetDistance between both audio files
  onsetDisArrOrig = []
  onsetDisArrTest = []
  onsetDistanceArray(otOrig, onsetDisArrOrig)
  onsetDistanceArray(otMic, onsetDisArrTest)
  '''
  equivOnsetIndex = findLatencySpot(onsetDisArrOrig[0], onsetDisArrTest)
  return otMic[equivOnsetIndex] - otOrig[0] '''
  try:
    equivOnsetIndex = findLatencySpot(onsetDisArrOrig[0], onsetDisArrTest) #what does this actually throw if nothing is found?
  except:
    return None
  else:
    if (equivOnsetIndex != None):
      equivOnsetIndex = findLatencySpot(onsetDisArrOrig[0], onsetDisArrTest)
      #print("is this really an array" + str(equivOnsetIndex))
      return otMic[equivOnsetIndex] - otOrig[0]
    return None

def returnS(data): #audio
  return librosa.stft(data)

def averageS(inputS):
  ave = 0
  i = 0
  while i < len(inputS):
    j = 0
    while j < len(inputS[i]):
      ave += inputS[i][j]
      j += 1
    i += 1
  return ave / (len(inputS) * len(inputS[0]))

def seperateAmbient(given, original): #needs more work
  amS = copy.deepcopy(given)
  nonAmS = copy.deepcopy(given)
  i = 0
  while i < len(original):
    j = 0
    while j < len(original[i]):
      if given[i][j] == original[i][j]:
        amS[i][j] = 0+0j
      elif given[i][j] < 0:
        nonAmS[i][j] = original[i][j]
      elif given[i][j] <= original[i][j]:
        amS[i][j] = 0+0j
      elif given[i][j] > original[i][j]:
        amS[i][j] -= original[i][j]
        nonAmS[i][j] = original[i][j]
      j += 1
    i += 1
  return [amS, nonAmS]

def inverseSTFT(inputS, referenceData):
  n = len(referenceData)
  #n_fft = 2048
  #pad = librosa.util.fix_length(data, size=(n + n_fft // 2))
  #D = librosa.stft(pad, n_fft=n_fft)
  return librosa.istft(inputS, length=n)

def noiseCancelation(data):
  antiNoise = -1 * data
  return antiNoise

def percentContribution(speakerSs, originalS):
  inputPerContList = []
  for speaker in speakerSs:
    inputS = copy.deepcopy(originalS)
    i = 0
    while i < len(speaker):
      j = 0
      while j < len(speaker[i]):
        inputS[i][j] = speaker[i][j] / originalS[i][j]
        j += 1
      i += 1
    inputPerContList.append(inputS)
  return inputPerContList

def perIncrease(micAudioS, originalS): #
  perIn = copy.deepcopy(originalS)
  i = 0
  while i < len(perIn):
    j = 0
    while j < len(perIn[i]):
      if micAudioS[i][j] !=0:
        perIn[i][j] /= micAudioS[i][j]
        j += 1
      else:
        perIn[i][j] = 1
        j += 1
    i += 1
  return perIn