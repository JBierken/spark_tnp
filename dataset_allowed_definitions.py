# allowed choices
def get_allowed_resonances():
    
    resonances = [
        'Z',
        'JPsi'
    ]
    return resonances


def get_allowed_eras(resonance):

    eras = {
        'Z': [
            # ultra legacy
            'Run2016_UL_HIPM',
            'Run2016_UL',
            'Run2017_UL',
            'Run2018_UL',
            # Double muon PD
            'Run2016_UL_HIPM_DM',
            'Run2016_UL_DM',
            'Run2017_UL_DM',
            'Run2018_UL_DM',
            # rereco (i.e. legacy)
            'Run2016',
            'Run2017',
            'Run2018',
            # Run 2022
            'Run2022',
            'Run2022_EE',
            # Run2023
            'Run2023'
        ],
        'JPsi': [
            # heavy ion
            'Run2016_HI_pPb_8TeV',
            # ultra legacy
            'Run2016_UL_HIPM',
            'Run2016_UL',
            'Run2017_UL',
            'Run2018_UL',
            # rereco (i.e. legacy)
            'Run2016',
            'Run2017',
            'Run2018',
            # Run 2022
            'Run2022',
            'Run2022_EE',
            # Run2023
            'Run2023',
            'Run2023_BPix'
        ],
    }
    return eras.get(resonance, [])


def get_allowed_sub_eras(resonance, era):
    
    subEras = {
        'Z': {
            # ultra legacy
            'Run2016_UL_HIPM': ['Run2016_UL_HIPM'] + [
                f'Run2016{b}' for b in 'BCDEF']+['DY_powheg', 'DY_madgraph'],
            'Run2016_UL': ['Run2016_UL'] + [
                f'Run2016{b}' for b in 'FGH']+['DY_powheg', 'DY_madgraph'],
            'Run2017_UL': ['Run2017_UL'] + [
                f'Run2017{b}' for b in 'BCDEF']+['DY_powheg', 'DY_madgraph'],
            'Run2018_UL': ['Run2018_UL'] + [
                f'Run2018{b}' for b in 'ABCD']+['DY_powheg', 'DY_madgraph'],

            # Double muon PD
            'Run2016_UL_HIPM_DM': ['Run2016_UL_HIPM_DM'] + [
                f'Run2016{b}' for b in 'BCDEF']+['DY_madgraph'],
            'Run2016_UL_DM': ['Run2016_UL_DM'] + [
                f'Run2016{b}' for b in 'FGH']+['DY_madgraph'],
            'Run2017_UL_DM': ['Run2017_UL_DM'] + [
                f'Run2017{b}' for b in 'BCDEF']+['DY_madgraph'],
            'Run2018_UL_DM': ['Run2018_UL_DM'] + [
                f'Run2018{b}' for b in 'ABCD']+['DY_madgraph'],
            # rereco (i.e. legacy)
            'Run2016': ['Run2016'] + [
               f'Run2016{b}' for b in 'BCDEFGH']+['DY_madgraph'],
            'Run2017': ['Run2017'] + [
               f'Run2017{b}' for b in 'BCDEF']+['DY_madgraph'],
            'Run2018': ['Run2018'] + [
               f'Run2018{b}' for b in 'ABCD']+['DY_madgraph'],
            # Run2022
            'Run2022': ['Run2022'] + [
               f'Run2022{b}' for b in 'BCD']+['DY_madgraph','DY_amcatnlo','DY_MassBinned',
                                              'DY_Boosted_PT40to100_1J','DY_Boosted_PT100to200_1J','DY_Boosted_PT200to400_1J','DY_Boosted_PT400to600_1J','DY_Boosted_PT600_1J',
                                              'DY_Boosted_PT40to100_2J','DY_Boosted_PT100to200_2J','DY_Boosted_PT200to400_2J','DY_Boosted_PT400to600_2J','DY_Boosted_PT600_2J'],
            'Run2022_EE': ['Run2022_EE'] + [
               f'Run2022{b}' for b in 'EFG']+['DY_madgraph','DY_amcatnlo','DY_MassBinned',
                                              'DY_Boosted_PT40to100_1J','DY_Boosted_PT100to200_1J','DY_Boosted_PT200to400_1J','DY_Boosted_PT400to600_1J','DY_Boosted_PT600_1J',
                                              'DY_Boosted_PT40to100_2J','DY_Boosted_PT100to200_2J','DY_Boosted_PT200to400_2J','DY_Boosted_PT400to600_2J','DY_Boosted_PT600_2J'],
            # Run2023
            'Run2023': ['Run2023'] + [
               f'Run2023{b}' for b in 'BC']+['DY_madgraph','DY_amcatnlo','DY_MassBinned',
                                             'DY_Boosted_PT40to100_1J','DY_Boosted_PT100to200_1J','DY_Boosted_PT200to400_1J','DY_Boosted_PT400to600_1J','DY_Boosted_PT600_1J',
                                             'DY_Boosted_PT40to100_2J','DY_Boosted_PT100to200_2J','DY_Boosted_PT200to400_2J','DY_Boosted_PT400to600_2J','DY_Boosted_PT600_2J'],
            'Run2023_BPix': ['Run2023'] + [
               f'Run2023{b}' for b in 'D']+['DY_madgraph','DY_amcatnlo','DY_MassBinned',
                                            'DY_Boosted_PT40to100_1J','DY_Boosted_PT100to200_1J','DY_Boosted_PT200to400_1J','DY_Boosted_PT400to600_1J','DY_Boosted_PT600_1J',
                                            'DY_Boosted_PT40to100_2J','DY_Boosted_PT100to200_2J','DY_Boosted_PT200to400_2J','DY_Boosted_PT400to600_2J','DY_Boosted_PT600_2J'],
        },
        'JPsi': {
            # ultra legacy
            'Run2016_UL_HIPM': ['Run2016_UL_HIPM'] + [
                f'Run2016{b}' for b in 'BCDEF']+['JPsi_pythia8'],
            'Run2016_UL': ['Run2016_UL'] + [
                f'Run2016{b}' for b in 'FGH']+['JPsi_pythia8'],
            'Run2017_UL': ['Run2017_UL'] + [
                f'Run2017{b}' for b in 'BCDEF']+['JPsi_pythia8'],
            'Run2018_UL': ['Run2018_UL'] + [
                f'Run2018{b}' for b in 'ABCD']+['JPsi_pythia8'],
            # Run2022
            'Run2022': ['Run2022'] + [
                f'Run2022{b}' for b in ['B','C', 'D']]+['JPsi_pythia8'],
            'Run2022_EE': ['Run2022_EE'] + [
                f'Run2022{b}' for b in ['E','F','G']]+['JPsi_pythia8'],
            # Run2023
            'Run2023': ['Run2023'] + [
                f'Run2023{b}' for b in ['B','C']]+['JPsi_pythia8'],
            'Run2023_BPix': ['Run2023'] + [
                f'Run2023{b}' for b in ['D']]+['JPsi_pythia8'],
            # heavy ion
            'Run2016_HI_pPb_8TeV': ['Run2016'],
            # rereco (i.e. legacy)
            'Run2016': ['Run2016'] + [
               f'Run2016{b}' for b in 'BCDEFGH']+['JPsi_pythia8'],
            'Run2017': ['Run2017'] + [
               f'Run2017{b}' for b in 'BCDEF']+['JPsi_pythia8'],
            'Run2018': ['Run2018'] + [
               f'Run2018{b}' for b in 'ABCD']+['JPsi_pythia8'],
        },
    }
    return subEras.get(resonance, {}).get(era, [])


def get_data_mc_sub_eras(resonance, era):
    eraMap = {
        # Keys for DATA, MC, MCAlt
        'Z': {
            # ultra legacy
            'Run2016_UL_HIPM': ['Run2016_UL_HIPM', 'DY_powheg', 'DY_madgraph'],
            'Run2016_UL': ['Run2016_UL', 'DY_powheg', 'DY_madgraph'],
            'Run2017_UL': ['Run2017_UL', 'DY_powheg', 'DY_madgraph'],
            'Run2018_UL': ["Run2018_UL", 'DY_powheg', 'DY_madgraph'],
            # Double muon PD
            'Run2016_UL_HIPM_DM': ['Run2016_UL_HIPM_DM', 'DY_madgraph', None],
            'Run2016_UL_DM': ['Run2016_UL_DM', 'DY_madgraph', None],
            'Run2017_UL_DM': ['Run2017_UL_DM', 'DY_madgraph', None],
            'Run2018_UL_DM': ['Run2018_UL_DM', 'DY_madgraph', None],
            # rereco (i.e. legacy)
            'Run2016': ['Run2016', 'DY_madgraph', None],
            'Run2017': ['Run2017', 'DY_madgraph', None],
            'Run2018': ['Run2018', 'DY_madgraph', None],
            # Run2022
            'Run2022': ['Run2022', 'DY_madgraph', 'DY_amcatnlo'],
            'Run2022_EE': ['Run2022_EE', 'DY_madgraph', 'DY_amcatnlo'],
            'Run2023': ['Run2023', 'DY_madgraph', 'DY_amcatnlo'],
            'Run2023_BPix': ['Run2023', 'DY_madgraph', 'DY_amcatnlo'],
        },
        'JPsi': {
            # ultra legacy
            'Run2016_UL_HIPM': ['Run2016_UL_HIPM', 'JPsi_pythia8', None],
            'Run2016_UL': ['Run2016_UL', 'JPsi_pythia8', None],
            'Run2017_UL': ['Run2017_UL', 'JPsi_pythia8', None],
            'Run2018_UL': ['Run2018_UL', 'JPsi_pythia8', None],
            # heavy ion
            'Run2016_HI_pPb_8TeV': ['Run2016', None, None],
            # rereco (i.e. legacy)
            'Run2016': ['Run2016', 'JPsi_pythia8', None],
            'Run2017': ['Run2017', 'JPsi_pythia8', None],
            'Run2018': ['Run2018', 'JPsi_pythia8', None],
            # Run2022
            'Run2022'   : ['Run2022', 'JPsi_pythia8', None],
            'Run2022_EE': ['Run2022', 'JPsi_pythia8', None],
            # Run2023
            'Run2023'     : ['Run2023', 'JPsi_pythia8', None],
            'Run2023_BPix': ['Run2023', 'JPsi_pythia8', None],
        },
    }
    return eraMap.get(resonance, {}).get(era, [None, None, None])

