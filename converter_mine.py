from tqdm import tqdm
from multiprocessing import Pool, RLock
import os
import sys
import uproot
import argparse
import pandas as pd
from glob import glob


def get_args():
    # get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--particle'      , default='muon'            , type=str)
    parser.add_argument('-r', '--resonance'     , default='Z'               , type=str)
    parser.add_argument('-y', '--year'          , default=2022              , type=int)
    parser.add_argument('-t', '--dataTier'      , default='MINIAOD'         , type=str)
    
    return parser.parse_args()

def job_wrapper(args):
    
    return convert(*args)

def hadd_root_files(path):
    # Remove previous tnp.root and tnp.parquet file
    os.system('rm ' + os.path.join(path, 'tnp.root'))
    os.system('rm ' + os.path.join(path, 'tnp.parquet'))
    
    # Hadd Root files to single tnp file
    os.system('hadd -f ' + os.path.join(path, 'tnp.root') + '  ' +  os.path.join(path, '*.root'))
    
    return

def convert(path):
    # Open root file as numpy arrays
    file        = os.path.join(path, 'tnp.root')
    with uproot.open(file) as rfile:
        tree    = rfile["muon/StandAloneEvents"] 
        #tree    = rfile["muon/Events"]
        
        #df_np   = tree.arrays(library='np')
        df_np   = tree.arrays(
                    [
                        "pair_mass",
                        "tag_pt", 
                        "tag_isTight",
                        "tag_charge",
                        "probe_charge",
                        "tag_pfIso04_neutral",
                        "tag_pfIso04_photon",
                        "tag_pfIso04_sumPU",
                        "tag_pfIso04_charged",
                        "probe_pt",
                        "probe_isTrkMatch",
                        "probe_isSA",
                        "probeSA_isTrkMatch",
                        "probe_eta", 
                        "probe_phi", 
                        "probe_dxy", 
                        "probe_dz", 
                        "nVertices",
                        "ls",
                        "probe_minDR",
                        "istlumi",
                        "HLT_Mu8_v", 
                        "HLT_Mu15_v", 
                        "HLT_Mu17_v", 
                        "HLT_Mu20_v", 
                        "HLT_IsoMu24_v",
                        "HLT_Mu50_v", 
                        "tag_hltL3fL1sMu5L1f0L2f5L3Filtered8", 
                        "tag_hltL3fL1sMu5L1f0L2f5L3Filtered8_dr", 
                        "tag_hltL3fL1sMu15DQIqL1f0L2f10L3Filtered15",
                        "tag_hltL3fL1sMu15DQIqL1f0L2f10L3Filtered15_dr",
                        "tag_hltL3fL1sMu15DQIL1f0L2f10L3Filtered17",
                        "tag_hltL3fL1sMu15DQIL1f0L2f10L3Filtered17_dr",
                        "tag_hltL3fL1sMu18L1f0L2f10QL3Filtered20Q",
                        "tag_hltL3fL1sMu18L1f0L2f10QL3Filtered20Q_dr",
                        "tag_hltL3fL1sSingleMu22L1f0L2f10QL3Filtered24Q",
                        "tag_hltL3fL1sSingleMu22L1f0L2f10QL3Filtered24Q_dr",
                        "tag_hltL3fL1sMu22Or25L1f10QL3Filtered50Q",
                        "tag_hltL3fL1sMu22Or25L1f10QL3Filtered50Q_dr",
                        ], # Variables for Tracking study 
                    library='np'
                )

    # change to pd (for some reason it did not work when directly importing as pd)
    df_pd       = pd.DataFrame(df_np)

    # safe as parquet
    df_pd.to_parquet(file.replace('.root', '.parquet'))

    # Remove temporary tnp.root file
    os.system('rm ' + file)
    
    return


def main():

    # get arguments
    args        = get_args()

    # Get list of all file paths in sub folde 
    file_path   = r'/eos/user/j/jbierken/TnP_ntuples/All_tracks/{part}/{res}/Run{year}/{tier}/*/*/*'.format(
                    part    = args.particle, 
                    res     = args.resonance, 
                    year    = args.year, 
                    tier    = args.dataTier
                )
    file_list   = glob(file_path)

    print(file_list)
    
    nthreads    = 16

    # multi core processing
    with Pool(nthreads) as pool:
        # Group files in single 'tnp.root' file
        results = list(tqdm(pool.imap(hadd_root_files, file_list), total=len(file_list)))
        
        # Convert root to parquet format
        results = list(tqdm(pool.imap(convert, file_list), total=len(file_list)))

        # Copy parquet files to hdfs server
        #os.system('hdfs dfs -cp hdfs://analytix/user/jbierken/parquet/')

if __name__=='__main__':
    main()
