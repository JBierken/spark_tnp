#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>

void createHistogram(const char* inputFileName, const char* outputFileName) {

    TFile *inputFile = new TFile(inputFileName, "READ");
    if (!inputFile || inputFile->IsZombie()) {
        std::cerr << "Errore nell'apertura del file di input: " << inputFileName << std::endl;
        return;
    }

    // get the tree
    TTree *tree = dynamic_cast<TTree*>(inputFile->Get("muon/StandAloneEvents"));
    if (!tree) {
        std::cerr << "Tree 'StandAloneEvents' non trovato nel file di input." << std::endl;
        inputFile->Close();
        return;
    }

    if (!tree->GetBranch("nVertices")) {
        std::cerr << "Branch 'nVertices' non trovato nel tree 'StandAloneEvents'." << std::endl;
        inputFile->Close();
        return;
    }

    // histo "pileup"
    TH1F *histogram = new TH1F("pileup", "Distribuzione di nVertices", 100, 0, 100); 
    tree->Draw("nVertices>>pileup");

    // output file
    TFile *outputFile = new TFile(outputFileName, "RECREATE");
    if (!outputFile || outputFile->IsZombie()) {
        std::cerr << "Errore nell'apertura del file di output: " << outputFileName << std::endl;
        inputFile->Close();
        return;
    }

 
    histogram->Write();

    inputFile->Close();
    outputFile->Close();

    std::cout << "Operazione completata. Istogramma salvato in: " << outputFileName << std::endl;
}

void get_nVertices() {
    createHistogram("/eos/user/m/mibarbie/TnP_ntuples_Run2023_AOD_isOnlySeeded/muon/Z/Run2023/AOD/DY_madgraph/merged.root", "/afs/cern.ch/user/m/mibarbie/spark_tnp/pileup/mc/mc_nVertices.root");
}
