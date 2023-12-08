# This is a test file on reading netcdf files (.nc) using python

from matplotlib import pyplot as plt
import pandas as pd
import netCDF4
fp='../example_data/PT_INCA_202106280700.nc'
nc = netCDF4.Dataset(fp)
print(nc.variables.keys())