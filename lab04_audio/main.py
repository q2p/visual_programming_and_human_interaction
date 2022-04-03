import random
import numpy as np
import matplotlib.pyplot as pyplot
import scipy.io.wavfile
import sounddevice
import math
import PIL.Image

fs = 44000
sf = 1.0 / float(fs)
pi2 = 2*math.pi
bps = 10

def play_sine(volume, wave, since, until, freq, a, d, s, r):
  for i in range(since, until):
    t = i / fs
    ot = (i - since) / fs
    m = 1
    if ot < a:
      m = ot/a
    elif ot < a+d:
      tr = (a+d-ot)/d
      m = tr + (1-tr) * s
    else:
      m = s

    if until - i <= r * fs:
      m = m * max(0, (until-i)/(r*fs))

    wave[i] += volume * m * math.sin(freq * t * pi2) / freq

def play_bass(volume_bass, volume_noise, wave, since, freq, punch, noise_decay, release):
  for i in range(since, since+int(release*fs)+1):
    t = (i - since) / fs
    exponent = 1 + 1.2 * max(0, 1-t/punch)
    amplitude = math.pow(max(0, 1-t/release), 16.0) / freq
    sine = math.sin(freq * t * pi2 - t * 10)
    sine = math.copysign(math.pow(abs(sine), exponent), sine)
    wave[i] += volume_bass * amplitude * sine
    wave[i] += volume_noise * random.random() * math.pow(max(0, 1-t/noise_decay), 32)


im = PIL.Image.open("notes.png")
pix = im.load()
length, notes = im.size
wave = np.zeros(int(length / bps * fs))
note_ratio = math.pow(2.0, 1.0/12.0)
scales = [55]
seeds = [random.random() * 100]
for y in range(1, notes-1):
  scales.append(scales[len(scales)-1] * note_ratio)
for y in range(0, notes-1):
  freq = scales[y]
  pr, pg, pb = 255, 255, 255
  since = 0
  for x in range(0, length-1):
    r, g, b = pix[x, notes-y-1]
    if r != pr or g != pg or b != pb:
      until = x * (fs // bps)

      if pr == 0 and pg == 0 and pb == 0:
        play_sine(1.0, wave, since, until, freq, 0.15, 0.3, 0.5, 0.15)
      if pr == 255 and pg == 0 and pb == 0:
        play_bass(0.3, 0.0003, wave, since, freq, 0.4, 4.0, 4.0)
      if pr == 0 and pg == 255 and pb == 0:
        play_bass(0.5, 0.0005, wave, since, freq, 0.6, 4.0, 6.0)

      pr, pg, pb = r, g, b
      since = until

wave = wave / wave.max()
scipy.io.wavfile.write("out.wav", fs, wave)

fig, (ax1, ax2) = pyplot.subplots(nrows=2)
ax1.plot(wave)
Pxx, freqs, bins, im = ax2.specgram(wave, NFFT=1024, Fs=fs, noverlap=900)
for ax in fig.axes:
  ax.axis("off")
  ax.margins(0,0)
  ax.xaxis.set_major_locator(pyplot.NullLocator())
  ax.yaxis.set_major_locator(pyplot.NullLocator())
pyplot.subplots_adjust(0,0,1,1,0,0)
sounddevice.play(wave, fs)
pyplot.show()