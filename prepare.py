from __future__ import print_function
import os
import importlib.util
import sys
import math
import itertools
import json
from array import array
import ctypes
import ROOT
import tdrstyle
import CMS_lumi

from dataset_allowed_definitions import get_data_mc_sub_eras
from muon_definitions import (get_full_name, get_eff_name,
                              get_bin_name,
                              get_extended_eff_name,
                              get_variables_name)
from registry import registry
import pickle

ROOT.gROOT.SetBatch()
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
tdrstyle.setTDRStyle()

def generateClopperPearsonInterval(num,den):
    confidenceLevel = 0.68
    alpha = 1 - confidenceLevel
    
    lowerLimit = round(ROOT.Math.beta_quantile(alpha/2,num,den-num + 1),4)
    if num==den:
        upperLimit=1
    else:
        upperLimit = round(ROOT.Math.beta_quantile(1-alpha/2,num + 1,den-num),4)
    return lowerLimit,upperLimit

def computeEff(n1, n2, e1, e2, doPassPlusFail):
    tot = n1 + n2
    if doPassPlusFail:
       tot = n2
    eff = n1 / tot
    #err = 1 / (n1 + n2) * math.sqrt(
    #    e1 * e1 * n2 * n2 + e2 * e2 * n1 * n1) / (n1 + n2)
    effD, effU = generateClopperPearsonInterval(n1,tot)
    return eff, effD, effU

def getEff(binName, fname, massRanges, shift=None, cutAndCount=False, doPassPlusFail=False, resonance='Z'):
    try:
        # MC Eff is always cut and count now
        tfile = ROOT.TFile(fname, 'read')
        if cutAndCount:
            hP = tfile.Get('{}_Pass'.format(binName))
            hF = tfile.Get('{}_Fail'.format(binName))
        else:
            hP = tfile.Get('{}_GenPass'.format(binName))
            hF = tfile.Get('{}_GenFail'.format(binName))

        blow, bhigh = massRanges[resonance].get(shift, massRanges[resonance]["nominal"])

        bin1 = hP.GetXaxis().FindBin(blow)
        bin2 = hP.GetXaxis().FindBin(bhigh)
        eP = ctypes.c_double(-1.0)
        eF = ctypes.c_double(-1.0)
        nP = hP.IntegralAndError(bin1, bin2, eP)
        nF = hF.IntegralAndError(bin1, bin2, eF)
        #doPassPlusFail should NOT be used if cutAndCount=True
        eff, effD, effU = computeEff(nP, nF, eP.value, eF.value, doPassPlusFail)
        errD = abs(eff-effD)
        errU = abs(eff-effU)
        tfile.Close()
        return eff, errD, errU
    except Exception as e:
        print('Exception for getEff', binName)
        print(e)
        # raise e
        return 1., 0., 0.


def getDataEff(binName, fname, massRanges, shift=None, cutAndCount=False, doPassPlusFail=False, resonance='Z'):
    blow, bhigh = massRanges[resonance].get(shift, massRanges[resonance]["nominal"])
    try:
        tfile = ROOT.TFile(fname, 'read')
        if cutAndCount:
            hP = tfile.Get('{}_Pass'.format(binName))
            hF = tfile.Get('{}_Fail'.format(binName))

            bin1 = hP.GetXaxis().FindBin(blow)
            bin2 = hP.GetXaxis().FindBin(bhigh)
            eP = ctypes.c_double(-1.0)
            eF = ctypes.c_double(-1.0)
            nP = hP.IntegralAndError(bin1, bin2, eP)
            nF = hF.IntegralAndError(bin1, bin2, eF)
            eff, effD, effU = computeEff(nP, nF, eP.value, eF.value, False)
        else:
            fitresP = tfile.Get('{}_resP'.format(binName))
            fitresF = tfile.Get('{}_resF'.format(binName))

            fitP = fitresP.floatParsFinal().find('nSigP')
            fitF = fitresF.floatParsFinal().find('nSigF')

            nP = fitP.getVal()
            nF = fitF.getVal()
            eP = fitP.getError()
            eF = fitF.getError()

            hP = tfile.Get('{}_Pass'.format(binName))
            hF = tfile.Get('{}_Fail'.format(binName))

            bin1 = hP.GetXaxis().FindBin(blow)
            bin2 = hP.GetXaxis().FindBin(bhigh)
            ePalt = ctypes.c_double(-1.0)
            eFalt = ctypes.c_double(-1.0)
            hP.IntegralAndError(bin1, bin2, ePalt)
            hF.IntegralAndError(bin1, bin2, eFalt)

            eP = min(eP, ePalt.value)
            eF = min(eF, eFalt.value)
            eff, effD, effU = computeEff(nP, nF, eP, eF, doPassPlusFail)

        errD = abs(eff-effD)
        errU = abs(eff-effU)
        tfile.Close()
        return eff, errD, errU

    except Exception as e:
        print('Exception for getDataEff', binName)
        print(e)
        # raise e
        return 1., 0., 0.


def getSF(binName, fname, massRanges, doPassPlusFail, shift=None, resonance='Z'):
    mcEff, mcErrD, mcErrU = getEff(binName, fname, massRanges, shift, False, doPassPlusFail, resonance)
    dataEff, dataErrD, dataErrU = getDataEff(binName, fname, massRanges, shift, False, doPassPlusFail, resonance)
    sf = dataEff / mcEff if mcEff else 0.0
    sf_err = 0.0
    if dataEff and mcEff:
        dataErr = max(dataErrD, dataErrU)
        mcErr = max(mcErrD, mcErrU)
        sf_err = sf * ((dataErr / dataEff)**2 + (mcErr / mcEff)**2)**0.5
    return sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU
  


def getSF_cutAndCount(binName, fnameData, fnameMC, massRanges, shift=None, resonance='Z'):
    mcEff, mcErrD, mcErrU = getEff(binName, fnameMC, massRanges, shift, True, False, resonance)
    dataEff, dataErrD, dataErrU = getDataEff(binName, fnameData, massRanges, shift, True, False, resonance)
    sf = dataEff / mcEff if mcEff else 0.0
    sf_err = 0.0
    if dataEff and mcEff:
        dataErr = max(dataErrD, dataErrU)
        mcErr = max(mcErrD, mcErrU)
        sf_err = sf * ((dataErr / dataEff)**2 + (mcErr / mcEff)**2)**0.5
    return sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU


def getSyst(binName, fname, fitTypes, shiftTypes, massRanges, doPassPlusFail, resonance='Z'):
    sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU = getSF(binName, fname, massRanges, doPassPlusFail, resonance=resonance)

    syst = {}
    for isyst in fitTypes:
        systfname = fname.replace('Nominal', isyst)
        # sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU
        tmp = getSF(binName, systfname, massRanges, doPassPlusFail, isyst, resonance=resonance)
        syst[isyst] = {
            'sf': tmp[0],
            'err': abs(tmp[0]-sf),
            'dataEff': tmp[2],
            'dataErr': abs(tmp[2]-dataEff),
            'mcEff': tmp[5],
            'mcErr': abs(tmp[5]-mcEff),
        }

    for isyst in shiftTypes:
        systUpfname = fname.replace('Nominal', isyst+'Up')
        systDnfname = fname.replace('Nominal', isyst+'Down')
        # sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU
        tmpUp = getSF(binName, systUpfname, massRanges, doPassPlusFail, isyst+'Up', resonance=resonance)
        tmpDn = getSF(binName, systDnfname, massRanges, doPassPlusFail, isyst+'Down', resonance=resonance)
        tmp = [
            (tmpUp[0]+tmpDn[0])/2,
            (abs(tmpUp[0]-sf)+abs(tmpDn[0]-sf))/2,
            (tmpUp[2]+tmpDn[2])/2,
            (abs(tmpUp[2]-dataEff)+abs(tmpDn[2]-dataEff))/2,
            (tmpUp[5]+tmpDn[5])/2,
            (abs(tmpUp[5]-mcEff)+abs(tmpDn[5]-mcEff))/2,
        ]
        syst[isyst] = {
            'sf': tmp[0],
            'err': tmp[1],
            'dataEff': tmp[2],
            'dataErr': tmp[3],
            'mcEff': tmp[4],
            'mcErr': tmp[5],
        }
        syst[isyst+'Up'] = {
            'sf': tmpUp[0],
            'err': abs(tmpUp[0]-sf),
            'dataEff': tmpUp[2],
            'dataErr': abs(tmpUp[2]-dataEff),
            'mcEff': tmpUp[5],
            'mcErr': abs(tmpUp[5]-mcEff),
        }
        syst[isyst+'Down'] = {
            'sf': tmpDn[0],
            'err': abs(tmpDn[0]-sf),
            'dataEff': tmpDn[2],
            'dataErr': abs(tmpDn[2]-dataEff),
            'mcEff': tmpDn[5],
            'mcErr': abs(tmpDn[5]-mcEff),
        }

    return syst


def getSyst_cutAndCount(binName, fnameData, fnameMC, fitTypes, shiftTypes, massRanges, resonance='Z'):
    sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU = getSF_cutAndCount(
        binName, fnameData, fnameMC, massRanges, resonance=resonance)

    syst = {}
    for isyst in fitTypes:
        systfnameData = fnameData.replace('Nominal', isyst)
        systfnameMC = fnameMC.replace('Nominal', isyst)
        # sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU
        tmp = getSF_cutAndCount(binName, systfnameData, systfnameMC, massRanges, isyst, resonance=resonance)
        syst[isyst] = {
            'sf': tmp[0],
            'err': abs(tmp[0]-sf),
            'dataEff': tmp[2],
            'dataErr': abs(tmp[2]-dataEff),
            'mcEff': tmp[5],
            'mcErr': abs(tmp[5]-mcEff),
        }

    for isyst in shiftTypes:
        systUpfnameData = fnameData.replace('Nominal', isyst+'Up')
        systDnfnameData = fnameData.replace('Nominal', isyst+'Down')
        systUpfnameMC = fnameMC.replace('Nominal', isyst+'Up')
        systDnfnameMC = fnameMC.replace('Nominal', isyst+'Down')
        # sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU
        tmpUp = getSF_cutAndCount(binName, systUpfnameData,
                                  systUpfnameMC, massRanges, isyst+'Up'  , resonance=resonance)
        tmpDn = getSF_cutAndCount(binName, systDnfnameData,
                                  systDnfnameMC, massRanges, isyst+'Down', resonance=resonance)
        tmp = [
            (tmpUp[0]+tmpDn[0])/2,
            (abs(tmpUp[0]-sf)+abs(tmpDn[0]-sf))/2,
            (tmpUp[2]+tmpDn[2])/2,
            (abs(tmpUp[2]-dataEff)+abs(tmpDn[2]-dataEff))/2,
            (tmpUp[5]+tmpDn[5])/2,
            (abs(tmpUp[5]-mcEff)+abs(tmpDn[5]-mcEff))/2,
        ]
        syst[isyst] = {
            'sf': tmp[0],
            'err': tmp[1],
            'dataEff': tmp[2],
            'dataErr': tmp[3],
            'mcEff': tmp[4],
            'mcErr': tmp[5],
        }
        syst[isyst+'Up'] = {
            'sf': tmpUp[0],
            'err': abs(tmpUp[0]-sf),
            'dataEff': tmpUp[2],
            'dataErr': abs(tmpUp[2]-dataEff),
            'mcEff': tmpUp[5],
            'mcErr': abs(tmpUp[5]-mcEff),
        }
        syst[isyst+'Down'] = {
            'sf': tmpDn[0],
            'err': abs(tmpDn[0]-sf),
            'dataEff': tmpDn[2],
            'dataErr': abs(tmpDn[2]-dataEff),
            'mcEff': tmpDn[5],
            'mcErr': abs(tmpDn[5]-mcEff),
        }

    return syst


def get_Res(binName, systfname, resonance='Z'):
     dataFName= systfname
     tfile=ROOT.TFile(dataFName,'read')
     fitres=tfile.Get('{}_fitResult'.format(binName))
     fitsig=fitres.floatParsFinal().find('sigma').getVal()
     fitsige=fitres.floatParsFinal().find('sigma').getError()
     fitresgen=tfile.Get('{}_fitResultgen'.format(binName))
     fitsiggen=fitresgen.floatParsFinal().find('sigma').getVal()
     fitsigegen=fitresgen.floatParsFinal().find('sigma').getError()
     tfile.Close()
     return fitsig, fitsige, fitsiggen, fitsigegen


def getResSyst(binName, fname, fitTypes, shiftTypes, resonance='Z'):
    data_res,data_err,mc_res,mc_err = get_Res(binName, fname, resonance=resonance)
     
    syst = {}
    for isyst in fitTypes:
        systfname = fname.replace('res3', isyst)
        tmp = get_Res(binName, systfname, resonance=resonance)
        syst[isyst] = {
            'data_res': tmp[0],
            'data_err': abs(tmp[0]-data_res),
            'mc_res': tmp[2],
            'mc_err': abs(tmp[2]-mc_res),
        }

    for isyst in shiftTypes:
        systUpfname = fname.replace('res3', isyst+'Up')
        systDnfname = fname.replace('res3', isyst+'Down')
        tmpUp = get_Res(binName, systUpfname, resonance=resonance)
        tmpDn = get_Res(binName, systDnfname, resonance=resonance)
        tmp = [
            (tmpUp[0]+tmpDn[0])/2,
            (abs(tmpUp[0]-data_res)+abs(tmpDn[0]-data_res))/2,
            (tmpUp[2]+tmpDn[2])/2,
            (abs(tmpUp[2]-mc_res)+abs(tmpDn[2]-mc_res))/2,
        ]
        syst[isyst] = {
            'data_res': tmp[0],
            'data_err': tmp[1],
            'mc_res': tmp[2],
            'mc_err': tmp[3],
        }
        syst[isyst+'Up'] = {
            'data_res': tmpUp[0],
            'data_err': abs(tmpUp[0]-data_res),
            'mc_res': tmpUp[2],
            'mc_err': abs(tmpUp[2]-mc_res),
        }
        syst[isyst+'Down'] = {
            'data_res': tmpDn[0],
            'data_err': abs(tmpDn[0]-data_res),
            'mc_res': tmpDn[2],
            'mc_err': abs(tmpDn[2]-mc_res),
        }

    return syst


def prepare(baseDir, particle, probe, resonance, era,
            config, num, denom, variableLabels, lumi,
            skipPlots=False, cutAndCount=False, doPassPlusFail=False):
    if denom!="ref":
        hists = {}
    
        effType = config.type() if 'type' in config else ''
        effName = get_eff_name(num, denom)
        extEffName = get_extended_eff_name(num, denom, variableLabels)
        binning = config.binning()
        dataSubEra, mcSubEra, mcSubEraAlt = get_data_mc_sub_eras(resonance, era)
    
        systList = config.get('systematics',
            	          {x: {'fitTypes': [],
            		       'shiftTypes': []}
                                for x in ['SF', 'dataEff', 'mcEff']})
    
        massRanges = config.massRanges() # Start from a sensible default, but allow customization
    
        def get_variable_name_pretty(variableLabel):
            variables = config.variables()
            return variables.get(variableLabel, {}).get('pretty', variableLabel)
    
        # create output histograms
        nVars = len(variableLabels)
        if nVars == 1:
            THX = ROOT.TH1F
        elif nVars == 2:
            THX = ROOT.TH2F
        elif nVars == 3:
            THX = ROOT.TH3F
        else:
            raise NotImplementedError(
                'More than 3 dimensions are not supported for scale factors'
            )
    
        hargs = [extEffName, extEffName]
        for variableLabel in variableLabels:
            hargs += [len(binning[variableLabel]) - 1,
            	  array('d', binning[variableLabel])]
        hist = THX(*hargs)
        axes = [hist.GetXaxis(), hist.GetYaxis(), hist.GetZaxis()]
        for vi, variableLabel in enumerate(variableLabels):
            axes[vi].SetTitle(get_variable_name_pretty(variableLabel))
        if nVars == 1:
            hist.GetYaxis().SetTitle('Scalefactor')
        if nVars == 2:
            hist.SetOption('colz')
            hist.GetZaxis().SetTitle('Scalefactor')
        hist_stat = hist.Clone(extEffName+'_stat')
        hist_syst = hist.Clone(extEffName+'_syst')
        histList_syst = {
            'combined_syst': hist.Clone(extEffName+'_combined_syst'),
        }
        if nVars == 2:
            histList_syst['combined_syst'].GetZaxis().SetTitle('Uncertainty')
    
        hist_dataEff = hist.Clone(extEffName+'_efficiencyData')
        if nVars == 1:
            hist_dataEff.GetYaxis().SetTitle('Efficiency')
        if nVars == 2:
            hist_dataEff.GetZaxis().SetTitle('Efficiency')
        hist_dataEff_errD = hist_dataEff.Clone(extEffName+'_efficiencyData_errD')
        hist_dataEff_errU = hist_dataEff.Clone(extEffName+'_efficiencyData_errU')
        hist_dataEff_stat = hist_dataEff.Clone(extEffName+'_efficiencyData_stat')
        hist_dataEff_syst = hist_dataEff.Clone(extEffName+'_efficiencyData_syst')
        histList_dataEff_syst = {
            'combined_syst': hist_dataEff.Clone(
                extEffName+'_efficiencyData_combined_syst'),
        }
        if nVars == 2:
            histList_dataEff_syst['combined_syst'].GetZaxis().SetTitle('Uncertainty')
        hist_mcEff = hist_dataEff.Clone(extEffName+'_efficiencyMC')
        hist_mcEff_errD = hist_dataEff.Clone(extEffName+'_efficiencyMC_errD')
        hist_mcEff_errU = hist_dataEff.Clone(extEffName+'_efficiencyMC_errU')
        hist_mcEff_stat = hist_dataEff.Clone(extEffName+'_efficiencyMC_stat')
        hist_mcEff_syst = hist_dataEff.Clone(extEffName+'_efficiencyMC_syst')
        histList_mcEff_syst = {
            'combined_syst': hist_dataEff.Clone(
                extEffName+'_efficiencyMC_combined_syst'),
        }
        if nVars == 2:
            histList_mcEff_syst['combined_syst'].GetZaxis().SetTitle('Uncertainty')
    
        # the individual systematics
        for iSyst in itertools.chain(systList['SF']['fitTypes'],
            			 systList['SF']['shiftTypes']):
            histList_syst[iSyst] = hist.Clone(extEffName+'_'+iSyst)
            histList_syst[iSyst+'_syst'] = hist.Clone(extEffName+'_'+iSyst+'_syst')
            if nVars == 2:
                histList_syst[iSyst+'_syst'].GetZaxis().SetTitle('Uncertainty')
        for iSyst in itertools.chain(systList['dataEff']['fitTypes'],
            			 systList['dataEff']['shiftTypes']):
            histList_dataEff_syst[iSyst] = hist_dataEff.Clone(extEffName+'_'+iSyst)
            histList_dataEff_syst[iSyst+'_syst'] = hist_dataEff.Clone(
                extEffName+'_'+iSyst+'_syst')
            if nVars == 2:
                histList_dataEff_syst[iSyst+'_syst'].GetZaxis().SetTitle('Uncertainty')
        for iSyst in itertools.chain(systList['mcEff']['fitTypes'],
            			 systList['mcEff']['shiftTypes']):
            histList_mcEff_syst[iSyst] = hist_mcEff.Clone(extEffName+'_'+iSyst)
            histList_mcEff_syst[iSyst+'_syst'] = hist_mcEff.Clone(
                extEffName+'_'+iSyst+'_syst')
            if nVars == 2:
                histList_mcEff_syst[iSyst+'_syst'].GetZaxis().SetTitle('Uncertainty')
    
        varName = get_variables_name(variableLabels)
    
        # iterate through the bin indices
        # this does nested for loops of the N-D binning (e.g. pt, eta)
        # binning starts at 1 (0 is underflow), same as ROOT
        indices = [list(range(1, len(binning[variableLabel])))
                   for variableLabel in variableLabels]
        output = {effName: {varName: {}}}
        all_systematics = {}
        for index in itertools.product(*indices):
            binName = get_full_name(num, denom, variableLabels, index)
            subVarKeys = [
                '{}:[{},{}]'.format(
            	variableLabels[i],
            	binning[variableLabels[i]][ind-1],
            	binning[variableLabels[i]][ind]
                ) for i, ind in enumerate(index)
            ]
            _out = output[effName][varName]
    
            # add binning definitions
            _out['binning'] = [
                {
            	'variable': vl,
            	'binning': binning[vl].tolist(),
                }
                for vl in variableLabels
            ]
    
            for subVarKey in subVarKeys:
                if subVarKey not in _out:
                    _out[subVarKey] = {}
                _out = _out[subVarKey]
    
            # the fitted distributions
            fitType = 'Nominal'
            dataFNameFit = os.path.join(baseDir, 'fits_data',
                                    particle, probe,
                                    resonance, era,
                                    fitType, effName,
                                    binName + '.root')
            dataFNameCNC = os.path.join(baseDir, 'flat',
                                    particle, probe,
                                    resonance, era,
                                    dataSubEra, 'Nominal',
                                    extEffName + '.root')
            mcFNameCNC = os.path.join(baseDir, 'flat',
                                  particle, probe,
                                  resonance, era,
                                  mcSubEra, 'Nominal',
                                  extEffName + '.root')
            # sf, sf_err, dataEff, dataErrD, dataErrU, mcEff, mcErrD, mcErrU
            if cutAndCount:
                sf, sf_stat, dataEff, dataStatD, dataStatU, mcEff, mcStatD, mcStatU = getSF_cutAndCount(
                binName, dataFNameCNC, mcFNameCNC, massRanges, resonance=resonance)
            else:
                sf, sf_stat, dataEff, dataStatD, dataStatU, mcEff, mcStatD, mcStatU = getSF(
                binName, dataFNameFit, massRanges, doPassPlusFail, resonance=resonance)
            #As statistical error, we take the maximum between up and down asym. errors
            dataStat = max(dataStatD, dataStatU)
            mcStat = max(mcStatD, mcStatU)
            fitTypes = set(systList['SF']['fitTypes']
                       + systList['dataEff']['fitTypes']
                       + systList['mcEff']['fitTypes'])
            shiftTypes = set(systList['SF']['shiftTypes']
                         + systList['dataEff']['shiftTypes']
                         + systList['mcEff']['shiftTypes'])
            if cutAndCount:
                sf_syst = getSyst_cutAndCount(binName, dataFNameCNC, mcFNameCNC,
            	                              fitTypes, shiftTypes, massRanges, resonance=resonance)
            else:
                sf_syst = getSyst(binName, dataFNameFit,
            	            fitTypes, shiftTypes, massRanges, doPassPlusFail, resonance=resonance)
    
            combined_syst = {}
            for kind in ['SF', 'dataEff', 'mcEff']:
                combined_syst[kind] = 0
                errKey = 'err'
                if kind == 'dataEff':
                    errKey = 'dataErr'
                if kind == 'mcEff':
                    errKey = 'mcErr'
                for t in itertools.chain(systList[kind]['fitTypes'],
                                         systList[kind]['shiftTypes']):
                    if sf_syst[t][errKey]>sf_stat:
                        combined_syst[kind] += sf_syst[t][errKey]**2
                combined_syst[kind] = combined_syst[kind]**0.5
            sf_err = (sf_stat**2 + combined_syst['SF']**2)**0.5
            dataErr = (dataStat**2 + combined_syst['dataEff']**2)**0.5
            dataErrD = (dataStatD**2 + combined_syst['dataEff']**2)**0.5
            dataErrU = (dataStatU**2 + combined_syst['dataEff']**2)**0.5
            mcErr = (mcStat**2 + combined_syst['mcEff']**2)**0.5
            mcErrD = (mcStatD**2 + combined_syst['mcEff']**2)**0.5
            mcErrU = (mcStatU**2 + combined_syst['mcEff']**2)**0.5
            _out['value'] = sf
            _out['stat'] = sf_stat
            _out['syst'] = combined_syst['SF']
            for s in itertools.chain(systList['SF']['fitTypes'],
                                       systList['SF']['shiftTypes']):
                _out[s] = sf_syst[s]['err']
    
            # copy systs for later schema
            all_systematics[index] = _out.copy()
    
            def set_bin(hist, index, val, err):
                index = list(index)
                val_args = index + [val]
                err_args = index + [err]
                hist.SetBinContent(*val_args)
                if err >= 0:
                    hist.SetBinError(*err_args)
    
            set_bin(hist, index, sf, sf_err)
            set_bin(hist_stat, index, sf, sf_stat)
            set_bin(hist_syst, index, sf, combined_syst['SF'])
            set_bin(histList_syst['combined_syst'], index,
                 combined_syst['SF'], -1)
            set_bin(hist_dataEff, index, dataEff, dataErr)
            set_bin(hist_dataEff_errD, index, dataEff, dataErrD)
            set_bin(hist_dataEff_errU, index, dataEff, dataErrU)
            set_bin(hist_dataEff_stat, index, dataEff, dataStat)
            set_bin(hist_dataEff_syst, index, dataEff, combined_syst['dataEff'])
            set_bin(histList_dataEff_syst['combined_syst'], index,
                 combined_syst['dataEff'], -1)
            set_bin(hist_mcEff, index, mcEff, mcErr)
            set_bin(hist_mcEff_errD, index, mcEff, mcErrD)
            set_bin(hist_mcEff_errU, index, mcEff, mcErrU)
            set_bin(hist_mcEff_stat, index, mcEff, mcStat)
            set_bin(hist_mcEff_syst, index, mcEff, combined_syst['mcEff'])
            set_bin(histList_mcEff_syst['combined_syst'], index,
                 combined_syst['mcEff'], -1)
            for iKey in sf_syst.keys():
                if iKey in histList_syst:
                    set_bin(histList_syst[iKey], index,
            	            sf_syst[iKey]['sf'], sf_syst[iKey]['err'])
                    set_bin(histList_syst[iKey+'_syst'], index,
            	            sf_syst[iKey]['err'], -1)
    
                if iKey in histList_dataEff_syst:
                    set_bin(histList_dataEff_syst[iKey], index,
            	        sf_syst[iKey]['dataEff'], sf_syst[iKey]['dataErr'])
                    set_bin(histList_dataEff_syst[iKey+'_syst'], index,
            	        sf_syst[iKey]['dataErr'], -1)
    
                if iKey in histList_mcEff_syst:
                    set_bin(histList_mcEff_syst[iKey], index,
            	        sf_syst[iKey]['mcEff'], sf_syst[iKey]['mcErr'])
                    set_bin(histList_mcEff_syst[iKey+'_syst'], index,
            	        sf_syst[iKey]['mcErr'], -1)
    
        hists[extEffName] = hist
        hists[extEffName+'_stat'] = hist_stat
        hists[extEffName+'_syst'] = hist_syst
        hists[extEffName+'_efficiencyData'] = hist_dataEff
        hists[extEffName+'_efficiencyData_errD'] = hist_dataEff_errD
        hists[extEffName+'_efficiencyData_errU'] = hist_dataEff_errU
        hists[extEffName+'_efficiencyData_stat'] = hist_dataEff_stat
        hists[extEffName+'_efficiencyData_syst'] = hist_dataEff_syst
        hists[extEffName+'_efficiencyMC'] = hist_mcEff
        hists[extEffName+'_efficiencyMC_errD'] = hist_mcEff_errD
        hists[extEffName+'_efficiencyMC_errU'] = hist_mcEff_errU
        hists[extEffName+'_efficiencyMC_stat'] = hist_mcEff_stat
        hists[extEffName+'_efficiencyMC_syst'] = hist_mcEff_syst
        for iKey in histList_syst.keys():
            hname = extEffName+'_'+iKey
            hists[hname] = histList_syst[iKey]
        for iKey in histList_dataEff_syst.keys():
            hname = extEffName+'_efficiencyData_'+iKey
            hists[hname] = histList_dataEff_syst[iKey]
        for iKey in histList_mcEff_syst.keys():
            hname = extEffName+'_efficiencyMC_'+iKey
            hists[hname] = histList_mcEff_syst[iKey]
    
        # save the efficiency
        plotDir = os.path.join(baseDir, 'plots',
                           particle, probe,
                           resonance, era,
                           effName, 'efficiency')
        os.makedirs(plotDir, exist_ok=True)
    
        effDir = os.path.join(baseDir, 'efficiencies',
                          particle, probe,
                          resonance, era,
                          effName)
        os.makedirs(effDir, exist_ok=True)
        effPath = os.path.join(effDir, extEffName)
    
        # JSON format
        with open('{}.json'.format(effPath), 'w') as f:
            f.write(json.dumps(output, indent=4, sort_keys=True))
    
        # Now build the new xPOG schema v1 if correctionlib and pydantic installed
    
        schemav1 = None
        libname = 'correctionlib.schemav1'
        if libname in sys.modules:
            schemav1 = sys.modules[libname]
        elif importlib.util.find_spec('correctionlib.schemav1') is not None:
            spec = importlib.util.find_spec('correctionlib.schemav1')
            schemav1 = importlib.util.module_from_spec(spec)
            sys.modules[libname] = schemav1
            spec.loader.exec_module(schemav1)
    
        if schemav1 is not None:
    
            def build_schema(dim, index):
                # If we reach recursion bottom, build and return the systematics node
                if dim == len(variableLabels) + 1:
                    keys, content = [], []
                    for syst, value in all_systematics[index].items():
            	        keys.append(syst)
            	        content.append(value) 
                    return schemav1.Category.parse_obj({
            	        "nodetype": "category",
            	        "keys": keys,
            	        "content": content
                    })
                # If not, build a binning node
                edges = list(map(float, binning[variableLabels[dim-1]]))
                content = [build_schema(dim+1, tuple(list(index)[0:dim-1]+[i]+list(index)[dim:])) for i in indices[dim-1]]
                return schemav1.Binning.parse_obj({
                    "nodetype": "binning",
                    "edges": edges,
                    "content": content
                     })
    
            inputs = [{"name": vl, "type": "real"} for vl in variableLabels]
            inputs += [{"name": "uncertainties", "type": "string"}]
    
            corr = schemav1.Correction.parse_obj({
                "version": 1,
                "name": effName,
                "description": effName,
                "inputs": inputs,
                "output": {"name": "weight", "type": "real"},
                "data": build_schema(1, tuple([1]*len(variableLabels)))
            })
            cset = schemav1.CorrectionSet.parse_obj({
                "schema_version": 1,
                "corrections": [corr]
            })
    
            # Write out schema json
            with open('{}_schemaV1.json'.format(effPath), "w") as fout:
                fout.write(cset.json(exclude_unset=True, indent=4))
    
        else:
            print("Warning: correctionlib not installed. Not producing schema jsons.")
    
        # ROOT histogram format
        tfile = ROOT.TFile.Open('{}.root'.format(effPath), 'recreate')
        for h in sorted(hists):
            hists[h].Write(h)
    
            if skipPlots:
                continue
    
            def setLog(canvas, hist, thr = 110.):
                if hist.GetXaxis().GetBinLowEdge(hist.GetXaxis().GetNbins()) > thr:
                    hist.GetXaxis().SetMoreLogLabels()
                    canvas.SetLogx()
                if hist.GetYaxis().GetBinLowEdge(hist.GetYaxis().GetNbins()) > thr:
                    hist.GetYaxis().SetMoreLogLabels()
                    canvas.SetLogy()
                if hist.GetZaxis().GetBinLowEdge(hist.GetZaxis().GetNbins()) > thr:
                    canvas.SetLogz()
    
            if nVars == 2:
                cName = 'c' + h
                canvas = ROOT.TCanvas(cName, cName, 1000, 800)
                ROOT.gStyle.SetPaintTextFormat("5.3f")
                canvas.SetRightMargin(0.24)
                hists[h].Draw('colz text')
                plotPath = os.path.join(plotDir, h)
                canvas.Modified()
                canvas.Update()
                
                CMS_lumi.cmsText = 'CMS'
                CMS_lumi.writeExtraText = True
                CMS_lumi.extraText = 'Preliminary'
                CMS_lumi.lumi = "%0.1f fb^{-1}" % (lumi)
                CMS_lumi.CMS_lumi(canvas, era, 0)
    
                if effType == 'trig':
                    setLog(canvas, hists[h])
    
                canvas.Print('{}.png'.format(plotPath))
                canvas.Print('{}.pdf'.format(plotPath))
                canvas.Print('{}.root'.format(plotPath))
    
            elif nVars == 3:
                axes = [hists[h].GetXaxis(),
                    hists[h].GetYaxis(),
                    hists[h].GetZaxis()]
                axislabels = ['x', 'y', 'z']
    
                def zAxisTitle(effName):
                    for iSyst in itertools.chain(systList['SF']['fitTypes'],
                                             systList['SF']['shiftTypes'],
                                             systList['dataEff']['fitTypes'],
                                             systList['dataEff']['shiftTypes'],
                                             systList['mcEff']['fitTypes'],
                                             systList['mcEff']['shiftTypes']):
                        if effName.endswith(iSyst+'_syst'):
                            return 'Uncertainty'
                                                                                
                    if effName.endswith('combined_syst'):
                        return 'Uncertainty'      
                    elif 'efficiency' in effName:
                        return 'Efficiency'
                    else:
                        return 'Scalefactor'
    
                for vi, variableLabel in enumerate(variableLabels):
                    if len(binning[variableLabel]) > 3:
                        continue
            	
                    projOpt = 'zyxe'.replace(axislabels[vi], '')
                    for ibin in range(1, len(binning[variableLabel])):
                        axes[vi].SetRange(ibin, ibin)
                        projEffName = h.replace(variableLabel, variableLabel+'_{}'.format(ibin))
                        hist_proj = hists[h].Project3D(projOpt).Clone(projEffName)
    
                        hist_proj.GetZaxis().SetTitle(zAxisTitle(projEffName))
    
                        cName = 'c' + projEffName
                        canvas = ROOT.TCanvas(cName, cName, 1000, 800)
                        ROOT.gStyle.SetPaintTextFormat("5.3f")
                        canvas.SetRightMargin(0.24)
                        hist_proj.Draw('colz text')
                        plotPath = os.path.join(plotDir, projEffName)
                        canvas.Modified()
                        canvas.Update()
    
                        CMS_lumi.cmsText = 'CMS'
                        CMS_lumi.writeExtraText = True
                        CMS_lumi.extraText = 'Preliminary'
                        CMS_lumi.lumi = "%0.1f fb^{-1}" % (lumi)
                        CMS_lumi.CMS_lumi(canvas, era, 0)
     
                        if effType == 'trig':
                            setLog(canvas, hist_proj)
    
                        canvas.Print('{}.png'.format(plotPath))
                        canvas.Print('{}.pdf'.format(plotPath))
                        canvas.Print('{}.root'.format(plotPath))
    
        tfile.Close()
    
        if skipPlots:
            return
    
        # gets a graph projection of an ND histogram for a given axis
        # with axis index (ie x,y,z = 0,1,2) and other dimensions ind
        # takes as input two histograms to account for asymmetric errors
        def get_graph(histD, histU, axis, axis_ind, *ind):
            ind = list(ind)
            ni = axis.GetNbins()
            xvals = [axis.GetBinCenter(i+1) for i in range(ni)]
            xvals_errLow = [xvals[i]-axis.GetBinLowEdge(i+1) for i in range(ni)]
            xvals_errHigh = [axis.GetBinUpEdge(i+1)-xvals[i] for i in range(ni)]
            yvals = [
                histD.GetBinContent(
                *ind[:axis_ind]
                + [i+1]
                + ind[axis_ind:]
                ) for i in range(ni)]
            yvals_errLow = [
                histD.GetBinError(
                *ind[:axis_ind]
                + [i+1]
                + ind[axis_ind:]
                ) for i in range(ni)]
            yvals_errHigh = [
                histU.GetBinError(
                *ind[:axis_ind]
                + [i+1]
                + ind[axis_ind:]
                ) for i in range(ni)]
            graph = ROOT.TGraphAsymmErrors(
                ni,
                array('d', xvals),
                array('d', yvals),
                array('d', xvals_errLow),
                array('d', xvals_errHigh),
                array('d', yvals_errLow),
                array('d', yvals_errHigh),
            )
            return graph
    
        # plot the efficiencies
        # some default colors for plots
        colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2,
                  ROOT.kMagenta+1, ROOT.kOrange+1, ROOT.kTeal-1,
                  ROOT.kRed-3, ROOT.kCyan+2]
    
        def plot_1d_eff(savename, graphs,
            	    labels=['Data', 'Simulation'],
            	    colors=colors,
            	    xlabel='', ylabel='Efficiency',
            	    xRange=[], additional_text=[],
                    ratio=False):
            ng = len(graphs)
            mg = ROOT.TMultiGraph()
            for gi in range(ng):
                graphs[gi].SetLineColor(colors[gi])
                graphs[gi].SetMarkerColor(colors[gi])
                mg.Add(graphs[gi])
            
            canvas = ROOT.TCanvas(savename, savename, 900, 800)
            
            if ratio:
                canvas.Divide(1,2)
                canvas.cd(1)
                plotpad = canvas.GetPad(1)
                plotpad.SetPad(0, 0.2, 1., .98)
                mg.GetXaxis().SetLabelSize(0.)
                mg.GetXaxis().SetTitleSize(0.)

            mg.Draw('AP0')
            mg.GetXaxis().SetTitle(xlabel)
            if xRange:
                mg.GetXaxis().SetLimits(*xRange)
                mg.GetXaxis().SetRangeUser(*xRange)
            mg.GetYaxis().SetTitle(ylabel)
            if effType == 'trig':
                mg.GetYaxis().SetRangeUser(0.6, 1.20)
            else:
                mg.GetYaxis().SetRangeUser(0.8, 1.10)
            legend = ROOT.TLegend(0.5, 0.70, 0.92, 0.92)
            legend.SetTextFont(42)
            legend.SetBorderSize(0)
            legend.SetFillColor(0)
            for gi in range(ng):
                legend.AddEntry(graphs[gi], labels[gi], 'l')
            legend.SetHeader('{} / {}'.format(num, denom))
            legend.Draw()
    
            if additional_text:
                nother = len(additional_text)
                dims = [0.18, 0.84-nother*0.04-0.02, 0.35, 0.84]
                text = ROOT.TPaveText(*dims+['NB NDC'])
                text.SetTextFont(42)
                text.SetBorderSize(0)
                text.SetFillColor(0)
                text.SetTextAlign(11)
                text.SetTextSize(0.03)
                for rtext in additional_text:
                    text.AddText(rtext)
                text.Draw()
    
            CMS_lumi.cmsText = 'CMS'
            CMS_lumi.writeExtraText = True
            CMS_lumi.extraText = 'Preliminary'
            CMS_lumi.lumi = "%0.1f fb^{-1}" % (lumi)
            CMS_lumi.CMS_lumi(canvas, era, 11)
   
            # ratio
            if ratio:
                canvas.cd(2)
                ratioPad = canvas.GetPad(2)
                ratioPad.SetPad(0.,0.,1.,0.31)

                ratioPad.SetFillStyle(4000)
                ratioPad.SetBottomMargin(0.35)

                x, xerr, y, yerr = [], [], [], []
                for j in range(graphs[0].GetN()):
                    x.append(graphs[0].GetPointX(j))
                    xerr.append(graphs[0].GetErrorX(j))

                    if graphs[1].GetPointY(j)==0:
                        y.append(0)
                        yerr.append(0)
                    else:
                        y.append(graphs[0].GetPointY(j) / graphs[1].GetPointY(j))
                        yerr.append(
                            (
                                graphs[0].GetErrorY(j)**2 / graphs[1].GetPointY(j)**2 
                                + graphs[1].GetErrorY(j)**2 
                                * graphs[0].GetPointY(j)**2 / graphs[1].GetPointY(j)**4
                            )**0.5
                        )

                graph = ROOT.TGraphErrors(
                    len(x),
                    array('f', x),
                    array('f', y),
                    array('f', xerr),
                    array('f', yerr)
                )

                graph.SetLineColor(colors[0])
                graph.SetMarkerColor(colors[0])
                graph.SetTitle(" ")
                graph.Draw("AP0")

                if xRange:
                    graph.GetXaxis().SetLimits(*xRange)
                    graph.GetXaxis().SetRangeUser(*xRange)

                graph.GetXaxis().SetTickSize(0.07)
                graph.GetXaxis().SetLabelSize(0.12)
                graph.GetXaxis().SetTitle(xlabel)
                graph.GetXaxis().SetTitleSize(0.16)
                graph.GetXaxis().SetTitleOffset(.8)
                
                graph.GetYaxis().SetTickSize(0.03)
                graph.GetYaxis().SetLabelSize(0.12)
                graph.GetYaxis().SetTitleSize(0.14)
                graph.GetYaxis().SetTitleOffset(0.5)
                graph.GetYaxis().SetTitle("Data/MC")
                
                # set ratio range to fixed value unless ratio not visible
                Ymax = 1.05
                Ymin = 0.95
                dY_tmp = max(
                    graph.GetYaxis().GetXmax()-Ymax,
                    Ymin - graph.GetYaxis().GetXmin(),
                    0
                )
                dY = math.ceil(dY_tmp * 100) / 100.0
                graph.GetYaxis().SetRangeUser(Ymin - dY, Ymax + dY)
                graph.GetYaxis().SetNdivisions(502)

                Xmax = graph.GetXaxis().GetXmax()
                Xmin = graph.GetXaxis().GetXmin()

                l = ROOT.TLine(Xmin, 1, Xmax, 1)
                l.SetLineColor(1) 
                l.Draw("same") 
                        
            canvas.Modified()
            canvas.Update()
            canvas.Print('{}.png'.format(savename))
            canvas.Print('{}.pdf'.format(savename))
            canvas.Print('{}.root'.format(savename))
    
            # save each graph
            tfile = ROOT.TFile('{}.root'.format(savename), 'update')
            for gi in range(ng):
                graphs[gi].SetTitle(labels[gi])
                graphs[gi].Write('g_{}_{}'.format(gi, labels[gi]))
            tfile.Close()
        
        
        # enumerate over the axis/variable to plot
        axes = [hists[extEffName].GetXaxis(),
                hists[extEffName].GetYaxis(),
                hists[extEffName].GetZaxis()]
        for vi, variableLabel in enumerate(variableLabels):
    
            # iterate over the other axis indices
            otherVariableLabels = [ovl for ovl in variableLabels
            		       if ovl != variableLabel]
            otherVariableIndices = [ovi for ovi, ovl in enumerate(variableLabels)
            			if ovl != variableLabel]
            indices = [list(range(1, len(binning[vl])))
            	   for vl in otherVariableLabels]
            if indices:
                for index in itertools.product(*indices):
                    graph_data = get_graph(hists[extEffName+'_efficiencyData_errD'],
            	                       hists[extEffName+'_efficiencyData_errU'],
                                       axes[vi], vi, *index)
                    graph_mc = get_graph(hists[extEffName+'_efficiencyMC_errD'],
            	                     hists[extEffName+'_efficiencyMC_errU'],
                                     axes[vi], vi, *index)
                    xlabel = get_variable_name_pretty(variableLabel)
                    ylabel = 'Efficiency'
                    xRange = [axes[vi].GetBinLowEdge(1),
            	          axes[vi].GetBinUpEdge(axes[vi].GetNbins())]
                    additional_text = []
                    for novi, (ovi, ovl) in enumerate(zip(otherVariableIndices,
                                                    otherVariableLabels)):
                        xlow = axes[ovi].GetBinLowEdge(index[novi])
                        xhigh = axes[ovi].GetBinUpEdge(index[novi])
                        rtext = '{} < {} < {}'.format(
                            xlow, get_variable_name_pretty(ovl), xhigh)
                        additional_text += [rtext]
                    plotDir = os.path.join(baseDir, 'plots',
                                        particle, probe,
                                        resonance, era,
                                        effName, 'efficiency')
                    os.makedirs(plotDir, exist_ok=True)
                    otherVariableLabel = get_bin_name(otherVariableLabels, index)
                    plotName = '{}_{}_vs_{}'.format(effName,
                                                    otherVariableLabel,
                                                    variableLabel)
                    plotPath = os.path.join(plotDir, plotName)

                    plot_1d_eff(plotPath, [graph_data, graph_mc],
                                labels=['Data', 'Simulation'],colors=colors,
                                xlabel=xlabel, ylabel=ylabel,
                                xRange=xRange, additional_text=additional_text, ratio=True)
    
            	    # dataEfficiency systs
                    graphs = [get_graph(hists[extEffName+'_efficiencyData_errD'],
                                        hists[extEffName+'_efficiencyData_errU'],
                                        axes[vi], vi, *index)]
                    labels = ['Nominal']
                    for iSyst in itertools.chain(
                            systList['dataEff']['fitTypes'],
                            systList['dataEff']['shiftTypes']):
                        graphs += [get_graph(
                            hists[extEffName+'_efficiencyData_'+iSyst],
                            hists[extEffName+'_efficiencyData_'+iSyst],
                            axes[vi], vi, *index)]
                        labels += [iSyst]
                    plotName = '{}_{}_vs_{}_efficiencyData_syst'.format(
                        effName,
                        otherVariableLabel,
                        variableLabel,
            	    )
                    plotPath = os.path.join(plotDir, plotName)
                    plot_1d_eff(plotPath, graphs,
                                labels=labels,
                                xlabel=xlabel, ylabel=ylabel,
                                xRange=xRange, additional_text=additional_text)
    
            	    # mcEfficiency systs
                    graphs = [get_graph(hists[extEffName+'_efficiencyMC_errD'],
                                        hists[extEffName+'_efficiencyMC_errU'],
                                        axes[vi], vi, *index)]
                    labels = ['Nominal']
                    for iSyst in itertools.chain(
                            systList['mcEff']['fitTypes'],
                            systList['mcEff']['shiftTypes']):
                        graphs += [get_graph(
                            hists[extEffName+'_efficiencyMC_'+iSyst],
                            hists[extEffName+'_efficiencyMC_'+iSyst],
                            axes[vi], vi, *index)]
                        labels += [iSyst]
                    plotName = '{}_{}_vs_{}_efficiencyMC_syst'.format(
                        effName,
                        otherVariableLabel,
                        variableLabel,
            	    )
                    plotPath = os.path.join(plotDir, plotName)
                    plot_1d_eff(plotPath, graphs,
                                labels=labels,
                                xlabel=xlabel, ylabel=ylabel,
                                xRange=xRange, additional_text=additional_text)
    
            # if no indices, easier, just itself
            else:
                graph_data = get_graph(hists[extEffName+'_efficiencyData_errD'],
                                   hists[extEffName+'_efficiencyData_errU'],
                                   axes[vi], vi)
                graph_mc = get_graph(hists[extEffName+'_efficiencyMC_errD'],
                                 hists[extEffName+'_efficiencyMC_errU'],
                                 axes[vi], vi)
    
                xlabel = get_variable_name_pretty(variableLabel)
                ylabel = 'Efficiency'
                xRange = [axes[0].GetBinLowEdge(1),
                      axes[0].GetBinUpEdge(axes[0].GetNbins())]
                plotDir = os.path.join(baseDir, 'plots',
                                   particle, probe,
                                   resonance, era,
                                   effName, 'efficiency')
                os.makedirs(plotDir, exist_ok=True)
                plotName = '{}_vs_{}'.format(effName, variableLabel)
                plotPath = os.path.join(plotDir, plotName)
                plot_1d_eff(plotPath, [graph_data, graph_mc],
                        xlabel=xlabel, ylabel=ylabel,
                        xRange=xRange, ratio=True)

    if denom=="ref":
        effName = get_eff_name(num, denom)
        ResName = "Z_ResAndUncertainty"
        binning = config.binning()
        dataSubEra, mcSubEra, mcSubEraAlt = get_data_mc_sub_eras(resonance, era)

        systList = config.get('systematics',
                              {x: {'fitTypes': [],
                                   'shiftTypes': []}
                               for x in ['dataRes', 'mcRes']})

        def get_variable_name_pretty(variableLabel):
            variables = config.variables()
            return variables.get(variableLabel, {}).get('pretty', variableLabel)

        # create output histograms
        nVars = 1
        THX = ROOT.TH1F
        hargs = [ResName, ResName]
        hargs += [len(binning["pt"]) - 1, array('d', binning["pt"])]
        hist = THX(*hargs)
        axes = [hist.GetXaxis(), hist.GetYaxis()]
        axes[0].SetTitle(get_variable_name_pretty("pt"))
        hist.GetYaxis().SetTitle('Uncertainty')
        Lis_pt= binning["pt"]
        for variableLabel in variableLabels:
            if variableLabel == "pt":
                continue       
            Lis_var=binning[variableLabel] #only work for two binvariables including pt       

        for varbin in range(1,len(Lis_var)):
            indices=[[varbin],list(range(1,len(Lis_pt)))]
            hist_dataRes = hist.Clone('_resolutionData')
            hist_dataRes.GetYaxis().SetTitle('Resolution')
            hist_dataRes_stat = hist_dataRes.Clone('_resolutionData_stat')
            hist_dataRes_syst = hist_dataRes.Clone('_resolutionData_syst')
            histList_dataRes_syst = {
                 'combined_syst': hist_dataRes.Clone(
                       '_resolutionData_combined_syst'),
             }

            hist_mcRes = hist_dataRes.Clone('_resolutionMC')
            hist_mcRes_stat = hist_dataRes.Clone('_resolutionMC_stat')
            hist_mcRes_syst = hist_dataRes.Clone('_resolutionMC_syst')
            histList_mcRes_syst = {
                 'combined_syst': hist_dataRes.Clone(
                     '_resolutionMC_combined_syst'),
             }

             # the individual systematics
            for iSyst in itertools.chain(systList['dataRes']['fitTypes'],
                                          systList['dataRes']['shiftTypes']):
                histList_dataRes_syst[iSyst] = hist_dataRes.Clone('_'+iSyst)
                histList_dataRes_syst[iSyst+'_syst'] = hist_dataRes.Clone(
                     '_'+iSyst+'_syst')

            for iSyst in itertools.chain(systList['mcRes']['fitTypes'],
                                          systList['mcRes']['shiftTypes']):
                histList_mcRes_syst[iSyst] = hist_mcRes.Clone('_'+iSyst)
                histList_mcRes_syst[iSyst+'_syst'] = hist_mcRes.Clone(
                     '_'+iSyst+'_syst')

            varName = get_variables_name(variableLabels)

            # iterate through the bin indices
            # this does nested for loops of the N-D binning (e.g. pt, eta)
            # binning starts at 1 (0 is underflow), same as ROOT
            hists={}
            for index in itertools.product(*indices):
                binName = get_full_name(num, denom, variableLabels, index)
                fitType = 'res3'
                dataFNameFit = os.path.join(baseDir, 'fits_data',
                                            particle, probe,
                                            resonance, era,
                                            fitType, effName,
                                            binName + '.root')
                data_res, dataStat, mc_res, mcStat = get_Res( binName, dataFNameFit, resonance=resonance)
                fitTypes = set(systList['dataRes']['fitTypes']
                               + systList['mcRes']['fitTypes'])
                shiftTypes = set(systList['dataRes']['shiftTypes']
                                 + systList['mcRes']['shiftTypes'])

                sf_syst = getResSyst(binName, dataFNameFit,
                                      fitTypes, shiftTypes, resonance=resonance)

                combined_syst = {}
                for kind in ['dataRes', 'mcRes']:
                    combined_syst[kind] = 0
                    temp=0
                    if kind == 'dataRes':
                        errKey = 'data_err'
                    if kind == 'mcRes':
                        errKey = 'mc_err'
                    for t in itertools.chain(systList[kind]['fitTypes']):
                        if sf_syst[t][errKey]>temp:
                            temp=sf_syst[t][errKey]
                    combined_syst[kind]=temp**2
                    for t in itertools.chain(systList[kind]['shiftTypes']):
                        combined_syst[kind] += sf_syst[t][errKey]**2
                    combined_syst[kind] = combined_syst[kind]**0.5
                dataErr = (dataStat**2 + combined_syst['dataRes']**2)**0.5
                mcErr = (mcStat**2 + combined_syst['mcRes']**2)**0.5

                def set_bin(hist, index, val, err):
                    ind = [index[1]]
                    val_args = ind + [val]
                    err_args = ind + [err]
                    hist.SetBinContent(*val_args)
                    if err >= 0:
                        hist.SetBinError(*err_args)

                
                set_bin(hist_dataRes, index, data_res, dataErr)
                set_bin(hist_dataRes_stat, index, data_res, dataStat)
                set_bin(hist_dataRes_syst, index, data_res, combined_syst['dataRes'])
                set_bin(histList_dataRes_syst['combined_syst'], index,
                        combined_syst['dataRes'], -1)
                set_bin(hist_mcRes, index, mc_res, mcErr)
                set_bin(hist_mcRes_stat, index, mc_res, mcStat)
                set_bin(hist_mcRes_syst, index, mc_res, combined_syst['mcRes'])
                set_bin(histList_mcRes_syst['combined_syst'], index,
                        combined_syst['mcRes'], -1)
                for iKey in sf_syst.keys():

                    if iKey in histList_dataRes_syst:
                        set_bin(histList_dataRes_syst[iKey], index,
                                sf_syst[iKey]['data_res'], sf_syst[iKey]['data_err'])
                        set_bin(histList_dataRes_syst[iKey+'_syst'], index,
                                sf_syst[iKey]['data_err'], -1)

                    if iKey in histList_mcRes_syst:
                        set_bin(histList_mcRes_syst[iKey], index,
                                sf_syst[iKey]['mc_res'], sf_syst[iKey]['mc_err'])
                        set_bin(histList_mcRes_syst[iKey+'_syst'], index,
                                sf_syst[iKey]['mc_err'], -1)
            hists['resolutionData%i'%varbin] = hist_dataRes
            hists['resolutionData_stat%i'%varbin] = hist_dataRes_stat
            hists['resolutionData_syst%i'%varbin] = hist_dataRes_syst
            hists['resolutionMC%i'%varbin] = hist_mcRes
            hists['resolutionMC_stat%i'%varbin] = hist_mcRes_stat
            hists['resolutionMC_syst%i'%varbin] = hist_mcRes_syst
            
            for iKey in histList_dataRes_syst.keys():
                hname = 'resolutionData_'+iKey+'%i'%varbin
                hists[hname] = histList_dataRes_syst[iKey]
            for iKey in histList_mcRes_syst.keys():
                hname = 'resolutionMC_'+iKey+'%i'%varbin
                hists[hname] = histList_mcRes_syst[iKey]

            # save the efficiency
            resDir = os.path.join(baseDir, 'resolutions',
                                  particle, probe,
                                  resonance, era,
                                  effName+"bin%i"%varbin)
            os.makedirs(resDir, exist_ok=True)
            resPath = os.path.join(resDir, ResName)    
            
            tfile = ROOT.TFile.Open('{}.root'.format(resPath), 'recreate')
            for h in sorted(hists):
                hists[h].Write(h)

                if skipPlots:
                    continue         
            tfile.Close()

def build_prepare_jobs(particle, probe, resonance, era,
                       config, **kwargs):
    _baseDir = kwargs.pop('baseDir', '')
    _numerator = kwargs.pop('numerator', [])
    _denominator = kwargs.pop('denominator', [])
    _registry = kwargs.pop('registry', None)

    if _registry is not None:
        registry.reset()
        registry.load_json(_registry)

    subEra = era.split('_')[0]  # data subera is beginning of era
    lumi = registry.luminosity(particle, probe, resonance, era, subEra, **kwargs)

    jobs = []
    # iterate through the efficiencies
    efficiencies = config.efficiencies()
    for num, denom in efficiencies:
        if _numerator and num not in _numerator:
            continue
        if _denominator and denom not in _denominator:
            continue

        # iterate through the output binning structure
        for variableLabels in config.binVariables():

            jobs += [[_baseDir, particle, probe, resonance, era,
                     config, num, denom, tuple(variableLabels), lumi]]
    return jobs
