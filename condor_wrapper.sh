#!/bin/bash
echo "Setting up environment"
cd /afs/cern.ch/user/m/mibarbie/spark_tnp
source env_cp_root_files_fit_jobs.sh
PYTHONPATH=/cvmfs/sft.cern.ch/lcg/releases/condor/23.0.2-36b2d/x86_64-el9-gcc13-opt/lib/python3:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages/itk:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/python:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages

PATH=/usr/hdp/spark/bin:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/scripts:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/bin:/cvmfs/sft.cern.ch/lcg/releases/gcc/13.1.0-b3d18/x86_64-el9/bin:/cvmfs/sft.cern.ch/lcg/releases/binutils/2.40-acaab/x86_64-el9/bin:/afs/cern.ch/cms/caf/scripts:/cvmfs/cms.cern.ch/common:/usr/sue/bin:/usr/share/Modules/bin:/usr/condabin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/puppetlabs/bin:/afs/cern.ch/user/m/mibarbie/.local/bin:/afs/cern.ch/user/m/mibarbie/bin

LD_LIBRARY_PATH=/cvmfs/sft.cern.ch/lcg/releases/MCGenerators/thepeg/2.2.3-3c3f6/x86_64-el9-gcc13-opt/lib/ThePEG:/cvmfs/sft.cern.ch/lcg/releases/MCGenerators/herwig++/7.2.3-46eae/x86_64-el9-gcc13-opt/lib/Herwig:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages/jaxlib/mlir/_mlir_libs:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages/torch/lib:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages/onnxruntime/capi/:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages/tensorflow:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages/tensorflow/contrib/tensor_forest:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib/python3.9/site-packages/tensorflow/python/framework:/cvmfs/sft.cern.ch/lcg/releases/java/11.0.21p9-cabd2/x86_64-el9-gcc13-opt/jre/lib/amd64:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib64:/cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/lib:/cvmfs/sft.cern.ch/lcg/releases/gcc/13.1.0-b3d18/x86_64-el9/lib:/cvmfs/sft.cern.ch/lcg/releases/gcc/13.1.0-b3d18/x86_64-el9/lib64:/cvmfs/sft.cern.ch/lcg/releases/binutils/2.40-acaab/x86_64-el9/lib:/cvmfs/sft.cern.ch/lcg/releases/R/4.3.0-3cb7c/x86_64-el9-gcc13-opt/lib64/R/library/readr/rcon

export PYTHONPATH=$PYTHONPATH
export PATH=$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH

echo "Setup complete"
echo "Will run:"
echo "$@"
eval "$@"
