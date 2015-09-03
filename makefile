URL=ftp://podaac-ftp.jpl.nasa.gov/allData/tellus/L3/land_mass/RL05/netcdf/
GFZNC=GRCTellus.GFZ.200204_201504.LND.RL05.DSTvSCS1409.nc
CSRNC=GRCTellus.CSR.200204_201504.LND.RL05.DSTvSCS1409.nc
JPLNC=GRCTellus.JPL.200204_201504.LND.RL05_1.DSTvSCS1411.nc
SCALEFACTOR=CLM4.SCALE_FACTOR.DS.G300KM.RL05.DSTvSCS1409.nc

all: processed.nc

processed.nc: scaler.nc gfz.nc csr.nc jpl.nc
	python process.py

scaler.nc:
	curl -o $@ $(URL)$(SCALEFACTOR)
gfz.nc:
	curl -o $@ $(URL)$(GFZNC)
csr.nc:
	curl -o $@ $(URL)$(CSRNC)
jpl.nc:
	curl -o $@ $(URL)$(JPLNC)

.SECONDARY: *
.PHONY:	clean

clean:
