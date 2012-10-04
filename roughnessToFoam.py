#! /usr/bin/env python
# -*- coding: utf-8 -*-

# roughnessToFoam.py
#
# 1. uses first *.map file as input - from case directory
# 2. runs roughnessToFoam.C --> which writes 0/z0 file (expecting a basic uniform value z0 file with all the boundary patches to exist already)
# 3. copies the terrain_solid z0 nonuniform values to nut[terrain_solid][z0] 

from PyFoam.RunDictionary.ParsedParameterFile   import ParsedParameterFile
from argparse import ArgumentParser
from subprocess import call
import os, sys, glob

def main(args):
    # 0 - reading input
    cwd = os.getcwd()
    os.chdir(args.target)
    mapFileName = glob.glob("*.map")[0]
    
    from pdb import set_trace
    #set_trace()
    
    # 0.5 creating z0 dummy file
    os.system("cp -r 0/p 0/z0")
    z0Dict = ParsedParameterFile("0/z0")
    z0Dict.header["object"] = "z0"
    z0Dict["boundaryField"]["terrain_*"]["value"] = "uniform 0"
    z0Dict["boundaryField"]["terrain_*"]["type"] = "fixedValue"
    z0Dict["dimensions"] = "[ 0 1 0 0 0 0 0]"
    z0Dict.writeFile()

    # 1 - running roughnessToFoam.C
    callString = "( echo %s; echo %d; echo %d; echo %d; echo %d; echo %d; echo %d) | roughnessToFoam" % (mapFileName, args.offsetX, args.offsetY, args.point_ax, args.point_ay, args.point_bx, args.point_by)
    os.system(callString)

    # 2 - reading modified z0 file - made with roughnessToFoam.C
    z0Dict = ParsedParameterFile("0/z0")
    for b in z0Dict["boundaryField"]:
        if b.find("terrain")>-1:
                z0 = z0Dict["boundaryField"][b]["value"]
                print "z0 taken from %s" % b

    # 3 - writing z0 into nut file
    nutDict = ParsedParameterFile("0/nut")
    try:
        print "terrain_* changed"
        nutDict["boundaryField"]["terrain_*"]["z0"] = z0
    except IOError:
        print "no terrain_* in nut file, changing ground"
        nutDict["boundaryField"]["ground"]["z0"] = z0
    nutDict.writeFile()
    os.chdir(cwd)

if __name__ == '__main__':
    # reading arguments
    parser = ArgumentParser()
    parser.add_argument('--offsetX', type=float, default=0, help='x offset of mesh surface vs. z0 polygon map file (WAsP format)')
    parser.add_argument('--offsetY', type=float, default=0, help='y offset of mesh surface vs. z0 polygon map file (WAsP format)')
    parser.add_argument('--point_ax',type=float, default=1, help='x of point (1,0) for mesh surface vs. z0 polygon map file (WAsP format)')
    parser.add_argument('--point_ay', type=float, default=0,help='y of point (1,0) for mesh surface vs. z0 polygon map file (WAsP format)')
    parser.add_argument('--point_bx',type=float, default=0, help='x of point (0,1) for mesh surface vs. z0 polygon map file (WAsP format)')
    parser.add_argument('--point_by',type=float, default=1, help='y of point (0,1) for mesh surface vs. z0 polygon map file (WAsP format)')
    parser.add_argument('--target',default='./', help='location of directory in which the case is located')
    args = parser.parse_args(sys.argv[1:])
    main(args)

class Chdir:         
    def __init__( self, newPath ):  
        self.savedPath = os.getcwd()
        os.chdir(newPath)

    def __del__( self ):
        os.chdir( self.savedPath )
