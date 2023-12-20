import netCDF4 as nc
import os

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "example_data", "PT_INCA_202106280700.nc")
d = nc.Dataset(p, "r", format="NETCDF4")

