'''
  Write rows to pydm_usage_stats in various tables
'''
from __future__ import print_function
from sqlalchemy import engine, create_engine


def _getdburl(file):
    kwds = {}
    try:
        with open(file) as f:
            for line in f:
                (key,val) = line.split()
                kwds[key] = val
    except IOError:
        raise IOError("Unable to open db connect file " + file)

    return engine.url.URL('mysql+mysqldb', **kwds)

class HandleMeasurement(object):

    def __init__(self, connect_file, id=0, nickname=None):
        # for connect_file use .ssh/stats_alchemy.txt
        self.meas_id=id
        self.meas_name=nickname
        self.root_dir=None

        # get db connection
        db_url = _getdburl(connect_file)
        self.engine = create_engine(db_url)

        if id != 0:
            # Check it's there; fetch nickname
            q = 'select FR.nickname as nick,FR.dir from Measurement M join FileRoot FR on M.fileRootId=FR.id where M.id=' + str(id)
            r = self.engine.execute(q)
            row = r.fetchone()
            if row == None:
                raise Exception("No such id in Measurement table")
            self.nickname = row['nick']
            self.root_dir = row['dir']
            print('Found nickname ' + self.nickname)
        else:
            if nickname is not None:
                # Check if it's there; fetch id
                q = 'select M.id as mid,FR.dir from Measurement M join FileRoot FR on M.fileRootId=FR.id where nickname="' + nickname + '"'
                r = self.engine.execute(q)
                row = r.fetchone()
                if row == None:
                    raise Exception("No row with nickname " + nickname)

                self.meas_id = row['mid']
                self.root_dir = row['dir']
                print('Found id ' + str(self.meas_id))
                
                row = r.fetchone()
                if row != None:
                    raise Exception("No unique row with nickname " + nickname)

        print("Root dir is: ",self.root_dir)

    def scanFiles(self):
      '''
      Look for edl files associated with our measurement context. 
      Make entries in File and MappingFileMeas tables
      '''
      from .getStats import get_stats
      
if __name__ == '__main__':
    manager = HandleMeasurement('/reg/neh/home5/jrb/.ssh/stats_alchemy.txt', 
                                nickname='mec')
    print("Instantiated")
