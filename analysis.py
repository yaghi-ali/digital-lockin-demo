import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def recover(t,y,frequency):
    t,y=np.asarray(t,float),np.asarray(y,float)
    if t.ndim!=1 or t.shape!=y.shape or t.size<10 or not np.all(np.isfinite([t,y])) or not np.isfinite(frequency) or frequency<=0 or np.any(np.diff(t)<=0):
        raise ValueError('Need finite increasing times, matching signal and positive frequency.')
    dt=np.diff(t)
    if not np.allclose(dt,dt[0],rtol=1e-5,atol=1e-12) or frequency>=.5/dt[0] or frequency*np.ptp(t)<2:
        raise ValueError('Need uniform sampling, frequency below Nyquist and at least two cycles.')
    design=np.column_stack([np.cos(2*np.pi*frequency*t),np.sin(2*np.pi*frequency*t),np.ones_like(t)])
    c=np.linalg.lstsq(design,y,rcond=None)[0]
    return {'amplitude':float(np.hypot(c[0],c[1])),'phase_rad':float(np.arctan2(-c[1],c[0])),'dc':float(c[2])},design@c

def run(out,seed=42):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    t=np.arange(4000)/2000;signal=.4*np.cos(2*np.pi*137*t+.7)
    y=2+signal+1.2*np.cos(2*np.pi*211*t)+np.random.default_rng(seed).normal(0,1.5,t.size)
    result,fit=recover(t,y,137);delta=np.linspace(-2,2,161)
    amplitudes=np.array([recover(t,y,137+d)[0]['amplitude'] for d in delta])
    result.update(seed=seed,data='synthetic',true_amplitude=.4,true_phase_rad=.7,amplitude_absolute_error=abs(result['amplitude']-.4),phase_absolute_error_rad=abs(np.angle(np.exp(1j*(result['phase_rad']-.7)))))
    np.savetxt(out/'recovery.csv',np.column_stack([t,y,fit]),delimiter=',',header='time_s,observed_au,recovered_au',comments='')
    fig,ax=plt.subplots(2,1,figsize=(9,6));ax[0].plot(t[:200],y[:200],alpha=.5,label='Noisy data');ax[0].plot(t[:200],fit[:200],label='Recovered reference + DC');ax[0].legend();ax[0].set(xlabel='Time (s)',ylabel='Signal (a.u.)',title='Digital synchronous detection')
    ax[1].plot(delta,amplitudes);ax[1].axhline(.4,color='k',ls='--',label='True amplitude');ax[1].set(xlabel='Reference frequency error (Hz)',ylabel='Estimated amplitude');ax[1].legend()
    fig.tight_layout();fig.savefig(out/'preview.png',dpi=160);plt.close(fig);(out/'metrics.json').write_text(json.dumps(result,indent=2));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results');p.add_argument('--seed',type=int,default=42);a=p.parse_args();print(json.dumps(run(a.out,a.seed),indent=2))
