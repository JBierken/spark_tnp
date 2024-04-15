#include <TFile.h>
#include <TH1F.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TGaxis.h>
#include <TStyle.h>
#include <TFile.h>
#include <TH1F.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TGaxis.h>
#include <TStyle.h>

#include <iostream>
using namespace std;

struct VariableInfo {
    const char* variable;
    const char* label;
};

void overlayHistograms(const char* dataFile, const char* mcFile, const char* outputFile, const char* label) {
    // root files
    TFile *dataRootFile = new TFile(dataFile, "READ");
    TFile *mcRootFile = new TFile(mcFile, "READ");

    // read
    TH1F *dataHistogram_pass = (TH1F*)dataRootFile->Get("NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_1_eta_onebin_1_phi_onebin_1_Pass;1");
    TH1F *mcHistogram_pass = (TH1F*)mcRootFile->Get("NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_1_eta_onebin_1_phi_onebin_1_Pass;1");
    TH1F *dataHistogram_fail = (TH1F*)dataRootFile->Get("NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_1_eta_onebin_1_phi_onebin_1_Fail;1");
    TH1F *mcHistogram_fail = (TH1F*)mcRootFile->Get("NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_1_eta_onebin_1_phi_onebin_1_Fail;1");

    //TH1F *dataHistogram = (TH1F*)dataRootFile->Get("IstoSomma");
    //TH1F *mcHistogram = (TH1F*)mcRootFile->Get("IstoSomma");

    // norm
    //dataHistogram->Scale(1.0 / dataHistogram->Integral());
    //mcHistogram->Scale(1.0 / mcHistogram->Integral());

    TCanvas *canvas = new TCanvas("overlayCanvas", "Overlay Histograms", 1500, 800);
    canvas->Divide(2, 2); 
    canvas->GetPad(1)->SetPad(0, 0.25, 0.5, 1);  
    canvas->GetPad(2)->SetPad(0, 0, 0.5, 0.25);
    canvas->GetPad(3)->SetPad(0.5, 0.25, 1, 1);
    canvas->GetPad(4)->SetPad(0.5, 0, 1, 0.25);

    canvas->cd(1); 
    //gStyle->SetOptStat(0);

    mcHistogram_pass->Draw("hist");
    mcHistogram_pass->SetLineColor(kRed);
    mcHistogram_pass->GetXaxis()->SetTitle(label);
    mcHistogram_pass->GetYaxis()->SetTitle("Entries");
    //mcHistogram_pass->Rebin(6);
    TGaxis::SetMaxDigits(3);   // expo 
    dataHistogram_pass->SetLineColor(kBlue);
    dataHistogram_pass->SetLineColor(kBlack);
    dataHistogram_pass->SetMarkerStyle(20);
    dataHistogram_pass->SetMarkerSize(1.0);
    //dataHistogram_pass->Rebin(6);
    dataHistogram_pass->Draw("P SAME");

    // text box
    TLatex *text_pass = new TLatex();
    text_pass->SetNDC(); 
    text_pass->SetTextSize(0.03);
    text_pass->DrawLatex(0.65, 0.70, "25 GeV < p_{T} < 60 GeV");
    text_pass->DrawLatex(0.65, 0.65, "-1.5 < #eta < -0.2");
    text_pass->DrawLatex(0.65, 0.60, "-1.2 < #phi < -0.8");
    text_pass->SetTextSize(0.05);
    text_pass->DrawLatex(0.45, 0.93, "Passing");

    // legend
    TLegend *legend_pass = new TLegend(0.75, 0.75, 0.85, 0.85);
    legend_pass->AddEntry(dataHistogram_pass, "Data", "p");
    legend_pass->AddEntry(mcHistogram_pass, "MC", "l");
    legend_pass->SetTextSize(0.03);
    legend_pass->SetTextAlign(22);
    legend_pass->Draw();

    // ratio plot
    canvas->cd(2);
    TH1F *ratioHistogram_pass = (TH1F*)dataHistogram_pass->Clone("ratioHistogram_pass");
    ratioHistogram_pass->Divide(mcHistogram_pass);
    ratioHistogram_pass->SetLineColor(kBlack);
    ratioHistogram_pass->SetMarkerStyle(20);
    ratioHistogram_pass->SetMarkerSize(0.8);
    ratioHistogram_pass->GetYaxis()->SetTitle("Data/MC");
    ratioHistogram_pass->GetYaxis()->SetTitleSize(0.1);
    ratioHistogram_pass->GetYaxis()->SetTitleOffset(0.4);
    ratioHistogram_pass->GetYaxis()->SetLabelSize(0.08);
    ratioHistogram_pass->GetXaxis()->SetTitleSize(0.1);
    ratioHistogram_pass->GetXaxis()->SetTitleOffset(0.9);
    ratioHistogram_pass->GetXaxis()->SetLabelSize(0.08);
    ratioHistogram_pass->SetMinimum(0.0);
    ratioHistogram_pass->SetMaximum(3.0);

    ratioHistogram_pass->Draw("ep");

        // Add a dashed horizontal line at y=1
    TLine *lineAtOne_pass = new TLine(ratioHistogram_pass->GetXaxis()->GetXmin(), 1, ratioHistogram_pass->GetXaxis()->GetXmax(), 1);
    lineAtOne_pass->SetLineStyle(2);  // Set line style to dashed
    lineAtOne_pass->SetLineColor(kBlack);
    lineAtOne_pass->Draw("SAME");

    canvas->cd(3); 
    gStyle->SetOptStat(0);

    mcHistogram_fail->Draw("hist");
    mcHistogram_fail->SetLineColor(kRed);
    mcHistogram_fail->GetXaxis()->SetTitle(label);
    mcHistogram_fail->GetYaxis()->SetTitle("Entries");
    //mcHistogram_fail->Rebin(6);
    TGaxis::SetMaxDigits(3);   // expo 
    dataHistogram_fail->SetLineColor(kBlue);
    dataHistogram_fail->SetLineColor(kBlack);
    dataHistogram_fail->SetMarkerStyle(20);
    dataHistogram_fail->SetMarkerSize(1.0);
    //dataHistogram_fail->Rebin(6);
    dataHistogram_fail->Draw("P SAME");

    // text box
    TLatex *text_fail = new TLatex();
    text_fail->SetNDC(); 
    text_fail->SetTextSize(0.03);
    text_fail->DrawLatex(0.65, 0.70, "25 GeV < p_{T} < 60 GeV");
    text_fail->DrawLatex(0.65, 0.65, "-1.5 < #eta < -0.2");
    text_fail->DrawLatex(0.65, 0.60, "-1.2 < #phi < -0.8");
    text_pass->SetTextSize(0.05);
    text_pass->DrawLatex(0.45, 0.93, "Failing");


    // legend
    TLegend *legend_fail = new TLegend(0.75, 0.75, 0.85, 0.85);
    legend_fail->AddEntry(dataHistogram_pass, "Data", "p");
    legend_fail->AddEntry(mcHistogram_pass, "MC", "l");
    legend_fail->SetTextSize(0.03);
    legend_fail->SetTextAlign(22);
    legend_fail->Draw();

    // ratio plot
    canvas->cd(4);
    TH1F *ratioHistogram_fail = (TH1F*)dataHistogram_fail->Clone("ratioHistogram_fail");
    ratioHistogram_fail->Divide(mcHistogram_fail);
    ratioHistogram_fail->SetLineColor(kBlack);
    ratioHistogram_fail->SetMarkerStyle(20);
    ratioHistogram_fail->SetMarkerSize(0.8);
    ratioHistogram_fail->GetYaxis()->SetTitle("Data/MC");
    ratioHistogram_fail->GetYaxis()->SetTitleSize(0.1);
    ratioHistogram_fail->GetYaxis()->SetTitleOffset(0.4);
    ratioHistogram_fail->GetYaxis()->SetLabelSize(0.08);
    ratioHistogram_fail->GetXaxis()->SetTitleSize(0.1);
    ratioHistogram_fail->GetXaxis()->SetTitleOffset(0.9);
    ratioHistogram_fail->GetXaxis()->SetLabelSize(0.08);
    ratioHistogram_fail->SetMinimum(0.0);
    ratioHistogram_fail->SetMaximum(3.0);

    ratioHistogram_fail->Draw("ep");

        // Add a dashed horizontal line at y=1
    TLine *lineAtOne_fail = new TLine(ratioHistogram_fail->GetXaxis()->GetXmin(), 1, ratioHistogram_fail->GetXaxis()->GetXmax(), 1);
    lineAtOne_fail->SetLineStyle(2);  // Set line style to dashed
    lineAtOne_fail->SetLineColor(kBlack);
    lineAtOne_fail->Draw("SAME");

    // save
    canvas->SaveAs(outputFile);

     double dataTotalEntries_pass = dataHistogram_pass->GetEntries();
    double mcTotalEntries_pass = mcHistogram_pass->GetEntries();

    double dataTotalEntries_fail = dataHistogram_fail->GetEntries();
    double mcTotalEntries_fail = mcHistogram_fail->GetEntries();

    cout << "Total number of entries (passing):" << endl;
    cout << "Data passing: " << dataTotalEntries_pass << endl;
    cout << "MC passing: " << mcTotalEntries_pass << endl;

    cout << "Total number of entries (failing):" << endl;
    cout << "Data failing " << dataTotalEntries_fail << endl;
    cout << "MC failing: " << mcTotalEntries_fail << endl;

    dataRootFile->Close();
    mcRootFile->Close();
}

//void make_single_plot(const VariableInfo& variableInfo) {
//    string dataFile = "/eos/user/m/mibarbie/2023_" + string(variableInfo.variable) + "/flat/muon/standAloneMuons/Z/Run2023/Run2023/Nominal/NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_eta_onebin_phi_onebin.root";
//    string mcFile = "/eos/user/m/mibarbie/2023_" + string(variableInfo.variable) + "/flat/muon/standAloneMuons/Z/Run2023/DY_madgraph/Nominal/NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_eta_onebin_phi_onebin.root";
//    string outputFile = "/afs/cern.ch/user/m/mibarbie/spark_tnp/2023_" + string(variableInfo.variable) + ".png";
//
//    overlayHistograms(dataFile.c_str(), mcFile.c_str(), outputFile.c_str(), variableInfo.label);
//}


void make_single_plot(const VariableInfo& variableInfo) {
    string dataFile = "/eos/user/m/mibarbie/2022_" + string(variableInfo.variable) + "/flat/muon/standAloneMuons/Z/Run2022/Run2022/Nominal/NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_eta_onebin_phi_onebin.root";
    string mcFile = "/eos/user/m/mibarbie/2022_" + string(variableInfo.variable) + "/flat/muon/standAloneMuons/Z/Run2022/DY_madgraph/Nominal/NUM_SAMatched_DEN_StandAloneMuons_pt_onebin_eta_onebin_phi_onebin.root";
    string outputFile = "/afs/cern.ch/user/m/mibarbie/spark_tnp/2022_" + string(variableInfo.variable) + ".png";

    overlayHistograms(dataFile.c_str(), mcFile.c_str(), outputFile.c_str(), variableInfo.label);
}

int make_control_plots() {
    VariableInfo variableInfo[] = {

        //{"nVertices", "N vertices"},
        {"tag_dxy", "tag dxy"},
        {"tag_dz", "tag dz"},
        {"probe_dxy", "probe dxy"},
        {"probe_dz", "probe dz"},
        {"probe_trackerLayers", "probe tracker layers"},
        {"probe_pixelLayers", "probe pixel layers"}

    };

    for (const VariableInfo& varInfo : variableInfo) {
        cout << "Making plot for " << varInfo.variable << "..." << endl;
        make_single_plot(varInfo);
    }

    return 0;
}