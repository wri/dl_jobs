from __future__ import print_function
import descarteslabs as dl

OUTPUT_BANDS=[
    'ndvi',
    'ndwi']

#
# HELPERS
#
def delete_product(prod_id):
    try:
        resp=dl.Catalog().remove_product(prod_id, add_namespace=True, cascade=True)
        print("DELETE_PROD",resp)
        return resp
    except Exception as e:
        print("DELETE_PROD_ERR",e)
        return {'error': str(e) }


def add_product(name,description,resolution):
    catalog=dl.Catalog()
    try:
        resp=catalog.add_product(
            name,
            name.upper(),
            description,
            resolution=resolution)
        print("ADDPROD: ",name,resp)
        return resp
    except Exception as e:
        print("ADDPROD ERROR: ",name,e)
        return {'error': str(e) }


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
        description='{}: {}'.format(name,color)
    )
    


def dl_write(im,image_id,meta,product_id,**kwargs):
    return dl.Catalog().upload_ndarray(
        im,
        product_id,
        image_id,
        proj4=None,
        wkt_srs=None,
        geotrans=None,
        raster_meta=meta,
        **kwargs)







