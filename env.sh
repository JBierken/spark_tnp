LCG_RELEASE=devswan/latest
LCG_ARCH=x86_64-el9-gcc13

if [[ "$HOSTNAME" == *"ithdp"* ]]; then
    # edge node
    source /cvmfs/sft.cern.ch/lcg/views/${LCG_RELEASE}/${LCG_ARCH}-opt/setup.sh
    echo "Sourcing hadoop edge node environment..."
    source hadoop-setconf.sh analytix 3.2 spark3
    echo "Done!"
elif [[ "$1" == *"lxplus7"* ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_102b/x86_64-centos7-gcc12-opt/setup.sh
    echo "Sourcing lxplus environment..."
    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
    echo "Done!"
elif [[ "$1" == *"lxplus"* ]]; then
    source /cvmfs/sft.cern.ch/lcg/views/${LCG_RELEASE}/${LCG_ARCH}-opt/setup.sh
    echo "Sourcing lxplus environment..."
    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
    export KRB5CCNAME=FILE:$XDG_RUNTIME_DIR/krb5cc
elif [[ "$HOSTNAME" == *"lxplus7"* ]]; then
    # lxplus CentOS7
    sed -i "s~ReplaceMe_by_cdWorkdir~cd $PWD~" condor_wrapper.sh
    sed -i "s~ReplaceMe_by_Hostname~$HOSTNAME~" condor_wrapper.sh

    source /cvmfs/sft.cern.ch/lcg/views/LCG_102b/x86_64-centos7-gcc12-opt/setup.sh
    echo "Sourcing lxplus environment..."
    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
    echo "Done!"
elif [[ "$HOSTNAME" == *"lxplus"* ]]; then
    # lxplus
    sed -i "s~ReplaceMe_by_cdWorkdir~cd $PWD~" condor_wrapper.sh
    sed -i "s~ReplaceMe_by_Hostname~$HOSTNAME~" condor_wrapper.sh

    source /cvmfs/sft.cern.ch/lcg/views/${LCG_RELEASE}/${LCG_ARCH}-opt/setup.sh
    echo "Sourcing lxplus environment..."
    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix 3.2 spark3
    export KRB5CCNAME=FILE:$XDG_RUNTIME_DIR/krb5cc
    kinit
    echo "Done!"
else
    source /cvmfs/sft.cern.ch/lcg/views/${LCG_RELEASE}/${LCG_ARCH}-opt/setup.sh
    echo "[Warning] Environment can only be lxplus or the CERN hadoop edge nodes. See README for more details"
    # still source lxplus env in case this is inside a condor node
    source /cvmfs/sft.cern.ch/lcg/etc/hadoop-confext/hadoop-swan-setconf.sh analytix
fi

# Compile the Roofit fitting function if it doesn't exist yet
if [ ! -f RooCMSShape_cc.so ]; then
    echo ""
    echo "Did not detect a RooCMSShape shared object file. Compiling with ACLiC... (should be needed only once)"
    root -l -b -q -e '.L RooCMSShape.cc+'
    echo "Done!"
fi

if [ ! -f RooErfExp_cc.so ]; then
    echo ""
    echo "Did not detect a RooErfExp shared object file. Compiling with ACLiC... (should be needed only once)"
    root -l -b -q -e '.L RooErfExp.cc+'
    echo "Done!"
fi
if [ ! -f RooCruijff_cxx.so ]; then
    echo ""
    echo "Did not detect a RooCruijff shared object file. Compiling with ACLiC... (should be needed only once)"
    root -l -b -q -e '.L RooCruijff.cxx+'
    echo "Done!"
fi
if [ ! -f RooDCBShape_cxx.so ]; then
    echo ""
    echo "Did not detect a RooDCBShape shared object file. Compiling with ACLiC... (should be needed only once)"
    root -l -b -q -e '.L RooDCBShape.cxx+'
    echo "Done!"
fi
