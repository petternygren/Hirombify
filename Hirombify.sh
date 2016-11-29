#!/bin/sh

cd /home/nemo/tools/Hirombify

datehh=$1
declare -a vars=("salinity" "temperature" "tke"\
                 "vos" "uos" "wos" "uice" "vice"\
                 "icethic" "icefrac")

for var in "${vars[@]}"; do
  sbatch -J Hirombify_ns01 -N 1 -t 00:30:00 --exclusive -o\
    log/$var'.log' Hirombify.py $var $datehh
done

# Build hourly GRIB files.
sbatch  -J Hirombify_ns01 -d singleton -o log/concat.log concat_grib.sh
