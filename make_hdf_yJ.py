# this script shows how to generate a spectrograph model file from the Zemax model of a spectrograph using PyZDDE
# env: py38

from pyechelle.CCD import CCD
from pyechelle.hdfbuilder import HDFBuilder
from pyechelle.spectrograph import InteractiveZEMAX

# Open Link to a standalone OpticStudio instance
zmx = InteractiveZEMAX(name='HISPEC')#, zemax_filepath="ZemaxModels/20231006A-1_HISPEC_SPECTRO_YJ_pyechelle.zmx")

# set basic grating specifications
zmx.set_grating(surface='ECHELLE', blaze=-76.5, theta=0., gamma=4)

# add CCD information (only one CCD supported so far. So for instruments with multiple CCDs, you have to generate
# separate models for now.
zmx.add_ccd(1, CCD(4096, 4096, pixelsize=10))

# Add here as many fiber/fields as you wish. You don't have to fiddle with the fields in OpticStudio. The
# existing fields will be ignored/deleted. This makes the corners of the box
# single mode can be the shape but it doesnt od antying, need to make size small (here set to 1um field width)
w = 5 # um, will be ignored
zmx.add_field(0., 0., w, w, shape='singlemode', name='Fiber3') # edit zemax each time for different fibers

# Add here a list with the diffraction orders you want to include
zmx.set_orders(1, 1, list(range(109, 151))) # 110-149

# Adjust settings for the Huygens PSF. Best to check out 'reasonable' parameters manually in ZEMAX first.
zmx.psf_settings(image_delta=1, image_sampling="256x256", pupil_sampling="128x128")

# at this point, you can interact with the spectrograph interactively, e.g. by doing something like:
# zmx.get_psf(wavelength=0.72, order=85, fiber=1, ccd_index=1)
# zmx.get_wavelength_range(order=85)
# zmx.get_transformation(wavelength=0.72, order=85, fiber=1, ccd_index=1)
# and it will/should pull the appropriate values from ZEMAX. This might be helpful for debugging.

# To generate an .HDF model file, you do:
hdf = HDFBuilder(zmx, './HISPEC_yJ_20231006A-1_trace3.hdf') # trace1 -0.13 in x
# this will take a long time...
hdf.save_to_hdf(n_transformation_per_order=50, n_psfs_per_order=15)






def save_wl_bounds():
    filebase ='20231006A_HISPEC_SPECTRO_YJ_pyechelle'
    surf  = 1   # surface of fiber offset
    param = 1   # parameter for fiber offset position x decenter


    filename = filebase + '_' +str(round(fiber_offset*1000))+ 'um.hdf'
    ln = pyz.createLink()
    
    fiber_offset=0
    ln.zSetSurfaceParameter(surf, param, fiber_offset) # set fiber offset
    ln.zPushLens() # update editor with params

    ln.zSetSurfaceParameter(surf, param, fiber_offset) # set fiber offset
    ln.zPushLens() # update editor with params
    print(filename)


    # Create echelle spectrograph
    spectrograph = PyEchelle.Echelle(ln, 'Spectrograph')

    # Analyze ZEMAX file to extract e.g. blaze and gamma angles
    spectrograph.analyseZemaxFile(echellename='ECHELLE', blazename='BLAZE', gammaname='GAMMA')

    # Define minimum and maximum order
    spectrograph.minord = 110
    spectrograph.maxord = 149

    # Define CCD including pixel size
    spectrograph.setCCD(PyEchelle.CCD(4096, 4096, 10, name='CCD')) #10um for YJ, 15um for HK

    # Calculate wavelength bounds for all orders
    spectrograph.calc_wl()
    ln.close()

    #import pickle
    fn='PyEchelle_Spectrograph/orders_'+ filename.strip('.hdf') + '.csv'
    f = open(fn,'w')
    f.write('order, minWL (nm), maxWL (nm)\n')
    # orders = pickle.load(open('PyEchelle_Spectrograph/' + fn)) #not sure why this doesnt work
    for order in spectrograph.orders:
        f.write('%s, %s, %s\n' %(order,1000*spectrograph.Orders[order].minWL, 1000*spectrograph.Orders[order].maxWL))

    f.close()


def save_psfs_centroids():
    import PyEchelle
    import pyzdde.zdde as pyz
    import sys

    from astropy.io import fits
    import matplotlib.pylab as plt
    import numpy as np

    ln = pyz.createLink()
    filename = '20220608C_HISPEC_SPECTRO_YJ_pyechelle.hdf'
    # Create echelle spectrograph
    spectrograph = PyEchelle.Echelle(ln, 'Spectrograph')

    # Analyze ZEMAX file to extract e.g. blaze and gamma angles
    spectrograph.analyseZemaxFile(echellename='ECHELLE', blazename='BLAZE', gammaname='GAMMA')

    # Define minimum and maximum order
    spectrograph.minord = 110
    spectrograph.maxord = 149

    # Define CCD including pixel size
    spectrograph.setCCD(PyEchelle.CCD(4096, 4096, 10, name='CCD')) #10um for YJ, 15um for HK until jason updates model?

    # Calculate wavelength bounds for all orders
    spectrograph.calc_wl()


    fn='PyEchelle_Spectrograph/psf_centroids_'+ filename.strip('.hdf') + '.fits'
    NFIBER =  len(fiber_locs)
    NORDER =  len(spectrograph.Orders.values())
    NWAVE  = 100
    psf_cents = np.zeros((NORDER,NFIBER,NWAVE,3))

    surf  = 1   # surface of fiber offset
    param = 1   # parameter for fiber offset position x decenter
    for io, o in enumerate(list(spectrograph.Orders.values())):
        wl = np.linspace(o.minWL, o.maxWL, NWAVE)
        ln.zSetSurfaceParameter(spectrograph.zmx_nsurf, 2, o.m)
        print('Trace order', o.m)
        for ifo, fiber_offset in enumerate(fiber_locs):
            Xstore = []
            Ystore = []
            ln.zSetSurfaceParameter(surf, param, fiber_offset) # set fiber offset
            for iw, w in enumerate(wl):
                ln.zSetWave(1, w, 1.)
                print(w)
                successful=False
                while not successful:
                    try:
                        psfparams,_ = ln.zGetPSF(which='huygens',timeout=1000)
                        successful=True
                    except TypeError:
                        print('Trying get PSF again')
                        plt.pause(0.1)

                psf_cents[io,ifo,iw] = [w,psfparams.centerCoordX, psfparams.centerCoordY]
                

    #savetofits        
    hdr = fits.Header()
    hdr['NAXIS1'] = (3, 'wave, X,Y')
    hdr['NAXIS2'] = (NWAVE,'number of wavelengths')
    hdr['NAXIS3'] = (NFIBER,'number of fibers')
    hdr['NAXIS4'] = (NORDER, 'number of orders')
    hdu = fits.PrimaryHDU(psf_cents,header=hdr)
    hdu.writeto(fn,overwrite=True)


if __name__=='__main__':
    pass
    #save_psfs_centroids()
    #save_wl_bounds()
