import pickle

#
# HELPERS
#
def save_pickle(obj,path):
    """ save object to pickle file
    """    
    with open(path,'wb') as file:
        pickle.dump(obj,file,protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(path):
    """ read pickle file
    """    
    with open(path,'rb') as file:
        obj=pickle.load(file)
    return obj


def log(msg,noisy,level='INFO'):
    if noisy:
        print("[{}] DL_JOBS: {}".format(level,msg))