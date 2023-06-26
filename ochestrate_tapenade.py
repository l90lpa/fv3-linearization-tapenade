import utils
import os
from shutil import copytree, rmtree

# Specify include search paths
includePaths = ["/home/lpada/repos/fv3/FMS/include", 
                "/home/lpada/repos/fv3/FMS/constants", 
                "/home/lpada/repos/fv3/FMS/drifters", 
                "/home/lpada/repos/fv3/FMS/fms", 
                "/home/lpada/repos/fv3/FMS/fms2_io/include", 
                "/home/lpada/repos/fv3/FMS/mpp/include",
                "/home/lpada/repos/fv3/MAPL/include", 
                "/home/lpada/repos/fv3/MAPL/base"]

# Create clean directory for preprocessed input files
if os.path.isdir("pp"):
    rmtree("pp")
os.mkdir("pp")
ppDir = os.path.abspath("pp/")

# Copy input files to preprocessing directory
utils.copydir('./GFDL_atmos_cubed_sphere/model', './pp/model', recursive=False, ignore=utils.include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))
os.remove(os.path.join(ppDir, "model/fv_cmp.F90"))
os.remove(os.path.join(ppDir, "model/fv_sg.F90"))
os.remove(os.path.join(ppDir, "model/fv_update_phys.F90"))
os.remove(os.path.join(ppDir, "model/lin_cloud_microphys.F90"))
# utils.copydir('./GFDL_atmos_cubed_sphere/tools', './pp/tools', recursive=False, ignore=utils.include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))
# utils.copydir('./GFDL_atmos_cubed_sphere/geos_utils', './pp/geos_utils', recursive=False, ignore=utils.include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))
# utils.copydir('./GFDL_atmos_cubed_sphere/FMS', './pp/FMS', recursive=False, ignore=utils.include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))
# utils.copydir('./GFDL_atmos_cubed_sphere/MAPL', './pp/MAPL', recursive=False, ignore=utils.include_patterns('*.f90', '*.F90', '*.h', '*.H', '*.inc'))

# Preprocess input files
for root, dirs, files in os.walk(ppDir):
    for file in files:
        if file.endswith(('.f90', '.F90', '.h', '.H', '.inc')):
            file = os.path.join(root, os.path.basename(file))
            utils.preprocessFortranFile(file, file, "", includePaths)

# Collect preprocessed input files
inputFiles = utils.getFortranFilesInDirectory(ppDir)

# Generate TLM
utils.generateTLM("./tapenade_3.16/bin/tapenade", "\"fv_dynamics_mod.fv_dynamics (u v pt delp q w delz)/(u v pt delp q w delz)\"", "tlm/", inputFiles, includePaths)