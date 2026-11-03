#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 10:33:55 2023

@author: andrea
"""


import matplotlib.pyplot as plt
import os
import numpy as np
import h5py

from sixs_tools import utilities3 as ut3
from matplotlib.colors import LogNorm

import trimesh
import skimage.measure as ms

import imageio.v3 as iio



class hdf5load(object):
    '''Meant to return an object with the data matrix and the axes as attributes
    But better verify than sorry...
    It expects two strings:
        The folder name eg: datdir   = "/home/user/data"
        the file name   eg: filename = "Sample2_hkl_map_1.hdf5"  
        
        syntax example:
        fdata = bu3.hdf5load(datdir, filename)
        
    The object will contains 2 two matrices: ratio between Counts and Contributions original matrices in the hdf5file
    the "data is manipulated to be consistet with the indexing [h, k, l], or [Qx, Qy, Qz].
    it therefore appear rotated compare to dataRaw."
    there are also the 3 (or 2) axes and the original vectors containinig the information to generate the axes.'''
    np.seterr(divide='warn', invalid='warn')
    def __init__(self,directory, hdf5file, verbose=False):
        np.seterr(divide='ignore', invalid='ignore')
        #self.data=0
        self.directory =  directory
        self.filename = hdf5file
        self.version = '20/02/2026'
        self.verbose = verbose
        fullpath = os.path.join(self.directory,self.filename)
        f = h5py.File(fullpath,'r')
        daxes = f['binoculars/axes']
        self.axes_names = list(daxes.keys())
        #print(daxes_keys)
        for el in self.axes_names: #generate the attributes from the axes names contained in the file
            #print(el)
            #list.append(attlist,leaf.name) 
            self.__dict__['_'+el] = daxes[el][()]
            #print(self.__getattribute__('_'+el))
            axetemp = daxes[el][()]
            self.__dict__[el] = np.linspace(axetemp[1],axetemp[2],int(1+axetemp[5]-axetemp[4]))
            #self.__dict__[el+'_orig'] = axetemp
                
        self.cont = f['binoculars/contributions'][()]
        self.ct = f['binoculars/counts'][()]
        self.dataRaw = self.ct/self.cont
        f.close()
        
    ##################### useful functions
    def isNone(self,var):
        if var == None: 
            return True
        else:
            return False
    
    def prjaxe(self,axename, axenum = None):
        '''Project on one of the measured axes
        axe is a string: eg 'H'.
        the result is added as attribute .img to the file
        axerange is [0.8, 0.9] and define the positions of the value to be used
        in the array on the desired axe
        axenum should be specified if two axes has the same number of data points.''' 
        #st = axerange[0]
        #nd = axerange[-1]
        try:
            axe = self.__getattribute__(axename)
            axeshape = axe.shape[0]
            datashape = self.dataRaw.shape
            if self.isNone(axenum):  # axenum can be specified in case of axes of identical lenght.
                axenum = datashape.index(axeshape) # this might be a weak point! but should work most of the times
            self.img = np.nanmean(self.dataRaw,axis = axenum)
            print('check the new attribute  ==> .img <==')
        except:
            print('Axe name not found')
            print('available axes: ',self.axes_names) 
        return
        
    def prjaxe_range(self,axename, axerange, axenum = None):
        '''Project on one of the measured axes
        axe is a string: eg 'H'.
        the result is added as attribute .img to the file
        axerange is [0.8, 0.9] and define the positions of the value to be used
        in the array on the desired axe
        axenum should be specified if two axes has the same number of data points.''' 
        #st = axerange[0]
        #nd = axerange[-1]
        try:
            axe = self.__getattribute__(axename)
            axeshape = axe.shape[0]
        except:
            print('Axe name not found')
        
        datashape = self.dataRaw.shape
        if self.isNone(axenum):
            axenum = datashape.index(axeshape) # this might be a weak point! but should work most of the times
        st = ut3.find_nearest(axe,axerange[0])[0]
        nd = ut3.find_nearest(axe,axerange[1])[0]
        if axenum == 2:
            datanan=self.dataRaw[:,:,st:nd]
        if axenum == 1:
            datanan=self.dataRaw[:,st:nd,:]
        if axenum == 0:
            datanan=self.dataRaw[st:nd,:,:]
        
        self.imgr = np.nanmean(datanan,axis = axenum)
        print('check the new attribute  ==> imgr <==')
        return

    def plotMap(self, axe, range, vmin=0.8, vmax=20, mapcolor='jet', rotate90=False):
        '''axe: H, K, L or any
        range: [stValue, endValue], value not position
        vmin, vmax: cmap extension for the colormap'''
        self.prjaxe_range(axe,range)
        other_axes = self.axes_names[:] #[:] is importtant to generate a newlist and not just a link.
        #print(axe)
        #print(other_axes)
        other_axes.remove(axe)
        if rotate90:
            x,y = np.meshgrid(self.__getattribute__(other_axes[0]), self.__getattribute__(other_axes[1]))
            plt.pcolormesh(x,y,np.rot90(self.imgr, k=-1), norm=LogNorm(vmin=vmin, vmax=vmax),cmap=mapcolor)
        if not rotate90:
            x,y = np.meshgrid(self.__getattribute__(other_axes[1]), self.__getattribute__(other_axes[0]))
            plt.pcolormesh(x,y,self.imgr, norm=LogNorm(vmin=vmin, vmax=vmax),cmap=mapcolor)
        plt.colorbar()



    def intslice(self,  Imap, H, K, dH, dK, dbkg, haxe='auto', kaxe='auto'):
        '''integrate over a 2D range in H, K and subtract the average background per pixel recalculated
        haxe, kaxe: the axes of the intensity map
        Imap      : is a 2D intesity map in the HK plane
        H K       : are the center of the ROI.
        dH dK     : are the half span of the ROI (use 0.1 to obtain a total width of 0.2)
        dbkg      : is the extension on each the side of the ROI where the bkg is calculated
        ##### ####
        it returns:
        TotBkgInt : The total bkg value estimated over the ROI
        Icorr     : the Intensity subtracted by the backgroung
        RoiInt    : the raw integral of the ROI (not condidering NaN)
        NvoxRoi   : the number of meaningful voxels present in the ROI (no Nan Voxels)
        '''
        if haxe =='auto':
            haxe = self.H
        if kaxe =='auto':
            kaxe = self.K
        # retrieve the position in the data matrix of the extension of the ROI
        iHst,value = ut3.find_nearest(haxe,H-dH)
        #print(iHst,value)
        iHnd,value = ut3.find_nearest(haxe,H+dH)
        #print(iHnd,value)
        iKst,value = ut3.find_nearest(kaxe,K-dK)
        #print(iKst,value)
        iKnd,value = ut3.find_nearest(kaxe,K+dK)
        #print(iKnd,value)
        roi = Imap[iHst:iHnd, iKst:iKnd]
        RoiInt = np.nansum(roi) #NaN sum of the ROI
        Nnans = np.count_nonzero(np.isnan(roi)) # Number of NaNs in the roi
        NvoxRoi = roi.shape[0]*roi.shape[1]-Nnans #meaningful voxels number, for Bkg calculation
        
        ###### retrive the background average intensiy per pixel
        #
        #    |﹉﹉﹉|
        #    | [ ] |
        #    |﹎﹎﹎|
        # 
        #bkg1 dH-dbk left side
        iHst,value = ut3.find_nearest(haxe,H-dH-dbkg)
        iHnd,value = ut3.find_nearest(haxe,H-dH)
        iKst,value = ut3.find_nearest(kaxe,K-dK)
        iKnd,value = ut3.find_nearest(kaxe,K+dK)
        bkg1 = Imap[iHst:iHnd, iKst:iKnd]
        bkg1Int = np.nansum(bkg1)
        Nnans_bkg1 = np.count_nonzero(np.isnan(bkg1))
        Nvoxbkg1 = bkg1.shape[0]*bkg1.shape[1]-Nnans_bkg1

        
        #bkg2 dH+dbk right side
        iHst,value = ut3.find_nearest(haxe,H+dH)
        iHnd,value = ut3.find_nearest(haxe,H+dH+dbkg)
        iKst,value = ut3.find_nearest(kaxe,K-dK)
        iKnd,value = ut3.find_nearest(kaxe,K+dK)
        bkg2 = Imap[iHst:iHnd, iKst:iKnd]
        bkg2Int = np.nansum(bkg2)
        Nnans_bkg2 = np.count_nonzero(np.isnan(bkg2))
        Nvoxbkg2 = bkg2.shape[0]*bkg2.shape[1]-Nnans_bkg2
        
        #bkg3 dK+dbk top side
        iHst,value = ut3.find_nearest(haxe,H-dH)
        #print(iHst,value)
        iHnd,value = ut3.find_nearest(haxe,H+dH)
        #print(iHnd,value)
        iKst,value = ut3.find_nearest(kaxe,K+dK)
        #print(iKst,value)
        iKnd,value = ut3.find_nearest(kaxe,K+dK+dbkg)
        bkg3 = Imap[iHst:iHnd, iKst:iKnd]
        bkg3Int = np.nansum(bkg3)
        Nnans_bkg3 = np.count_nonzero(np.isnan(bkg3))
        Nvoxbkg3 = bkg3.shape[0]*bkg3.shape[1]-Nnans_bkg3
        
        #bkg4 dK-dbk bottom side
        iHst,value = ut3.find_nearest(haxe,H-dH)
        #print(iHst,value)
        iHnd,value = ut3.find_nearest(haxe,H+dH)
        #print(iHnd,value)
        iKst,value = ut3.find_nearest(kaxe,K-dK-dbkg)
        #print(iKst,value)
        iKnd,value = ut3.find_nearest(kaxe,K-dK)
        bkg4 = Imap[iHst:iHnd, iKst:iKnd]
        bkg4Int = np.nansum(bkg4)
        Nnans_bkg4 = np.count_nonzero(np.isnan(bkg4))
        Nvoxbkg4 = bkg4.shape[0]*bkg4.shape[1]-Nnans_bkg4
        
        TotBkgVox = Nvoxbkg1 + Nvoxbkg2 + Nvoxbkg3 + Nvoxbkg4
        TotBkgInt = bkg1Int + bkg2Int + bkg3Int + bkg4Int
        #AveBkg = TotBkgInt/TotBkgVox
        #Icorr  = RoiInt-(AveBkg*NvoxRoi)
        Icorr  = RoiInt-(NvoxRoi/TotBkgVox)*TotBkgInt
        # roi - (#roi/#bkg) *bkg?
        
            
        return TotBkgInt, Icorr, RoiInt, NvoxRoi   
    
    def intRod(self, H, K, dH, dK, dL, dbkg, haxe='auto', kaxe='auto', laxe='auto', volume='auto',save_fs = False):
        '''Not too advance metod to numerically integrate the rod volume data.
        h, k define the center position of the signal to be integrated.
        it make use of the above function == > inteslice< == 
        it returns:
        fs          : the structure factor [sqrt(I)/pi]
        LIntervCent : the L value attributed to each L intagration range
        integrals   : the ROI integral - ROI bkgs
        RoiInts     : the ROI integral
        TotBkgInts  : the ROI bkgs
        TotNVoxs    : the meaningful voxel in each ROI 
        
        syntax example:
        fdata = bu3.hdf5load(datdir, filename)
        fs_r, Lsvalue, Lintegrals,RoiInts,TotoBkgInts,TotNVoxs = fdata.intRod( H,K, dH, dK, dL, dbkg)
        fdata.plotfs()
        
        save_fs = False 
        Falseby defalt, if set to True it will save the structure factors and L values
        
        '''
        
        if haxe =='auto':
            haxe = self.H
        if kaxe =='auto':
            kaxe = self.K
        if laxe =='auto':
            laxe = self.L
        if volume == 'auto':
            volume = self.dataRaw
            
        lnd = laxe.max()
        lst = laxe.min()
        
        #Lsteps = round((lnd-lst)/dL)+1 # number of steps
        Lsteps = np.shape(laxe)[0]
        
        Lintervals = np.linspace(lst,lnd,Lsteps) # start/end of each interval
        LIntervCent = np.linspace(lst+dL/2,lnd-dL/2,Lsteps-1)  # center position for each interval 
        # the empty retunr variables
        integrals = np.zeros_like(LIntervCent)
        RoiInts = np.zeros_like(LIntervCent)
        TotBkgInts = np.zeros_like(LIntervCent)
        TotNVoxs = np.zeros_like(LIntervCent)
        for pos,el  in enumerate(LIntervCent):
            #print(Lintervals[pos])
            #print('Nvoxels= ',)
            #print(laxe.shape, np.shape(Lintervals))
            Li_st, Lval = ut3.find_nearest(laxe, Lintervals[pos])
            Li_nd, Lval = ut3.find_nearest(laxe, Lintervals[pos+1])
            Imap = np.nansum(volume[:,:,Li_st:Li_nd],axis = 2)
            SliceThick=Li_nd-Li_st
                   
            TotBkgInt, Icorr, RoiInt, Nvox = self.intslice( Imap, H, K, dH, dK, dbkg)
            integrals[pos] = Icorr
            RoiInts[pos] = RoiInt
            TotBkgInts[pos] = TotBkgInt
            TotNVoxs[pos] = Nvox*SliceThick
        
            
        fs = np.sqrt(integrals)
        self.fs = fs
        self.L_fs = LIntervCent
        self._Hlist = np.ones(len(self.L_fs))*H
        self._Klist = np.ones(len(self.L_fs))*K
        if Lsteps > round((lnd-lst)/dL): #provide the binning at the right spacing.
            print('dL bigger than Binoculars L voxel spacing.')
            L_bin,fs_bin = ut3.binto(LIntervCent, fs, round((lnd-lst)/dL))
            self.fs = fs_bin
            self.L_fs = L_bin
            fs = np.sqrt(fs_bin) #for the output
            LIntervCent = L_bin  #for the output
            self._Hlist = np.ones(len(self.L_fs))*H
            self._Klist = np.ones(len(self.L_fs))*K
            
        if save_fs == True:
            filename =  self.filename[:-5]+'_ROD'+str(H)+'_'+str(K)+'.txt'
            try:
                self.saveList(filename=filename)
            except:
                self.saveXY(filename=filename)
                raise
            
        return fs, LIntervCent, integrals, RoiInts, TotBkgInts, TotNVoxs
    
    def intsliceErr(self,  Imap, ImapCT, H, K, dH, dK, dbkg, haxe='auto', kaxe='auto'):
        '''integrate over a 2D range in H, K and subtract the average background per pixel recalculated
        haxe, kaxe: the axes of the intensity map
        Imap      : is a 2D intesity map in the HK plane
        ImapCT    : the 2D map of the contribution matrix (before dividing for the contributions)
        H K       : are the center of the ROI.
        dH dK     : are the half span of the ROI (use 0.1 to obtain a total width of 0.2)
        dbkg      : is the extension on each the side of the ROI where the bkg is calculated
        ##### ####
        it returns:
        TotBkgInt : The total bkg value estimated over the ROI
        Icorr     : the Intensity subtracted by the backgroung
        RoiInt    : the raw integral of the ROI (not condidering NaN)
        NvoxRoi   : the number of meaningful voxels present in the ROI (no Nan Voxels)
        Ierr      : the error on the integrated intensity, with the contribution from the Bkg
        #### ####
        I = sum(i) 		N = sum(ct) 	
		u(N) = sqrt(N) 	
		u(I)/I = u(N)/N	u(I)=I/sqrt(N)
        
        same for each bkgs, that then must be added to each other under sqrt
            
        '''
        if haxe =='auto':
            haxe = self.H
        if kaxe =='auto':
            kaxe = self.K
        # retrieve the position in the data matrix of the extension of the ROI
        iHst,value = ut3.find_nearest(haxe,H-dH)
        #print(iHst,value)
        iHnd,value = ut3.find_nearest(haxe,H+dH)
        #print(iHnd,value)
        iKst,value = ut3.find_nearest(kaxe,K-dK)
        #print(iKst,value)
        iKnd,value = ut3.find_nearest(kaxe,K+dK)
        #print(iKnd,value)
        roi = Imap[iHst:iHnd, iKst:iKnd]
        roiCT = ImapCT[iHst:iHnd, iKst:iKnd]
        RoiInt = np.nansum(roi) #NaN sum of the ROI
        roiErr = RoiInt/np.sqrt(np.nansum(roiCT))
        Nnans = np.count_nonzero(np.isnan(roi)) # Number of NaNs in the roi
        NvoxRoi = roi.shape[0]*roi.shape[1]-Nnans #meaningful voxels number, for Bkg calculation
        
        ###### retrive the background average intensiy per pixel
        #
        #    |﹉﹉﹉|
        #    | [ ] |
        #    |﹎﹎﹎|
        # 
        #bkg1 dH-dbk left side
        iHst,value = ut3.find_nearest(haxe,H-dH-dbkg)
        iHnd,value = ut3.find_nearest(haxe,H-dH)
        iKst,value = ut3.find_nearest(kaxe,K-dK)
        iKnd,value = ut3.find_nearest(kaxe,K+dK)
        bkg1 = Imap[iHst:iHnd, iKst:iKnd]
        bkg1CT = ImapCT[iHst:iHnd, iKst:iKnd]
        bkg1Int = np.nansum(bkg1)
        bkg1Err = bkg1Int/np.sqrt(np.nansum(bkg1CT))
        Nnans_bkg1 = np.count_nonzero(np.isnan(bkg1))
        Nvoxbkg1 = bkg1.shape[0]*bkg1.shape[1]-Nnans_bkg1

        
        #bkg2 dH+dbk right side
        iHst,value = ut3.find_nearest(haxe,H+dH)
        iHnd,value = ut3.find_nearest(haxe,H+dH+dbkg)
        iKst,value = ut3.find_nearest(kaxe,K-dK)
        iKnd,value = ut3.find_nearest(kaxe,K+dK)
        bkg2 = Imap[iHst:iHnd, iKst:iKnd]
        bkg2CT = ImapCT[iHst:iHnd, iKst:iKnd]
        bkg2Int = np.nansum(bkg2)
        bkg2Err = bkg2Int/np.sqrt(np.nansum(bkg2CT))
        
        Nnans_bkg2 = np.count_nonzero(np.isnan(bkg2))
        Nvoxbkg2 = bkg2.shape[0]*bkg2.shape[1]-Nnans_bkg2
        
        #bkg3 dK+dbk top side
        iHst,value = ut3.find_nearest(haxe,H-dH)
        #print(iHst,value)
        iHnd,value = ut3.find_nearest(haxe,H+dH)
        #print(iHnd,value)
        iKst,value = ut3.find_nearest(kaxe,K+dK)
        #print(iKst,value)
        iKnd,value = ut3.find_nearest(kaxe,K+dK+dbkg)
        bkg3 = Imap[iHst:iHnd, iKst:iKnd]
        bkg3Int = np.nansum(bkg3)
        bkg3CT = ImapCT[iHst:iHnd, iKst:iKnd]
        bkg3Err = bkg3Int/np.sqrt(np.nansum(bkg3CT))
        Nnans_bkg3 = np.count_nonzero(np.isnan(bkg3))
        Nvoxbkg3 = bkg3.shape[0]*bkg3.shape[1]-Nnans_bkg3
        
        #bkg4 dK-dbk bottom side
        iHst,value = ut3.find_nearest(haxe,H-dH)
        #print(iHst,value)
        iHnd,value = ut3.find_nearest(haxe,H+dH)
        #print(iHnd,value)
        iKst,value = ut3.find_nearest(kaxe,K-dK-dbkg)
        #print(iKst,value)
        iKnd,value = ut3.find_nearest(kaxe,K-dK)
        bkg4 = Imap[iHst:iHnd, iKst:iKnd]
        bkg4CT = ImapCT[iHst:iHnd, iKst:iKnd]
        bkg4Int = np.nansum(bkg4)
        bkg4Err = bkg4Int/np.sqrt(np.nansum(bkg4CT))
        Nnans_bkg4 = np.count_nonzero(np.isnan(bkg4))
        Nvoxbkg4 = bkg4.shape[0]*bkg4.shape[1]-Nnans_bkg4
        
        # 
        BkgErr = np.sqrt(bkg1Err**2 + bkg2Err**2 + bkg3Err**2 + bkg4Err**2)
        TotBkgVox = Nvoxbkg1 + Nvoxbkg2 + Nvoxbkg3 + Nvoxbkg4
        TotBkgInt = bkg1Int + bkg2Int + bkg3Int + bkg4Int
        #AveBkg = TotBkgInt/TotBkgVox
        #Icorr  = RoiInt-(AveBkg*NvoxRoi)
        Icorr  = RoiInt-(NvoxRoi/TotBkgVox)*TotBkgInt
        Ierr = np.sqrt(roiErr**2 + BkgErr**2)
        # roi - (#roi/#bkg) *bkg?
        
            
        return TotBkgInt, Icorr, RoiInt, NvoxRoi, Ierr
    
    
    def intRodErr(self, H, K, dH, dK, dL, dbkg, haxe='auto', kaxe='auto', laxe='auto', volume='auto',volumeCT='auto',save_fs = False):
        '''Not too advance metod to numerically integrate the rod volume data.
        h, k define the center position of the signal to be integrated.
        it make use of the above function == > inteslice< == 
        it returns:
        fs          : the structure factor [sqrt(I)/pi]
        LIntervCent : the L value attributed to each L intagration range
        integrals   : the ROI integral - ROI bkgs
        RoiInts     : the ROI integral
        TotBkgInts  : the ROI bkgs
        TotNVoxs    : the meaningful voxel in each ROI 
        
        syntax example:
        fdata = bu3.hdf5load(datdir, filename)
        fs_r, Lsvalue, Lintegrals,RoiInts,TotoBkgInts,TotNVoxs = fdata.intRod( H,K, dH, dK, dL, dbkg)
        fdata.plotfs()
        
        save_fs = False 
        Falseby defalt, if set to True it will save the structure factors and L values
        
        '''
        
        if haxe =='auto':
            haxe = self.H
        if kaxe =='auto':
            kaxe = self.K
        if laxe =='auto':
            laxe = self.L
        if volume == 'auto':
            volume = self.dataRaw
        if volumeCT == 'auto':
            volumeCT = self.ct
            
        
            
        lnd = laxe.max()
        lst = laxe.min()
        
        #Lsteps = round((lnd-lst)/dL)+1 # number of steps
        Lsteps = np.shape(laxe)[0]
        
        Lintervals = laxe #np.linspace(lst,lnd,Lsteps) # start/end of each interval
        LIntervCent = np.linspace(lst+dL/2,lnd-dL/2,Lsteps-1)  # center position for each interval 
        integrals = np.zeros_like(LIntervCent)
        RoiInts = np.zeros_like(LIntervCent)
        TotBkgInts = np.zeros_like(LIntervCent)
        TotNVoxs = np.zeros_like(LIntervCent)
        Ierr = np.zeros_like(LIntervCent)
        for pos,el  in enumerate(LIntervCent):
            #print(Lintervals[pos])
            #print('Nvoxels= ',)
            Li_st, Lval = ut3.find_nearest(laxe, Lintervals[pos])
            Li_nd, Lval = ut3.find_nearest(laxe, Lintervals[pos+1])
            Imap = np.nansum(volume[:,:,Li_st:Li_nd],axis = 2)
            ImapCT = np.nansum(volumeCT[:,:,Li_st:Li_nd],axis = 2)
            SliceThick=Li_nd-Li_st
                   
            TotBkgInt, Icorr, RoiInt, Nvox, Ie = self.intsliceErr( Imap, ImapCT, H, K, dH, dK, dbkg)
            #if np.isnan(Ie):
            #    print('Nan at: ', pos)
            integrals[pos] = Icorr
            RoiInts[pos] = RoiInt
            TotBkgInts[pos] = TotBkgInt
            TotNVoxs[pos] = Nvox*SliceThick
            Ierr[pos] = Ie
        
            
        fs = np.sqrt(integrals)
        fs_err = (1/2)*Ierr
        self.fs = fs
        self.L_fs = LIntervCent
        self.fs_err = fs_err
        self._Hlist = np.ones(len(self.L_fs))*H
        self._Klist = np.ones(len(self.L_fs))*K
        if Lsteps > round((lnd-lst)/dL): #provide the binning at the right spacing.
            print('dL bigger than Binoculars L voxel spacing.')
            L_bin,fs_bin = ut3.binto(LIntervCent, fs, round((lnd-lst)/dL))
            # missing function to obtain error from binning
            L_bin,fs_bin, fs_err  = ut3.bintoErr(LIntervCent, fs, fs_err,round((lnd-lst)/dL))
            self.fs = fs_bin
            self.L_fs = L_bin
            self.fs_err = fs_err
            fs = fs_bin #for the output
            LIntervCent = L_bin  #for the output
            self._Hlist = np.ones(len(self.L_fs))*H
            self._Klist = np.ones(len(self.L_fs))*K
            
        if save_fs == True:
            filename =  self.filename[:-5]+'_ROD'+str(H)+'_'+str(K)+'.txt'
            try:
                self.saveList(filename=filename)
            except:
                self.saveXY(filename=filename)
                raise
            
        return fs, LIntervCent, fs_err, integrals, RoiInts, TotBkgInts, TotNVoxs


    def saveXY(self, xy = ['L_fs', 'fs','fs_err'], filename = 'Auto'):
        '''It saves a txt file with the xy list of variables: listed as ['x','y','z'].
        
        it expect a list of strings. 
        It dos not export images nor  x y arributes of inconsistent lenght
    
        '''
        if filename =='Auto':
            filesave = self.filename[:-5] + '_extr.txt'
        else:
            filesave = filename
        longname = os.path.join(self.directory,filesave)
    
        #x = np.empty(self._npts)
        #y = np.empty(self._npts)
        
        x = self.__getattribute__(xy[0])
        y = self.__getattribute__(xy[1])
        
        try:
            err = self.__getattribute__(xy[2])
            err_out = err.round(5)
        except: # if there is no fs_err return nans for that column.
            err_out = np.zeros_like(x)*np.nan
            
            

        #print (y.shape)
        yout = y.round(5)
        xout = x.round(5)
        if len(np.shape(x))<2 and len(np.shape(y))<2: 
            if len(x) == len(y):
                outdata = np.c_[xout,yout,err_out]          
                headerline = '   '.join(xy)     # generating the header         
                np.savetxt(longname, outdata, delimiter = '\t',fmt = '%.5e' ,header=headerline)
            else:
                print('X, Y must have the same leght')
        else:
            print('Both X and Y must be 1D.')

    def saveList(self, xy = ['_Hlist', '_Klist', 'L_fs', 'fs','fs_err'], filename = 'Auto'):
        '''It saves a txt file with the xy list of variables: listed as ['x','y','z'].
        first element of the list must exist
        it expect a list of strings. 
        It dos not export images nor  x y arributes of inconsistent lenght
    
        '''
        if filename == 'Auto':
            filesave = self.filename[:-5] + '_extr.txt'
        else:
            filesave = filename
        longname = os.path.join(self.directory,filesave)
        x0 = self.__getattribute__(xy[0]) #reference len
        
        ll = []
        for i in range(len(xy)):
            #print(xy[i])
            try:
                if len(self.__getattribute__(xy[i]))==len(x0):
                    globals()[f'x{i}']=self.__getattribute__(xy[i])
                else:
                    print('variables must have the same lenght')
                    
            except: # if there is no fs_err return nans for that column.
                globals()[f'x{i}'] = np.zeros_like(x0)*np.nan
                
            ll.append(globals()[f'x{i}'])
                    
        #globals()[f'x{el}'] = np.arange(5)
        #ll.append(globals()[f'x{el}'])
        # try:
        #     err = self.__getattribute__(xy[2])
        #     err_out = err.round(5)
        # except: # if there is no fs_err return nans for that column.
        #     err_out = np.zeros_like(x)*np.nan
            
       
        titi = np.asanyarray(ll)
        outdata = titi.T
        headerline = '   '.join(xy)
        np.savetxt(longname, outdata, delimiter = '\t',fmt = '%.5e' ,header=headerline)
   
    
    def saveAsNpy_old(self, logdata=False):
       '''It saves axis as grid and data as vector.
       meant to be ued to load into Blender.
       data are normalised to 1 and NaNs filled with 0'''
       
       #int(1+axetemp[5]-axetemp[4])
       nx = int(1+ self.__getattribute__("_"+self.axes_names[0])[5]- self.__getattribute__("_"+self.axes_names[0])[4])
       ny = int(1+ self.__getattribute__("_"+self.axes_names[1])[5]- self.__getattribute__("_"+self.axes_names[1])[4])
       nz = int(1+ self.__getattribute__("_"+self.axes_names[2])[5]- self.__getattribute__("_"+self.axes_names[2])[4])
       
       xmin = self.__getattribute__("_"+self.axes_names[0])[1]
       xmax =self.__getattribute__("_"+self.axes_names[0])[2]
       
       ymin = self.__getattribute__("_"+self.axes_names[1])[1]
       ymax =self.__getattribute__("_"+self.axes_names[1])[2]
       
       zmin = self.__getattribute__("_"+self.axes_names[2])[1]
       zmax =self.__getattribute__("_"+self.axes_names[2])[2]
       if self.verbose:
           print('X',nx, xmin, xmax)
           print('y',ny, ymin, ymax)
           print('Z',nz, zmin, zmax)
           
           
       X,Y,Z = np.mgrid[
           xmin:xmax:(nx*1j),   # 1j tells NumPy to produce `nx` points inclusive
           ymin:ymax:(ny*1j),
           zmin:zmax:(nz*1j)
           ]
       grid = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
       
       self.grid=grid
       if self.verbose:
           print(np.shape(grid))
       
       np.save(os.path.join(self.directory, self.filename[:-5]+"_grid.npy"),grid)
       
       filled = np.nan_to_num(self.dataRaw, nan=0.0)
       flat = filled.flatten()
       if logdata:
           flat = np.log10(flat)
           print('data log 10')
       vals = flat/max(flat) 
       self.vals = vals
       if self.verbose:
           print(np.shape(vals))
       np.save(os.path.join(self.directory, self.filename[:-5]+"_vals.npy"), vals)
       
       # def genGrid(nx, ny, nz, xmin, xmax, ymin, ymax, zmin, zmax):
       #     X,Y,Z = np.mgrid[
       #         xmin:xmax:(nx*1j),   # 1j tells NumPy to produce `nx` points inclusive
       #         ymin:ymax:(ny*1j),
       #         zmin:zmax:(nz*1j)
       #         ]
       #     coords = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
       #     return coords
       
    def _in_range(self, val,low, high):
        """Return True if low ≤ val ≤ high, otherwise False."""
        return float(low) <= float(val) <= float(high)

       
       
    def saveAsNpy(self, LowT=0,HighT=1,contrast=1,logdata=False):
        '''meant to genenrate an x y  z Intensity npy file for blender 
        LowT: low threshold
        HighT: high threshold
          Both meant to be  between 0 and 1
        contrast is the exponent applied to the data to artificially change the contrast'''
        X = self.__getattribute__(self.axes_names[0])
        Y = self.__getattribute__(self.axes_names[1])
        Z = self.__getattribute__(self.axes_names[2])
        rows = []
        data = np.nan_to_num(self.dataRaw, nan=0.0)
        if self.verbose: print(data.shape)
        if logdata:
            data = np.nan_to_num(self.dataRaw, nan=0.0)
            data = np.log10(data+1)
        
        dataM = np.nanmax(np.abs(data))
        dataN = data/dataM
        for i, elx in enumerate(X):
            for ii, ely in enumerate(Y):
                for iii, elz in enumerate(Z):
                    val = dataN[i, ii, iii]            
                    line = [elx, ely, elz, val]
                    if self._in_range(val, LowT, HighT):
                        rows.append(line)
        
        arr_4xN = np.asanyarray(rows)
        arr_4xN[:,3]=arr_4xN[:,3]**contrast # apply contrast
        savename = os.path.join(self.directory, self.filename[:-5]+"_4N.npy")
        np.save(savename, arr_4xN)
        if self.verbose:
            print('savend in:', savename)
            print(len(arr_4xN[:,3]),' datapoints')
        return arr_4xN 
    
    def save2tiff(self):
        """It try to save the data as tiff, two possibilities: either dataRaw is two dimension 
        or it exist a OBJ.imgr becore of an axe projection"""
        outname = self.filename[:-5]+'.tiff'
        outFullName = os.path.join(self.directory, outname)
        if len(self.dataRaw.shape)==2:
            print(outFullName)
            iio.imwrite(outFullName, self.dataRaw)
            
        if len(self.dataRaw.shape)>2 and (hasattr(self, 'imgr')):
            print(outFullName)
            iio.imwrite(outFullName, self.imgr)
            
            

            
    
    def exportIsoSurf(self, isoLevel ):
        """Genertate a file .obj to import into blender containing the isosurfaces at the desired levels. """
        I = np.nan_to_num(self.dataRaw, nan=0.0)
        #I = self.dataRaw
        I.astype(np.float32)
        if len(np.shape(self.dataRaw))!=3:
            print("data are not a volume: exiting")
            return
        origin = np.zeros(3)
        for pos,el  in enumerate( self.axes_names):
            origin[pos] = np.min(self.__getattribute__(el))
        if self.verbose: print(I.shape)
        
        intervals=np.zeros(3)
        for pos,el  in enumerate( self.axes_names):
            intervals[pos] = self.__getattribute__("_"+el)[3]
        if self.verbose: print(intervals)
            #iso = 0.5 * I.max()            # choose threshold
        verts, faces, normals, _ = ms.marching_cubes(I, level=isoLevel, spacing=(intervals[0],intervals[1],intervals[2]))
        
        verts_world = verts + origin #place back the origin
        mesh = trimesh.Trimesh(vertices=verts_world, faces=faces, vertex_normals=normals)
        nameOut= str(self.filename[:-5]+"_IsoSurf.obj")
        
        Volume_out = mesh.export(self.directory+nameOut, file_type='obj');
        if self.verbose: print("file saved")
        return
    
    
    
    def exportIsoSurfs(self, isoLevels ):
        """Genertate a file .obj to import into blender containing the multiple isosurfaces at the desired isoLevels. 
        isoLevels eg: [10, 30, 60, 120]"""
        #I = self.dataRaw
        I = np.nan_to_num(self.dataRaw, nan=0.0)
        I.astype(np.float32)
        if len(np.shape(self.dataRaw))!=3:
            print("data are not a volume: exiting")
            return
        if self.verbose: print(I.shape)
        intervals=np.zeros(3)
        for pos,el  in enumerate( self.axes_names):
            intervals[pos] = self.__getattribute__("_"+el)[3]
        
        origin = np.zeros(3)
        for pos,el  in enumerate( self.axes_names):
            origin[pos] = np.min(self.__getattribute__(el))
            
        if self.verbose: print(intervals)
        
        meshes = []
        for i, iso in enumerate(isoLevels, start=1):
            if not (I.min() <= iso <= I.max()):
                raise ValueError(f"Iso value {iso:.3f} out of range [{I.min():.3f},{I.max():.3f}]")
            verts, faces, normals, _ = ms.marching_cubes(
                I,
                level=iso,
                spacing=(intervals[0],intervals[1],intervals[2]),
                # verbose=False   # keep quiet
            )
            verts_world = verts + origin #place back the origin
            mesh = trimesh.Trimesh(
                vertices=verts_world,
                faces=faces,
                vertex_normals=normals,
                process=False          # keep raw topology
            )
            mesh_name = f"iso_{i}_thr_{iso:.2f}"
            if self.verbose:print(mesh_name)
            
            meshes.append((mesh, mesh_name))
        
        # let's save it!
        scene = trimesh.Scene()
        for mesh, name in meshes:
        # Adding with a custom node name creates an OBJ “o <name>” line
             scene.add_geometry(mesh, node_name=name)
        
        nameOut= str(self.filename[:-5]+"IsoSurfScene.obj")
        output = scene.export(self.directory+nameOut, file_type="obj");
        
        if self.verbose: print("file saved ", self.directory+nameOut)
        return
        
        
# iso_levels = [3, 10, 50, 500]
# ## generate the meshes
# meshes = []          # will hold (mesh, name) tuples
# for i, iso in enumerate(iso_levels, start=1):
#     # safety check – iso must lie inside the data range
#     if not (I.min() <= iso <= I.max()):
#         raise ValueError(f"Iso value {iso:.3f} out of range [{I.min():.3f},{I.max():.3f}]")

#     verts, faces, normals, _ = ms.marching_cubes(
#         I,
#         level=iso,
#         spacing=(voxel, voxel, voxel),
#         # verbose=False   # keep quiet
#     )
#     mesh = trimesh.Trimesh(
#         vertices=verts,
#         faces=faces,
#         vertex_normals=normals,
#         process=False          # keep raw topology
#     )
#     # Give each mesh a readable name – will become an OBJ object name
#     mesh_name = f"iso_{i}_thr_{iso:.2f}"
#     meshes.append((mesh, mesh_name))

# ## save it

# scene = trimesh.Scene()

# for mesh, name in meshes:
#     # Adding with a custom node name creates an OBJ “o <name>” line
#     scene.add_geometry(mesh, node_name=name)

# # Export once – all objects end up in the same file
# outfile = os.path.join(savefolder, "S3469volume_SceneIsos_intensities02.obj")
# output = scene.export(outfile, file_type="obj");
# print(f"Exported {len(meshes)} iso‑surfaces to {outfile}")     
        
        

        