#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 11:21:04 2024

@author: andrea
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals
import h5py   ### h5py should take its place
import os
import numpy as np
import pickle
import time
import datetime
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm


############# to help debug
from inspect import currentframe, getframeinfo
from inspect import currentframe

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno
##################################
'''
Started the 10/02/2024, after the correction of the shisted points in the data acquisition.
It also pass from tables to h5py, which should grat faster reading/loading of the data.
Alias dict for SBS reading should be in the same folder as this file.

Aim is to keep this file as simple as possible and handle exceprions and complexity in 
other modlues that uses the output from here

'''
##################################
class DataSet(object):
    '''Load a dataset and return an object containings the main measured variables contained in the file together with some metadata.
    it can be coplementd with nxs5Util to add extra functionalities.
    Usage:
    f42 = rn5.DataSet('filename42.nxs', 'folder_fulpath')
    '''
    def __init__(self,filename, directory = '', verbose=False):
        self.version = 'RN5 04/09/2026'
        self.__version__ = self.version
        self.directory = directory 
        self.filename = filename
        self.attlist = []
        self. _coefPz = 1 # assigned just in case
        self. _coefPn = 1 # assigned just in case
        self.verbose = verbose # explicits/prints some of the handled IO issues
        self.fullpath = os.path.join(directory,filename)
        if directory=='':
            self.directory='/'.join(filename.split('/')[:-1])+'/'   
        self._fullpath = os.path.join(self.directory,self.filename)
        try:
            path = os.path.dirname(__file__)
            pathAlias = os.path.join(path, 'alias_dict.txt')
            self._alias_dict = pickle.load(open(pathAlias,'rb'))
            #
        except :#FileNotFoundError:
            print('First Alias Not Found')       
        if self.verbose :
            print('#######################################################')
            print('Treating', filename)
        try:
            hf = h5py.File(self.fullpath, 'r')            
        except:
            if self.verbose :
                print ('h5py error reading/opening the file', ' Line: ', get_linenumber())
                #raise 
            return
        try:
            toto = hf['com/scan_data/data_01']
            self.scantype = 'SBS'
        except:
            self.scantype = 'FLY'
        ####### reading FLY: #################################################
        ####### the data
        if self.scantype == 'FLY':
            try:
                scandata = hf.get('com/scan_data/')
                for leaf in scandata:
                    #print(leaf)
                    list.append(self.attlist,leaf) 
                    self.__dict__[leaf] = np.asanyarray(scandata.get(leaf))
                #self.attlist = attlist
            except:
                raise
        ###### reading SBS ###################################################
        ###### the data
        if self.scantype == 'SBS':
            scandata = hf.get('com/scan_data/')
            if  self._alias_dict:  #### Reading with dictionary
                for leaf in scandata:
                    try :
                        leaf_att = scandata.get(leaf)
                        leafname = leaf_att.attrs['long_name'].decode('UTF-8')
                        #print(leafname.split('/')[-1])
                        try:
                            alias = self._alias_dict[leafname] # if attribute not in alias_dict
                        except:
                            alias = leafname.split('/')[-1] # if attribute not in alias_dict use the end of the string
                        
                        if alias in self.attlist:
                            alias = leaf+'_'+alias
                            self.__dict__[alias]=np.asanyarray(leaf_att)
                            list.append(self.attlist,alias)
                        if alias not in self.attlist:
                            #print(alias)
                            self.__dict__[alias]=np.asanyarray(leaf_att)
                            list.append(self.attlist,alias)
                        
                    except :
                        self.__dict__[leaf] = np.asanyarray(scandata.get(leaf))
                        list.append(self.attlist,leaf)
                        pass
                if hasattr(self,'sensorsTimestamps'): # try to fix naming inconsistencies
                    self.epoch = self.__getattribute__('sensorsTimestamps')
                    list.append(self.attlist, 'epoch')  
                if hasattr(self,'att_sbs_xpad'):  # try to fix naming inconsistencies
                    self.attenuation = self.__getattribute__('att_sbs_xpad')
                    list.append(self.attlist, 'attenuation')  
                    
        ############### Read metadata: ROIs, attenuation factor  ##############
        #######################################################################
        ############## Detector metadata
        self.dets = self.det2d()
        
        #if self.verbose: print('metadata @ ',get_linenumber(), self.dets)
        if self.dets:
            ## xpads70
            for el in self.dets:
                if '70' in el:
                    try:
                        self.mask_xpads70 = np.array(hf.get('/com/SIXS/i14-c-c00-ex-config-xpads70/mask'))
                        list.append(self.attlist,'mask_xpads70')
                    except:
                        if self.verbose: print('metadata @ ',get_linenumber())
                    ## the ROIs
                    self._get_ROIs( hf, '70')
            ## xpads140
            for el in self.dets:
                if '140' in el:
                    try:
                        self.mask_xpads140 = np.array(hf.get('/com/SIXS/i14-c-c00-ex-config-xpads140/mask'))
                        list.append(self.attlist,'mask_xpads140')
                    except:
                        if self.verbose: print('metadata @ ',get_linenumber())
                    ## the ROIs
                    self._get_ROIs( hf, '140')
            ## merlin
            for el in self.dets:
                if 'merlin' in el:
                    try:
                        self.mask_merlin = np.array(hf.get('/com/SIXS/i14-c-c00-ex-config-merlin/mask'))
                        list.append(self.attlist,'mask_merlin')
                    except:
                        if self.verbose: print('metadata @ ',get_linenumber())
                    ## the ROIs
                    self._get_ROIs(hf, 'merlin')
            ## eiger 1m   
            for el in self.dets:
                if 'eiger' in el:
                    try:
                        self.mask_eiger = np.array(hf.get('/com/SIXS/i14-c-c00-ex-config-eiger1m/mask'))
                        list.append(self.attlist,'mask_eiger')
                    except:
                        if self.verbose: print('metadata @ ',get_linenumber())
                    ## the ROIs
                    self._get_ROIs( hf, 'eiger')
        
        #############  Att coeff
        try:
            self.attcoef =  np.array(hf.get('/com/SIXS/i14-c-c00-ex-config-att/att_coef'))[0]
            list.append(self.attlist,'attcoef')
        except:
            if self.verbose: print('metadata att-coef @ ',get_linenumber())
            
        try:
            self.attcoef_old =  np.array(hf.get('/com/SIXS/i14-c-c00-ex-config-att-old/att_coef'))[0]
            list.append(self.attlist,'attcoef_old')
        except:
            if self.verbose: print('metadata att-coef @ ',get_linenumber())
        ########### Integration Time:
        try:
            if self.scantype == 'FLY':
                self.integration_time = np.array(hf.get('/com/SIXS/i14-c-c00-ex-config-global/integration_time'))[0]
                list.append(self.attlist,'integration_time')
            if self.scantype == 'SBS':
                self.integration_time = self.integration_times[-1]
                list.append(self.attlist,'integration_time')
        except:
            if self.verbose: print('metadata Integration Time @ ',get_linenumber())
            
            
            
        ##### closing the file    
        hf.close()
  
###############   functions        
    def det2d(self):
        '''it retunrs the name/s of the 2D detector'''
        list2D = []
        for el in self.attlist:
              bla = self.__getattribute__(el)
              #print(el, bla.shape)
              # get the attributes from list one by one
              if isinstance(bla, (np.ndarray, np.generic) ):
                  if len(bla.shape) == 3: # check for image stacks
                      list2D.append(el)
        if len(list2D)>0:
            self._list2D = list2D
            return list2D
        else:
            return False
        
    def _get_ROIs(self, hfile, strdet):
        '''hfile is the already open hdf5 object file
        strdet is the string that define the detector'''
        meta = hfile.get('com/SIXS')  # as metadata
        for el in meta.keys():
            if 'roicounter' in el: # selecting only the attributes with 'roicounters'
                if strdet in el:
                    x = []
                    y = []
                    w = []
                    h = []
                    detrois = meta.get(el)
                    attrname = el.split('-')[4] # selecting the name of the detector after the splitting
                    attrname = attrname.replace('.','_') # replace the . with _ for easier access to the attribute
                    self.__dict__[attrname+'_ROIs']=[] # generate the empty attribute
                    list.append(self.attlist, attrname+'_ROIs')
                    for el2name in detrois.keys():
                        dset = detrois.get(el2name)          # bizarre way to read the encoded string saved as array
                        ldata  = dset[()].decode('UTF8').split('\n')
                        data  = np.asarray(ldata).astype(int)
                        if 'height' in el2name:
                            h = data
                        if 'width' in el2name:
                            w = data
                        if 'x' in el2name:
                            x = data
                        if 'y' in el2name:
                            y = data
                    rois= np.c_[x, y, w, h]
                    self.__dict__[attrname+'_ROIs'] = rois    # use ROIs[0,:] ===>  array([  0,   0, 560, 240])
                        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            