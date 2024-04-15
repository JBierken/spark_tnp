import os
import subprocess
import glob
import getpass
from pyspark.sql import SparkSession

from registry import registry
from dataset_allowed_definitions import get_allowed_sub_eras
from pyspark.sql.functions import when
from pyspark.sql.functions import col
from pyspark.sql.functions import sqrt, cos, cosh, radians



def run_convert(spark, particle, resonance, era, dataTier, subEra, customDir='', baseDir='', use_pog_space=False, use_local=False):
    '''
    Converts a directory of root files into parquet
    '''

    if baseDir == '':
        if use_pog_space is False:
            inDir = os.path.join('hdfs://analytix/user', getpass.getuser())
            outDir = os.path.join('hdfs://analytix/user', getpass.getuser())
        else:
            inDir = 'hdfs://analytix/cms/muon_pog'
            outDir = 'hdfs://analytix/cms/muon_pog'
        inDir = os.path.join(inDir, 'root', customDir, particle, resonance, era, dataTier, subEra)
        outDir = os.path.join(outDir, 'parquet', customDir, particle, resonance, era, dataTier, subEra)
    else:
        if use_local is False and 'hdfs' not in baseDir:
            print('>>>>>>>>> Warning! Custom baseDir given to convert but `useLocalSpark` flag not enabled and no `hdfs` in baseDir.')
            print('>>>>>>>>> Distributed spark clusters can only read files in hdfs. Make sure baseDir is an `hdfs` path, e.g.:')
            print('>>>>>>>>> `hdfs://analytix/user/[user]/[your-custom-dir]`')
            print('>>>>>>>>> Or else, if this is a local test, use the `--useLocalSpark` flag (see command help).')
        inDir = baseDir
        outDir = baseDir

    # The following glob command works only on the edge nodes, which has a fuse-style hdfs mountpoint    
    # if 'hdfs' in inDir:
    #     inDir = inDir.replace('hdfs://analytix', '/hdfs/analytix.cern.ch')
    #     fnames = glob.glob(os.path.join(inDir, f'{inDir}/*.root'))
    # else:
    #     fnames = glob.glob(f'{inDir}/*.root')
    # fnames = [f.replace('/hdfs/analytix.cern.ch', 'hdfs://analytix') for f in fnames]
    
    # Make sure path is in hdfs format (not fuse-style format)
    inDir = inDir.replace('/hdfs/analytix.cern.ch', 'hdfs://analytix')
    outDir = outDir.replace('/hdfs/analytix.cern.ch', 'hdfs://analytix')

    # The following glob command works in both lxplus and edge nodes
    cmd = "hdfs dfs -find {} -name '*.root'".format(inDir)
    fnames = subprocess.check_output(cmd, shell=True).strip().split(b'\n')
    fnames = [fname.decode('ascii') for fname in fnames]
    
    outName = os.path.join(outDir, 'tnp.parquet')
    if use_local is True and 'hdfs' not in outName:
        outName = 'file://' + outName
    else:
        outName = outName.replace('/hdfs/analytix.cern.ch', 'hdfs://analytix') # just in case

    print(f'>>>>>>>>> Path to input root files: {inDir}')
    print(f'>>>>>>>>> Path to output parquet files: {outName}')
    
    # treename = 'tpTree/fitter_tree' # old tnp tool tree name
    # treename = 'muon/tree' # old miniAOD tree name
    treename = 'muon/StandAloneEvents'

    print(f'>>>>>>>>> Number of files to process: {len(fnames)}')
    if len(fnames) == 0:
        print('>>>>>>>>> Error! No ROOT files found to convert with desired options.')
        print('>>>>>>>>> Exiting...')
        return
    print(f'>>>>>>>>> First file: {fnames[0]}')

    # process batchsize files at a time
    batchsize = 100
    new = True
    
    while fnames:
        current = fnames[:batchsize]
        fnames = fnames[batchsize:]

        rootfiles = spark.read.format("root")\
                         .option('tree', treename)\
                         .load(current)

        rootfiles = rootfiles.select("run","event","pair_mass", "tag_pt","tag_eta","tag_phi", "tag_isTight","tag_charge","probe_charge","tag_pfIso04_neutral","tag_pfIso04_photon","tag_pfIso04_sumPU","tag_pfIso04_charged","tag_hltL3crIsoL1sSingleMu22L1f0L2f10QL3f24QL3trkIsoFiltered","tag_hltL3fL1sSingleMu22L1f0L2f10QL3Filtered24Q","probe_pt","probe_isTrkMatch","probe_isSA","probeSA_isTrkMatch","probe_eta","nVertices","ls","probe_minDR","istlumi","HLT_IsoMu24_v","HLT_Mu50_v","tag_hltL3fL1sSingleMu22L1f0L2f10QL3Filtered24Q_dr","probe_phi","probe_trkPt","probe_trkEta","probe_trkPhi","tag_dxy","tag_dz","probe_dxy","probe_dz","probe_pixelLayers","probe_trackerLayers","probe_trkStripHits","probe_trkPixelHits","probe_trkHits","probe_pixelHits") #selection of variables for AOD                
       
       # Adding a new column "pair_mass_corrected" based on the condition
        rootfiles = rootfiles.withColumn("pair_mass_corr", when((col("probe_isTrkMatch")  & ~col("probeSA_isTrkMatch")) , sqrt(2*col("tag_pt")*col("probe_trkPt")*(cosh(col("tag_eta")-col("probe_trkEta"))-cos((col("tag_phi")-(col("probe_trkPhi"))))))).otherwise(col("pair_mass")))                     
        # merge rootfiles. chosen to make files of 8-32 MB (input)
        # become at most 1 GB (parquet recommendation)
        # https://parquet.apache.org/documentation/latest/
        # .coalesce(int(len(current)/32)) \
        # but it is too slow for now, maybe try again later
        if new:
            rootfiles.write.parquet(outName)
            new = False
        else:
            rootfiles.write.mode('append')\
                     .parquet(outName)


def run_all(particle, resonance, era, dataTier, subEra=None, customDir='', baseDir='', use_pog_space=False, use_local=False):

    if subEra is not None:
        subEras = [subEra]
    else:
        subEras = get_allowed_sub_eras(resonance, era)
        # subEras by default includes whole era too, so remove for convert
        subEras.remove(era)

    local_jars = ','.join([
        './laurelin-1.6.0.jar',
        './log4j-api-2.13.0.jar',
        './log4j-core-2.13.0.jar',
    ])
    
    import os

    # java8 
    java_home = "/cvmfs/sft.cern.ch/lcg/releases/java/8u362-88cd4/x86_64-el9-gcc13-opt/"

    
    spark = SparkSession\
        .builder\
        .appName("TnP")\
        .config("spark.jars", local_jars)\
        .config("spark.driver.extraClassPath", local_jars)\
        .config("spark.executor.extraClassPath", local_jars)\
        .config("spark.dynamicAllocation.maxExecutors", "100")\
        .config("spark.driver.memory", "10g")\
        .config("spark.executor.memory", "10g")\
        .config("spark.sql.shuffle.partitions", "500")\
        .config("spark.executor.cores", "1")\
        .config("spark.sql.broadcastTimeout", "36000")\
        .config("spark.network.timeout", "600s")\
        .config("spark.executorEnv.JAVA_HOME", java_home)\
        .config("spark.yarn.appMasterEnv.JAVA_HOME", java_home)
        
    
    if use_local is True:
        spark = spark.master("local")

    spark = spark.getOrCreate()

    print('\n\n------------------ DEBUG ----------------')
    sc = spark.sparkContext
    print(sc.getConf().toDebugString())
    print('---------------- END DEBUG ----------------\n\n')

    for subEra in subEras:
        print('\n>>>>>>>>> Converting:', particle, resonance, era, subEra)
        run_convert(spark, particle, resonance, era, dataTier, subEra, customDir, baseDir, use_pog_space, use_local)

    spark.stop()
