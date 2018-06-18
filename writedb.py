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
            q = 'select FR.nickname as nick,FR.dir,FR.id as frid from FileRoot FR where FR.id=' + str(id)
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
        else:
            print("No files found")
            return

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
                    first = False

                r = connect.execute(qf)
        connect.close()
    def scan_objects(self, dryrun=True):
        from getStats import get_grep
        testing=False

        olist = get_grep('*.edl', self.rootdir, grep_options='-H -n')
        print('#objects found=', len(olist))
        if len(olist) > 0:
            print('First object info:')
            print('Rel filepath: ',olist[0][0], 'Line#: ',olist[0][1],
                  'Line contents: ', olist[0][2])
        else:
            print('Nothing found')
            return
        
        if testing: return

        # Get ready for queries
        connect = self.engine.connect()
        with connect.begin() as trans:

            last_file = ''
            last_file_id = None

            # Get all the widget ids, store in dict
            wids = {}
            wq = 'select id, edlName from Widget'
            r = connect.execute(wq)
            for row in r:
                wids[row[1]] = row[0]
            r.close()

        try:
            start=True
            for i in olist:
                widget_name = i[2].split()[1]
                if widget_name not in wids:
                    wmsg = 'Unknown edl object ' + widget_name
                    if (dryrun):
                        print(wmsg)
                        continue
                    else:
                        raise Exception(wmsg)

                if last_file != i[0]:
                    fiq = 'select id from File where relPath="' + i[0]
                    fiq += '" and fileRootId="'+ str(self.rootdir_id) + '"'
                    innerTrans = connect.begin()
                    try:
                        fres = connect.execute(fiq)
                        innerTrans.commit()
                        row = fres.fetchone()
                        if row is None:
                            msg = "Unscanned file at " + i[0]
                            if (dryrun):
                                print(msg)
                            else:
                                raise Exception(msg)
                        last_file = i[0]
                        last_file_id = row['id']
                        if (dryrun): 
                            print("Found entry for file ", last_file)

                    except:
                        innerTrans.rollback()
                        print("Unscanned file at " + relPath)
                        raise
                iq = 'insert into mappingfilewidget set widgetId="' + str(wids[widget_name])
                iq += '",fileId="' + str(last_file_id) + '",lineNumber="' + str(i[1]) 
                iq += '"'
                if (dryrun):
                    print("Insert query would be: ")
                    print(iq)

                else:
                    r = connect.execute(iq)

        except:
            raise

        connect.close()

if __name__ == '__main__':
    '''
       Have so far handled file roots with ids 1-10
       Plan for the remainder (11-59) is
             * Do scan_files for all that need it (16-59)  [DONE]
             * Do scan_objects(dryrun=True)   for all
                This will gag if a widget occurs in a file which hasn't been
                registered in the Widget table.   Fix all such instances 
                until all fileroots pass
             * Do scan_objects(dryrun=False) in lots of 10 or so

       For blocks of 10 or so
           Run this program once invoking scan_files, scan_objects(dryrun=True)
           If there are missing widgets, insert them into Widgets table
           Run program on same block with scan_objects(dryrun=False) 
               and scan_files call commented out
    '''
    allIds = list(range(60))
    for anId in allIds[51:60] :
        manager = HandleFileroot('/reg/neh/home5/jrb/.ssh/stats_alchemy.txt', id=anId)
        #                         nickname='common')
        #                         nickname='hometest')
        # manager.scan_files()
        manager.scan_objects(dryrun=False)

