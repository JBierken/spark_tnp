import ROOT
import os
import re
from pathlib import Path
import shutil
from PIL import Image

print( '''


 ,-----(``)--------.
(                   `--.
 >     Catch me        )
(      if you can     )  
 `---(            )--'
      `-----(_)--'
                      0
                         0
                            o      ___
                               ,-""   `.
                             ,'  _   e )`-._
                            /  ,' `-._<.===-'
                           /  /
                          /  ;
              _          /   ;
 (`._    _.-"" ""--..__,'    |
 <_  `-""                     \ 
  <`-  Enrico the Goose says:  :
   (__   <__. MUON POG rules   ;
     `-.   '-.__.      _.'    /
        \      `-.__,-'    _,'
         `._    ,    /__,-'
            ""._\__,'< <____
                 | |  `----.`.
                 | |        \ `.
                 ; |___      \-``
                 \   --<
                  `.`.<
                    `-'
________________________________________________________________________
  \ \    / /   / \    | |     | | |   \       / \ |__   __| |  ___|         
   \ \  / /   /   \   | |     | | | |\ \     /   \   | |    | |___          
    \ \/ /   / /^\ \  | |___  | | | |_\ \   / /^\ \  | |    | |___          
     \__/   /_/   \_\ |_____| |_| |______| /_/   \_\ |_|    |_____|         
________________________________________________________________________''')

print('== = Geese are being captured = ==')
print('=== = = in the UL_####/geese/ dir = = ===')

def validateFits(inFile, baseDir, resonance, effType, KSCut, Chi2ProbCut, nSigFCut, nPredvsDataCut):
    '''
    For UL samples, validateFits validates each root file to resolve the failed fits (a wild "goose" chase).
    Call this function via the flag '--validate' from the usual $./tnp_fitter.py fit [flags] command.
    
    The input 'inFile' is each root file in your specified UL_####/fits_data/ directory.
    '''


    ###So that we don't falsely accuse mass ranges of being out of fit ranges, compute the following binnings, relevant for nEvents...
    #Useful esp. with integral data, aka ensuring you are accounting for moving the integral window--within the ROOT platform, FindBin() finds GeV binning (aka, A and B values)  
    if resonance == 'JPsi':
        if 'massRangeUp' in inFile:
            A = 2.96
            B = 3.36
        elif 'massRangeDown' in inFile:
            A = 2.84
            B = 3.24
        else:
            A = 2.90
            B = 3.30
    else:
        if effType=='trig':
            if 'massRangeUp' in inFile:
                A = 75
                B = 135
            elif 'massRangeDown' in inFile:
                A = 65
                B = 125
            else:
                A = 70
                B = 130
        else:
            if 'massRangeUp' in inFile:
                A = 75
                B = 115
            elif 'massRangeDown' in inFile:
                A = 65
                B = 105
            else:
                A = 70
                B = 110


    fit = ROOT.TFile.Open(inFile, "READ")
    
    ###Get all the informatics in the root files, so can retrieve with ease:
    tests = fit.Get(inFile.split('/')[-1][:-5]+'_statTests') #use when have only tests (one value available before the 'for' loop)

    histoPass = fit.Get(inFile.split('/')[-1][:-5]+'_Pass')
    histoFail = fit.Get(inFile.split('/')[-1][:-5]+'_Fail')
    nEventsPass = histoPass.Integral(histoPass.FindBin(A), histoPass.FindBin(B)) 
    nEventsFail = histoFail.Integral(histoFail.FindBin(A), histoFail.FindBin(B))

    nSigFail = fit.Get(inFile.split('/')[-1][:-5]+'_resF').floatParsFinal().find("nSigF").getVal()
    nBkgFail = fit.Get(inFile.split('/')[-1][:-5]+'_resF').floatParsFinal().find("nBkgF").getVal()
    nSigPass = fit.Get(inFile.split('/')[-1][:-5]+'_resP').floatParsFinal().find("nSigP").getVal()
    nBkgPass = fit.Get(inFile.split('/')[-1][:-5]+'_resP').floatParsFinal().find("nBkgP").getVal()

    nSigFail_err = fit.Get(inFile.split('/')[-1][:-5]+'_resF').floatParsFinal().find("nSigF").getError()
    nBkgFail_err = fit.Get(inFile.split('/')[-1][:-5]+'_resF').floatParsFinal().find("nBkgF").getError()
    nSigPass_err = fit.Get(inFile.split('/')[-1][:-5]+'_resP').floatParsFinal().find("nSigP").getError()
    nBkgPass_err = fit.Get(inFile.split('/')[-1][:-5]+'_resP').floatParsFinal().find("nBkgP").getError()

    nPredEventsFail = nSigFail + nBkgFail
    nPredEventsPass = nSigPass + nBkgPass
    nPredEventsFail_err = nSigFail_err + nBkgFail_err
    nPredEventsPass_err = nSigPass_err + nBkgPass_err


    def mytitle():
        '''
        The function mytitle() is an easy naming function to make the failed fit nomenclature more succint. 
        This picks up the title for the systematic parameter used (i.e. AltSig, etc.) + NUM + DEN + pt_bin + eta_bin
        '''

        words = inFile.split('/')
        sysname = words[7]
        endpt = words[-1]
        filename = endpt.split('.')
        name = filename[0]
        title = sysname + '_' + name

        return title


    def catchgeese():
        '''
        catchgeese() finds the appropriate .png file for the selected fit failure, using pulls or new mathematical parameters,
        such as the chi2probability distribution, or KS.
        catchgeese() is used within the 'for' loop to ensure access to TTree 'tests', or inside any `VALIDATION parameters` set
        '''

        myfile = inFile.replace(".root",".png")

        ###Ensures a directory exists where 'geese' (aka failed fits) will be housed:
        if not os.path.exists(baseDir + '/geese/'): os.makedirs(baseDir + '/geese/')

        target = (baseDir + '/geese/')
        goosechase = shutil.copy(myfile, target+mytitle()+".png")
        
        return goosechase

    #Set thresholds within tnp_fitter.py --below are the defaults
    # nPredvsDataCut = 0.02
    # nSigFCut = 1.0
    # KSCut = 0.005
    # Chi2ProbCut = 0.99
    
    
    #Parameters to catch failed fits here:
    if ROOT.TMath.Abs(nPredEventsFail-nEventsFail)/nEventsFail > nPredvsDataCut or nSigFail < nSigFCut :
        catchgeese()
        if ROOT.TMath.Abs(nPredEventsFail-nEventsFail)/nEventsFail > nPredvsDataCut :
            print('Found potential fit failure > ' + str(nPredvsDataCut) + ' nPredvnData criteria: ' + mytitle())
        elif nSigFail < nSigFCut :
            print('Found potential fit failure < ' + str(nSigFCut) + ' nSigF criteria: ' + mytitle())

    for index, entry in enumerate(tests):
        if entry.ksF < KSCut or ROOT.TMath.Prob(entry.chi2F,35) < Chi2ProbCut :
            catchgeese()
            print('Found potential fit failure via KS < ' + str(KSCut) + ' or Chi2 Probability Distribution < ' + str(Chi2ProbCut) + ' criteria: ' + mytitle())
