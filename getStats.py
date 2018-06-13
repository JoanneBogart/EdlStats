'''
Given a root directory, return list of files satisfying glob expression under it.
'''
from __future__ import print_function
from subprocess import run, PIPE
from shlex import split as sh_split
from os import linesep

def get_stats(wild, root_dir='.', fmt='%n', sep='?'):
    argstring="find ./ -name '" + wild + "' -exec stat -c '" + fmt + "' '{}' \;"
    res = run(sh_split(argstring), cwd=root_dir, stdout=PIPE, universal_newlines=True)
    return __parse(res.stdout, sep=sep)

def get_grep(wild, root_dir='.', grep_options='-H', grep_string='object ',sep=':'):
    argstring="find ./ -name '" + wild + "' -exec grep " + grep_options + " '" + grep_string + "' '{}' \;"
    res = run(sh_split(argstring), cwd=root_dir, stdout=PIPE, universal_newlines=True)
    return __parse(res.stdout, sep=sep)

'''
toParse is a string with line separators.  For each line, reformat
into list of fields. Fields in toParse lines are separated by a separator 
character sep.
'''

def __parse(toParse, sep='?'):
    #print("here are output lines")
    #print(toParse)

    lines = toParse.splitlines()
    out = []
    for l in lines:
        if len(l.strip()) > 0:
            tokens = l.split(sep)
            out.append(tokens)
    return out

if __name__ == '__main__':
    jrbtestRoot = '/reg/neh/home5/jrb/caqtdm_jrbfork/caQtDM_Viewer'
    bigtestRoot = '/reg/g/pcds/package/epics/3.14-dev/screens/edm/mec/current'
    print('Root is ',jrbtestRoot)
    flist = get_stats('*.edl', jrbtestRoot,
                     '%n?%Z?%X')
    print("Found ", len(flist), " files")
    for f in flist:
        print('File path: ', f[0], 'Modify from epoch: ', f[1], 
              'Last access: ', f[2])


    olist = get_grep('*.edl', root_dir=jrbtestRoot, grep_options='-H -n')
    print("Found ", len(olist), " objects")
    for i in olist:
        print('File path: ', i[0], 'line #: ', i[1],
              'line contents : ', i[2])

    
