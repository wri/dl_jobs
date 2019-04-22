import descarteslabs as dl
import numpy as np
from affine import Affine
from rasterio.crs import CRS

PRODUCT_NAME='tasks_test'
PRODUCT_ID='6d27def1bb7fb0138933a4ee2e33cce9f5af999a:tasks_test'





DESCRIPTION="TEST TASKS TO CATALOG"



INPUTS=[
    'airbus:oneatlas:phr:v2:PHR1A_201604030525439_1850267101-001_R2C1',
    'airbus:oneatlas:phr:v2:PHR1B_201603210525340_1866537101-001_R1C1',
    'airbus:oneatlas:phr:v2:PHR1B_201703130529519_2221140101-001_R2C1']


PROFILE={
    'compress': 'lzw',
    'count': 3,
    'crs': CRS.from_dict(init='epsg:32644'),
    'driver': 'GTiff',
    'dtype': 'uint8',
    'height': 416,
    'interleave': 'pixel',
    'nodata': None,
    'tiled': False,
    'transform': Affine(1.0, 0.0, 228527.210289,
       0.0, -1.0, 1927206.43733),
    'width': 416}


INPUT_BANDS=[
    'red',
    'green',
    'blue',
    'nir' ]

OUTPUT_BANDS=[
    'ndvi',
    'ndwi']

MAX_VALUE=1
NBITS=8
DATA_RANGE=[0,2]
DTYPE='Float32'
EPS=1e-8
#
# HELPERS
#
def crs_res_bounds(profile):
    """ get crs, resolution and bounds form image profile """
    affine=profile['transform']
    res=affine.a
    minx=affine.c
    # miny=affine.f <=== y-offset shifted by height using affine.f
    miny=affine.f-profile['height']*res
    maxx=minx+profile['width']*res
    maxy=miny+profile['height']*res
    crs=str(profile['crs'])
    return crs,res,(minx,miny,maxx,maxy)


def delete_product(prod_id=PRODUCT_NAME):
    try:
        resp=dl.Catalog().remove_product(prod_id, add_namespace=True, cascade=True)
        print("DELETE_PROD",resp)
    except Exception as e:
        print("DELETE_PROD_ERR",e)


def add_product(prod_id=PRODUCT_NAME):
    catalog=dl.Catalog()
    try:
        resp=catalog.add_product(prod_id,prod_id.upper(),DESCRIPTION,resolution='10m')
        print("ADDPROD: ",prod_id,resp)
        return resp
    except Exception as e:
        print("ADDPROD ERROR: ",prod_id,e)


    return catalog.add_product(
        prod_id,
        prod_id.upper(),
        DESCRIPTION,
        resolution='10m')


def add_bands(prod_id):
    catalog=dl.Catalog()
    results=[]
    for i,b in enumerate(OUTPUT_BANDS):
        results.append(add_band(prod_id,b,i+1,catalog=catalog))
    return results


def add_band(prod_id,name,srcband,catalog=None):
    if name.lower()=='ndvi':
        color='Red'
    else:
        color='Green'
    if not catalog:
        catalog=dl.Catalog()
    return catalog.add_band(
        product_id=prod_id,
        name=name, 
        data_range=DATA_RANGE,
        srcband=srcband,
        dtype=DTYPE,
        nbits=NBITS,
        type='spectral',
        color=color,
        description=f'{name}: {color}'
    )
    
#
# MAIN
#
def cloud_score():
    pass

def water_mask():
    pass

def get_image():
    inputs=INPUTS
    crs,res,bounds=crs_res_bounds(PROFILE)
    print('get_image1:',crs,res,*bounds)
    im,meta=dl.raster.ndarray(
        inputs, 
        bands=INPUT_BANDS, 
        resolution=res, 
        bounds=bounds, 
        bounds_srs=crs)
    print('get_image2:',meta,im.shape)
    return im,meta


def dl_get_image():
    print('FROM DL')
    return get_image()


def preprocess(*args):
    cloud_score()
    water_mask()
    return args[0]


def predictions(im):
    im=im.astype(np.float)
    nir=(im[:,:,3]-im[:,:,0])/(im[:,:,3]+im[:,:,0]+EPS)
    ndwi=(im[:,:,1]-im[:,:,3])/(im[:,:,1]+im[:,:,3]+EPS)
    im=np.dstack([nir+1,ndwi+1])
    print('PRED',im.shape)
    return im


def local_write(*args):
    print('TO DISK')
    return dl_write(*args)


def dl_write(im,image_id,meta,product_id=PRODUCT_ID,**kwargs):
    return dl.Catalog().upload_ndarray(
        im,
        product_id,
        image_id,
        proj4=None,
        wkt_srs=None,
        geotrans=None,
        raster_meta=meta,
        **kwargs)







