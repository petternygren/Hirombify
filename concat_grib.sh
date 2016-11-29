#!/bin/sh

cd /home/nemo/tools/Hirombify

# Build hourly GRIB files.
for i in $(seq -f "%03g" 0 59); do
  cat rundir/*$i'H00M' > output/BS01_NEMO_$datehh'00+'$i'H00M'
done
