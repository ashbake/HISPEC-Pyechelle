from pyechelle.simulator import Simulator
from pyechelle.telescope import Telescope
from pyechelle.sources import Phoenix, CSVSource, ConstantFlux, IdealEtalon, LFC
from pyechelle.spectrograph import ZEMAX, LocalDisturber,GlobalDisturber
import numpy as np
from astropy.io import fits
from pyechelle.model_viewer import plot_psfs

output_path = './output/'

fiber_model = 'HISPEC_yJ_20231006A-1_trace3'

for fib in [1]:#,2,3]:
    sim = Simulator(ZEMAX(fiber_model))
    sim.set_ccd(1) # always leave as 1
    sim.set_bias(0)
    sim.set_read_noise(0)
    sim.set_fibers([fib])
    sim.set_sources([ConstantFlux(2e-5)])# Constant(intensity [microW / micron / s])
    #sim.set_sources([IdealEtalon(d=0.1,n_photons=10000)])# Constant(intensity [microW / micron / s])
    #sim.set_sources([CSV(filepath='./MakeSource/telluric_wave_flux_yJ.csv',\
    #sim.set_sources([CSVSource(file_path='./MakeSource/yj_etalon_flux_pump_1397.0nm.csv',\
    #    wavelength_units='micron',flux_units='photon/s',\
    #    list_like=True)])
    #sim.set_sources([Constant(1e-5),Constant(1e-5),Constant(1e-5),Constant(1e-5)])
    #sim.set_sources(Phoenix(t_eff=4000, log_g=4.0));source='Phoenix'# Constant(intensity [microW / micron / s])
    sim.set_exposure_time(.1) # s
    outname = output_path+fiber_model+'_constant'+str(fib) + '.fits'
    sim.set_output(outname, overwrite=True)
    sim.set_telescope(Telescope(9.96,0)) # Telescope(primary diameter, secondary diameter)
    sim.set_orders([*range(110, 149)]) # a list of all expected orders 59 to 97 or 110 to 149
    #sim.set_orders([110,130,149]) 
    sim.max_cpu =1 # set number of cpu to use
    sim.run()


# plot psfs
#fig = plot_psfs(ZEMAX(fiber_model))
#fig.show()



