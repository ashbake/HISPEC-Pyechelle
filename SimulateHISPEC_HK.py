from pyechelle.simulator import Simulator
from pyechelle.telescope import Telescope
from pyechelle.sources import Constant,CSV, Etalon, Phoenix
from pyechelle.spectrograph import ZEMAX, LocalDisturber,GlobalDisturber
import numpy as np
from astropy.io import fits
from pyechelle.model_viewer import plot_psfs


output_path = './output/'


fiber_model ='fixed_20231006B-1_HISPEC_SPECTRO_HK_pyechelle'

# order
# -65, -195, 65, 195, 325

d_sys  = [0]
for fib in [1,2,3]:
    sim = Simulator(ZEMAX(fiber_model))
    #spec= GlobalDisturber(ZEMAX(fiber_model),ty=d_sy*1000)
    #sim = Simulator(spec)
    sim.set_ccd(1) # always leave as 1
    sim.set_bias(0)
    sim.set_read_noise(0)
    #sim.set_read_noise(3)
    sim.set_fibers([fib]) # always leave as 1
    #sim.set_fibers([1])
    #sim.set_sources([Constant(5e-5)])# Constant(intensity [microW / micron / s]) # 10s exp time
    sim.set_sources([CSV(filepath='./MakeSource/telluric_wave_flux_HK.csv',\
        wavelength_unit='micron',delimiter=',',flux_in_photons=True,\
        list_like=True)])
    #sim.set_sources([Constant(1e-5),Constant(1e-5),Constant(1e-5),Constant(1e-5),Constant(1e-5)])
    #source = 'only-325'
    #sim.set_sources(Phoenix(t_eff=4000, log_g=4.0));source='Phoenix'# Constant(intensity [microW / micron / s])
    sim.set_exposure_time(100**2) # s, data in transmission but code thinks ph/s so for 100**2 seconds will get snr of 100
    #sim.cuda = True # use Cuda raytrace
    outname = output_path+fiber_model+'_telluric_fiber'+str(fib) + '.fits'
    sim.set_output(outname, overwrite=True)
    sim.set_telescope(Telescope(9.96,0)) # Telescope(primary diameter, secondary diameter)
    sim.set_orders([*range(59, 97)]) 
    #sim.set_orders([59,60,77,97])
    sim.max_cpu =1 # set number of cpu to use
    sim.run()

# plot psfs
#fig = plot_psfs(ZEMAX(fiber_model))
#fig.show()


