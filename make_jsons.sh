#!/bin/bash
#!/usr/bin/env python3

variables=("probe_pixelLayers" "probe_trackerLayers")
labels=("probe pixel layers" "probe tracker layers") 

for ((i=0; i<${#variables[@]}; ++i)); do
    # Copia il file di input in un file temporaneo
    cd configs
    cp 2023_pt_reduced.json temp_${variables[i]}.json
    
    # Sostituisci "pair_mass_corr" con il nome della variabile corrente
    sed -i "33s/pair_mass_corr/${variables[i]}/g" temp_${variables[i]}.json
    sed -i "34s/pair_mass_corr/${variables[i]}/g" temp_${variables[i]}.json

    # Sostituisci "m(#mu#mu) (GeV)" con l'etichetta corrente
    sed -i "s/m(\\#mu\\#mu) (GeV)/${labels[i]}/g" temp_${variables[i]}.json

    cd ..
    #pwd
    #source env.sh
    #flatten_command="./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_${variables[i]}.json --baseDir /eos/user/m/mibarbie/2023_${variables[i]}"
    #echo "Eseguo: $flatten_command"
    #./tnp_fitter.py flatten muon standAloneMuons Z Run2023 configs/temp_${variables[i]}.json --baseDir /eos/user/m/mibarbie/2023_${variables[i]}

    # Rimuovi il file temporaneo dopo aver eseguito il comando
    #rm config/temp_${variables[i]}_${labels[i]}.json
done
