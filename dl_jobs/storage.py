from __future__ import print_function
import os
from descarteslabs.client.services.storage import Storage
import dl_jobs.image_io as io
import dl_jobs.config as c
DLS_ROOT=c.get('dls_root')

def file_key(*key_parts,key=None,root=DLS_ROOT):
    if not key:
        if root:
            key_parts=[root]+list(key_parts)
        key=os.path.join(*key_parts)
    return key


def file_upload(path,folder=DLS_ROOT,client=None):
    if client is None:
        client=Storage()
    with open(path, "rb") as file:
        fname=path.split('/')[-1]
        storage_path='{}/{}'.format(folder,fname)
        client.set_file(storage_path, file)
    return storage_path


def files_upload(paths,folder=DLS_ROOT,client=None):
    if client is None:
        client=Storage()
    print('DLS: uploading {} files'.format(len(paths)))
    KEYS=[file_upload(p,folder=folder,client=client) for p in paths]
    return KEYS


def file_url(*key_parts,key=None,root=DLS_ROOT,client=None):
    if client is None:
        client=Storage()
    key=file_key(*key_parts,key=key,root=root)
    return client.get_signed_url(key)


def image_read(*key_parts,key=None,root=DLS_ROOT,client=None):
    if client is None:
        client=Storage()
    key=file_key(*key_parts,key=key,root=root)
    name=key.split('/')[-1]
    path='/cache/{}'.format(name)
    print('DLS: image_read',name)
    client.get_file(key,path)
    return io.read(path)


def ls(*path_parts,path=None,root=DLS_ROOT,client=None):
    if client is None:
        client=Storage()
    if not path:
        if root:
            path_parts=[root]+list(path_parts)
        path=os.path.join(*path_parts)
    return client.list(path)