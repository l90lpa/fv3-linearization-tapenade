import os
from shutil import copytree, rmtree, ignore_patterns
from utils import *

# Specify include search paths
includePaths = list(map(os.path.abspath, 
                        ["FMS/include", 
                         "FMS/constants", 
                         "FMS/drifters", 
                         "FMS/fms", 
                         "FMS/fms2_io/include", 
                         "FMS/mpp/include",
                         "MAPL/include", 
                         "MAPL/base"]))

# Create clean directory for preprocessed input files
if os.path.isdir("pp"):
    rmtree("pp")
os.mkdir("pp")
ppDir = os.path.abspath("pp")

# Copy input files to preprocessing directory
copydir('./GFDL_atmos_cubed_sphere/model', './pp/model', recursive=False, ignore=ignore_patterns('*.c', 
                                                                                                 'fv_cmp.F90', 
                                                                                                 'fv_sg.F90', 
                                                                                                 'fv_update_phys.F90', 
                                                                                                 'lin_cloud_microphys.F90'))
# copydir('./GFDL_atmos_cubed_sphere/tools', './pp/tools', recursive=False, ignore=include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))
# copydir('./GFDL_atmos_cubed_sphere/geos_utils', './pp/geos_utils', recursive=False, ignore=include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))
# copydir('./GFDL_atmos_cubed_sphere/FMS', './pp/FMS', recursive=False, ignore=include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))
# copydir('./GFDL_atmos_cubed_sphere/MAPL', './pp/MAPL', recursive=False, ignore=include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))

# Preprocess input files
for root, dirs, files in os.walk(ppDir):
    for file in files:
        if file.endswith(('.f90', '.F90', '.h', '.H', '.inc')):
            file = os.path.join(root, os.path.basename(file))
            preprocessFortranFile(file, file, "", includePaths)

# Collect preprocessed input files
inputFiles = getFortranFilesInDirectory(ppDir)

# Generate TLM
generateTLM("./tapenade_3.16/bin/tapenade", "\"fv_dynamics_mod.fv_dynamics (u v pt delp q w delz)/(u v pt delp q w delz)\"", "tlm/", inputFiles, includePaths)