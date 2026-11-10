import unittest
import numpy as np
from analysis import recover
class Tests(unittest.TestCase):
    def test_exact_amplitude_phase_and_offset(self):
        t=np.arange(4000)/2000;y=2+.4*np.cos(2*np.pi*137*t+.7)
        r,fit=recover(t,y,137)
        np.testing.assert_allclose([r['amplitude'],r['phase_rad'],r['dc']],[.4,.7,2],atol=1e-12)
        np.testing.assert_allclose(fit,y,atol=1e-12)
    def test_interference_and_noise(self):
        t=np.arange(4000)/2000
        for seed in [1,42,93]:
            y=2+.4*np.cos(2*np.pi*137*t+.7)+1.2*np.cos(2*np.pi*211*t)+np.random.default_rng(seed).normal(0,1.5,t.size)
            r,_=recover(t,y,137);self.assertLess(abs(r['amplitude']-.4),.09)
    def test_nyquist(self):
        with self.assertRaises(ValueError):recover(np.arange(100)/100,np.ones(100),50)
    def test_nonuniform_sampling(self):
        with self.assertRaises(ValueError):recover(np.arange(100)**1.1,np.ones(100),.1)
