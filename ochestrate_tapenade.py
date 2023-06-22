import os
import shutil
import subprocess
import time


def getAbsoluteFilePathInDirectory(directory):
    filepaths = []
    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for file in files:
            if file.endswith(('.f90', '.F90')):
                filepaths.append(os.path.join(root, file))
    return filepaths


def generateTLM(tapenadePath, rootFunc, inputFiles, outputDirectory):
    if os.path.isdir(outputDirectory):
        shutil.rmtree(outputDirectory)
    os.mkdir(outputDirectory)

    args = ['-r8', '-tgtvarname', '_tl', '-tgtfuncname', '_tlm', '-adjvarname', '_ad', '-adjfuncname', '_adm', '-d', '-O', outputDirectory, '-head', rootFunc]
    args.extend(inputFiles)

    print("Running Tapenade...")
    start = time.time()
    process = subprocess.run(executable=tapenadePath, args=args,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
    print("Elapsed time: ", time.time() - start)
    print("Return code: ", process.returncode)
    print("stdout:\n", process.stdout)
    print("stderr:\n", process.stderr)

inputFiles = getAbsoluteFilePathInDirectory("TestCode")
generateTLM('./tapenade_3.16/bin/tapenade', 'primal_mod.pow2 (x, y)/(x, y)', inputFiles, 'tlm/')

