import fileinput
import os
import re
import shutil
import subprocess
import tempfile
import time

from fnmatch import filter
from os.path import isdir, join

def include_patterns(*patterns):
    """Factory function that can be used with copytree() ignore parameter.

    Arguments define a sequence of glob-style patterns
    that are used to specify what files to NOT ignore.
    Creates and returns a function that determines this for each directory
    in the file hierarchy rooted at the source directory when used with
    shutil.copytree().
    
    Example: shutil.copytree(src_dir, dst_dir, ignore=include_patterns('*.f90', '*.F90', '.h', '.H', '.inc'))

    Taken from: https://stackoverflow.com/a/52072685
    """
    def _ignore_patterns(path, names):
        keep = set(name for pattern in patterns
                            for name in filter(names, pattern))
        ignore = set(name for name in names
                        if name not in keep and not isdir(join(path, name)))
        return ignore
    return _ignore_patterns

def copydir(srcDir, dstDir, recursive = True, ignore = None):
    if recursive:
        shutil.copytree(srcDir, dstDir, ignore=ignore, dirs_exist_ok=True)
    else:
        srcFileNames = []
        for name in os.listdir(srcDir):
            file = os.path.join(srcDir, name)
            if os.path.isfile(file):
                srcFileNames.append(name)
        if ignore is not None:
            ignored_names = ignore(srcDir, srcFileNames)
        else:
            ignored_names = set()

        if not os.path.isdir(dstDir):
            os.mkdir(dstDir)

        for name in srcFileNames:
            if name in ignored_names:
                continue
            shutil.copy(os.path.join(srcDir, name), dstDir)

def getFortranFilesInDirectory(directory):
    """
    Example: inputFiles = getFortranFilesInDirectory("TestCode")
    """
    filepaths = []
    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for file in files:
            if file.endswith(('.f90', '.F90')):
                filepaths.append(os.path.join(root, file))
    return filepaths

def preprocessFortranFile(outputFile, inputFile, definitions, includeSearchPaths):
    """ Runs the gfortran preprocessor on the input file, skipping expansion of `#include`
    
    Example: preprocessFortranFile(outFile, inFile, "-D NAME -D KEY=VALUE")
    """

    skipIncludes = len(includeSearchPaths) == 0

    # Create a temporary file, and copy the input file into it
    if os.path.isdir("./tmp"):
        shutil.rmtree("./tmp")
    os.mkdir("./tmp")
    tmpFile = tempfile.NamedTemporaryFile(dir='./tmp', suffix=os.path.splitext(inputFile)[1], )
    shutil.copy2(inputFile, tmpFile.name)

    if skipIncludes:
        # Comment out `#include`
        includeRegex = re.compile(r"(\s*#\s*include)")
        with fileinput.FileInput(tmpFile.name, inplace=True) as file:
            for line in file:
                line = line.replace("#print*, my_state", "!#print*, my_state") # TODO: remove temporary hack
                print(includeRegex.sub(r"!\1", line), end='')

    # Run gfortran preprocessor
    if skipIncludes:
        command = "gfortran -E -P -C -cpp {} -o {} {}".format(definitions, outputFile, tmpFile.name)
    else:
        prefixedIncludeSearchPaths = ["-I"] * (2 * len(includeSearchPaths))
        prefixedIncludeSearchPaths[1::2] = includeSearchPaths
        prefixedIncludeSearchPaths = " ".join(prefixedIncludeSearchPaths)
        command = "gfortran -E -P -C -cpp {} {} -o {} {}".format(definitions, prefixedIncludeSearchPaths, outputFile, tmpFile.name)

    os.system(command)


    if skipIncludes:
        # Uncomment `#include`
        commentedIncludeRegex = re.compile(r"!(\s*#\s*include)")
        with fileinput.FileInput(outputFile, inplace=True) as file:
            for line in file:
                print(commentedIncludeRegex.sub(r"\1", line), end='')

    
    # Clean-up temporary file
    tmpFile.close()    
    if os.path.isfile(tmpFile.name):
        os.remove(tmpFile.name)


def generateTLM(tapenadePath, rootFunc, outputDirectory, inputFiles, includeSearchPaths):
    """ Runs the gfortran preprocessor on the input file, skipping expansion of `#include`
    
    Example: generateTLM('./tapenade_3.16/bin/tapenade', '\"primal_mod.pow2 (x, y)/(x, y)\"', 'tlm/', [filePath1, filePath2], [dir1, dir2])
    """
    if os.path.isdir(outputDirectory):
        shutil.rmtree(outputDirectory)
    os.mkdir(outputDirectory)

    prefixedIncludeSearchPaths = ["-I"] * (2 * len(includeSearchPaths))
    prefixedIncludeSearchPaths[1::2] = includeSearchPaths

    command = [tapenadePath]
    command.extend(["-linelength", "200", "-r8", "-tgtvarname", "_tl", "-tgtfuncname", "_tlm", "-adjvarname", "_ad", "-adjfuncname", "_adm", "-d", "-O", outputDirectory, "-head", rootFunc])
    command.extend(prefixedIncludeSearchPaths)
    command.extend(inputFiles)
    command = " ".join(command)

    print(command)

    os.system(command)
    
    # start = time.time()
    # process = subprocess.call(command,
    #                     shell=True,
    #                     stdout=subprocess.PIPE, 
    #                     stderr=subprocess.PIPE,
    #                     universal_newlines=True)
    # for line in process.stdout:
    #     print(line, end="") 
    # return_code = process.wait()
    # if return_code:
    #     raise subprocess.CalledProcessError(return_code, tapenadePath)
    # print("Elapsed time: ", time.time() - start)