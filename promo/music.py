# Generates a soft synthetic background track (placeholder music) for the promo.
import numpy as np, sys, wave
sr=44100; dur=35.5; n=int(sr*dur); t=np.arange(n)/sr
out=np.zeros(n)
def note(freq,start,length,amp=1.0,kind='pluck'):
    i0=int(start*sr); i1=min(n,int((start+length)*sr)); 
    if i1<=i0: return
    tt=np.arange(i1-i0)/sr
    if kind=='pluck':
        env=np.exp(-tt*3.2)*(1-np.exp(-tt*400))
        w=np.sin(2*np.pi*freq*tt)+0.35*np.sin(2*np.pi*freq*2*tt)*np.exp(-tt*6)+0.12*np.sin(2*np.pi*freq*3*tt)*np.exp(-tt*9)
    else:
        a=min(1.2,length*0.4); env=np.minimum(1,tt/a)*np.minimum(1,(length-tt)/a)
        w=np.sin(2*np.pi*freq*tt)+0.5*np.sin(2*np.pi*freq*2.0*tt+0.3)+0.25*np.sin(2*np.pi*freq*0.5*tt)
        w*= (1+0.08*np.sin(2*np.pi*5.5*tt))  # slow shimmer
    out[i0:i1]+=w*env*amp
# chords: Cmaj7 Am7 Fmaj7 G(add9)  (freqs in Hz)
C=[261.63,329.63,392.0,493.88]; Am=[220.0,261.63,329.63,392.0]; F=[174.61,220.0,261.63,329.63]; G=[196.0,246.94,293.66,440.0]
prog=[C,Am,F,G]
bar=3.55  # seconds per chord
for k in range(int(np.ceil(dur/bar))):
    ch=prog[k%4]; st=k*bar
    for f in ch: note(f/2,st,bar,0.10,'pad')
    # arpeggio plucks, 8 per bar
    step=bar/8
    pat=[0,2,1,3,2,1,3,2]
    for j,pi in enumerate(pat):
        note(ch[pi]*2,st+j*step,step*1.6,0.22)
    if k%2==0: note(ch[0]/2, st, bar, 0.14,'pad')
# simple delay (echo)
d=int(0.27*sr); echo=np.zeros(n); echo[d:]=out[:-d]*0.32; out+=echo
# gentle lowpass via moving average
k=np.ones(9)/9; out=np.convolve(out,k,mode='same')
# fades
fi=int(1.0*sr); fo=int(2.5*sr)
out[:fi]*=np.linspace(0,1,fi); out[-fo:]*=np.linspace(1,0,fo)**1.5
out/=np.max(np.abs(out)); out*=0.45
wav=wave.open(sys.argv[1],'w'); wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(sr)
wav.writeframes((out*32767).astype(np.int16).tobytes()); wav.close(); print('ok')
