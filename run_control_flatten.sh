#!/bin/bash

# commands array
commands=(
   # "./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_nVertices.json --baseDir /eos/user/m/mibarbie/2023_nVertices"
   # "./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_tag_dxy.json --baseDir /eos/user/m/mibarbie/2023_tag_dxy"
   # "./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_tag_dz.json --baseDir /eos/user/m/mibarbie/2023_tag_dz"
   # "./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_probe_dxy.json --baseDir /eos/user/m/mibarbie/2023_probe_dxy"
   # "./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_probe_dz.json --baseDir /eos/user/m/mibarbie/2023_probe_dz"
   # "./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_probe_trackerLayers.json --baseDir /eos/user/m/mibarbie/2023_probe_trackerLayers"
   # "./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_probe_pixelLayers.json --baseDir /eos/user/m/mibarbie/2023_probe_pixelLayers"
   
    "./tnp_fitter.py flatten muon standAloneMuons Z Run2022 configs/temp_nVertices.json --baseDir /eos/user/m/mibarbie/2022_nVertices"
    "./tnp_fitter.py flatten muon standAloneMuons Z Run2022 configs/temp_tag_dxy.json --baseDir /eos/user/m/mibarbie/2022_tag_dxy"
    "./tnp_fitter.py flatten muon standAloneMuons Z Run2022 configs/temp_tag_dz.json --baseDir /eos/user/m/mibarbie/2022_tag_dz"
    "./tnp_fitter.py flatten muon standAloneMuons Z Run2022 configs/temp_probe_dxy.json --baseDir /eos/user/m/mibarbie/2022_probe_dxy"
    "./tnp_fitter.py flatten muon standAloneMuons Z Run2022 configs/temp_probe_dz.json --baseDir /eos/user/m/mibarbie/2022_probe_dz"
    "./tnp_fitter.py flatten muon standAloneMuons Z Run2022 configs/temp_probe_trackerLayers.json --baseDir /eos/user/m/mibarbie/2022_probe_trackerLayers"
    "./tnp_fitter.py flatten muon standAloneMuons Z Run2022 configs/temp_probe_pixelLayers.json --baseDir /eos/user/m/mibarbie/2022_probe_pixelLayers"
)

for command in "${commands[@]}"
do
    echo "Executing: $command"
    $command
    echo "---------------------------------------------"
done

echo "Completed!"
