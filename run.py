# -*- coding: iso-8859-15 -*-
import wave
import struct
import scipy.fftpack 
import sys
import numpy
from math import floor
from math import ceil
from numpy.linalg import norm
# from scipy.io import wavfile
# import matplotlib.pyplot as plt

MAX_FRAMES = 16384
TEMPER = 1.05946309436 # Twelfth root of two


# samplerate, data = wavfile.read('gmaj.wav') 		# load the data
# a = data.T[0] 										# this is a two channel soundtrack, I get the first track
# b=[(ele/2**8.)*2-1 for ele in a]					# this is 8-bit track, b is now normalized on [-1,1)

wav_file = wave.open('gmaj.wav', 'r')
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

BASIS = [ Pitch(110, 0, 2) ]; # Start with a basis of A2 (110Hz), add the rest of the second octave below
for i in range(30):
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

def HarmonicProductSpectrum(basebin):
	res = 0.0
	for i in range(1,5): # Spectrum Depth
		bi = basebin * i
		if(bi > len(spectrum)):
			break
		res += norm([spectrum[bi], spectrum[bi + 1]])
	return res

#
#
#

maxf = 0
maxn = "--"
minnz = 0

for pitch in BASIS:
	notename = '%s%d' % (NOTES_SHP[pitch.note], pitch.octave)

	basebin = bin(pitch.frequency)
	s_1  = HarmonicProductSpectrum(basebin - 2)
	s    = HarmonicProductSpectrum(basebin)
	s1   = HarmonicProductSpectrum(basebin + 2)

	#imax = max(s_2, s_1, s, s1, s2)
	imax = s
	if(imax > maxf):
		maxf = imax
		maxn = notename
	if(minnz == 0 or s < minnz):
		minnz = s

	print('---')
	#print('\t\t\t %f' % s_1)
	print('%s\t %5f Hz\t %2f' % (notename, pitch.frequency, s))
	#print('\t\t\t %f' % s1)


sample = filter(lambda x: x > minnz, spectrum)
s_mean 		= numpy.mean(sample)
s_stdev 	= numpy.std(sample)


Candidates = []
for pitch in BASIS:
	if HarmonicProductSpectrum(bin(pitch.frequency)) > (s_mean + 3 * s_stdev):
		Candidates.append(pitch)



print('')
print('===')
print('Maximum:          %s\t%f' % (maxn, maxf))

print('')
print('Nonzero Mean:   %f' % s_mean)
print('Nonzero Stdev:  %f' % s_stdev)

print('')
print('Candidates:  %s' % ' '.join([ ('%s%d' % (NOTES_SHP[x.note], x.octave)) for x in Candidates ]))


# c = fft(b) # calculate fourier transform (complex numbers list)
# d = len(c)/2  # you only need half of the fft list (real signal symmetry)
# plt.plot(abs(c[:(d-1)]),'r') 
# plt.show()