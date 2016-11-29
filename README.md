## **Hirombify**
Program outputs NEMO data on Hiromb grids as grib. This might be useful for legacy systems when Hiromb is no longer available.
Transforming NS01 -> BS01 takes 20min on frost, using one node for each variable.

For transformations between grids other then NS01->BS01 new gridMap (found in bs01_map.p) needs to be calculated. Its a dictionary of each (i1,j1,k1) -> (i2,j2,k2) for the target grid. Also the bs01_template file needs to have its dimentions changed.

The program is design to run on a HPC system with the slurm scheduler!
