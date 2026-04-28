'''
accept the name of a file in the language-samples directory, and split it into
test files and a training file.
default:
    ten one-line files, five ten-line files, two 10000 character files
    remainder of file training data

    report number of lines and chars of training data.
'''

import os.path
import sys

#tiny user interface
default = [('.A.',10,1,-1), ('.B.',5,10,-1), ('.C.',2,-1,10000)]

command = default
indir = 'language-samples' 
infile = 'french'
if len(sys.argv) > 1: infile = sys.argv[1]

def main():
    with open(os.path.join(indir,infile+'.txt')) as fi:
        for tag, numf, lines, chars in command:
            for i in range(numf):
                with open(infile+ tag + str(i) + '.test','w') as fo:
                    if lines > 0:
                        for _ in range(lines):
                            fo.write(fi.readline())
                    else:
                        sofar = 0
                        while sofar < chars:
                            x = fi.readline()
                            sofar += len(x)
                            fo.write(fi.readline())

        with open(infile+'.train','w') as fo:
            sofar = 0
            while True:
                x = fi.read()
                sofar += len(x)
                if len(x) == 0: break
                fo.write(x)
        print(infile+'.train contains', sofar, 'characters')









if __name__ == '__main__': main()
