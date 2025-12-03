# random number generator for WFE

import numpy as np
import matplotlib.pylab as plt
import pyzdde.zdde as pyz


mode='HK'
# YJ
if mode=='YJ':
    lam0      = 980 #nm
    wfe_max   = 50 #nm
    nzernikes = 32
    order=110
elif mode=='HK':
    # HK
    lam0 = 1488#nm
    order=97
    wfe_max   = 125#75 #nm # this is 0.0504waves
    nzernikes = 32


# compute coefficients
coeffs_unnorm = np.random.random(nzernikes) # before normalizign to sum to right waves
sumcoeffs = np.sqrt(np.sum(coeffs_unnorm**2))

normfac = (wfe_max/lam0)/sumcoeffs

coeffs = np.round(normfac * coeffs_unnorm,3) 

# interface to Zemax (check surface numbers!)
#if 'ln' not in locals():
ln= pyz.createLink() #added this bc of my copy/paste into terminal habit

def get_surfaces(echellename='ECHELLE',aberrname='ABERRATIONS'):
    for i in range(ln.zGetNumSurf()):
        comm = ln.zGetComment(i)
        if comm == echellename:
            echelle_surface = i
        elif comm == aberrname:
            aberr_surface = i
    
    return echelle_surface, aberr_surface
#echelle_surface, aberr_surface = get_surfaces(echellename='ECHELLE',aberrname='ABERRATION')
echelle_surface, aberr_surface = 15, 10

ln.zSetSurfaceParameter(aberr_surface, 13, nzernikes) # param 13 defines number of zernikes to include
ln.zSetSurfaceParameter(echelle_surface, 2, order) # set echelle order
ln.zSetWave(1, lam0/1000, 1.)

for i in np.arange(nzernikes):
    ln.zSetSurfaceParameter(aberr_surface, 15+i, coeffs[i]) # parameter 15 starts zernike definition

ln.zPushLens() # update editor with params

ln.close()

