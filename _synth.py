# -*- coding: utf-8 -*-
# 東方系オリジナルBGM合成エンジン（完全オリジナル作曲・既存曲の流用なし）
# レシピ準拠: A minor中心 / Am->G->F->E系下降進行 / G#->A解決 / ZUNペット風リード
import numpy as np, wave, sys

SR = 22050
def t_arr(n): return np.arange(n)/SR

NB = {'C':0,'C#':1,'Db':1,'D':2,'D#':3,'Eb':3,'E':4,'F':5,'F#':6,'Gb':6,
      'G':7,'G#':8,'Ab':8,'A':9,'A#':10,'Bb':10,'B':11}
def midi(name, octv): return NB[name] + 12*(octv+1)
def mf(m): return 440.0*2**((m-69)/12.0)

QUAL = {'':[0,4,7],'maj':[0,4,7],'m':[0,3,7],'min':[0,3,7],'dim':[0,3,6],
        '7':[0,4,7,10],'maj7':[0,4,7,11],'m7':[0,3,7,10],'min7':[0,3,7,10],
        'm7b5':[0,3,6,10],'7b5':[0,4,6,10]}

def parse_chord(sym):
    # returns (root_pc, intervals, bass_pc)
    bass=None
    if '/' in sym:
        sym,b=sym.split('/'); bass=NB[b]
    i=1
    if len(sym)>1 and sym[1] in '#b': i=2
    root=sym[:i]; qual=sym[i:]
    iv=QUAL.get(qual,[0,4,7])
    rpc=NB[root]
    if bass is None: bass=rpc
    return rpc, iv, bass

# ---------- instruments ----------
def adsr(n,a,d,s,r):
    a=int(a*SR); d=int(d*SR); r=int(r*SR)
    a=max(a,1); d=max(d,1); r=max(r,1)
    sus=max(n-a-d-r,0)
    env=np.concatenate([
        np.linspace(0,1,a,endpoint=False),
        np.linspace(1,s,d,endpoint=False),
        np.full(sus,s),
        np.linspace(s,0,r)])
    if len(env)<n: env=np.concatenate([env,np.zeros(n-len(env))])
    return env[:n]

def saw(f,n):
    ph=np.cumsum(np.full(n,f/SR)); return 2*(ph-np.floor(ph+0.5))
def squ(f,n,duty=0.5):
    ph=np.cumsum(np.full(n,f/SR))%1.0; return np.where(ph<duty,1.0,-1.0)
def sine(f,n):
    return np.sin(2*np.pi*f*t_arr(n))
def tri(f,n):
    ph=np.cumsum(np.full(n,f/SR))%1.0; return 4*np.abs(ph-0.5)-1

def lp1(x,cut):  # simple one-pole lowpass
    a=np.exp(-2*np.pi*cut/SR); y=np.zeros_like(x); p=0.0
    for i in range(len(x)):
        p=(1-a)*x[i]+a*p; y[i]=p
    return y
def lp_fast(x,cut):  # vectorized approx one-pole via lfilter-like cumulative
    a=np.exp(-2*np.pi*cut/SR)
    # iterative but in numpy with scipy unavailable -> use recursive python only for short; fallback
    b=1-a
    y=np.empty_like(x); acc=0.0
    # use np for speed via manual loop in chunks is slow; use lfilter if scipy present
    try:
        from scipy.signal import lfilter
        return lfilter([b],[1,-a],x)
    except Exception:
        for i in range(len(x)):
            acc=b*x[i]+a*acc; y[i]=acc
        return y

def zunpet(f,n,vel=1.0):
    # 強アタック・高音鋭い・ビブラート強めのシンセブラス/トランペット
    vib=1+0.012*np.sin(2*np.pi*5.6*t_arr(n)+np.random.rand()*6)
    fa=f*vib
    ph=np.cumsum(fa/SR)
    s=2*(ph-np.floor(ph+0.5))                  # saw
    sq=np.where((ph%1.0)<0.5,1.0,-1.0)         # square
    w=0.65*s+0.35*sq
    w=np.tanh(w*1.8)                            # 軽いオーバードライブ＝チープさ
    env=adsr(n,0.012,0.10,0.78,0.09)
    return w*env*vel

def piano(f,n,vel=1.0):
    # 倍音を足した減衰音（16分アルペジオ用）
    out=np.zeros(n); t=t_arr(n)
    for k,amp in [(1,1.0),(2,0.45),(3,0.22),(4,0.12),(5,0.06)]:
        out+=amp*np.sin(2*np.pi*f*k*t)
    env=np.exp(-t*5.5)*adsr(n,0.002,0.02,0.7,0.05)
    return out*env*vel*0.7

def strings(f,n,vel=1.0):
    # デチューン重ねたsawのパッド
    out=np.zeros(n)
    for det in (-0.16,-0.06,0.06,0.16):
        out+=saw(f*2**(det/12),n)
    out/=4
    env=adsr(n,0.10,0.15,0.85,0.18)
    return out*env*vel*0.5

def bell(f,n,vel=1.0):
    t=t_arr(n)
    out=np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.76*t)+0.25*np.sin(2*np.pi*f*5.4*t)
    return out*np.exp(-t*7)*vel*0.5

def bassv(f,n,vel=1.0):
    w=0.7*squ(f,n,0.5)+0.3*saw(f,n)
    env=adsr(n,0.004,0.05,0.7,0.04)
    y=w*env*vel
    return y

def kick(n,vel=1.0):
    t=t_arr(n); f=110*np.exp(-t*30)+45
    y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
    return np.tanh(y*1.5)*vel
def snare(n,vel=1.0):
    t=t_arr(n)
    no=(np.random.rand(n)*2-1)*np.exp(-t*22)
    to=np.sin(2*np.pi*190*t)*np.exp(-t*26)*0.5
    return (no*0.9+to)*vel
def hat(n,vel=1.0,op=False):
    t=t_arr(n)
    no=(np.random.rand(n)*2-1)*np.exp(-t*(40 if not op else 14))
    # crude highpass: differentiate
    no=np.diff(no,prepend=0)
    return no*vel*0.6

# ---------- light reverb ----------
def reverb(x,mix=0.18):
    out=x.copy()
    for d,g in [(0.029,0.5),(0.037,0.42),(0.041,0.36),(0.053,0.3)]:
        di=int(d*SR); e=np.zeros(len(x)+di); e[di:]=x*g; out=out+e[:len(x)]
    return (1-mix)*x+mix*out

# ---------- sequencer ----------
class Track:
    def __init__(self,bpm,bars_chords,seed=0,style='boss'):
        self.bpm=bpm; self.prog=bars_chords; self.style=style
        self.rng=np.random.RandomState(seed)
        self.spb=60.0/bpm           # sec per beat
        self.s16=self.spb/4         # sec per 16th
        self.nbar=len(bars_chords)
        self.total=int(self.nbar*4*self.spb*SR)+SR//2
        self.buf=np.zeros(self.total+SR)
    def place(self,sig,at_sec,gain=1.0):
        i=int(at_sec*SR)
        self.buf[i:i+len(sig)]+=sig*gain
    def render_note(self,inst,f,start,dur,gain,vel=1.0):
        np.random.seed(self.rng.randint(1<<30))
        n=int(dur*SR)
        if inst=='zun': s=zunpet(f,n,vel)
        elif inst=='pi': s=piano(f,n,vel)
        elif inst=='st': s=strings(f,n,vel)
        elif inst=='be': s=bell(f,n,vel)
        elif inst=='ba': s=bassv(f,n,vel)
        else: s=sine(f,n)*adsr(n,0.01,0.05,0.7,0.05)*vel
        self.place(s,start,gain)

NMIN=[0,2,3,5,7,8,10]      # A natural minor scale degrees (rel A)
NHARM=[0,2,3,5,7,8,11]     # harmonic minor (G# leading tone)
PENT=[0,3,5,7,10]          # A minor pentatonic (A C D E G)

def scale_freq(deg_idx, scale, base_oct=5):
    # deg_idx can exceed length -> octave up
    L=len(scale); o=deg_idx//L; pc=scale[deg_idx%L]
    return mf(midi('A',base_oct+o)+pc)

def build(track, scale, lead_density='mid', lead_inst='zun', pad=True,
          arp=True, drums=True, bassline=True, bell_arp=False, lead_oct=5,
          lead_gain=0.5):
    T=track; spb=T.spb; s16=T.s16
    for bi,sym in enumerate(T.prog):
        rpc,iv,bpc=parse_chord(sym)
        bar0=bi*4*spb
        # ----- bass: 8分 root-root-5th-root -----
        if bassline:
            broot=mf(midi('A',2)+ (rpc-9))   # relative to A; rpc is pitch class; map near A2
            # choose root freq close to A1-A2 range
            rootf=mf((midi('A',2)+((rpc-9)%12)) )
            fifthf=rootf*2**(7/12)
            pat=[rootf,rootf,fifthf,rootf,rootf,fifthf,fifthf,rootf]
            for j,bf in enumerate(pat):
                T.render_note('ba',bf,bar0+j*spb/2,spb/2*0.9,0.55*lead_gain+0.18)
        # ----- pad: strings 全音符 -----
        if pad:
            for off in iv[:3]:
                pf=mf(midi('A',3)+((rpc-9)%12)+off)
                T.render_note('st',pf,bar0,4*spb*0.98,0.12)
        # ----- arpeggio: piano 16分 chord tones -----
        if arp:
            tones=[mf(midi('A',4)+((rpc-9)%12)+o) for o in iv]
            tones+=[mf(midi('A',5)+((rpc-9)%12)+iv[0])]
            seq=[0,1,2,1,3,2,1,0] if len(tones)>=4 else [0,1,2,1,2,1,0,1]
            seq=(seq*2)[:16]
            for j in range(16):
                af=tones[seq[j]%len(tones)]
                inst='be' if bell_arp else 'pi'
                T.render_note(inst,af,bar0+j*s16,s16*1.3,0.14)
        # ----- drums -----
        if drums:
            for beat in range(4):
                if beat in (0,2):
                    T.render_note_raw(kick(int(0.18*SR),1.0),bar0+beat*spb,0.9)
                if beat in (1,3):
                    T.render_note_raw(snare(int(0.16*SR),0.9),bar0+beat*spb,0.5)
            hsub = 4 if T.style!='boss' else 2  # boss=16分ハイハット
            steps = 16 if T.style=='boss' else 8
            for j in range(steps):
                T.render_note_raw(hat(int(0.05*SR),0.5,op=(j%8==7)),bar0+j*(4*spb/steps),0.22)
            if (bi%4)==3:  # 4小節ごとにタムフィル
                for k in range(4):
                    ff=mf(midi('A',3)-k*2)
                    T.render_note_raw(sine(ff,int(0.10*SR))*np.exp(-t_arr(int(0.10*SR))*16),
                                      bar0+3*spb+k*s16,0.5)
    # ----- lead melody (last pass, full progression) -----
    build_lead(T, scale, lead_density, lead_inst, lead_oct, lead_gain)

def build_lead(T, scale, density, inst, lead_oct, gain):
    spb=T.spb; s16=T.s16; rng=T.rng
    # rhythmic patterns in 16th counts (sum=16)
    if density=='low':
        pats=[[4,4,4,4],[8,4,4],[4,4,8],[2,2,4,8]]
    elif density=='high':
        pats=[[1,1,1,1,2,2,2,2,2,2],[2,2,2,2,1,1,1,1,2,2],[1,1,2,1,1,2,2,2,2,2],[2,2,2,2,2,2,2,2]]
    else:
        pats=[[2,2,2,2,2,2,2,2],[2,2,4,2,2,4],[2,2,2,2,4,4],[1,1,2,2,2,2,2,2,2]]
    deg=7  # start mid (A5 area index)
    for bi,sym in enumerate(T.prog):
        rpc,iv,bpc=parse_chord(sym)
        ctones=[ (o)%12 for o in iv ]  # pitch classes rel root? we map by nearest scale deg
        bar0=bi*4*spb
        pat=pats[rng.randint(len(pats))]
        # phrase ending: every 4th bar resolve to A (deg multiple of len(scale))
        ending = ((bi%4)==3)
        pos=0; k=0
        # chord-tone target degrees: find scale indices whose pc matches chord tones
        chord_pcs=set(((rpc-9)%12 + o)%12 for o in iv)
        for di,dur in enumerate(pat):
            strong = (pos%4==0)
            if ending and di==len(pat)-1:
                deg = (deg//len(scale))*len(scale)   # land on A (root)
            else:
                step = rng.choice([-2,-1,1,1,2,2,3,-3,4,-1])
                deg = max(0,min(len(scale)*3-1, deg+step))
                if strong:
                    # snap toward a chord tone
                    best=deg
                    for cand in range(max(0,deg-2),deg+3):
                        if scale[cand%len(scale)]%12 in chord_pcs: best=cand;break
                    deg=best
            f=scale_freq(deg,scale,base_oct=lead_oct)
            # approach note: insert G#->A feeling handled by harmonic scale containing 11
            ng=int(dur*s16*SR)
            note=zunpet(f,ng, vel=0.95) if inst=='zun' else None
            if inst!='zun':
                if inst=='be': note=bell(f,ng,0.8)
                else: note=piano(f,ng,0.9)
            note=reverb(note,0.22)
            T.place(note,bar0+pos*s16,gain)
            pos+=dur; k+=1
            if pos>=16: break

def Track_raw(self):
    pass
def render_note_raw(self,sig,at,gain):
    i=int(at*SR); self.buf[i:i+len(sig)]+=sig*gain
Track.render_note_raw=render_note_raw

def finalize(T, fname, loop_bars=None):
    spb=T.spb
    end=int(T.nbar*4*spb*SR)
    y=T.buf[:end+int(0.3*SR)]
    # master: soft tail blend for seamless loop -> crossfade tail into head
    y=np.tanh(y*0.9)
    y=y/ (np.max(np.abs(y))+1e-9) *0.92
    # crossfade last 0.25s with silence-trim for loop continuity
    xf=int(0.18*SR)
    if len(y)>2*xf:
        head=y[:xf].copy()
        y[-xf:]=y[-xf:]*np.linspace(1,0,xf)+head*np.linspace(0,1,xf)
        y=y[:end]
    pcm=(np.clip(y,-1,1)*32767).astype(np.int16)
    w=wave.open(fname,'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes()); w.close()
    print(fname, round(len(pcm)/SR,1),'s', len(pcm.tobytes()),'bytes')

# ============ 6 tracks ============
def make(name, bpm, prog, scale, **kw):
    seed=sum(ord(c) for c in name)
    T=Track(bpm,prog,seed=seed,style=kw.pop('style','boss'))
    build(T,scale,**kw)
    finalize(T,name)

if __name__=='__main__':
    # 1: あおい 波/雨  哀愁・王道  Am G F E
    make('assets/bgm1.wav',150,
         ['Am','G','F','E','Am','G','F','E','Dm','Am','F','E','Am','G','F','E'],
         NHARM, style='mid', lead_density='low', lead_gain=0.5)
    # 2: すゞな 風/鈴  ネイティブフェイス疾走  Am G F G
    make('assets/bgm2.wav',172,
         ['Am','G','F','G','Am','G','F','G','Am','Dm','G','C','F','Dm','E','Am'],
         NHARM, style='boss', lead_density='high', bell_arp=True, lead_gain=0.5)
    # 3: まつり 花火/祭  和風ペンタ  Am Dm G C / F Dm E Am
    make('assets/bgm3.wav',165,
         ['Am','Dm','G','C','F','Dm','E','Am','Am','Dm','G','C','F','Dm','E','Am'],
         PENT, style='boss', lead_density='mid', lead_gain=0.5)
    # 4: ねむ 箱/夢  優雅・洋館  Am F Dm E
    make('assets/bgm4.wav',158,
         ['Am','F','Dm','E','Am','F','C','E','Dm','Am','F','E','Am','F','Dm','E'],
         NHARM, style='mid', lead_density='low', lead_gain=0.48)
    # 5: しじま 静寂  狂気・不安定  Am Bb Am E + dim
    make('assets/bgm5.wav',174,
         ['Am','Bb','Am','E','Am','G#dim','Am','E','Am','Bb','F','E','Am','G','F','E'],
         NHARM, style='boss', lead_density='high', lead_gain=0.52)
    # 6: うた ラスボス  section10/12 full design  BPM168
    make('assets/bgm6.wav',168,
         ['Am','G','F','E','Am','G','F','E',          # intro
          'Am','G','F','E','Am','Dm','G','C',          # A
          'F','G','Am','Am','F','G','C','E',           # B
          'F','G','Am','Am','F','G','C','E',           # chorus1
          'F','G','Am','G','F','E','Am','Am'],         # chorus2
         NHARM, style='boss', lead_density='high', lead_gain=0.55)
    print('done')
