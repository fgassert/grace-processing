#!/usr/bin/env python

import numpy as np
import netCDF4 as nc
import scipy.stats as stats
import rasterio as rio
from rasterio import Affine as A

NETCDFS=['jpl.nc','csr.nc','gfz.nc']
SCALER='scaler.nc'
SLOPE='slope.csv'
R2='r2.csv'
P='p.csv'
ERR='err.csv'
OUT='grace.tif'

def main():
    # load and average netcdfs
    arr = None
    for f in NETCDFS:
        ds = nc.Dataset(f,'r')
        if arr is None:
            print ds.variables.keys()
            arr = np.asarray(ds.variables['lwe_thickness']) / len(NETCDFS)
        else:
            arr += np.asarray(ds.variables['lwe_thickness']) / len(NETCDFS)

    # multiply by scale factor
    ds = nc.Dataset(SCALER,'r')
    print ds.variables.keys()
    scaler = np.asarray(ds.variables['SCALE_FACTOR'])
    print scaler.shape
    arr = arr*scaler

    # extract error grids
    m_err = np.asarray(ds.variables['MEASUREMENT_ERROR'])
    l_err = np.asarray(ds.variables['LEAKAGE_ERROR'])
    t_err = np.sqrt(m_err*m_err + l_err*l_err)

    # compute slopes, coefficients
    print arr.shape
    slope_arr = np.zeros(arr.shape[1:])
    r2_arr = np.zeros(arr.shape[1:])
    p_arr = np.zeros(arr.shape[1:])
    print slope_arr.shape
    time = np.arange(arr.shape[0])
    print time.shape
    for i in range(arr.shape[1]):
        for j in range(arr.shape[2]):
            b1, b0, r2, p, sd = stats.linregress(arr[:,i,j], time)
            slope_arr[i,j]=b1
            r2_arr[i,j]=r2
            p_arr[i,j]=p

    # dump to csv
    np.savetxt(SLOPE,slope_arr,delimiter=',')
    np.savetxt(R2,r2_arr,delimiter=',')
    np.savetxt(P,p_arr,delimiter=',')
    np.savetxt(ERR,t_err,delimiter=',')

    # rescale to WGS84 and dump to tif bands
    rows = arr.shape[1]
    cols = arr.shape[2]
    d = 1
    transform = A.translation(-cols*d/2,-rows*d/2) * A.scale(d,d)
    slope_arr = np.flipud(np.roll(slope_arr.astype(rio.float64),180))
    r2_arr = np.flipud(np.roll(r2_arr.astype(rio.float64),180))
    p_arr = np.flipud(np.roll(p_arr.astype(rio.float64),180))
    t_err = np.flipud(np.roll(t_err.astype(rio.float64),180))

    with rio.open(OUT, 'w',
                  'GTiff',
                  width=cols,
                  height=rows,
                  dtype=rio.float64,
                  crs={'init': 'EPSG:4326'},
                  transform=transform,
                  count=4) as out:
        out.write_band(1, slope_arr)
        out.write_band(2, r2_arr)
        out.write_band(3, p_arr)
        out.write_band(4, t_err)

if __name__ == "__main__":
    main()
