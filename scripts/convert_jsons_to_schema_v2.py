#!/usr/bin/env python

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '..')
from correctionlib.schemav2 import Binning, Category, Correction, CorrectionSet

def build_uncertainties(sf):
    keys = ["nominal"]
    keys += ["up_syst", "down_syst"] if "syst" in sf else []
    keys += ["up_stat", "down_stat"] if "stat" in sf else []
    
    content = [sf["value"]]
    content += [sf["value"] + sf["syst"], sf["value"] - sf["syst"]] if "syst" in sf else []
    content += [sf["value"] + sf["stat"], sf["value"] - sf["stat"]] if "stat" in sf else []
    
    return Category.parse_obj({
        "nodetype": "category",
        "keys": keys,
        "content": content
    })


def parse_str(key, prefix="abseta:"):
    if not key.startswith(prefix + "["):
        raise ValueError(f"{key} missing prefix {prefix}")
    lo, hi = map(float, key[len(prefix + "["):-1].split(","))
    return lo, hi


def build_pts(sf):
    # Could happen that higher pt bin edge comes
    # lexicographically before lower one, so sort bins first
    sf_sorted_data = {}
    sf_sorted_hi = {}
    for binstr, data in sf.items():
        if not binstr.startswith("pt:["):
            raise ValueError
        lo, hi = map(float, binstr[len("pt:["):-1].split(","))
        sf_sorted_data[lo] = data
        sf_sorted_hi[lo] = hi

    edges = []
    content = []
    for i in sorted(sf_sorted_data):
        lo = i
        data = sf_sorted_data[i]
        if len(edges) == 0:
            edges.append(lo)
        if edges[-1] != lo:
            raise ValueError
        edges.append(sf_sorted_hi[lo])
        content.append(build_uncertainties(data))
    
    return Binning.parse_obj({
        "nodetype": "binning",
        "edges": edges,
        "content": content,
    })


def build_etas(sf):
    bins = [parse_str(s, "abseta:") for s in sf]
    edges = sorted(set(edge for bin in bins for edge in bin))
    content = [None] * (len(edges) - 1)
    for s, data in sf.items():
        lo, hi = parse_str(s, "abseta:")
        found = False
        for i, bin in enumerate(bins):
            if bin[0] >= lo and bin[1] <= hi:
                content[i] = build_pts(data)
                found = True

        
    return Binning.parse_obj({
        "nodetype": "binning",
        "edges": edges,
        "content": content,
    })

def build_content(sf, binning_array):

    bin_strings = {}
    binning = {}
    for element in binning_array:
        bin_edges = element['binning']
        bin_var = element['variable']
        binning[bin_var] = bin_edges
        bin_strings[bin_var] = []
        for idx in range(len(bin_edges)-1):
            bin_strings[bin_var] += [bin_var + ':[' + str(bin_edges[idx]) + ',' + str(bin_edges[idx+1]) + ']']
    
    # print(bin_strings)
    dimensions = len(binning)
    bin_vars = list(binning.keys())

    # iterate through the bin indices
    # this does nested for loops of the N-D binning (e.g. pt, eta)
    # binning starts at 1 (0 is underflow), same as ROOT
    indices = [list(range(1, len(binning[bin_var]))) for bin_var in bin_vars]

    def build_schema_recursively(dim, index):

        # If we reach recursion bottom, build and return the systematics node
        if dim == dimensions + 1:

            index_to_string_mapping = {}
            for d, bin_var in enumerate(bin_vars):
                index_to_string_mapping[bin_var] = bin_strings[bin_var][index[d]-1]

            # print('map:', index_to_string_mapping)

            def get_systematics(sf, keys):
                for key in keys.values():
                    sf = sf[key]
                return sf

            systematics = get_systematics(sf, index_to_string_mapping)

            keys, content = [], []
            for syst, value in systematics.items(): # all_systematics[index].items():
                keys.append(syst)
                content.append({"key": syst, "value": value}) 
            return Category.parse_obj({
                "nodetype": "category",
                "input": "systematics",
                "content": content
            })

        # If not, build a binning node
        edges = list(map(float, binning[bin_vars[dim-1]]))
        content = [build_schema_recursively(dim+1, tuple(list(index)[0:dim-1]+[i]+list(index)[dim:])) for i in indices[dim-1]]
        return Binning.parse_obj({
            "nodetype": "binning",
            "input": bin_vars[dim-1],
            "edges": edges,
            "flow": "error",
            "content": content,
        })

    content = build_schema_recursively(1, tuple([1] * dimensions))
    return content


import json, os

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

# # Load data
# if 'https://' in file_name:
#     import requests
#     sf = requests.get(file_name).json()
# else:
#     with open(file_name) as f:
#         sf = json.load(f)

all_corrections = []

for json_file in all_json_files:
    with open(json_file) as f:

        print('Processing ', json_file)
        
        sf = json.load(f)

        sf_name = list(sf.keys())[0]
        sf_description = sf_name
        sf_vars_string = list(sf[sf_name].keys())[0]

        binning_array = sf[sf_name][sf_vars_string].pop('binning')

        bin_vars = []
        for binning in binning_array:
            bin_vars.append(binning['variable'])

        inputs = [{"name": bin_var, "type": "real"} for bin_var in bin_vars]
        inputs += [{"name": "uncertainties", "type": "string"}]
        
        data = build_content(sf[sf_name][sf_vars_string], binning_array)
        # print(data)

        corr = Correction.parse_obj({
            "version": 1,
            "name": sf_name,
            "description": sf_description,
            "inputs": inputs,
            "output": {"name": "weight", "type": "real"},
            "data": data
        })

        all_corrections.append(corr)
# exit(0)

cset = CorrectionSet.parse_obj({
    "schema_version": 2,
    "corrections": all_corrections
})

# Write out converted json
# with open(os.path.splitext(file_name)[0]+'_schemaV2.json', "w") as fout:
with open('output' + '_schemaV2.json', "w") as fout:
    fout.write(cset.json(exclude_unset=True, indent=4))