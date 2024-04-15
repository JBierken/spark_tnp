#LCG_RELEASE=devswan/latest
#LCG_ARCH=x86_64-el9-gcc13

if [[ "$HOSTNAME" == *"ithdp"* ]]; then
    # edge node
    source hadoop-setconf.sh analytix 3.2 spark3
    #source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
     export KRB5CCNAME=FILE:$XDG_RUNTIME_DIR/krb5cc
     kinit
     source /cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-centos7-gcc11-opt/setup.sh
     CC7_LD_LIBRARY_PATH=$LD_LIBRARY_PATH 
     CC7_PYTHONPATH=$PYTHONPATH
     CC7_PYSPARK_PYTHON=$PYSPARK_PYTHON
     source /cvmfs/sft.cern.ch/lcg/views/devswan/latest/x86_64-el9-gcc13-opt/setup.sh
     PYSPARK_DRIVER_PYTHON=$PYSPARK_PYTHON
     PYSPARK_PYTHON=$CC7_PYSPARK_PYTHON
     export JAVA_HOME=/cvmfs/sft.cern.ch/lcg/releases/java/8u362-88cd4/x86_64-el9-gcc13-opt/
     source /cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/setup.sh
     source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
     pyspark --conf spark.executorEnv.JAVA_HOME=$JAVA_HOME --conf spark.yarn.appMasterEnv.JAVA_HOME=$JAVA_HOME
     #pyspark --conf spark.executorEnv.PYTHONPATH=$CC7_PYTHONPATH --conf spark.executorEnv.LD_LIBRARY_PATH=$CC7_LD_LIBRARY_PATH 
    echo "Done!"
#elif [[ "$1" == *"lxplus"* ]]; then
#    source /cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/setup.sh
#    #source /cvmfs/sft.cern.ch/lcg/views/${LCG_RELEASE}/${LCG_ARCH}-opt/setup.sh
#    echo "Sourcing lxplus environment..."
#    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
#    export KRB5CCNAME=FILE:$XDG_RUNTIME_DIR/krb5cc

elif [[ "$HOSTNAME" == *"lxplus7"* ]]; then
    #lxplus CentOS7
    #sed -i "s~ReplaceMe_by_cdWorkdir~cd $PWD~" condor_wrapper.sh
    #sed -i "s~ReplaceMe_by_Hostname~$HOSTNAME~" condor_wrapper.sh

    source /cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-centos7-gcc11-opt/setup.sh
    #source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark2
    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark2
    echo "Sourcing lxplus7 environment..."
    kinit
    echo "Done!"
elif [[ "$HOSTNAME" == *"lxplus"* ]]; then
    # lxplus
    #export PYSPARK_SUBMIT_ARGS="--conf spark.executorEnv.JAVA_HOME=$JAVA_HOME --conf spark.yarn.appMasterEnv.JAVA_HOME=$JAVA_HOME pyspark-shell"
    #export JAVA_HOME=/cvmfs/sft.cern.ch/lcg/releases/java/8u362-88cd4/x86_64-el9-gcc13-opt/
    source /cvmfs/sft.cern.ch/lcg/views/LCG_105_swan/x86_64-el9-gcc13-opt/setup.sh
    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
    #export JAVA_HOME=/cvmfs/sft.cern.ch/lcg/releases/java/8u362-88cd4/x86_64-el9-gcc13-opt/ù
    export KRB5CCNAME=FILE:$XDG_RUNTIME_DIR/krb5cc
    #pyspark

    echo "Done!"
else
    echo "attenzione!"
    #source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
    #echo "Sourcing lxplus environment..."
    #source /cvmfs/sft.cern.ch/lcg/views/devswan/latest/x86_64-el9-gcc13-opt/setup.sh
    #export KRB5CCNAME=FILE:$XDG_RUNTIME_DIR/krb5cc
    #echo "Done!"
fi

# Compile the Roofit fitting function if it doesn't exist yet
if [ ! -f RooCMSShape_cc.so ]; then
    echo ""
    echo "Did not detect a RooCMSShape shared object file. Compiling with ACLiC... (should be needed only once)"
    root -l -b -q -e '.L RooCMSShape.cc+'
    echo "Done!"
fi

if [ ! -f RooDCBShape_cxx.so ]; then
    echo ""
    echo "Did not detect a RooDCBShape shared object file. Compiling with ACLiC... (should be needed only once)"
    root -l -b -q -e '.L RooDCBShape.cxx+'
    echo "Done!"
fi

