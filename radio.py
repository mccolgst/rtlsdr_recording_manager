from rtlsdr import RtlSdr
from pylab import psd, xlabel, ylabel, show, imshow, plt
from drawnow import drawnow

sdr = RtlSdr()

sdr.sample_rate = 2.048e6 # Hz
sdr.center_freq = 93.3e6 # Hz
sdr.freq_correction = 60 # PPM?
sdr.gain = 'auto'


plt.ion()

def plot_samples():
    samples = sdr.read_samples(512)

    # use matplotlib to estimate and plot the PSD
    #plt.plot(samples)
    psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Relative power (dB)')
    plt.ylim(-70, 40)

#for x in xrange(0, 10):
while True:
    drawnow(plot_samples)
    #plt.pause(.00000001)
