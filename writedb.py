'''
  Write rows to pydm_usage_stats in various tables
'''
from __future__ import print_function
from sqlalchemy import engine, create_engine
from os import path
from time import mktime,localtime

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

class HandleFileroot(object):

    def __init__(self, connect_file, id=0, nickname=None):
        # for connect_file use .ssh/stats_alchemy.txt
        #self.meas_id=id
        self.nickname=nickname
        self.rootdir=None
        self.rootdir_id=None

        # get db connection
        db_url = _getdburl(connect_file)
        self.engine = create_engine(db_url)

        if id != 0:
            # Check it's there; fetch nickname
            q = 'select FR.nickname as nick,FR.dir,FR.id as frid from FileRoot where FR.id=' + str(id)
            r = self.engine.execute(q)
            row = r.fetchone()
            if row == None:
                raise Exception("No such id in FileRoot table")
            self.nickname = row['nick']
            self.rootdir = row['dir']
            self.rootdir_id = row['frid']
            print('Found nickname ' + self.nickname)
        else:
            if nickname is not None:
                # Check if it's there; fetch id
                q = 'select FR.dir,FR.id as frid from FileRoot FR where nickname="' + nickname + '"'
                r = self.engine.execute(q)
                row = r.fetchone()
                if row == None:
                    raise Exception("No row with nickname " + nickname)

                self.rootdir = row['dir']
                self.rootdir_id = row['frid']
                print('Found id ' + str(self.rootdir_id))
                
                row = r.fetchone()
                if row != None:
                    raise Exception("No unique row with nickname " + nickname)

    def scan_files(self):
        '''
        Look for edl files associated with our file root
        Make entries in File and MappingFileMeas tables
        '''
        from getStats import get_stats

        file_entries = get_stats('*.edl', self.rootdir, fmt='%n?%Y?%X?%x')
        print("#Entries found: ",len(file_entries))
        if len(file_entries) > 0:
            print("First entry: ",file_entries[0][0])
            print("Last modified: ", file_entries[0][1])
            print("Last accessed (count): ", file_entries[0][2])
            print("Last accessed (ascii ts): ", file_entries[0][3])
        # For each file make an entry in File

        connect = self.engine.connect()
        with connect.begin() as trans:

            first = True
            for e in file_entries:
                basename = path.basename(e[0])
                unusedSec = mktime(localtime()) - int(e[2])
                qf = "insert into File (fileRootId, relPath,basename,modifyTimeU,lastAccessU,unused) values ('" + str(self.rootdir_id) + "','" + e[0] + "','" + basename + "','"
                qf += str(e[1]) + "','" + str(e[2]) + "','" + str(unusedSec) + "')"
                if first:
                    print("Insert into File is: ")
                    print(qf)
                    firt = False

                r = connect.execute(qf)
        connect.close()
      
if __name__ == '__main__':
    manager = HandleFileroot('/reg/neh/home5/jrb/.ssh/stats_alchemy.txt', 
                             nickname='hometest')
    #print("Instantiated")
    manager.scan_files()

