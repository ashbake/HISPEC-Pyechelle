# this script shows how to generate a spectrograph model file from the Zemax model of a spectrograph using PyZDDE
# env: py38

from pyechelle.CCD import CCD
from pyechelle.hdfbuilder import HDFBuilder
from pyechelle.spectrograph import InteractiveZEMAX

# Open Link to a standalone OpticStudio instance
zmx = InteractiveZEMAX(name='HISPEC')#, zemax_filepath="ZemaxModels/20231006A-1_HISPEC_SPECTRO_YJ_pyechelle.zmx")

# set basic grating specifications
zmx.set_grating(surface='ECHELLE', blaze=-75.2, theta=0., gamma=4)

# add CCD information (only one CCD supported so far. So for instruments with multiple CCDs, you have to generate
# separate models for now.
zmx.add_ccd(1, CCD(4096, 4096, pixelsize=10))

# Add here as many fiber/fields as you wish. You don't have to fiddle with the fields in OpticStudio. The
# existing fields will be ignored/deleted. This makes the corners of the box
# single mode can be the shape but it doesnt od antying, need to make size small (here set to 1um field width)
w = 5 # um, will be ignored
zmx.add_field(0., 0., w, w, shape='singlemode', name='Fiber3') # edit zemax each time for different fibers

# Add here a list with the diffraction orders you want to include
zmx.set_orders(1, 1, list(range(56, 99))) # 59 - 97

# Adjust settings for the Huygens PSF. Best to check out 'reasonable' parameters manually in ZEMAX first.
zmx.psf_settings(image_delta=1, image_sampling="256x256", pupil_sampling="128x128")

# at this point, you can interact with the spectrograph interactively, e.g. by doing something like:
# zmx.get_psf(wavelength=0.72, order=85, fiber=1, ccd_index=1)
# zmx.get_wavelength_range(order=85)
# zmx.get_transformation(wavelength=0.72, order=85, fiber=1, ccd_index=1)
# and it will/should pull the appropriate values from ZEMAX. This might be helpful for debugging.

# To generate an .HDF model file, you do:
hdf = HDFBuilder(zmx, './HISPEC_HK_20231006B-1_trace3.hdf') # trace1 -0.13 in x
# this will take a long time...
hdf.save_to_hdf(n_transformation_per_order=50, n_psfs_per_order=15)




if __name__=='__main__':
    pass

