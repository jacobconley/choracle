# -*- coding: iso-8859-15 -*-
import wave
import struct
import scipy.fftpack 
import sys
import numpy
import bisect
from math import floor
from math import ceil
from math import pow
from numpy.linalg import norm
# from scipy.io import wavfile
# import matplotlib.pyplot as plt

MAX_FRAMES = 16384
TEMPER = 1.05946309436 # Twelfth root of two


# samplerate, data = wavfile.read('gmaj.wav') 		# load the data
# a = data.T[0] 										# this is a two channel soundtrack, I get the first track
# b=[(ele/2**8.)*2-1 for ele in a]					# this is 8-bit track, b is now normalized on [-1,1)

wav_file = wave.open('input.wav', 'r')
nchan, swidth, srate, scount, comptype, compname = wav_file.getparams()
nyquist = floor(srate / 2)

nframe = scount if scount < MAX_FRAMES else MAX_FRAMES
binwidth = nyquist / nframe
swbytes = 8 if swidth == 1 else ((swidth * 8) - 1) # Sample width is in bytes.  In .WAV, any sample width greater than 1 byte is signed.

print('Sample width: %d' % swidth)
print('Sample count: %d' % scount)
print('Sample rate:  %d' % srate)
print('Nyquist frequency: %d' % nyquist)

print('Reading %d samples (%f sec)' % (nframe, (nframe / srate)))
print('Fourier bin width: %f' % binwidth)
print('')

data_raw = wav_file.readframes(nframe)
wav_file.close()

NOTES 		= [ 'A', 'AB', 'B', 'C', 'CD', 'D', 'DE', 'E', 'F', 'FG', 'G', 'GA' ];
NOTES_SHP 	= [ 'A', 'A♯', 'B', 'C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯' ];
NOTES_FLT	= [ 'A', 'B♭', 'B', 'C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭' ];

class Pitch:
	def __init__(self, frequency, note, octave):
		self.frequency = frequency
		self.note = note
		self.octave = octave


	def Interval(self, ratio, halfsteps):
		return Pitch(self.frequency * ratio,  (self.note + halfsteps) % 12,  self.octave + ceil((self.note + halfsteps) / 12))

	def MinorThird():
		return self.Interval(6/5, 3)
	def MajorThird():
		return self.Interval(5/4, 4)
	def PerfectFifth():
		return self.Interval(3/2, 7)
	def Octave():
		return Pitch(self.frequency * 2, self.note, self.octave + 1)

BASIS = [ Pitch(164.813778, 7, 2) ]; # Start with a basis of E2 (164.8Hz), add the rest of the second octave below
for i in range(24):
	BASIS.append(BASIS[i].Interval(TEMPER, 1))


unpstr = '<{0}h'.format(nframe * nchan)
data_unpacked = list(struct.unpack(unpstr, data_raw))
data_chan = data_unpacked[0::nchan]
data_norm = [(x / 2**swbytes)*2-1 for x in data_chan]

#transform = fft(data_norm)
#spectrum = transform[:floor(len(transform) / 2)]
spectrum = scipy.fftpack.rfft(data_norm)

# F = K * srate / bins
# K = F * bins / srate
def bin(frequency):
	return ceil(frequency * nframe / srate)

DEPTH = 5
def HarmonicProductSpectrum(basebin):
	res = 0.0
	for i in range(1, DEPTH): # Spectrum Depth
		bi = int(basebin * i)
		if(bi > len(spectrum)):
			break
		res += norm([spectrum[bi], spectrum[bi + 1]])
	return pow(res, 1.0 / DEPTH)

#
#
#


Candidates = []
HPSpectra  = []

for pitch in BASIS:
	notename = '%s%d' % (NOTES_SHP[pitch.note], pitch.octave)

	basebin = bin(pitch.frequency)
	s    = HarmonicProductSpectrum(basebin)

	i = bisect.bisect(HPSpectra, s)
	HPSpectra.insert(i, s)
	Candidates.insert(i, notename)


	print('---')
	print('%s\t %5f Hz\t %2f' % (notename, pitch.frequency, s))

Result = Candidates[-5:]

print('')
print('===')
print('Results:     %s' % ' '.join(Result))
