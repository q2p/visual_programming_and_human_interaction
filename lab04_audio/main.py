import random
import numpy as np
import matplotlib.pyplot as pyplot
import scipy.io.wavfile
import sounddevice
import math
import PIL.Image


fs = 11000
sf = 1.0 / float(fs)
pi2 = 2*math.pi
pi05 = 0.5*math.pi
pf_falloff = pow(0.5, 4000*sf)
bps = 10

def playback(pcm):
  pcm = pcm / pcm.max()
  scipy.io.wavfile.write("out.wav", fs, pcm)

  # fig, (ax1, ax2) = pyplot.subplots(nrows=2)
  # ax1.plot(pcm)
  # Pxx, freqs, bins, im = ax2.specgram(pcm, NFFT=1024, Fs=fs, noverlap=900)
  # for ax in fig.axes:
  #   ax.axis('off')
  #   ax.margins(0,0)
  #   ax.xaxis.set_major_locator(pyplot.NullLocator())
  #   ax.yaxis.set_major_locator(pyplot.NullLocator())
  # pyplot.subplots_adjust(0,0,1,1,0,0)
  # sounddevice.play(pcm, fs, blocking)
  # pyplot.show()
  sounddevice.play(pcm, fs, blocking=True)

class HPF:
  pfa = 0.0
  prs = 0.0
  def filter(self, rs, cutoff):
    RC = 1.0/(pi2*max(0.000001,abs(cutoff)))
    alpha = RC/(RC+sf)
    fa = alpha * (self.pfa + rs - self.prs)
    self.prs = rs
    return fa

class LPF:
  pfa = 0.0
  def filter(self, rs, cutoff):
    RC = 1.0/(pi2*max(0.000001,abs(cutoff)))
    alpha = sf/(RC+sf)
    fa = self.pfa + (alpha * (rs - self.pfa))
    return fa

class Track:
  pcm = np.zeros(1)
  def __init__(self, duration):
    self.pcm = np.zeros(int(duration * fs))

class Sine:
  def play(self, t, freq):
    return math.sin((freq * t) * pi2)

class Triangle:
  def play(self, t, freq):
    t = freq * t
    return 4 * abs((t - int(t)) - 0.5) - 1

class Square:
  def play(self, t, freq, window):
    t = freq * t
    return 1 if t - int(t) < window else -1

class Saw:
  def play(self, t, freq):
    t = freq * t
    return 2 * (t - int(t)) - 1

def sqmm(freq, phase, min, max, window, t):
  t = phase + freq * t
  return max if t - int(t) < window else min

def sin(freq, phase, t):
  return math.sin(phase + pi2 * freq * t)

def map(v, f1, f2, t1, t2):
  return t1 + (t2 - t1) * (v - f1) / (f2 - f1)

def map11(v, t1, t2):
  return t1 + (t2 - t1) * (1 + v) * 0.5

def map10(v, t1, t2):
  return t1 + (t2 - t1) * v

def map1101(v):
  return (1 + v) * 0.5

def sin_range(freq, phase, min, max, t):
  return map11(sin(freq, phase, t), min, max)

def half_step(freq, phase, t):
  step = sqmm(freq/2, 0, 1, 2, 1/2, t)
  return sin(freq * step, phase, t)

def pm(freq1, freq2, phase1, phase2, scale, t):
  return math.sin(phase1 + freq1 * pi2 * t + scale * math.sin(phase2 + freq2 * pi2 * t))

def eoe(t, duration, apow, fmax, fpow):
  t = max(0.0, min(1.0, t/duration))
  a = math.pow(1-t, apow)
  return a * math.sin(fmax * pi2 * math.pow(math.sin(t*pi05), fpow))

sine = Track(0.2)
for i in range(0, sine.pcm.size-1):
  t = i/fs
  sine.pcm[i] = 0.1*half_step(100, 0, t)

sine = Track(2.0)
for i in range(0, sine.pcm.size-1):
  t = i/fs
  r = 1 - math.pow(t * 0.5, 2)
  v = sin(200, 0.0, t)
  a = math.pow(abs(v), r)
  sine.pcm[i] = 0.1 * math.copysign(a, v) * math.pow(0.1, 1-r)

sine = Track(0.2)
for i in range(0, sine.pcm.size-1):
  t = i/fs
  # sine.pcm[i] += 0.1 * pm(100, 800, 0, 0, 0.3, t)
  sine.pcm[i] += 0.1 * pm(100, 100/2, 0, 0, 1, t)
  # sine.pcm[i] += 0.1 * pm(20, 200, 0, 0, 0.1, t)

hpf = HPF()
sine = Track(10)
for i in range(0, sine.pcm.size-1):
  t = i/fs
  c = map1101(math.cos(pi2*t/5))
  c = map10(math.pow(c, 0.4), 0, 2**23)
  sine.pcm[i] += 0.5 * hpf.filter(random.random(), c)

lpf = LPF()
sine = Track(5)
for i in range(0, sine.pcm.size-1):
  off = 0.1
  t = i/fs - off
  r = 0
  if t > 0:
    c = max(0,map10(pow(t/1, 0.005), 2000, 0))
    sine.pcm[i] += 0.4 * lpf.filter(random.random(), c)
    sine.pcm[i] += 0.5 * eoe(t, 2, 6, 80, 0.8)

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

inst = Sine()
im = PIL.Image.open("notes.png")
pix = im.load()
length, height = im.size
sine = Track(length // bps)
ratio = math.pow(2.0, 1.0/12.0)
scales = [55]
seeds = [random.random() * 100]
for y in range(1, height-1):
  scales.append(scales[len(scales)-1] * ratio)
  seeds.append(random.random() * 100)
for y in range(0, height-1):
  freq = scales[y]
  pr, pg, pb = 255, 255, 255
  since = 0
  for x in range(0, length-1):
    r, g, b = pix[x, height-y-1]
    if r != pr or g != pg or b != pb:
      until = x * (fs // bps)

      if pr == 0 and pg == 0 and pb == 0:
        play_sine(1.0, sine.pcm, since, until, freq, 0.15, 0.3, 0.5, 0.15)
      if pr == 255 and pg == 0 and pb == 0:
        play_bass(0.6, 0.0005, sine.pcm, since, freq, 0.4, 4.0, 4.0)
      if pr == 0 and pg == 255 and pb == 0:
        play_bass(1.0, 0.001, sine.pcm, since, freq, 0.6, 4.0, 6.0)

      pr, pg, pb = r, g, b
      since = until

playback(sine.pcm)
