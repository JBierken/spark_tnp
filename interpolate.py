from __future__ import print_function
import os
import json
import pickle

from scipy.interpolate import LinearNDInterpolator

from muon_definitions import (get_eff_name,
                              get_extended_eff_name,
                              get_variables_name)

def interpolate(particle, probe, resonance, era, config,
                baseDir, num, denom, directories, workingPoints,
               ):

    variableLabels = config.binVariables()

    effName = get_eff_name(num[0], denom[0])
    extEffName = get_extended_eff_name(num[0], denom[0], variableLabels[0])
    varName = get_variables_name(variableLabels[0])

    files = []

    #open json files
    for dir in directories:
        fileDir = os.path.join(dir, 'efficiencies', particle, probe, resonance,
                               era, effName, extEffName + '.json')
        file = open(fileDir)

        #return json objects as a dictionary
        files.append(json.load(file))

    isMVA = False
    if len(files) > 1:
        isMVA = True 

    if isMVA == False: #2D interpolation as function of observables used for binning
        #loop over bins (same bins for all the working points)
        firstVarBins = list(files[0][effName][varName].keys())

        #create empty vectors to be filled
        firstVarValues = []
        secondVarValues = []
        sf = []
        error = []
        varUp = []
        varDown = []

        for iBin in range(len(files[0][effName][varName]['binning'][0]['binning'])-1):

            last_iBin = len(files[0][effName][varName]['binning'][0]['binning'])-2

            #take the center of the bin..
            if (iBin!=0 and iBin!=last_iBin):
                firstVar_binStart = files[0][effName][varName]['binning'][0]['binning'][iBin]
                firstVar_binEnd = files[0][effName][varName]['binning'][0]['binning'][iBin+1]
                firstVar = firstVar_binStart + (firstVar_binEnd - firstVar_binStart)/2

            #unless it is the first or last bin (needed for correct range of interpolation)
            elif iBin==0:
                firstVar = files[0][effName][varName]['binning'][0]['binning'][iBin]
            elif iBin==last_iBin:
                firstVar = files[0][effName][varName]['binning'][0]['binning'][iBin+1]

            #loop over bins of the second observable (same bins for all the working points)
            secondVarBins = list(files[0][effName][varName][firstVarBins[iBin]].keys())
            for jBin in range(len(files[0][effName][varName]['binning'][1]['binning'])-1):

                last_jBin = len(files[0][effName][varName]['binning'][1]['binning'])-2

                #take the center of the bin..
                if (jBin!=0 and jBin!=last_jBin):
                    secondVar_binStart = files[0][effName][varName]['binning'][1]['binning'][jBin]
                    secondVar_binEnd = files[0][effName][varName]['binning'][1]['binning'][jBin+1]
                    secondVar = secondVar_binStart + (secondVar_binEnd - secondVar_binStart)/2

                #unless it is the first or last bin (needed for correct range of interpolation)
                elif jBin==0:
                    secondVar = files[0][effName][varName]['binning'][1]['binning'][jBin]
                elif jBin==last_jBin:
                    secondVar = files[0][effName][varName]['binning'][1]['binning'][jBin+1]

                firstVarValues.append(firstVar)
                secondVarValues.append(secondVar)

                #scale factors
                var = files[0][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['stat'] + files[0][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['syst']

                sf.append(files[0][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['value'])
                error.append(var)

                #variations
                varUp.append(files[0][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['value'] + var)
                varDown.append(files[0][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['value'] - var)

        interp = LinearNDInterpolator(list(zip(firstVarValues, secondVarValues)), sf)
        interpUp = LinearNDInterpolator(list(zip(firstVarValues, secondVarValues)), varUp)
        interpDown = LinearNDInterpolator(list(zip(firstVarValues, secondVarValues)), varDown)        

    elif (len(variableLabels[0]) == 1) and (isMVA == True): #2D interpolation as function of one observable and MVA working points
        
        if workingPoints is None:
            raise NotImplementedError(
            'Working points need to be specified in the command line with the --workingPoints flag'
        )    
        
        #loop over bins (same bins for all the working points)
        varBins = list(files[0][effName][varName].keys())

        #create empty vectors to be filled
        varValues = []
        wpValues = []
        sf = []
        error = []
        varUp = []
        varDown = []

        for iBin in range(len(files[0][effName][varName]['binning'][0]['binning'])-1):

            last_iBin = len(files[0][effName][varName]['binning'][0]['binning'])-2

            #take the center of the bin..
            if (iBin!=0 and iBin!=last_iBin):
                var_binStart = files[0][effName][varName]['binning'][0]['binning'][iBin]
                var_binEnd = files[0][effName][varName]['binning'][0]['binning'][iBin+1]
                var = var_binStart + (var_binEnd - var_binStart)/2

            #unless it is the first or last bin (needed for correct range of interpolation)
            elif iBin==0:
                var = files[0][effName][varName]['binning'][0]['binning'][iBin]
            elif iBin==last_iBin:
                var = files[0][effName][varName]['binning'][0]['binning'][iBin+1]

            #loop over working points
            for i in range(len(files)):

                varValues.append(var)

                #fix values of working points
                if (i!=0 and i!=(len(files)-1)):
                    wp = float(workingPoints[i]) + (float(workingPoints[i]) - float(workingPoints[i+1]))/2
                elif (i==0):
                    wp = float(workingPoints[i])
                else: #last point should always be 1
                    wp = 1

                wpValues.append(wp)

                #scale factors
                sf.append(files[i][effName][varName][varBins[iBin]]['value'])
                error.append(files[i][effName][varName][varBins[iBin]]['stat'] +
                         files[i][effName][varName][varBins[iBin]]['syst'])

                #variations
                varUp.append(files[i][effName][varName][varBins[iBin]]['value'] + error[i])
                varDown.append(files[i][effName][varName][varBins[iBin]]['value'] - error[i])

        interp = LinearNDInterpolator(list(zip(varValues, wpValues)), sf)
        interpUp = LinearNDInterpolator(list(zip(varValues, wpValues)), varUp)
        interpDown = LinearNDInterpolator(list(zip(varValues, wpValues)), varDown)

    elif (len(variableLabels[0]) == 2) and (isMVA == True): #3D interpolation as function of observables used for binning and MVA working points
        
        if workingPoints is None:
            raise NotImplementedError(
            'Working points need to be specified in the command line with the --workingPoints flag'
        )    
        
        # loop over bins (same bins for all the working points)
        firstVarBins = list(files[0][effName][varName].keys())

        #create empty vectors to be filled
        firstVarValues = []
        secondVarValues = []
        wpValues = []
        sf = []
        error = []
        varUp = []
        varDown = []

        for iBin in range(len(files[0][effName][varName]['binning'][0]['binning'])-1):

            last_iBin = len(files[0][effName][varName]['binning'][0]['binning'])-2

            #take the center of the bin..
            if (iBin!=0 and iBin!=last_iBin):
                firstVar_binStart = files[0][effName][varName]['binning'][0]['binning'][iBin]
                firstVar_binEnd = files[0][effName][varName]['binning'][0]['binning'][iBin+1]
                firstVar = firstVar_binStart + (firstVar_binEnd - firstVar_binStart)/2

            #unless it is the first or last bin (needed for correct range of interpolation)
            elif iBin==0:
                firstVar = files[0][effName][varName]['binning'][0]['binning'][iBin]
            elif iBin==last_iBin:
                firstVar = files[0][effName][varName]['binning'][0]['binning'][iBin+1]

            #loop over bins of the second observable (same bins for all the working points)
            secondVarBins = list(files[0][effName][varName][firstVarBins[iBin]].keys())
            for jBin in range(len(files[0][effName][varName]['binning'][1]['binning'])-1):

                last_jBin = len(files[0][effName][varName]['binning'][1]['binning'])-2

                #take the center of the bin..
                if (jBin!=0 and jBin!=last_jBin):
                    secondVar_binStart = files[0][effName][varName]['binning'][1]['binning'][jBin]
                    secondVar_binEnd = files[0][effName][varName]['binning'][1]['binning'][jBin+1]
                    secondVar = secondVar_binStart + (secondVar_binEnd - secondVar_binStart)/2

                #unless it is the first or last bin (needed for correct range of interpolation)
                elif jBin==0:
                    secondVar = files[0][effName][varName]['binning'][1]['binning'][jBin]
                elif jBin==last_jBin:
                    secondVar = files[0][effName][varName]['binning'][1]['binning'][jBin+1]

                #loop over working points
                for i in range(len(files)):

                    firstVarValues.append(firstVar)
                    secondVarValues.append(secondVar)

                    #fix values of working points
                    if (i!=0 and i!=(len(files)-1)):
                        wp = float(workingPoints[i]) + (float(workingPoints[i]) - float(workingPoints[i+1]))/2
                    elif (i==0):
                        wp = float(workingPoints[i])
                    else: #last point should always be 1
                        wp = 1

                    wpValues.append(wp)

                    #scale factors
                    sf.append(files[i][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['value'])
                    error.append(files[i][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['stat'] +
                             files[i][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['syst'])

                    #variations
                    varUp.append(files[i][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['value'] + error[i])
                    varDown.append(files[i][effName][varName][firstVarBins[iBin]][secondVarBins[jBin]]['value'] - error[i])

        interp = LinearNDInterpolator(list(zip(firstVarValues, secondVarValues, wpValues)), sf)
        interpUp = LinearNDInterpolator(list(zip(firstVarValues, secondVarValues, wpValues)), varUp)
        interpDown = LinearNDInterpolator(list(zip(firstVarValues, secondVarValues, wpValues)), varDown)

    else:
        raise NotImplementedError(
            'Interpolation is only supported in 2 and 3 dimensions'
        )

    #save interpolation results to apply scale factors in the analysis
    outDir = os.path.join(baseDir, 'interpolation_' + era + '.pck')
    outDir_varUp = os.path.join(baseDir, 'interpolation_varUp_' + era + '.pck')
    outDir_varDown = os.path.join(baseDir, 'interpolation_varDown_' + era + '.pck')

    if not os.path.exists(baseDir):
        os.makedirs(baseDir)

    with open(outDir, 'wb') as file_handle:
        pickle.dump(interp, file_handle)
    with open(outDir_varUp, 'wb') as file_handle:
        pickle.dump(interpUp, file_handle)
    with open(outDir_varDown, 'wb') as file_handle:
        pickle.dump(interpDown, file_handle)

    return
