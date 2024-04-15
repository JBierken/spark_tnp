#include <TFile.h>
#include <TH1F.h>

void renameHistogram(const char* fileName, const char* oldHistName, const char* newHistName) {
    // Apri il file ROOT in modalità di lettura/scrittura
    TFile* file = new TFile(fileName, "UPDATE");

    // Controlla se il file è stato aperto correttamente
    if (!file || file->IsZombie()) {
        std::cerr << "Errore nell'apertura del file " << fileName << std::endl;
        return;
    }

    // Estrai l'istogramma esistente dal file
    TH1F* oldHist = dynamic_cast<TH1F*>(file->Get(oldHistName));

    // Controlla se l'istogramma esiste nel file
    if (!oldHist) {
        std::cerr << "Errore: Istogramma " << oldHistName << " non trovato nel file " << fileName << std::endl;
        file->Close();
        return;
    }

    // Rinomina l'istogramma
    oldHist->SetName(newHistName);

    // Scrivi le modifiche nel file
    file->Write();

    // Chiudi il file
    file->Close();
}

int rename() {
    // Specifica il nome del file ROOT, il vecchio nome dell'istogramma e il nuovo nome dell'istogramma
    const char* fileName = "ScaleFactor.root";
    const char* oldHistName = "pileupweight";
    const char* newHistName = "pileup";

    // Chiama la funzione per rinominare l'istogramma nel file
    renameHistogram(fileName, oldHistName, newHistName);

    return 0;
}
