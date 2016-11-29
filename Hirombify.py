#!/software/apps/python/2.7.9/smhi-1/bin/python

__author__ = 'Petter Nygren'
__status__ = 'Testing'

import sys, glob
import pickle
import datetime, time
import pygrib
import numpy as np
from netCDF4 import Dataset
import multiprocessing
import ConfigParser
import sharedmem

class GridConvert(multiprocessing.Process):
  
  def __init__(self, gridMap, gridDum, gridlev, data, dataName, factor,
               template, prefix, outputPath, timeStep, datehh):
    
    multiprocessing.Process.__init__(self)
    
    self.gridMap = gridMap
    self.gridDum = gridDum
    self.gridlev = gridlev

    self.template   = template
    self.prefix     = prefix
    self.outputPath = outputPath
    self.timeStep   = timeStep

    self.date = datehh

    self._extract_map()

    self.ncData   = data
    self.dataName = dataName
    self.factor = factor

  def run(self):

    self.res =\
    self._sub_field(np.array(self.ncData.variables[self.dataName]
                                                  [self.timeStep])*self.factor)
    self._write_grib()
    del self.res

  def _extract_map(self):
    
    self.n = [(k[-1], self.gridMap[k][-1]) for k in
              filter(lambda k: self.gridMap[k] != None, self.gridMap.keys())]
    self.y = [(k[1], self.gridMap[k][1]) for k in
              filter(lambda k: self.gridMap[k] != None, self.gridMap.keys())]
    self.x = [(k[0], self.gridMap[k][0]) for k in
              filter(lambda k: self.gridMap[k] != None, self.gridMap.keys())]

    del self.gridMap
    return self.n, self.y, self.x

  def _sub_field(self, field):
    
    tempDum = self.gridDum[:]
    del self.gridDum

    if len(field.shape) == 3:
      tempDum[zip(*self.n)[0], zip(*self.y)[0], zip(*self.x)[0]] =\
      field[zip(*self.n)[1], zip(*self.y)[1], zip(*self.x)[1]]
    else:
      tempDum[0, zip(*self.y)[0], zip(*self.x)[0]] =\
      field[zip(*self.y)[1], zip(*self.x)[1]]
      tempDum = tempDum[0]

    return tempDum

  def _write_grib(self):
    
    self.grbout = open(self.outputPath+self.prefix+self.date+'+'+
                       str(self.timeStep).zfill(3)+'H00M','wb') 
    
    self.template.dataDate = int(self.date[:8])
    self.template.dataTime = self.timeStep
    
    if len(self.res.shape) == 3:
      for idx in range(self.res.shape[0]):
        self.template.values = self.res[idx]
        self.template.level  = self.gridlev[idx]
        self.msg             = self.template.tostring()
        self.grbout.write(self.msg)
    else:
      self.template.values = self.res
      self.msg             = self.template.tostring()
      self.grbout.write(self.msg)

    self.grbout.close()

def main():
  settings = ConfigParser.ConfigParser()
  settings.read('default_frost.cfg')
  
  picklePath = settings.get('path', 'pickle')
  ncHandle   = Dataset(glob.glob(settings.get('path', 'data')+
                                 settings.get('forcing', 'prefix')+
                                 sys.argv[2]+'*'+
                                 settings.get(sys.argv[1], 'sufix')+'*')[-1],
                       'r', format='NETCDF4')

  gridMap, gridDum, gridlev =\
  pickle.load(open(picklePath, 'rb'))
  sharedGridMap = multiprocessing.Manager().dict()
  sharedGridMap = gridMap
  del gridMap

  template = pygrib.open(settings.get('path', 'template')).\
             message(int(settings.get(sys.argv[1], 'index')))

  def _job_que(njobs):
    
    hours = range(njobs)

    for t in hours:

      yield GridConvert(sharedGridMap, gridDum, gridlev, ncHandle,
                        settings.get(sys.argv[1], 'var'),
                        int(settings.get(sys.argv[1], 'factor')),
                        template, settings.get(sys.argv[1], 'prefix'),
                        settings.get('path', 'output'), t, sys.argv[2])

  jobs = _job_que(int(settings.get('parallel', 'njobs')))

  while True:
    
    try:
      for job in [jobs.next() for _ in
                  range(int(settings.get('parallel', 'cores')))]:
        job.start()
        time.sleep(2) 
      job.join()
    except:
      break

if __name__== "__main__":
  main()
