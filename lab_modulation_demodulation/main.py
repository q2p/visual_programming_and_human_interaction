import cmath
import math
import random

def generic_mod_component(b, i, step, sq):
  component = 1
  for k in range(0, step):
    sub = 2 ** (step - k) if k != 0 else 0
    component *= sub - (1 - 2*b[i + 2*k])
  return math.sqrt(sq) * component
  
def generic_mod(b, i, step, sq):
  re = generic_mod_component(b, i+0, step, sq)
  im = generic_mod_component(b, i+1, step, sq)
  return complex(re, im)

def bpsk(b, i):
  v = math.sqrt(2.0)*(1-2*b[i])
  return complex(v, v)

def qpsk(b, i):
  return generic_mod(b, i, 1, 2.0)

def qam16(b, i):
  return generic_mod(b, i, 2, 10.0)

def qam64(b, i):
  return generic_mod(b, i, 3, 42.0)

def qam256(b, i):
  return generic_mod(b, i, 4, 170.0)

def qam1024(b, i):
  return generic_mod(b, i, 5, 682.0)

def generate(bits):
  b = []
  for i in range(0, bits):
    b.append(random.randint(0, 1))
  return b

def modulate(b, modulator):
  c = []
  for i in range(0, len(b), modulator.step):
    c.append(modulator.func(b, i))
  return c

def demodulate(c, modulator):
  ret = []
  for comp_in in c:
    min_distance_bits = []
    min_distance = 2
    for next_value in range(0, 1 << modulator.step):
      next_bits = []
      for j in range(0, modulator.step):
        next_bits.append((next_value >> j) & 1)
      comp_next = modulator.func(next_bits, 0)
      dx = comp_in.real - comp_next.real
      dy = comp_in.imag - comp_next.imag
      distance = dx * dx + dy * dy
      if distance < min_distance:
        min_distance_bits = next_bits
        min_distance = distance
    ret = ret + min_distance_bits
  return ret

class Modulator:
  def __init__(self, title, step, func):
    self.title = title
    self.step = step
    self.func = func

modulators = [
  Modulator("BPSK", 1, bpsk),
  Modulator("QPSK", 2, bpsk),
  Modulator("16QAM", 4, qam16),
  Modulator("64QAM", 6, qam64),
  Modulator("256QAM", 8, qam256),
  Modulator("1024QAM", 10, qam1024),
]

for modulator in modulators:
  print(modulator.title)
  bits = generate(modulator.step)
  print('modulated:', bits)
  comp = modulate(bits, modulator)
  bits_demod = demodulate(comp, modulator)
  print('demodulated:', bits_demod)
  