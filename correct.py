#!/bin/env python3


import ROOT as R
import glob
import os
import sys


file_list= glob.glob("/volatile/halla/moller12gev/rahmans/raw_output/standardPlots/scratch/moller/*.root")

corrupt= 0
good= 0
for file_name in file_list:
  f= R.TFile(file_name)
  good=good+1
  if f.IsZombie() or  f.GetSize()<1000: 
    print(f.GetName()+" is zombie \n")
    corrupt=corrupt+1
    os.system("rm "+file_name)
    good=good-1
  if f.TestBit(R.TFile.kRecovered):
    print(f.GetName()+" is corrupt but recovered\n")
    corrupt=corrupt+1
    os.system("rm "+file_name)
    good=good-1

print("Corrupt: "+str(corrupt))
print("Good: "+str(good))


