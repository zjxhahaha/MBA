import os,shutil
import SimpleITK as sitk 
import random,os
from random import randint, seed 
from PIL import Image
import nibabel as nib
import numpy as np

def resampleVolume(outspacing, vol):
    """
    Resample body data to a specified spacing size \ n
    Paras
    The spacing specified by outputting is for example [1,1,1]
    Vol: The image information read by sitk, here is the body data \ n
    Return: Data after resampling
    """
    outsize = [0, 0, 0]

    inputsize = vol.GetSize()
    inputspacing = vol.GetSpacing()
 
    transform = sitk.Transform()
    transform.SetIdentity()

    outsize[0] = round(inputsize[0] * inputspacing[0] / outspacing[0])
    outsize[1] = round(inputsize[1] * inputspacing[1] / outspacing[1])
    outsize[2] = round(inputsize[2] * inputspacing[2] / outspacing[2])
 

    resampler = sitk.ResampleImageFilter()
    resampler.SetTransform(transform)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetOutputOrigin(vol.GetOrigin())
    resampler.SetOutputSpacing(outspacing)
    resampler.SetOutputDirection(vol.GetDirection())
    resampler.SetSize(outsize)
    newvol = resampler.Execute(vol)
    return newvol


def resample2size(img,new_size=[91,109,91]):
    original_size=img.GetSize()
    original_spacing = img.GetSpacing()

    new_space =[int(round(old_size*old_space/new_size)) for old_size,old_space,new_size in zip(original_size,original_spacing,new_size)]

    resampled_img=sitk.Resample(img,new_size,sitk.Transform(),sitk.sitkLinear,
                            img.GetOrigin(),new_space,img.GetDirection(),0,img.GetPixelID())
    return resampled_img

seg_path = "generate_mask/test_img/True_mask_format"
root_img_path = "/data/ziyang/workspace/Age-Estimation/brain_age_prediction/data/NC/combine/T1_mask/Test/T1/"
# save_path = "/data/ziyang/workspace/Age-Estimation/brain_age_prediction/data/NC/combine/T1_mask/Test/true_mask/"
save_path = "generate_mask/test_img/True_mask_resample"
T1_file_list = os.listdir(root_img_path)
seg_file_list = os.listdir(seg_path)


N = 0
for idx in range(0, len(T1_file_list)):
    img = nib.load(os.path.join(root_img_path, T1_file_list[idx]))
    affine = img.affine
    mask_voxel_num = 0.0
    
    while mask_voxel_num <= 10:
        Random_seg_idx = np.random.randint(0, len(seg_file_list))
        seg_file = seg_file_list[Random_seg_idx]
        print(seg_file)
        seg_img = sitk.ReadImage(os.path.join(seg_path, seg_file))
        seg_img = resample2size(seg_img)
        seg_img = sitk.GetArrayFromImage(seg_img)
        seg_img = np.where((seg_img <= 0.0), seg_img, 1)

        mask_voxel_num = np.sum(seg_img)
        print(mask_voxel_num, Random_seg_idx)
    masked_img = img.get_fdata() * (1 - seg_img)
    seg_img = sitk.GetImageFromArray(seg_img)
    
    
    name = T1_file_list[idx].replace('.nii.gz', '_masked_img.nii.gz')
    # sitk.WriteImage(masked_img, os.path.join(save_path, name))
    nib.Nifti1Image(masked_img,affine).to_filename(os.path.join(save_path, name))


  