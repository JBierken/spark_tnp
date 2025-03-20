# Import needed modules
import numpy as np
import argparse
import ROOT
import sys
import os

# Number of events in File (--> from CMS DAS)
Nevents     = {
                'Run2022': {
                    'Jpsi'          : 49003949,
                    'Run2022B'      : 5328210,
                    'Run2022C1'     : 20162441,
                    'Run2022C2'     : 138329693,
                    'Run2022D'      : 75440027
                },
                'Run2022_EE': {
                    'Jpsi'          : 49443374,
                    'Run2022E'      : 141480973,
                    'Run2022F'      : 449906805,
                    'Run2022G'      : 76689396
                },
                'Run2023': {
                    'Jpsi'          : 29880675,
                    'Run2023B_M0'   : 17453684,
                    'Run2023B_M1'   : 17438819,
                    'Run2023C1_M0'  : 54715896, 
                    'Run2023C2_M0'  : 17063451,
                    'Run2023C3_M0'  : 20015377,
                    'Run2023C4_M0'  : 138943783, 
                    'Run2023C1_M1'  : 54621922,
                    'Run2023C2_M1'  : 17059895,
                    'Run2023C3_M1'  : 20010429,
                    'Run2023C4_M1'  : 0
                },
                'Run2023_BPix': {
                    'Jpsi'          : 15060334,
                    'Run2023D_M0'   : 100211533,
                    'Run2023D_M1'   : 100281976,
                    'Run2023D2_M0'  : 21462916,
                    'Run2023D2_M1'  : 21463645
                }

            }

# Cross-section
#Xsection    = 913100.0      # 2022 
#Xsection    = 917000.0      # 2022EE 
Xsection    = {
                'Run2022':      913100.0,
                'Run2022_EE':   917000.0,
                'Run2023':      913100.0,
                'Run2023_BPix': 913100.0
            }

#Effective Luminosity
L_eff       = {
                'Run2022': {
                    'HLT_Mu8_v':    6.4,
                    'HLT_Mu15_v':   61.0,
                    'HLT_Mu17_v':   27.0,
                    'HLT_IsoMu24_v':35200.0,
                    'HLT_Mu50_v':   35200.0
                },
                'Run2022_EE': {
                    'HLT_Mu8_v':    6.4,
                    'HLT_Mu15_v':   61.0,
                    'HLT_Mu17_v':   27.0,
                    'HLT_IsoMu24_v':35200.0,
                    'HLT_Mu50_v':   35200.0
                },
                'Run2023': {
                    'HLT_Mu8_v':    5.4,
                    'HLT_Mu15_v':   42.0,
                    'HLT_Mu17_v':   78.0,
                    'HLT_IsoMu24_v':27200.0,
                    'HLT_Mu50_v':   27200.0
                },
                'Run2023_BPix': {
                    'HLT_Mu8_v':    5.4,
                    'HLT_Mu15_v':   42.0,
                    'HLT_Mu17_v':   78.0,
                    'HLT_IsoMu24_v':27200.0,
                    'HLT_Mu50_v':   27200.0
                }
            }

# Get arguments
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--era'       ,   required=True)
    parser.add_argument('-se', '--subera'   ,   default='Jpsi')

    return parser.parse_args()


def get_prescale(era, subera):
    
    # Define histogram with prescale values
    h_prescale          = ROOT.TH1D("prescale", "prescale", 500, 0.0, 500.0)
    for i, val in enumerate(np.linspace(0, 500, 500)):
        
        # Define flag based on which trigger is fired
        if (val > 50):      flag = 'HLT_Mu50_v'
        elif (val > 24):    flag = 'HLT_IsoMu24_v'
        elif (val > 17):    flag = 'HLT_Mu17_v'
        elif (val > 15):    flag = 'HLT_Mu15_v'
        else:               flag = 'HLT_Mu8_v'

        # Define prescale weight
        h_prescale.SetBinContent(i, (Xsection[era] * L_eff[era][flag]) / Nevents[era][subera])

    return h_prescale

def make_root(h, era):

    # Output filename
    baseDir              = os.path.dirname(__file__)
    outFileName         = os.path.join(baseDir, "prescale/mc/", "{era}.root".format(era=era))

    # Open and go to ROOT file
    outFile             = ROOT.TFile.Open(outFileName, "RECREATE")
    outFile.cd()

    # write histogram to file
    h.Write()

    # close root file
    outFile.Close()

if __name__=='__main__':

    # Error message for starting code (used for automatic resubmission checks)
    sys.stderr.write('###starting###\n')

    # get arguments
    args                = get_args()

    # get prescale factors
    prescales           = get_prescale(era=args.era, subera=args.subera)

    # make ROOT file with prescale weights
    make_root(h=prescales, era=args.era)
    
    # Error message for starting code (used for automatic resubmission checks)
    sys.stderr.write('###done###\n')

