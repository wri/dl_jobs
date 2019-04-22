import pickle
from datetime import datetime

#
# FILES
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


#
# Timer
#
TS_FMT="%b %d %Y %H:%M:%S"
class Timer(object):

    def __init__(self,ts_fmt=TS_FMT):
        self.ts_fmt=TS_FMT
        self._start_time=None
        self._end_time=None


    def start(self):
        if not self._start_time:
            self._start_time=datetime.now()
        return self._start_time.strftime(self.ts_fmt)


    def stop(self):
        if not self._end_time:
            self._end_time=datetime.now()
        return self._end_time.strftime(self.ts_fmt)


    def duration(self):
        delta=self._end_time-self._start_time
        return str(delta).split('.')[0]


#
# OUTPUT
#



def vspace(n=2):
    print("\n"*n)


def line(char='-',length=100):
    print(char*length)


def log(msg,noisy,level='INFO'):
    if noisy:
        print("[{}] DL_JOBS: {}".format(level,msg))