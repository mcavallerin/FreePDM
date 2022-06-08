"""
    :copyright: Copyright 2022 by the FreePDM team
    :license:   MIT License.
"""

from directorymodel import DirectoryModel
import os
import sys

# right now it should only show a directory that you specify
#  and print the values about that directory. 

def handleDirectory(dir):
    dm = DirectoryModel(dir)
    print("  nr Dir/File  Filename")
    for list in dm.dirList:
        print(list[0].rjust(4, ' ') + ' ' + list[1].ljust(9, ' ') + ' ' + list[2])
  
    ip = input("Press a number or'q' to quit ") 
    if ip == 'q':
        exit()
    num = int(ip)
    if num >= 0 and num <= len(dm.dirList): # We have a number here...
        item = dm.dirList[num]
        print(item)
        if item[1] == 'Directory':
            dir = dir + '/' + dm.dirList[num][2]
            return(dir)
        if item[1] == 'FCStd':
            print(item[2])

def main():
    dir = os.path.expanduser('~')
    if len(sys.argv) == 2:
        dir = sys.argv[1]
    
    handleDirectory(dir)

        

if __name__=="__main__":
    main();