from __future__ import print_function

import os
import itertools
from glob import glob
import numpy as np
import pandas as pd
import uproot
import pickle
import boost_histogram as bh

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from registry import registry
from dataset_allowed_definitions import get_allowed_sub_eras, get_data_mc_sub_eras
from muon_definitions import (get_miniIso_dataframe,
                              get_weighted_dataframe,
                              get_binned_dataframe,
                              get_extended_eff_name,
                              get_full_name)

useParquet = True


def run_flattening(spark, particle, probe, resonance, era, subEra,
                   config, shift='Nominal', **kwargs):
    _numerator = kwargs.pop('numerator', [])
    _denominator = kwargs.pop('denominator', [])
    _baseDir = kwargs.pop('baseDir', '')
    _testing = kwargs.pop('testing', False)
    _registry = kwargs.pop('registry', None)

    doProbeMultiplicity = False

    print('Running flattening for', particle, probe, resonance, era, subEra, shift)

    if _registry is not None:
        registry.reset()
        registry.load_json(_registry)

    if useParquet:
        fnames = list(registry.parquet(
            particle, probe, resonance, era, subEra, **kwargs))
    else:
        fnames = registry.root(particle, probe, resonance, era, subEra, **kwargs)
        # Assume path in registry is already correct, no need for redirector
        # fnames = ['root://eoscms.cern.ch/'+f for f in fnames]
        fnames = [f for f in fnames]

    jobPath = os.path.join(particle, probe, resonance, era, subEra)
    if shift:
        jobPath = os.path.join(jobPath, shift)
    if _testing:
        jobPath = os.path.join('testing', jobPath)
    else:
        jobPath = os.path.join('flat', jobPath)
    if _baseDir:
        jobPath = os.path.join(_baseDir, jobPath)
    os.makedirs(jobPath, exist_ok=True)

    doGen = subEra in ['DY_madgraph', 'DY_powheg', 'DY_amcatnlo', 'JPsi_pythia8']

    # default numerator/denominator defintions
    efficiencies = config.efficiencies()

    # get the dataframe
    if useParquet:
        print('Loading parquet files:', fnames)
        if isinstance(fnames, list):
            baseDF = spark.read.parquet(*fnames)
        else:
            baseDF = spark.read.parquet(fnames)
    else:
        print('Loading root files, first file: ', fnames[0])
        treename = registry.treename(particle, probe, resonance, era, subEra, **kwargs)
        baseDF = spark.read.format("root")\
                      .option('tree', treename)\
                      .load(fnames)

    # create the definitions columns
    definitions = config.definitions()

    for d in definitions:
        baseDF = baseDF.withColumn(d, F.expr(definitions[d]))

    # select tags
    selection = config.selection()
    if "pair_probeMultiplicity" in selection:
        doProbeMultiplicity = True
        selection = selection.split("and pair_probeMultiplicity")[0] + selection.split("and pair_probeMultiplicity")[1]
    baseDF = baseDF.filter(selection)

    if doGen:
        if 'mc_selection' in config:
            baseDF = baseDF.filter(config.mc_selection())
    else:
        if 'data_selection' in config:
            baseDF = baseDF.filter(config.data_selection())

    # build the weights (pileup for MC)
    baseDF = get_weighted_dataframe(
        baseDF, doGen, resonance, era, subEra, shift=shift)
 
    # create the binning structure
    fitVariable = config.fitVariable()
    binningSet = set([fitVariable])
    if doGen:
        fitVariableGen = config.fitVariableGen()
        binningSet = binningSet.union(set([fitVariableGen]))
    binVariables = config.binVariables()
    for bvs in binVariables:
        binningSet = binningSet.union(set(bvs))

    binning = config.binning() 

    pklFile=open("./binning.pkl","wb")
    pickle.dump(binning,pklFile)
    pklFile.close()

    variables = config.variables()
    for bName in binningSet:
        baseDF = get_binned_dataframe(
            baseDF, bName+"Bin",
            variables[bName]['variable'],
            binning[bName])

    # build the unrealized yield dataframes
    # they are binned in the ID, bin variables, and fit variable
    yields = {}
    yields_gen = {}

    for numLabel, denLabel in efficiencies:
        den = baseDF.filter(denLabel)
        if doProbeMultiplicity:
            count = den.groupBy("tag_pt", "event").count()
            den = den.join(count, on=["tag_pt", "event"])
            den = den.filter("count==1")
        for binVars in binVariables:
            key = (numLabel, denLabel, tuple(binVars))
            yields[key] = den.groupBy(
                numLabel, *[b+'Bin' for b in
                            binVars+[fitVariable]])\
                .agg({'weight2': 'sum', 'weight': 'sum'})
            if doGen:
                yields_gen[key] = den.groupBy(
                    numLabel, *[b+'Bin' for b in
                                binVars+[fitVariableGen]])\
                    .agg({'weight2': 'sum', 'weight': 'sum'})

    def get_values(df, mLabel, **binValues):
        for k, v in binValues.items():
            df = df[df[k] == v]
        df = df.set_index(mLabel)
        # fill empty bins with 0
        # includes underflow and overflow in the ROOT numbering scheme
        # (0 is underflow, len(binning)+1 is overflow)
        values = pd.Series(np.zeros(len(binning['mass'])+1))
        values[df.index] = df['sum(weight)']
        values = values.to_numpy()
        sumw2 = pd.Series(np.zeros(len(binning['mass'])+1))
        if 'sum(weight2)' in df.columns:
            sumw2[df.index] = df['sum(weight2)']
        else:
            sumw2[df.index] = df['sum(weight)']  # no weights provided
        sumw2 = sumw2.to_numpy()
        return values, sumw2

    def get_hist(values, sumw2, edges, overflow=True):
        hist = bh.Histogram(bh.axis.Variable(edges), storage=bh.storage.Weight())
        if overflow:
            hist.view(flow=True).value = values
            hist.view(flow=True).variance = sumw2
        else:
            hist.view(flow=False).value = values[1:-1]
            hist.view(flow=False).variance = sumw2[1:-1]
        return hist

    # realize each of the yield tables
    # then produce the histograms and saves them
    # this is the first time things are put into memory
    for num_den_binVars in yields:
        num, den, binVars = num_den_binVars
        if _numerator and num not in _numerator:
            continue
        if _denominator and den not in _denominator:
            continue
        extended_eff_name = get_extended_eff_name(num, den, binVars)

        eff_outname = f'{jobPath}/{extended_eff_name}.root'
        hists = {}

        print('Processing', eff_outname)
        realized = yields[num_den_binVars].toPandas()

        for bins in itertools.product(
                *[range(1, len(binning[b])) for b in binVars]):
            binname = get_full_name(num, den, binVars, bins)
            binargs = {b+'Bin': v for b, v in zip(binVars, bins)}
            mLabel = fitVariable + 'Bin'

            passargs = {num: True}
            passargs.update(binargs)
            values, sumw2 = get_values(realized, mLabel, **passargs)
            if not sum(values):
                print('Warning: integral = 0 for', binname, 'Pass')
            edges = binning[fitVariable]
            hists[binname+'_Pass'] = get_hist(values, sumw2, edges)

            failargs = {num: False}
            failargs.update(binargs)
            values, sumw2 = get_values(realized, mLabel, **failargs)
            if not sum(values):
                print('Warning: integral = 0 for', binname, 'Fail')
            edges = binning[fitVariable]
            hists[binname+'_Fail'] = get_hist(values, sumw2, edges)

        if doGen:
            realized = yields_gen[num_den_binVars].toPandas()
            for bins in itertools.product(
                    *[range(1, len(binning[b])) for b in binVars]):
                binname = get_full_name(num, den, binVars, bins)
                binargs = {b+'Bin': v for b, v in zip(binVars, bins)}
                mLabel = fitVariableGen + 'Bin'

                passargs = {num: True}
                passargs.update(binargs)
                values, sumw2 = get_values(realized, mLabel, **passargs)
                if not sum(values):
                    print('Warning: integral = 0 for', binname, 'Pass_Gen')
                edges = binning[fitVariableGen]
                hists[binname+'_Pass_Gen'] = get_hist(values, sumw2, edges)

                failargs = {num: False}
                failargs.update(binargs)
                values, sumw2 = get_values(realized, mLabel, **failargs)
                if not sum(values):
                    print('Warning: integral = 0 for', binname, 'Fail_Gen')
                edges = binning[fitVariableGen]
                hists[binname+'_Fail_Gen'] = get_hist(values, sumw2, edges)

        with uproot.recreate(eff_outname) as f:
            for h, hist in sorted(hists.items()):
                f[h] = hist

    del baseDF


def run_all(spark, particle, probe, resonance, era,
            config, shift='Nominal', **kwargs):
    # data only option
    dataOnly = kwargs.pop('dataOnly', False)
    # flatten each sub-era if True
    bySubEraAlso = kwargs.pop('bySubEraAlso', False)
    if bySubEraAlso:
        subEras = get_allowed_sub_eras(resonance, era)
    else:
        subEras = get_data_mc_sub_eras(resonance, era)
    for subEra in subEras:
        if subEra==None:
            continue
        if dataOnly and 'Run20' not in subEra:
            continue
        run_flattening(spark, particle, probe, resonance, era, subEra,
                       config, shift, **kwargs)


def run_spark(particle, probe, resonance, era, config, **kwargs):
    _shiftType = kwargs.pop('shiftType', [])
    _useLocalSpark = kwargs.pop('useLocalSpark', False)

    local_jars = ','.join([
        './laurelin-1.6.0.jar',
        './log4j-api-2.13.0.jar',
        './log4j-core-2.13.0.jar',
    ])

    spark = SparkSession\
        .builder\
        .appName("TnP")

    if useParquet == False:
        spark = spark\
        .config("spark.jars", local_jars)\
        .config("spark.driver.extraClassPath", local_jars)\
        .config("spark.executor.extraClassPath", local_jars)\
        .config("spark.dynamicAllocation.maxExecutors", "100")\
        .config("spark.driver.memory", "6g")\
        .config("spark.executor.memory", "4g")\
        .config("spark.executor.cores", "2")
    else:
        spark = spark\
        .config("spark.sql.broadcastTimeout", "36000")\
        .config("spark.network.timeout", "600s")\
        .config("spark.driver.memory", "6g")\
        .config("spark.executor.memory", "10g")


    if _useLocalSpark == True:
        spark = spark.master("local")

    spark = spark.getOrCreate()

    sc = spark.sparkContext
    print(sc.getConf().toDebugString())

    shiftTypes = config.shifts()

    for shiftType in shiftTypes:
        if _shiftType and shiftType not in _shiftType:
            continue
        run_all(spark, particle, probe, resonance, era,
                config.shift(shiftType), shift=shiftType, **kwargs)

    spark.stop()
