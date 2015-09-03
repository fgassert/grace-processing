#!/usr/bin/env python

import numpy as np
import netCDF4 as nc
import scipy.stats as stats

NETCDFS=['jpl.nc','csr.nc','gfz.nc']
SCALER='scaler.nc'
SLOPE='slope.csv'
R2='r2.csv'
P='p.csv'

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

if __name__ == "__main__":
    main()
