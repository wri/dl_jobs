import os
import random
import numpy as np
import rasterio as rio
from rasterio.windows import Window
import rasterio.transform as transform


DEFAULT_BATCH_SIZE=8
INPUT_DTYPE=np.float
TARGET_DTYPE=np.int64


#
# READ/WRITE
#
def read(path,window=None,dtype=None,window_profile=True):
    """ read image
    """
    with rio.open(path,'r') as src:
        profile=src.profile
        if window:
            image=src.read(window=Window(*window))
            if window_profile:
                profile=windowed_profile(window,profile)  
        else:
            image=src.read()
        if dtype:
            image=image.astype(dtype)
    return image, profile



def write(im,path,profile,makedirs=True):
    """ write image
    Args: 
        - im (np.array): image
        - path (str): destination path
        - profile (dict): image profile
    """  
    if makedirs:
        dirname=os.path.dirname(path)
        if dirname:
            os.makedirs(os.path.dirname(path),exist_ok=True)
    transform=profile.get('affine')
    if transform:
        profile['transform']=transform
    with rio.open(path,'w',**profile) as dst:
        dst.write(im)
        

#
# WINDOW/PROFILE HELPERS
#
def window_origin(src_transform,window_transform):
    """ origin of window from src and window affine-transform """
    x=(window_transform.c-src_transform.c)/window_transform.a
    y=(window_transform.f-src_transform.f)/window_transform.e
    return round(x),round(y)


def profiles_to_window(src_profile,win_profile):
    """ pixel window from src and window profile """
    x,y=window_origin(src_profile['transform'],win_profile['transform'])
    return Window(x,y,win_profile['width'],win_profile['height'])


def bounds_from_profile(profile):
    """ bounds from profile """
    profile=profile.copy()
    a=profile['transform']
    h=profile['height']
    w=profile['width']
    return transform.array_bounds(h,w,a)


def load_profile_window(path,win_profile):
    """ read window of image based on profile """
    with rio.open(path,'r') as src:
        src_profile=src.profile
        window=profiles_to_window(src_profile,win_profile)
        im=src.read(window=window)
    return im,src_profile


def crop_src_by_window_profile(src,win_profile):
    im=src.read()
    window=profiles_to_window(src.profile,win_profile)
    imin=window.row_off
    jmin=window.col_off
    imax=imin+window.width
    jmax=jmin+window.height
    return im[:,imin:imax,jmin:jmax]


def crs_res_bounds(profile):
    """ get crs, resolution and bounds form image profile """
    affine=profile['transform']
    res=affine.a
    minx=affine.c
    miny=affine.f-profile['height']*res
    maxx=minx+profile['width']*res
    maxy=miny+profile['height']*res
    crs=str(profile['crs'])
    return crs,res,(minx,miny,maxx,maxy)


def windowed_profile(window,profile):
    """ new profile based on original profile and window """
    crs,res,(minx,miny,maxx,maxy)=crs_res_bounds(profile)
    col_off, row_off, width, height=window
    deltax=col_off*res
    deltay=row_off*res
    xmin=minx+deltax
    ymax=maxy+deltay
    affine=Affine(res, 0.0, xmin,0.0, -res, ymax)
    profile=profile.copy()
    profile['width']=width
    profile['height']=height
    profile['transform']=affine
    profile['blockxsize']=min(width,profile.get('blockxsize',0))
    profile['blockysize']=min(width,profile.get('blockysize',0))
    return profile



#
# OTHER
#
def bands_last(im):
    shape=im.shape
    ndim=im.ndim
    if ndim==3:
        if shape[0]<shape[-1]:
            im=im.swapaxes(0,1).swapaxes(1,2)
    elif ndim==4:
        if shape[1]<shape[-1]:
            im=im.swapaxes(1,2).swapaxes(2,3)
    return im


