#!/usr/bin/env python

import sys
import os
import subprocess
import math
import time
import argparse

parser = argparse.ArgumentParser(description="Submit array jobs to GREX.")
parser.add_argument("-s", dest="src", action="store", required=False, default="/home/jmammei/REMOLL/remoll_version", help="source folder where simulation directory exists")
parser.add_argument("-v", dest="version", action="store", required=False, default="real_shield", help= "choose the version of simulation to use. current options are develop, kryp_shield, and real_shield")
parser.add_argument("-j", dest="jsub_dir", action="store", required=True, help="choose directory to write the slurm submission scripts")
parser.add_argument("-t", dest="tmp_dir", action="store", required=True, help="choose directory to write the slurm output logs")
parser.add_argument("-o", dest="out_dir", action="store", required=True, help="choose where to write the output root files")
parser.add_argument("-g", dest="gen", action= "store", required=False, default="moller",  help="choose generator to use. Options are moller, elastic, inelastic, beam, etc.")
parser.add_argument("-d", dest="det_list", action= "store", required=False, default=[28], help="provide list of sensitive detectors. Example: [28, 29]. By default, all detectors detect low energy neutrals and secondaries. All detectors with detector id<33 are boundary hit detectors")
parser.add_argument("-r", dest="run_range", action = "store", required=False, default="1", help="provide run range. Example: \"2-5\"")
parser.add_argument("-n", dest="n_events", action= "store", required=False, default=1000, help= "provide number of events per job in the array")
parser.add_argument("--time", dest="time", action= "store", required= False, default= "00:25:00", help= "provide the estimated run time. Ex: \"00:25:00\". Usually it is 10 minutes for 1000 moller events.")

args=parser.parse_args()


if not os.path.exists(args.jsub_dir):
        os.system("mkdir -p "+args.jsub_dir)
if not os.path.exists(args.tmp_dir):
        os.system("mkdir -p "+args.tmp_dir)
if not os.path.exists(args.out_dir):
        os.system("mkdir -p "+args.out_dir)

out=os.path.realpath(args.out_dir)
		
jsubf=open(args.jsub_dir+"/"+args.gen+".sh", "w")
jsubf.write("#!/bin/bash\n")
jsubf.write("#SBATCH --partition=compute\n")
jsubf.write("#SBATCH --job-name=remoll\n")
jsubf.write("#SBATCH --time="+args.time+" \n")
jsubf.write("#SBATCH --nodes=1\n")
jsubf.write("#SBATCH --ntasks=1\n")
jsubf.write("#SBATCH --cpus-per-task=5\n")
jsubf.write("#SBATCH --mem=5G\n")
jsubf.write("#SBATCH --output="+args.tmp_dir+"/"+args.gen+"_%A_%a.out\n")
jsubf.write("source /home/jmammei/REMOLL/environment/cedar_env.sh \n")

macro="$TMPDIR/"+args.gen+"_${SLURM_JOBID}_${SLURM_ARRAY_TASK_ID}.mac"
jsubf.write("touch "+macro+"\n")
jsubf.write("echo /remoll/setgeofile geometry/mollerMother_merged.gdml >>"+macro+"\n")
jsubf.write("echo /remoll/physlist/register QGSP_BERT_HP >>"+macro+"\n")
jsubf.write("echo /remoll/physlist/parallel/enable >>"+macro+"\n") 
jsubf.write("echo /remoll/parallel/setfile geometry/mollerParallel.gdml >>"+macro+"\n")
jsubf.write("echo /run/numberOfThreads 5 >>"+macro+"\n")
jsubf.write("echo /run/initialize >>"+macro+"\n")
jsubf.write("echo /remoll/addfield map_directory/hybridJLAB.txt >>"+macro+"\n")
jsubf.write("echo /remoll/addfield map_directory/upstreamJLAB_1.25.txt >>"+macro+"\n")	
jsubf.write("echo /remoll/evgen/set "+args.gen+" >>"+macro+"\n")
if args.gen=="beam":
    jsubf.write("echo /remoll/evgen/beam/origin 0 0 -7.5 m >>"+macro+"\n")
    jsubf.write("echo /remoll/evgen/beam/rasx 5 mm >>"+macro+"\n")
    jsubf.write("echo /remoll/evgen/beam/rasy 5 mm >>"+macro+"\n")
    jsubf.write("echo /remoll/evgen/beam/corrx 0.065 >>"+macro+"\n")
    jsubf.write("echo /remoll/evgen/beam/corry 0.065 >>"+macro+"\n")
    jsubf.write("echo /remoll/evgen/beam/rasrefz -4.5 m >>"+macro+"\n")
else:
    jsubf.write("echo /remoll/oldras false >>"+macro+"\n")
jsubf.write("echo /remoll/beamene 11 GeV >>"+macro+"\n")
jsubf.write("echo /remoll/beamcurr 85 microampere >>"+macro+"\n")
jsubf.write("echo /remoll/SD/disable_all >>"+macro+"\n")
for det in args.det_list:
    jsubf.write("echo /remoll/SD/enable "+str(det)+" >>"+macro+"\n")
    jsubf.write("echo /remoll/SD/detect lowenergyneutral "+str(det)+" >>"+macro+"\n")
    jsubf.write("echo /remoll/SD/detect secondaries "+str(det)+" >>"+macro+"\n")
    if (det<33):
       jsubf.write("echo /remoll/SD/detect boundaryhits "+str(det)+" >>"+macro+"\n")
jsubf.write("echo /remoll/kryptonite/volume logicUSTracker >>"+macro+"\n")
jsubf.write("echo /remoll/kryptonite/volume logicDSTracker >>"+macro+"\n")
jsubf.write("echo /remoll/kryptonite/volume logicWasher_12 >>"+macro+"\n")
jsubf.write("echo /remoll/kryptonite/enable >>"+macro+"\n")
jsubf.write("echo /remoll/filename "+out+"/"+args.gen+"_${SLURM_JOBID}_${SLURM_ARRAY_TASK_ID}.root >>"+macro+"\n")
jsubf.write("echo /run/beamOn "+str(args.n_events)+" >>"+macro+"\n")  
jsubf.write("cat "+macro+"\n")

jsubf.write("cp -r "+args.src+"/"+args.version+" $TMPDIR\n")
jsubf.write("cd $TMPDIR/"+args.version+" \n")
jsubf.write("echo \"Current working directory is `pwd`\"\n")
jsubf.write("./build/remoll "+macro+"\n")
jsubf.write("echo \"Program remoll finished with exit code $? at: `date`\"\n")
jsubf.close()
	        
                
subprocess.call("sbatch --array="+args.run_range+" "+args.jsub_dir+"/"+args.gen+".sh",shell=True)
		
		

		
	
	
