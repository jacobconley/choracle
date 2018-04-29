# -*- coding: iso-8859-15 -*-
import wave
import struct
import numpy
import scipy.fftpack 
import sys
import numpy
import bisect
from math import floor
from math import ceil
from math import pow
# from scipy.io import wavfile
# import matplotlib.pyplot as plt

if(len(sys.argv) < 1):
	print('[!] Missing file path argument')
	sys.exit(1)

MAX_FRAMES = 16384
TEMPER = 1.05946309436 # Twelfth root of two

# Musical notes enum as an array, since Python is shit
NOTES 		= [ 'A', 'AB', 'B', 'C', 'CD', 'D', 'DE', 'E', 'F', 'FG', 'G', 'GA' ]; # Neutral names
NOTES_SHP 	= [ 'A', 'A♯', 'B', 'C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯' ]; # As sharps
NOTES_FLT	= [ 'A', 'B♭', 'B', 'C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭' ]; # As flats

class Pitch:
	def __init__(self, frequency, note, octave):
		self.frequency = frequency
		self.note = note
		self.octave = octave


	def Interval(self, ratio, halfsteps):
		return Pitch(self.frequency * ratio,  (self.note + halfsteps) % 12,  int(self.octave + ceil((self.note + halfsteps) / 12)))
	def HalfStep(self):
		return Pitch(self.frequency * TEMPER, (self.note + 1) % 12, int(self.octave + ceil((self.note + 1) / 12)))

	# Made these to facilitate some more advanced musical analysis later on, such as identifying the chord itself 
	#
	def MinorThird():
		return self.Interval(6/5, 3)
	def MajorThird():
		return self.Interval(5/4, 4)
	def PerfectFifth():
		return self.Interval(3/2, 7)
	def Octave():
		return Pitch(self.frequency * 2, self.note, self.octave + 1)

# BASIS is the domain over which we compute the harmonic products.
# Instead of doing it continuously, we do it over discrete musical notes.  We construct this array by iteration
BASIS = [ Pitch(164.813778, 7, 2) ]; # Start with  E2 (164.8Hz)
for i in range(24):
	BASIS.append(BASIS[i].HalfStep())

##
##
##

# Load the file and read its metadata
wav_file = wave.open(sys.argv[-1], 'r')
nchan, swidth, srate, scount, comptype, compname = wav_file.getparams()

# Some additional calculations
nyquist = srate / 2
nframe = scount if scount < MAX_FRAMES else MAX_FRAMES		# Cap the number of frames read to MAX_FRAMES
binwidth = nyquist / nframe									# [Hz] Width of the DFT bin 

print('')
print('Sample width: %d bytes' % swidth)
print('Sample rate:  %d' % srate)

print('Reading %d samples (%f sec)' % (nframe, (float(nframe) / srate)))
print('Nyquist frequency: %f Hz' % nyquist)
print('Fourier bin width: %f Hz' % binwidth)
print('')


# Read the data.
swbits = 8 if swidth == 1 else ((swidth * 8) - 1) 							# [Bits] Sample width is given in bytes.  In .WAV, any sample width greater than 1 byte is signed.
packing = '<%s' % (('H' if swidth == 1 else 'h') * (nframe * nchan))		# .WAV is little-endian.  1-byte samples are unsigned, everything else is signed
data = list(struct.unpack(packing,  wav_file.readframes(nframe)  ))			#
data = [(x / 2**swbits)*2-1 for x in data]									# Normalize the data on [0, 1].  Not strictly necessary, but a good idea
wav_file.close()

# Compute the fourier spectrum of the first channel
# rfft returns only the positive half of the fft output since we have a real-valued signal and the fft is symmetric
# rfft returns a complex array; we take numpy.abs to get a real-valued magnitude array
fourier = numpy.abs(scipy.fftpack.rfft( data[0::nchan] ))	# .WAV stores channels contiguously within each frame, so we just take a slice (every nth element)

# F = K * srate / bins
# K = F * bins / srate

# Return the Fourier bin index associated with a given frequency.
# Singularity: bin(0.0) will return 1, which may not be expected, as bin 0 is the DC offset bin.  Doesn't matter for our purposes
# 
# Understanding this correspondence is a bit tricky because there are a lot of factors of 2 involved
# Given frequency f, bin index i, sampling rate S, sample count N:
# There are N bins on the original spectrum output.  rfft takes only N/2 bins as the output is symmetric for real-valued signals
# Also on the original spectrum output, python gives us a complex array - each bin has two adjacent indices, a real part and a complex part - but we take numpy.abs above
#	So: First 2N total complex output indices.  Then, we take the frequency-positive half, for N indices.  Then we take numpy.abs, for N/2 indices
# 
# Anyways, after we take the abs, there is one index for each bin, which is nice
# So, bins [1, N/2 -1] correspond to frequencies [0, S/2]
#	Remember that S/2 is the Nyquist frequency, which makes sense if you think about it.  Coincidence?????
#
# 
def bin(frequency):
	return int(ceil(frequency * nframe / srate / 2))


# Harmonic Product computation
# It's the geometric mean of the fourier spectrum values over HPDEPTH harmonics.  
HPDEPTH = 5
def HarmonicProduct(basebin):
	res = 0.0
	for i in range(1, HPDEPTH): # Spectrum Depth
		bi = int(basebin * i);
		if(bi > len(fourier)):
			break
		res += fourier[bi]
	return pow(res, 1.0 / HPDEPTH)

#
#
#

# Candidate arrays 
candidateNotes	= []	# [string]	Array of note names
candidateValues	= []	# [float] 	Array of harmonic product values

# Compute the harmonic product for each pitch in our domain
for pitch in BASIS:
	notename = '%s%d' % (NOTES_SHP[pitch.note], pitch.octave)
	s  = HarmonicProduct(bin(pitch.frequency))

	# We use the bisect module to easily keep the candidate arrays sorted
	i = bisect.bisect(candidateValues, s)
	candidateValues.insert(i, s)
	candidateNotes.insert(i, notename)


	print('---')
	print('%s\t %5f Hz\t %2f' % (notename, pitch.frequency, s))

Result = candidateNotes[-5:]

print('')
print('===')
print('Top 5 choices:     %s' % ' '.join(Result))
