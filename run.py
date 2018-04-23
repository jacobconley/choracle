import wave
import struct
import scipy.fftpack 
from math import floor
# from scipy.io import wavfile
# import matplotlib.pyplot as plt

MAX_FRAMES = 16384


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

def bin_freq(frequency):
	return floor(frequency / binwidth)


unpstr = '<{0}h'.format(nframe * nchan)
data_unpacked = list(struct.unpack(unpstr, data_raw))
data_chan = data_unpacked[0::nchan]
data_norm = [(x / 2**swbytes)*2-1 for x in data_chan]

#transform = fft(data_norm)
#spectrum = transform[:floor(len(transform) / 2)]
spectrum = scipy.fftpack.rfft(data_norm)

# G2 - 98 HZ
g2 = bin_freq(98)
print(spectrum[g2 - 2])
print(spectrum[g2 - 1])
print(spectrum[g2])
print(spectrum[g2 + 1])
print(spectrum[g2 + 2])


# c = fft(b) # calculate fourier transform (complex numbers list)
# d = len(c)/2  # you only need half of the fft list (real signal symmetry)
# plt.plot(abs(c[:(d-1)]),'r') 
# plt.show()