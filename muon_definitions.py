import os
import uproot
import itertools
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.ml.feature import Bucketizer
from pyspark.sql.functions import pandas_udf
import correctionlib
import numpy as np

from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("YourAppName").getOrCreate()


#def get_pileup(resonance, era, subEra):
   #'''
   #Get the pileup distribution scalefactors to apply to simulation
   #for a given era.
   #'''
#
   ## get the pileup
   #dataPileup = {
   #   # Note: for now use ReReco version of pileup
   #   # TODO: need to redo splitting by 2016 B-F/F-H
   #   'Run2016_UL_HIPM': 'pileup/data/Run2016.root',
   #   'Run2016_UL': 'pileup/data/Run2016.root',
   #   'Run2017_UL': 'pileup/data/Run2017.root',
   #   'Run2018_UL': 'pileup/data/Run2018.root',
   #   # Double muon PD
   #   'Run2016_UL_HIPM_DM': 'pileup/data/Run2016.root',
   #   'Run2016_UL_DM': 'pileup/data/Run2016.root',
   #   'Run2017_UL_DM': 'pileup/data/Run2017.root',
   #   'Run2018_UL_DM': 'pileup/data/Run2018.root',
   #   'Run2016': 'pileup/data/Run2016.root',
   #   'Run2017': 'pileup/data/Run2017.root',
   #   'Run2018': 'pileup/data/Run2018.root',
   #   # Run2022 : Centrally produced ROOT files by LUMI POG (https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData#Centrally_produced_ROOT_histogra)
   #   'Run2022': 'pileup/data/Run2022_LUM.root',
   #   'Run2022_EE': 'pileup/data/Run2022_LUM.root',
   #   # Run2023 
   #   #'Run2023': 'pileup/data/Run2023D.root',
   #   #'Run2023': 'pileup/data/Run2023_LUM.root',
   #   'Run2022': 'pileup/data/pileupHistogram-Cert_Collisions2022_355100_357900_eraBCD_GoldenJson-13p6TeV-69200ub-99bins.root',
   #   #'Run2023': 'pileup/data/pileupHistogram-Cert_Collisions2023_369803_370790_eraD_GoldenJson-13p6TeV-69200ub-99bins.root',
   #   'Run2023': 'pileup/data/data_nVertices.root',
   #}
   #mcPileup = {
   #   # TODO: do the two eras have different profiles?
   #   'Run2016_UL_HIPM': 'pileup/mc/Run2016_UL.root',
   #   'Run2016_UL': 'pileup/mc/Run2016_UL.root',
   #   'Run2017_UL': 'pileup/mc/Run2017_UL.root',
   #   'Run2018_UL': 'pileup/mc/Run2018_UL.root',
   #   # Double muon PD
   #   'Run2016_UL_HIPM_DM': 'pileup/mc/Run2016_UL.root',
   #   'Run2016_UL_DM': 'pileup/mc/Run2016_UL.root',
   #   'Run2017_UL_DM': 'pileup/mc/Run2017_UL.root',
   #   'Run2018_UL_DM': 'pileup/mc/Run2018_UL.root',
   #   'Run2016': 'pileup/mc/Run2016.root',
   #   'Run2017': 'pileup/mc/Run2017.root',
   #   'Run2018': 'pileup/mc/Run2018.root',
   #   # Run2022 (nTrueInteractions profile got privately by Sergio over our MC ntuples.)
   #   'Run2022': 'pileup/mc/Run2022.root',
   #   'Run2022_EE': 'pileup/mc/Run2022EE.root',
   #   # Run2023 (nTrueInteractions profile got privately by Sergio over our MC ntuples.)
   #   #'Run2023': 'pileup/mc/Run2023_BPix.root',
   #   'Run2023': 'pileup/mc/mc_nVertices.root',
 #
   #}
   #
   ## get absolute path
   #baseDir = os.path.dirname(__file__)
   #dataPileup = {k: os.path.join(baseDir, dataPileup[k]) for k in dataPileup}
   #mcPileup = {k: os.path.join(baseDir, mcPileup[k]) for k in mcPileup}
   #with uproot.open(dataPileup[era]) as f:
   #    data_edges = f['pileup'].axis(0).edges()
   #    data_pileup = f['pileup'].values()
   #    #data_pileup = np.ones_like(data_pileup)
   #    #data_pileup /= sum(data_pileup)
   #with uproot.open(mcPileup[era]) as f:
   #    mc_edges = f['pileup'].axis(0).edges()
   #    mc_pileup = f['pileup'].values()
   #    #mc_pileup /= sum(mc_pileup)
   #pileup_edges = data_edges if len(data_edges) < len(mc_edges) else mc_edges
   #pileup_ratio = [d/m if m else 1.0 for d, m in zip(                     
   #    data_pileup[:len(pileup_edges)-1], mc_pileup[:len(pileup_edges)-1])]
   #
   #print(data_pileup)
   #print(mc_pileup)
   #print(pileup_edges)
   #print(pileup_ratio)
   #
   #multiply=[d*m for d, m in zip(pileup_ratio, mc_pileup)]
   #
   #print(multiply)
#
   #return pileup_ratio, pileup_edges

def get_prescale(resonance, era, subEra):
   '''
   Get the prescale factors to apply to simulation
   for a given era.
   '''
   mcPrescale = {
       # TODO: do the two eras have different profiles?
       #'Run2016_UL_HIPM': 'pileup/mc/Run2016_UL.root',
       #'Run2016_UL': 'pileup/mc/Run2016_UL.root',
       'Run2017_UL': 'prescale/mc/Run2017_UL.root',
       #'Run2018_UL': 'pileup/mc/Run2018_UL.root',
       #'Run2016': 'pileup/mc/Run2016.root',
       #'Run2017': 'pileup/mc/Run2017.root',
       #'Run2018': 'pileup/mc/Run2018.root'
   }
   # get absolute path
   baseDir              = os.path.dirname(__file__)
   #dataPileup          = {k: os.path.join(baseDir, dataPileup[k]) for k in dataPileup}
   mcPrescale           = {k: os.path.join(baseDir, mcPrescale[k]) for k in mcPrescale}
   with uproot.open(mcPrescale[era]) as f:
       mc_edges         = f['prescale'].edges
       mc_prescale      = f['prescale'].values
       #mc_pileup       /= sum(mc_pileup)
   prescale_edges       = mc_edges
   prescale_values      = mc_prescale.astype('float64')

   return prescale_values, prescale_edges

def get_tag_dataframe(df, resonance, era, subEra, shift=None):
   '''
   Produces a dataframe reduced by the default tag selection
   used by the Muon POG.
   The optional shift parameter will change the tag
   for systematic uncertainties.
   '''
   if resonance == 'Z':
       if '2017' in era:
           tag_sel      = 'tag_pt>29 and tag_abseta<2.4 and tag_IsoMu27==1'\
                            + ' and pair_probeMultiplicity==1'
       else:
           tag_sel      = 'tag_pt>26 and tag_abseta<2.4 and tag_IsoMu24==1'\
                            + ' and pair_probeMultiplicity==1'
       if shift == 'TagIsoUp':
           tag_sel      = tag_sel + ' and tag_combRelIsoPF04dBeta<0.3'
       elif shift == 'TagIsoDown':
           tag_sel      = tag_sel + ' and tag_combRelIsoPF04dBeta<0.1'
       else:
           tag_sel      = tag_sel + ' and tag_combRelIsoPF04dBeta<0.2'

   return df.filter(tag_sel)


def get_miniIso_dataframe(df):
   '''
   Produces a dataframe with a miniIsoAEff, miniIso_riso2,
   miniIso_CorrectedTerm and miniIsolation column.
   '''
   miniIsoAEff_udf      = F.udf(lambda abseta:
                                0.0735 if abseta <= 0.8
                                else (0.0619 if abseta <= 1.3
                                    else (0.0465 if abseta <= 2.0
                                        else (0.0433 if abseta <= 2.2
                                                else 0.0577))),
                                T.FloatType())
   miniIsoRiso2_udf     = F.udf(lambda pt:
                                max(0.05, min(0.2, 10.0/pt)),
                                T.FloatType())
   miniIsolation_udf    = F.udf(lambda charged, photon, neutral, corr, pt:
                                (charged+max(0.0, photon+neutral-corr))/pt,
                                T.FloatType())
   miniIsoDF            = df.withColumn('miniIsoAEff', miniIsoAEff_udf(df.abseta))
   miniIsoDF            = miniIsoDF.withColumn('miniIso_riso2',
                                                miniIsoRiso2_udf(miniIsoDF.pt))
   miniIsoDF            = miniIsoDF.withColumn(
                            'miniIso_CorrectedTerm',
                            (F.col('fixedGridRhoFastjetCentralNeutral') *
                            F.col('miniIsoAEff') * F.col('miniIso_riso2')/0.09))
   miniIsoDF            = miniIsoDF.withColumn(
                            'miniIsolation', 
                            miniIsolation_udf(miniIsoDF.miniIsoCharged,
                                                miniIsoDF.miniIsoPhotons,
                                                miniIsoDF.miniIsoNeutrals,
                                                miniIsoDF.miniIso_CorrectedTerm,
                                                miniIsoDF.pt)
                        )
   return miniIsoDF

def check_and_fill_missing_passing(doGen, passing_data_counts):

    all_values_df       = spark.range(1, 101).select(F.col("id").alias("nVertices"))
    missing_values_df   = all_values_df.join(passing_data_counts, on="nVertices", how="left_outer")
    if not doGen:
        filled_df       = missing_values_df.fillna(0, subset=['passing_data'])
    else:
        filled_df       = missing_values_df.fillna(0, subset=['passing_mc'])
    
    return filled_df.orderBy('nVertices')

def check_and_fill_missing_failing(doGen, passing_data_counts):

    all_values_df       = spark.range(1, 101).select(F.col("id").alias("nVertices"))
    missing_values_df   = all_values_df.join(passing_data_counts, on="nVertices", how="left_outer")
    if not doGen:
        filled_df       = missing_values_df.fillna(0, subset=['failing_data'])
    else: 
        filled_df       = missing_values_df.fillna(0, subset=['failing_mc'])
    
    return filled_df.orderBy('nVertices')

def check_and_fill_missing_fake(doGen, passing_data_counts):

    all_values_df       = spark.range(1, 101).select(F.col("id").alias("nVertices"))
    missing_values_df   = all_values_df.join(passing_data_counts, on="nVertices", how="left_outer")
    if not doGen:
        filled_df       = missing_values_df.fillna(0, subset=['fake_data'])
    else: 
        filled_df       = missing_values_df.fillna(0, subset=['fake_mc'])
    
    return filled_df.orderBy('nVertices')

def get_data_passing(df, doGen, resonance, era, subEra, shift=None):
   
    passing_data_counts = df.filter(
                            (F.col('probe_isTrkMatch') == True) & (F.col('probeSA_isTrkMatch') == False)) \
                            .groupBy('nVertices') \
                            .count() \
                            .withColumnRenamed('count', 'passing_data') \
                            .orderBy('nVertices')  
    passing_data_counts = check_and_fill_missing_passing(doGen, passing_data_counts)
    
    return passing_data_counts

def get_data_failing(df, doGen, resonance, era, subEra, shift=None):

    failing_data_counts = df.filter(
                            (F.col('probe_isTrkMatch') == False) & (F.col('probeSA_isTrkMatch') == False)) \
                            .groupBy('nVertices') \
                            .count() \
                            .withColumnRenamed('count', 'failing_data') \
                            .orderBy('nVertices')
    failing_data_counts = check_and_fill_missing_failing(doGen, failing_data_counts)
    
    return failing_data_counts

def get_data_fake(df, doGen, resonance, era, subEra, shift=None):

    fake_data_counts    = df.filter(
                            (F.col('probe_isTrkMatch') == True) & (F.col('probeSA_isTrkMatch') == True)) \
                            .groupBy('nVertices') \
                            .count() \
                            .withColumnRenamed('count', 'fake_data') \
                            .orderBy(F.col('nVertices'))
    fake_data_counts    = check_and_fill_missing_fake(doGen, fake_data_counts)
    
    return fake_data_counts    

def get_mc_passing(df, doGen, resonance, era, subEra, shift=None):
   
    passing_mc_counts = df.filter(
                            (F.col('probe_isTrkMatch') == True) & (F.col('probeSA_isTrkMatch') == False)) \
                            .groupBy('nVertices') \
                            .count() \
                            .withColumnRenamed('count', 'passing_mc') \
                            .orderBy('nVertices')  
    passing_mc_counts = check_and_fill_missing_passing(doGen, passing_mc_counts)
    
    return passing_mc_counts

def get_mc_failing(df, doGen, resonance, era, subEra, shift=None):

    failing_mc_counts = df.filter(
                            (F.col('probe_isTrkMatch') == False) & (F.col('probeSA_isTrkMatch') == False)) \
                            .groupBy('nVertices') \
                            .count() \
                            .withColumnRenamed('count', 'failing_mc') \
                            .orderBy('nVertices')
    failing_mc_counts = check_and_fill_missing_failing(doGen, failing_mc_counts)
    
    return failing_mc_counts

def get_mc_fake(df, doGen, resonance, era, subEra, shift=None):

    fake_mc_counts    = df.filter(
                                (F.col('probe_isTrkMatch') == True) & (F.col('probeSA_isTrkMatch') == True)) \
                                .groupBy('nVertices') \
                                .count() \
                                .withColumnRenamed('count', 'fake_mc') \
                                .orderBy(F.col('nVertices'))
    fake_mc_counts    = check_and_fill_missing_fake(doGen, fake_mc_counts)
    
    return fake_mc_counts    

def save_to_parquet(nVertices_dist, filename):
    
    nVertices_dist.write.mode("overwrite").parquet(filename)
 
def read_from_parquet(spark, filename):
    
    return spark.read.parquet(filename)

def get_weighted_dataframe(df, doGen, resonance, era, subEra, shift=None):

    global_filter               = ((F.col('probe_dxy') != -99.0) & (F.col('probe_dz') != -99.0))
    df                          = df.filter(global_filter)

    data_passing_filename       = 'data_passing.parquet'
    data_failing_filename       = 'data_failing.parquet'
    data_fake_filename          = 'data_fake.parquet'
    
    if not doGen:  # data
        # Get passing/failing/fake counts from dataFrame
        passing_data_counts     = get_data_passing( df, doGen, resonance, era, subEra, shift=None)
        failing_data_counts     = get_data_failing( df, doGen, resonance, era, subEra, shift=None)
        fake_data_counts        = get_data_fake(    df, doGen, resonance, era, subEra, shift=None)
        
        passing_data_counts.show(120)
        failing_data_counts.show(120)
        
        # Write passing/failing/fake counts to parquet file
        save_to_parquet(passing_data_counts,    data_passing_filename)
        save_to_parquet(failing_data_counts,    data_failing_filename)
        save_to_parquet(fake_data_counts,       data_fake_filename)

        weightedDF              = df.withColumn('weight', F.lit(1.0))

    else:   # mc
        print("MC elaboration")

        #Read passing/failing/fake counts from data parquet files
        passing_data_counts     = read_from_parquet(spark,  data_passing_filename)
        failing_data_counts     = read_from_parquet(spark,  data_failing_filename)
        fake_data_counts        = read_from_parquet(spark,  data_fake_filename)

        # Get passing/failing/fake counts from dataFrame
        passing_mc_counts     = get_mc_passing( df, doGen, resonance, era, subEra, shift=None)
        failing_mc_counts     = get_mc_failing( df, doGen, resonance, era, subEra, shift=None)
        fake_mc_counts        = get_mc_fake(    df, doGen, resonance, era, subEra, shift=None)
        
        passing_mc_counts.show(120)
        failing_mc_counts.show(120)
        
        # Calculate passing/failing/fake weights for mc (based on data counts)
        weights_expr_passing    = F.when(
                                        passing_mc_counts['passing_mc'] != 0, 
                                        passing_data_counts['passing_data'] / passing_mc_counts['passing_mc']
                                    ) \
                                   .otherwise(passing_data_counts['passing_data'])
        weights_expr_failing    = F.when(
                                        failing_mc_counts['failing_mc'] != 0, 
                                        failing_data_counts['failing_data'] / failing_mc_counts['failing_mc']
                                    ) \
                                   .otherwise(failing_data_counts['failing_data'])
        weights_expr_fake       = F.when(
                                        fake_mc_counts['fake_mc'] != 0, 
                                        fake_data_counts['fake_data'] / fake_mc_counts['fake_mc']
                                    ) \
                                   .otherwise(fake_data_counts['fake_data'])

        # Apply passing/failing/fake weights on mc dataframes
        weightedDF              = df.join(passing_data_counts,  'nVertices', 'left') \
                                    .join(failing_data_counts,  'nVertices', 'left') \
                                    .join(passing_mc_counts,    'nVertices', 'left') \
                                    .join(failing_mc_counts,    'nVertices', 'left') \
                                    .join(fake_data_counts,     'nVertices', 'left') \
                                    .join(fake_mc_counts,       'nVertices', 'left') \
                                    .withColumn(
                                        'weight', 
                                        F.when((F.col('probe_isTrkMatch') == True)  & (F.col('probeSA_isTrkMatch') == False),   weights_expr_passing)
                                         .when((F.col('probe_isTrkMatch') == False) & (F.col('probeSA_isTrkMatch') == False),   weights_expr_failing)
                                         .when((F.col('probe_isTrkMatch') == True)  & (F.col('probeSA_isTrkMatch') == True),    weights_expr_fake)
                                         .otherwise(F.lit(1.0))
                                    )

    weightedDF                  = weightedDF.withColumn('weight2', F.col('weight') * F.col('weight'))
    
    return weightedDF

def get_prescaled_dataframe(df, doGen, resonance, era, subEra):
  
  prescale_values, prescale_edges   = get_prescale(resonance, era, subEra)

  # build the weights (prescale for MC)
  if doGen:
    prescaleMap                     = {e: v for e, v in zip(prescale_edges[:-1], prescale_values)}
    mapping_expr                    = F.create_map([F.lit(x) for x in itertools.chain(*prescaleMap.items())])
    
    scaledDF                        = df.withColumn('prescale_weight',mapping_expr.getItem(F.floor('tag_pt')))
  else:
    scaledDF                        = df.withColumn('prescale_weight', F.lit(1.0))
  
  return scaledDF

def get_binned_dataframe(df, bin_name, variable_name, edges):
   '''
   Produces a dataframe with a new column `bin_name` corresponding
   to the variable `variable_name` binned with the given `edges`.
   '''
   splits                           = [-float('inf')]+list(edges)+[float('inf')]
   bucketizer                       = Bucketizer(
                                        splits      = splits, 
                                        inputCol    = variable_name, 
                                        outputCol   = bin_name
                                    )
   binnedDF                         = bucketizer.transform(df)
   
   return binnedDF


def get_selection_dataframe(df, selection_name, selection_func):
   '''
   Produces a new dataframe with a new column `selection_name`
   from the function `selection_func`.
   '''
   return df.withColumn(selection_name, selection_func(df))


# common names for the fit bins
# used to read the appropriate histogram for fitting
# and get the correct labels for saving things
def get_eff_name(num, denom):
   
    return 'NUM_{num}_DEN_{den}'.format(num=num, den=denom)


def get_bin_name(variableNames, index):
   
    return '_'.join(['{}_{}'.format(variableName, ind)
                    for variableName, ind in zip(variableNames, index)])


def get_variables_name(variableNames):
   
    return '_'.join(variableNames)


def get_full_name(num, denom, variableNames, index):
   
    eff_name                        = get_eff_name(num,             denom)
    bin_name                        = get_bin_name(variableNames,   index)
   
    return '{}_{}'.format(eff_name, bin_name)


def get_full_pass_name(num, denom, variableNames, index):
   
    full_name                       = get_full_name(num, denom, variableNames, index)
   
    return '{}_Pass'.format(full_name)


def get_full_fail_name(num, denom, variableNames, index):
    
    full_name                       = get_full_name(num, denom, variableNames, index)
   
    return '{}_Fail'.format(full_name)


def get_extended_eff_name(num, denom, variableNames):
    
    eff_name                        = get_eff_name(num, denom)
   
    variables_name                  = get_variables_name(variableNames)
   
    return '{}_{}'.format(eff_name, variables_name)

