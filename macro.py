import sys
import os
import subprocess
import math
import time

if not sys.argv[1]:
	home = "/home/rahmans/remoll-root/remoll"
else:
	home= sys.argv[1]
if not sys.argv[2]:
	macro= "/home/rahmans/jobSubmission/rasterStudy/macro"
else:
	macro= sys.argv[2]
if not sys.argv[3]:
        jsub= "/home/rahmans/jobSubmission/rasterStudy/jsub"
else:
        jsub = sys.argv[3]
if not sys.argv[4]:
	field= "/home/rahmans/remoll-root/remoll/map_directory"
else:
	field= sys.argv[4]
if not sys.argv[5]:
	geometry = "/home/rahmans/remoll-root/remoll/geometry"
else:
	geometry= sys.argv[5]	
if not sys.argv[6]:   
	scratch= "/global/scratch/rahmans/scratch/rasterStudy"
else:
	scratch= sys.argv[6]
if not sys.argv[7]:
        tmp= "/global/scratch/rahmans/tmp/rasterStudy"
else:
        tmp= sys.argv[7]
if not sys.argv[8]:
	batch= "101_hybrid_kryp"
else:
	batch= sys.argv[8]
if not sys.argv[9]:
	generator="moller"
else:
	generator=sys.argv[9]



if generator=="beam":
  detector = [28]
else:
  detector = [28]

runrange= range(1,1001)


if generator=="beam" or generator=="elastic" or generator=="inelastic":
  eventsperfile = 1000
else:
  eventsperfile = 1000

jsub=jsub+"/"+generator
macro=macro+"/"+generator
scratch=scratch+"/"+generator
tmp=tmp+"/"+ generator

if not os.path.exists(jsub):
        os.system("mkdir "+jsub)
if not os.path.exists(macro):
        os.system("mkdir "+macro)
if not os.path.exists(tmp):
        os.system("mkdir "+tmp)
if not os.path.exists(scratch):
        os.system("mkdir "+scratch)



jsub=jsub+"/"+batch
macro=macro+"/"+batch 
scratch=scratch+"/"+batch
tmp=tmp+"/"+batch

if not os.path.exists(jsub):
	os.system("mkdir "+jsub)
if not os.path.exists(macro):
	os.system("mkdir "+macro)
if not os.path.exists(tmp):
	os.system("mkdir "+tmp)
if not os.path.exists(scratch):
	os.system("mkdir "+scratch)

for i in runrange:
  macrof=open(macro+"/"+generator+"_"+ str(i)+ ".mac", "w")
  macrof.write("/remoll/setgeofile "+geometry+"/mollerMother_merged.gdml\n")
  macrof.write("/remoll/physlist/register QGSP_BERT_HP\n")
  macrof.write("/remoll/physlist/parallel/enable\n") 
  macrof.write("/remoll/parallel/setfile "+geometry+"/mollerParallel.gdml\n")
  macrof.write("/run/numberOfThreads 5\n")
  macrof.write("/run/initialize\n")
  macrof.write("/remoll/addfield "+field+"/hybridJLAB.txt\n")
  macrof.write("/remoll/addfield "+field+"/upstreamJLAB_1.25.txt\n")	
  macrof.write("/remoll/evgen/set "+generator+"\n")
  if generator=="beam":
    macrof.write("/remoll/evgen/beam/origin 0 0 -19.81 m\n")
    macrof.write("/remoll/evgen/beam/rasx 5 mm\n")
    macrof.write("/remoll/evgen/beam/rasy 5 mm\n")
    macrof.write("/remoll/evgen/beam/corrx 0.065\n")
    macrof.write("/remoll/evgen/beam/corry 0.065\n")
    macrof.write("/remoll/evgen/beam/rasrefz -4.5 m\n")
  else:
    macrof.write("/remoll/oldras false\n")
  macrof.write("/remoll/beamene 11 GeV\n")
  macrof.write("/remoll/beamcurr 85 microampere\n")
  macrof.write("/remoll/SD/disable_all\n")
  for det in detector:
    macrof.write("/remoll/SD/enable "+str(det)+"\n")
    macrof.write("/remoll/SD/detect lowenergyneutral "+str(det)+"\n")
    macrof.write("/remoll/SD/detect secondaries "+str(det)+"\n")
    if (det<33):
       macrof.write("/remoll/SD/detect boundaryhits "+str(det)+"\n")
  macrof.write("/remoll/kryptonite/volume logicUSTracker\n")
  macrof.write("/remoll/kryptonite/volume logicDSTracker\n")
  macrof.write("/remoll/kryptonite/volume logicWasher_12\n")
  macrof.write("/remoll/kryptonite/enable\n")
  macrof.write("/remoll/filename "+scratch+"/"+generator+"_"+str(i)+".root\n")
  macrof.write("/run/beamOn "+str(eventsperfile))  
  macrof.close()
		
  jsubf=open(jsub+"/"+generator+"_"+ str(i)+ ".sh", "w")
  jsubf.write("#!/bin/bash\n")
  jsubf.write("#SBATCH --job-name=remoll\n")
  jsubf.write("#SBATCH --time=00:25:00\n")
  jsubf.write("#SBATCH --nodes=1\n")
  jsubf.write("#SBATCH --ntasks=1\n")
  jsubf.write("#SBATCH --cpus-per-task=5\n")
  jsubf.write("#SBATCH --mem=5G\n")
  jsubf.write("#SBATCH --output="+tmp+"/"+generator+"_"+ str(i)+ ".out\n")
  jsubf.write("source /home/rahmans/bin/cedar_env.csh \n")
  jsubf.write("cd "+home+"/build\n")
  jsubf.write("echo \"Current working directory is `pwd`\"\n")
  jsubf.write("./remoll "+macro+"/"+generator+"_"+ str(i)+ ".mac\n")
  jsubf.write("echo \"Program remoll finished with exit code $? at: `date`\"\n")
  jsubf.close()
	        
                
  time.sleep(1)
  subprocess.call("sbatch "+jsub+"/"+generator+"_"+ str(i)+ ".sh",shell=True)
		
		

		
	
	
