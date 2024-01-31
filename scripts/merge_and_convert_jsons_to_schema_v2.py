#!/usr/bin/env python

import sys
import json
import os
import math
import numpy as np
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '..')
from correctionlib.schemav2 import Binning, Category, Correction, CorrectionSet

# TODO: how do we want to report uncertainties? value and systs separately, or value +/- syst already?
# def build_uncertainties(sf):
#     keys = ["nominal"]
#     keys += ["up_syst", "down_syst"] if "syst" in sf else []
#     keys += ["up_stat", "down_stat"] if "stat" in sf else []
    
#     content = [sf["value"]]
#     content += [sf["value"] + sf["syst"], sf["value"] - sf["syst"]] if "syst" in sf else []
#     content += [sf["value"] + sf["stat"], sf["value"] - sf["stat"]] if "stat" in sf else []
    
#     return Category.parse_obj({
#         "nodetype": "category",
#         "keys": keys,
#         "content": content
#     })



def build_content(sf, sf2, binning_array, binning_array2):

    bin_strings = {}
    binning = {}
    for element in binning_array:
        bin_edges = element['binning']
        bin_var = element['variable']
        binning[bin_var] = bin_edges
        bin_strings[bin_var] = []
        for idx in range(len(bin_edges)-1):
            bin_strings[bin_var] += [bin_var + ':[' + str(bin_edges[idx]) + ',' + str(bin_edges[idx+1]) + ']']

    bin_strings2 = {}
    binning2 = {}

    for element in binning_array2:
        bin_edges = element['binning']
        bin_var = element['variable'].split("2")[0]
        binning2[bin_var] = bin_edges
        bin_strings2[bin_var] = []
        for idx in range(len(bin_edges)-1):
            bin_strings2[bin_var] += [bin_var + ':[' + str(bin_edges[idx]) + ',' + str(bin_edges[idx+1]) + ']']


    dimensions = len(binning)
    dimensions2 = len(binning2)
    bin_vars = list(binning.keys())
    bin_vars2 = list(binning2.keys())

    # iterate through the bin indices
    # this does nested for loops of the N-D binning (e.g. pt, eta)
    # binning starts at 1 (0 is underflow), same as ROOT
    indices = [list(range(1, len(binning[bin_var]))) for bin_var in bin_vars]
    indices2 = [list(range(1, len(binning2[bin_var]))) for bin_var in bin_vars2]

    def build_schema_recursively(dim, index, dimensions, bin_vars, bin_strings, binning, sf, indices):

        # If we reach recursion bottom, build and return the systematics node
        if dim == dimensions + 1:

            index_to_string_mapping = {}
            for d, bin_var in enumerate(bin_vars):
                index_to_string_mapping[bin_var] = bin_strings[bin_var][index[d]-1]

            def get_systematics(sf, keys):
                for key in keys.values():
                    if key in sf.keys():
                    	sf = sf[key]
                    else:
                        key = key.replace(":", "2:")
                        sf = sf[key]
                return sf

            systematics = get_systematics(sf, index_to_string_mapping)

            if ("stat" in systematics and "syst" in systematics) and ("comb_syst" not in systematics):

                comb_syst = systematics["value"]*np.sqrt((systematics["stat"]/systematics["value"])*(systematics["stat"]/systematics["value"]) +
                                                         (systematics["syst"]/systematics["value"])*(systematics["syst"]/systematics["value"]))

                systematics['systup']   = systematics["value"] + comb_syst
                systematics['systdown'] = systematics["value"] - comb_syst

            keys, content = [], []
            for syst, value in systematics.items():
                keys.append(syst)
                syst = syst if syst != "value" else "nominal"
                content.append({"key": syst, "value": value}) 
            return Category.parse_obj({
                "nodetype": "category",
                "input": "scale_factors",
                "content": content
            })

        # If not, build a binning node
        edges = list(map(float, binning[bin_vars[dim-1]]))
        if "pt" == bin_vars[dim-1] or "p" == bin_vars[dim-1]:
            edges[-1] = math.inf if edges[-1]<9999.9 else edges[-1]
        content = [build_schema_recursively(dim+1, tuple(list(index)[0:dim-1]+[i]+list(index)[dim:]), dimensions, bin_vars, bin_strings, binning, sf, indices) for i in indices[dim-1]]
        #return Binning.parse_obj({
        #    "nodetype": "binning",
        #    "input": bin_vars[dim-1],
        #    "edges": edges,
        #    "flow": "error",
        #    "content": content,
        #})

        return content
    content = build_schema_recursively(1, tuple([1] * (dimensions-1)), dimensions, bin_vars, bin_strings, binning, sf, indices)


    nodes = []
    for i in range(0,len(indices[0])):
        if "pt" == bin_vars[1] or "p" == bin_vars[1]:
            binning[bin_vars[1]][-1] = math.inf if binning[bin_vars[1]][-1]<9999.9 else binning[bin_vars[1]][-1]

        sub_content = content[i*len(binning[bin_vars[1]]):(i+1)*len(binning[bin_vars[1]])]
        nodes.append(
            Binning.parse_obj({
                "nodetype": "binning",
                "input": bin_vars[1],
                "edges": binning[bin_vars[1]],
                "flow": "error",
                "content": content[i],
         })
    )
    content = build_schema_recursively(1, tuple([1] * (dimensions2-1)), dimensions2, bin_vars2, bin_strings2, binning2, sf2, indices2)
    edges = binning[bin_vars[0]] + [binning2[bin_vars[0]][1]]
    for i in range(0,len(indices2[0])):
        if "pt" == bin_vars2[1] or "p" == bin_vars2[1]:
            binning2[bin_vars2[1]][-1] = math.inf if binning2[bin_vars2[1]][-1]<9999.9 else binning2[bin_vars2[1]][-1]

        nodes.append(
            Binning.parse_obj({
                "nodetype": "binning",
                "input": bin_vars2[1],
                "edges": binning2[bin_vars2[1]],
                "flow": "error",
                "content": content[i],
         })
    )

    return Binning.parse_obj({
        "nodetype": "binning",
        "input": bin_vars[0],
        "edges": edges,
        "flow": "error",
        "content": nodes,
    })



if __name__ != "__main__" or len(sys.argv) < 2:
    print(f'Please run this script as {sys.argv[0]} dir_with_json_dirs (output of spark_tnp)')
    sys.exit(1)
else:
    rootdir = sys.argv[1]

all_json_files = []
for root, subdirs, files in os.walk(rootdir):
    for subdir in subdirs:
        for subroot, subsubdirs, subfiles in os.walk(os.path.join(rootdir, subdir)):
            json_files = [os.path.join(subroot, subfile) for subfile in subfiles if subfile.endswith('.json') and 'schemaV1' not in subfile]
            all_json_files += json_files

all_corrections = []

for i in range(0,len(all_json_files),2):
    with open(all_json_files[i]) as f:
        print('Processing ', all_json_files[i])
        print('Processing ', all_json_files[i+1])
 
        f2 = open(all_json_files[i+1])
       
        sf = json.load(f)
        sf2 = json.load(f2)
        sf_name = list(sf.keys())[0]
        sf_description = sf_name
        sf_vars_string = list(sf[sf_name].keys())[0]

        binning_array = sf[sf_name][sf_vars_string].pop('binning')

        sf_name2 = list(sf2.keys())[0]
        sf_description2 = sf_name2
        sf_vars_string2 = list(sf2[sf_name2].keys())[0]
        binning_array2 = sf2[sf_name2][sf_vars_string2].pop('binning')
   
        bin_vars = []
        for binning in binning_array:
            bin_vars.append(binning['variable'])

        inputs = [{"name": bin_var, "type": "real", "description": "Probe " + bin_var} for bin_var in bin_vars]
        inputs += [{"name": "scale_factors", "type": "string", "description": "Choose nominal scale factor or one of the uncertainties"}]
        
        data = build_content(sf[sf_name][sf_vars_string],sf2[sf_name2][sf_vars_string2], binning_array, binning_array2)

        corr = Correction.parse_obj({
            "version": 1,
            "name": sf_name,
            "description": sf_description,
            "inputs": inputs,
            "output": {"name": "weight", "type": "real", "description": "Output scale factor (nominal) or uncertainty"},
            "data": data
        })

        all_corrections.append(corr)

cset = CorrectionSet.parse_obj({
    "schema_version": 2,
    "description": """This json file contains different scale factors centrally derived by the Muon POG. Corrections are supplied for various reconstructions, working points, IDs, isolation cuts, and resonances (Z or JPsi). In general, the scale factors are factorized into ID*ISO*HLT, and the names follow the next convention: NUM_{NumeratorNAME}_DEN_{DenominatorNAME} where 'NumeratorNAME' can be 'TightID' and denominator can be 'TrackerMuons', for example. Nominal scale factors and uncertainties are provided. 'nominal', 'stat', 'syst', 'systup', and 'systdown' are provided for all the cases. Additional systematic uncertainties may be included such as 'massBin', 'AltSig', etc. Please note the different meanings of the input labels.
 'nominal'  : Nominal central scale factor value
 'systup'   : Combined statistical+systematic up boundary (Consistent with XPOG format)
 'systdown' : Combined statistical+systematic down boundary (Consistent with XPOG format)
 'stat'     : Statistical uncertainty
 'syst'     : Systematic uncertainty
""",
    "corrections": all_corrections
})

# Write out converted json
# with open(os.path.splitext(file_name)[0]+'_schemaV2.json', "w") as fout:
with open('output' + '_schemaV2.json', "w") as fout:
    fout.write(cset.json(exclude_unset=True, indent=4))
