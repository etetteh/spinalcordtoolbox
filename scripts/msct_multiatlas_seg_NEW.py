#!/usr/bin/env python
########################################################################################################################
#
# Asman et al. groupwise multi-atlas segmentation method implementation, with a lot of changes
#
#
# ----------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2014 Polytechnique Montreal <www.neuro.polymtl.ca>
# Authors: Sara Dupont
# Created: 2016-06-15
#
# About the license: see the file LICENSE.TXT
########################################################################################################################
import os
import numpy as np
from sct_utils import printv, slash_at_the_end
from msct_gmseg_utils_NEW import pre_processing

class ModelParam:
    def __init__(self):
        self.path_data = ''
        self.todo = 'load'# 'compute' or 'load'
        self.new_model_dir = 'gmseg/'

class DataParam:
    def __init__(self):
        self.denoising = True
        self.axial_res = 0.3
        self.register_param = ''
class Param:
    def __init__(self):
        self.verbose = 1

class ModelDictionary:
    def __init__(self, model_param=None, data_param=None, param=None):
        self.model_param = model_param if model_param is not None else ModelParam()
        self.data_param = data_param if data_param is not None else DataParam()
        self.param = param if param is not None else Param()

        self.slices = []
        self.mean_image = None

    def compute_model(self):
        printv('\nComputing the model dictionary ...', self.param.verbose, 'normal')
        os.mkdir(self.param.new_model_dir)
        param_fic = open(self.model_param.new_model_dir + 'info.txt', 'w')
        param_fic.write(str(self.param))
        param_fic.close()

        printv('\n\tLoading data dictionary ...', self.param.verbose, 'normal')
        self.load_data()
        self.mean_image = np.mean([dic_slice.im for dic_slice in self.slices], axis=0)

        printv('\n\tCo-register all the data into a common groupwise space (using the white matter segmentations) ...', self.param.verbose, 'normal')
        self.coregister_data()

        ## TODO: COMPLETE COMPUTE _DIC

    def load_data(self):
        '''
        Data should be organized with one folder per subject containing:
            - A WM/GM contrasted image containing 'im' in its name
            - a segmentation of the SC containing 'seg' in its name
            - a/several manual segmentation(s) of GM containing 'gm' in its/their name(s)
            - a file containing vertebral level information as a nifti image or as a text file containing 'level' in its name
        '''
        path_data = slash_at_the_end(self.model_param.path_data, slash=1)

        # total number of slices: J
        j = 0

        for sub in os.listdir(path_data):
            # load images of each subject
            if os.path.isdir(path_data+sub):
                fname_data = ''
                fname_sc_seg = ''
                list_fname_gmseg = []
                fname_level = None
                for file_name in os.listdir(path_data+sub):
                    if 'gm' in file_name:
                        list_fname_gmseg.append(path_data+sub+'/'+file_name)
                    elif 'seg' in file_name:
                        fname_sc_seg = path_data+sub+'/'+file_name
                    elif 'im' in file_name:
                        fname_data = path_data+sub+'/'+file_name
                    if 'level' in file_name:
                        fname_level = path_data+sub+'/'+file_name

                # preprocess data
                list_slices_sub, info = pre_processing(fname_data, fname_sc_seg, fname_level=fname_level, fname_manual_gmseg=list_fname_gmseg, new_res=self.data_param.axial_res, denoising=self.data_param.denoising)
                for slice_sub in list_slices_sub:
                    slice_sub.set(slice_id=slice_sub.id+j)
                    self.slices.append(slice_sub)

                j += len(list_slices_sub)

    def coregister_data(self):
        pass

    '''
    def register_data(self, fname_src, fname_dest, paramreg):
        from sct_register_multimodal import Param as Param_reg_mm
        from sct_register_multimodal import register

        param_register = Param_reg_mm()
        # loop across registration steps
        warp_forward = []
        warp_inverse = []
        for i_step in range(0, len(paramreg.steps)):
            printv('\n--\nESTIMATE TRANSFORMATION FOR STEP #' + str(i_step), self.param.verbose)
            # identify which is the src and dest
            if paramreg.steps[str(i_step)].type == 'im':
                src = 'src.nii'
                dest = 'dest_RPI.nii'
                interp_step = 'spline'
            elif paramreg.steps[str(i_step)].type == 'seg':
                src = 'src_seg.nii'
                dest = 'dest_seg_RPI.nii'
                interp_step = 'nn'
            else:
                src = dest = interp_step = None
                sct.run('ERROR: Wrong image type.', 1, 'error')
            # if step>0, apply warp_forward_concat to the src image to be used
            if i_step > 0:
                sct.printv('\nApply transformation from previous step', self.param.verbose)
                sct.run('sct_apply_transfo -i ' + src + ' -d ' + dest + ' -w ' + ','.join(
                    warp_forward) + ' -o ' + sct.add_suffix(src, '_reg') + ' -x ' + interp_step, self.param.verbose)
                src = sct.add_suffix(src, '_reg')
            # register src --> dest
            warp_forward_out, warp_inverse_out = register(src, dest, paramreg, param_register , str(i_step))
            warp_forward.append(warp_forward_out)
            warp_inverse.insert(0, warp_inverse_out)

        # Concatenate transformations
        sct.printv('\nConcatenate transformations...', self.param.verbose)
        sct.run('sct_concat_transfo -w ' + ','.join(warp_forward) + ' -d dest.nii -o warp_src2dest.nii.gz', self.param.verbose)
        sct.run('sct_concat_transfo -w ' + ','.join(warp_inverse) + ' -d dest.nii -o warp_dest2src.nii.gz', self.param.verbose)

        # Apply warping field to src data
        sct.printv('\nApply transfo source --> dest...', self.param.verbose)
        sct.run('sct_apply_transfo -i src.nii -o src_reg.nii -d dest.nii -w warp_src2dest.nii.gz -x ' + interp, self.param.verbose)
        sct.printv('\nApply transfo dest --> source...', self.param.verbose)
        sct.run('sct_apply_transfo -i dest.nii -o dest_reg.nii -d src.nii -w warp_dest2src.nii.gz -x ' + interp,
                self.param.verbose)
    '''




