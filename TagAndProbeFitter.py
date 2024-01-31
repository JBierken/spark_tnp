from array import array
import ROOT
import os
import tdrstyle
import pickle 
ROOT.gROOT.SetBatch()
tdrstyle.setTDRStyle()


class TagAndProbeFitter:

    def __init__(self, name, resonance='Z', addName='', ver='', shift=''):
        
        self._name = name
        self._w = ROOT.RooWorkspace('w'+addName)
        self._useMinos = True
        self._hists = {}
        self._resonance = resonance
        self._version=ver
        f=open('./binning.pkl','rb+')
        binning=pickle.load(f)
        self._pt=binning["pt"]
        self._abseta=binning["abseta"]
        f.close()
        if resonance == 'Z' and 'resolution' in ver:
            self._peak = 90
            self._fit_range_min = 75
            self._fit_range_max = 105
            self._fit_var_min = 60
            self._fit_var_max = 120 
        elif resonance == 'Z' and 'resolution' not in ver:
            self._peak = 90
            self._fit_var_min = 60
            self._fit_var_max = 140
            self._fit_range_min = 70
            self._fit_range_max = 110
        elif resonance == 'JPsi':
            self._peak = 3.10
            self._fit_var_min = 2.80
            self._fit_var_max = 3.40
            self._fit_range_min = 2.90
            self._fit_range_max = 3.30
        if 'resolution' in self._version:
            self.set_fit_var(v='mass')
        else:
            self.set_fit_var()
        self.set_fit_range()

    def wsimport(self, *args):
        # getattr since import is special in python
        # NB RooWorkspace clones object
        if len(args) < 2:
            # Useless RooCmdArg: https://sft.its.cern.ch/jira/browse/ROOT-6785
            args += (ROOT.RooCmdArg(), )
        return getattr(self._w, 'import')(*args)

    def set_fit_var(self, v='x', vMin=None, vMax=None,
                    unit='GeV', label='m(#mu#mu)'):
        if vMin is None:
            vMin = self._fit_var_min
        if vMax is None:
            vMax = self._fit_var_max
        self._fitVar = v
        self._fitVarMin = vMin
        self._fitVarMax = vMax
        self._w.factory('{}[{}, {}]'.format(v, vMin, vMax))
        if unit:
            self._w.var(v).setUnit(unit)
        if label:
            self._w.var(v).setPlotLabel(label)
            self._w.var(v).SetTitle(label)

    def set_fit_range(self, fMin=None, fMax=None):
        if fMin is None:
            fMin = self._fit_range_min
        if fMax is None:
            fMax = self._fit_range_max
        self._fitRangeMin = fMin
        self._fitRangeMax = fMax

    def set_histograms(self, hPass, hFail, peak=None, fitSignalOnly = False):
        if peak is None:
            peak = self._peak
        self._hists['Pass'] = hPass.Clone()
        self._hists['Fail'] = hFail.Clone()
        self._hists['Pass'].SetDirectory(ROOT.gROOT)
        self._hists['Fail'].SetDirectory(ROOT.gROOT)
        self._nPass = hPass.Integral()
        self._nFail = hFail.Integral()
        pb = hPass.FindBin(peak)
        nb = hPass.GetNbinsX()
        window = [int(pb-0.1*nb), int(pb+0.1*nb)]
        self._nPass_central = hPass.Integral(*window)
        self._nFail_central = hFail.Integral(*window)
        hPassName = 'hPass' if not fitSignalOnly else 'hSigPass'
        hFailName = 'hFail' if not fitSignalOnly else 'hSigFail'
        dhPass = ROOT.RooDataHist(
            hPassName, hPassName,
            ROOT.RooArgList(self._w.var(self._fitVar)), hPass)
        dhFail = ROOT.RooDataHist(
            hFailName, hFailName,
            ROOT.RooArgList(self._w.var(self._fitVar)), hFail)
        self.wsimport(dhPass)
        self.wsimport(dhFail)

    def set_gen_shapes(self, hPass, hFail, peak=None):
        if peak is None:
            peak = self._peak
        self._hists['GenPass'] = hPass.Clone()
        self._hists['GenFail'] = hFail.Clone()
        self._hists['GenPass'].SetDirectory(ROOT.gROOT)
        self._hists['GenFail'].SetDirectory(ROOT.gROOT)
        self._nGenPass = hPass.Integral()
        self._nGenFail = hFail.Integral()
        pb = hPass.FindBin(peak)
        nb = hPass.GetNbinsX()
        window = [int(pb-0.1*nb), int(pb+0.1*nb)]
        self._nGenPass_central = hPass.Integral(*window)
        self._nGenFail_central = hFail.Integral(*window)
        dhPass = ROOT.RooDataHist(
            'hGenPass', 'hGenPass',
            ROOT.RooArgList(self._w.var(self._fitVar)), hPass)
        dhFail = ROOT.RooDataHist(
            'hGenFail', 'hGenFail',
            ROOT.RooArgList(self._w.var(self._fitVar)), hFail)
        self.wsimport(dhPass)
        self.wsimport(dhFail)

    def set_workspace(self, lines, template=True, fitSignalOnly = False):
        for line in lines:
            self._w.factory(line)

        nSigP = 0.9*self._nPass
        nBkgP = 0.1*self._nPass
        nSigF = 0.1*self._nFail
        nBkgF = 0.9*self._nFail
        nPassHigh = 1.1*self._nPass
        nFailHigh = 1.1*self._nFail

        if template:
            self._w.factory(
                "HistPdf::sigPhysPass({}, hGenPass)".format(self._fitVar))
            self._w.factory(
                "HistPdf::sigPhysFail({}, hGenFail)".format(self._fitVar))
            self._w.factory(
                "FCONV::sigPass({}, sigPhysPass , sigResPass)".format(
                    self._fitVar))
            self._w.factory(
                "FCONV::sigFail({}, sigPhysFail , sigResFail)".format(
                    self._fitVar))
            # update initial guesses
            nSigP = self._nGenPass_central / self._nGenPass * self._nPass if self._nGenPass > 0. else 0.
            nSigF = self._nGenFail_central / self._nGenFail * self._nFail if self._nGenFail > 0. else 0.
            if nSigP < 0.5:
                nSigP = 0.9 * self._nPass
            if nSigF < 0.5:
                nSigF = 0.1 * self._nFail

        # build extended pdf
        self._w.factory("nSigP[{}, 0.5, {}]".format(nSigP, nPassHigh))
        self._w.factory("nSigF[{}, 0.5, {}]".format(nSigF, nFailHigh))
        if not fitSignalOnly:
            self._w.factory("nBkgP[{}, 0.5, {}]".format(nBkgP, nPassHigh))
            self._w.factory("nBkgF[{}, 0.5, {}]".format(nBkgF, nFailHigh))
            self._w.factory("SUM::pdfPass(nSigP*sigPass, nBkgP*bkgPass)")
            self._w.factory("SUM::pdfFail(nSigF*sigFail, nBkgF*bkgFail)")
        else:
            self._w.factory("SUM::pdfPass(nSigP*sigPass)")
            self._w.factory("SUM::pdfFail(nSigF*sigFail)")

        self._w.importClassCode("sigPass")
        self._w.importClassCode("sigFail")
        if not fitSignalOnly:
            self._w.importClassCode("bkgPass")
            self._w.importClassCode("bkgFail")

    def set_workspace_resolution(self, lines, template=True, fitSignalOnly = False):
        for line in lines:
           self._w.factory(line)

    def fit(self, outFName, mcTruth=False, template=True, doPassPlusFail=False, fitSignalOnly=False):
        pdfPass = self._w.pdf('pdfPass')
        pdfFail = self._w.pdf('pdfFail')
        pdfPassName = 'pdfPass'
        pdfFailName = 'pdfFail'

        # if we are fitting MC truth, then set background things to constant
        if (mcTruth and template):
            self._w.var('nBkgP').setVal(0)
            self._w.var('nBkgP').setConstant()
            self._w.var('nBkgF').setVal(0)
            self._w.var('nBkgF').setConstant()

        # set the range on the fit var
        # needs to be smaller than the histogram range for the convolution
        self._w.var(self._fitVar).setRange(
            self._fitRangeMin, self._fitRangeMax)
        self._w.var(self._fitVar).setRange(
            'fitRange', self._fitRangeMin, self._fitRangeMax)

        hPassName = 'hPass' if not fitSignalOnly else 'hSigPass'
        hFailName = 'hFail' if not fitSignalOnly else 'hSigFail'
            
        # fit passing histogram
        resPass = pdfPass.fitTo(self._w.data(hPassName),
                                ROOT.RooFit.Minimizer("Minuit", "minimize"),
                                ROOT.RooFit.Optimize(1),
                                ROOT.RooFit.Save(),
                                ROOT.RooFit.Range("fitRange"),
                                ROOT.RooFit.Minos(True),
                            )

        # when convolving, set fail sigma to fitted pass sigma
        if template:
            self._w.var('sigmaF').setVal(
                self._w.var('sigmaP').getVal())
            self._w.var('sigmaF').setRange(
                0.8 * self._w.var('sigmaP').getVal(),
                3.0 * self._w.var('sigmaP').getVal())

        # fit failing histogram
        resFail = pdfFail.fitTo(self._w.data(hFailName),
                                ROOT.RooFit.Minimizer("Minuit", "minimize"),
                                ROOT.RooFit.Optimize(1),
                                ROOT.RooFit.Save(),
                                ROOT.RooFit.Range("fitRange"),
                                ROOT.RooFit.Minos(True),
                            )

        # plot
        # need to run chi2 after plotting full pdf

        # pass
        pFrame = self._w.var(self._fitVar).frame(
            self._fitRangeMin, self._fitRangeMax)
        pFrame.SetTitle('Passing probes')
        self._w.data(hPassName).plotOn(pFrame)
        self._w.pdf(pdfPassName).plotOn(pFrame,         
                                      ROOT.RooFit.LineColor(ROOT.kRed),
                                      )
        # -2 for the extened PDF norm for bkg and sig
        ndofp = resPass.floatParsFinal().getSize() - 2
        chi2p = pFrame.chiSquare(ndofp)
        self._w.data(hPassName).plotOn(pFrame)

        # residuals/pull
        pullP = pFrame.pullHist()
        pFrame2 = self._w.var(self._fitVar).frame(
            self._fitRangeMin, self._fitRangeMax)
        pFrame2.addPlotable(pullP, 'P')

        self._w.pdf(pdfPassName).plotOn(pFrame,
                                      ROOT.RooFit.Components('sigPass'),
                                      ROOT.RooFit.LineWidth(0),
                                      ) # invisible plotting, needed for chi2                                                                                                                                                                                                  
        self._w.pdf(pdfPassName).plotOn(pFrame,
                                      ROOT.RooFit.Components('bkgPass'),
                                      ROOT.RooFit.LineColor(ROOT.kBlue),
                                      ROOT.RooFit.LineStyle(ROOT.kDashed),
                                      )

        # fail
        fFrame = self._w.var(self._fitVar).frame(
            self._fitRangeMin, self._fitRangeMax)
        fFrame.SetTitle('Failing probes')
        self._w.data(hFailName).plotOn(fFrame)
        self._w.pdf(pdfFailName).plotOn(fFrame,
                                      ROOT.RooFit.LineColor(ROOT.kRed),
                                      )
        # -2 for the extened PDF norm for bkg and sig
        ndoff = resFail.floatParsFinal().getSize() - 2
        chi2f = fFrame.chiSquare(ndoff)
        self._w.data(hFailName).plotOn(fFrame)

        # residuals/pull
        pullF = fFrame.pullHist()
        fFrame2 = self._w.var(self._fitVar).frame(
            self._fitRangeMin, self._fitRangeMax)
        fFrame2.addPlotable(pullF, 'P')

        self._w.pdf(pdfFailName).plotOn(fFrame,
                                      ROOT.RooFit.Components('sigFail'),
                                      ROOT.RooFit.LineWidth(0),
                                      ) # invisible plotting, needed for chi2                                                                                                                                                                                                  
        self._w.pdf(pdfFailName).plotOn(fFrame,
                                      ROOT.RooFit.Components('bkgFail'),
                                      ROOT.RooFit.LineColor(ROOT.kBlue),
                                      ROOT.RooFit.LineStyle(ROOT.kDashed),
                                      )

        # gof tests
        statTests = ROOT.TTree('statTests', 'statTests')
        branches = {}
        branches['chi2P'] = array('f', [0])
        branches['chi2F'] = array('f', [0])
        branches['ksP'] = array('f', [0])
        branches['ksF'] = array('f', [0])
        for b in branches:
            statTests.Branch(b, branches[b], '{}/F'.format(b))

        # chi2
        branches['chi2P'][0] = chi2p
        branches['chi2F'][0] = chi2f

        # KS
        binWidth = self._hists['Pass'].GetBinWidth(1)
        nbins = int((self._fitRangeMax - self._fitRangeMin) / binWidth)
        hPdfPass = self._w.pdf(pdfPassName).createHistogram(
            'ks_pdfPass',
            self._w.var(self._fitVar),
            ROOT.RooFit.Binning(nbins),
        )
        hDataPass = self._w.data(hPassName).createHistogram(
            'ks_hPass',
            self._w.var(self._fitVar),
            ROOT.RooFit.Binning(nbins),
        )
        ksP = hDataPass.KolmogorovTest(hPdfPass)
        branches['ksP'][0] = ksP

        hPdfFail = self._w.pdf(pdfFailName).createHistogram(
            'ks_pdfFail',
            self._w.var(self._fitVar),
            ROOT.RooFit.Binning(nbins),
        )
        hDataFail = self._w.data(hFailName).createHistogram(
            'ks_hFail',
            self._w.var(self._fitVar),
            ROOT.RooFit.Binning(nbins),
        )
        ksF = hDataFail.KolmogorovTest(hPdfFail)
        branches['ksF'][0] = ksF

        statTests.Fill()

        # make canvas
        canvas = ROOT.TCanvas('c', 'c', 1100*2, 450*2)
        canvas.Divide(3, 1)

        # print parameters
        canvas.cd(1)
        eff = -1
        e_eff = 0

        nSigP = self._w.var("nSigP")
        nSigF = self._w.var("nSigF")

        nP = nSigP.getVal()
        e_nP = nSigP.getError()
        rele_nP = e_nP / nP if nP > 0. else 0.
        nF = nSigF.getVal()
        e_nF = nSigF.getError()
        rele_nF = e_nF / nF if nF > 0. else 0.
        nTot = nP + nF
        if doPassPlusFail:
           nTot = nF
        eff = nP / nTot
        
        # Compute Clopper-Pearson interval
        confidenceLevel = 0.68
        alpha = 1 - confidenceLevel
    
        lowerLimit = round(ROOT.Math.beta_quantile(alpha/2,nP,nTot-nP + 1),4)
        if nP==nTot:
            upperLimit=1
        else:
            upperLimit = round(ROOT.Math.beta_quantile(1-alpha/2,nP + 1,nTot-nP),4)
        e_eff = max(abs(eff-lowerLimit),abs(eff-upperLimit))

        text1 = ROOT.TPaveText(0, 0.8, 1, 1)
        text1.SetFillColor(0)
        text1.SetBorderSize(0)
        text1.SetTextAlign(12)

        text1.AddText("Fit status pass: {}, fail: {}".format(
            resPass.status(), resFail.status()))
        text1.AddText("#chi^{{2}}/ndof pass: {:.3f}, fail: {:.3f}".format(
            chi2p, chi2f))
        text1.AddText("KS pass: {:.3f}, fail: {:.3f}".format(ksP, ksF))
        text1.AddText("eff = {:.4f} #pm {:.4f}".format(eff, e_eff))

        text = ROOT.TPaveText(0, 0, 1, 0.8)
        text.SetFillColor(0)
        text.SetBorderSize(0)
        text.SetTextAlign(12)
        text.AddText("    --- parameters ")

        def argsetToList(argset):
            arglist = []
            if not argset:
                return arglist
            argiter = argset.createIterator()
            ax = argiter.Next()
            while ax:
                arglist += [ax]
                ax = argiter.Next()
            return arglist

        text.AddText("    pass")
        listParFinalP = argsetToList(resPass.floatParsFinal())
        for p in listParFinalP:
            pName = p.GetName()
            pVar = self._w.var(pName)
            text.AddText("    - {} \t= {:.3f} #pm {:.3f}".format(
                pName, pVar.getVal(), pVar.getError()))

        if doPassPlusFail:
           text.AddText("    total")
        else:
           text.AddText("    fail")
        listParFinalF = argsetToList(resFail.floatParsFinal())
        for p in listParFinalF:
            pName = p.GetName()
            pVar = self._w.var(pName)
            text.AddText("    - {} \t= {:.3f} #pm {:.3f}".format(
                pName, pVar.getVal(), pVar.getError()))

        text1.Draw()
        text.Draw()

        # print fit frames
        canvas.cd(2)
        plotpadP = ROOT.TPad("plotpadP", "top pad", 0.0, 0.21, 1.0, 1.0)
        ROOT.SetOwnership(plotpadP, False)
        plotpadP.SetBottomMargin(0.00)
        plotpadP.SetRightMargin(0.04)
        plotpadP.SetLeftMargin(0.16)
        plotpadP.Draw()
        ratiopadP = ROOT.TPad("ratiopadP", "bottom pad", 0.0, 0.0, 1.0, 0.21)
        ROOT.SetOwnership(ratiopadP, False)
        ratiopadP.SetTopMargin(0.00)
        ratiopadP.SetRightMargin(0.04)
        ratiopadP.SetBottomMargin(0.5)
        ratiopadP.SetLeftMargin(0.16)
        ratiopadP.SetTickx(1)
        ratiopadP.SetTicky(1)
        ratiopadP.Draw()
        if plotpadP != ROOT.TVirtualPad.Pad():
            plotpadP.cd()
        pFrame.Draw()
        ratiopadP.cd()
        pFrame2.Draw()
        prims = ratiopadP.GetListOfPrimitives()
        for prim in prims:
            if 'frame' in prim.GetName():
                prim.GetXaxis().SetLabelSize(0.19)
                prim.GetXaxis().SetTitleSize(0.21)
                prim.GetXaxis().SetTitleOffset(1.0)
                prim.GetXaxis().SetLabelOffset(0.03)
                prim.GetYaxis().SetLabelSize(0.19)
                prim.GetYaxis().SetLabelOffset(0.006)
                prim.GetYaxis().SetTitleSize(0.21)
                prim.GetYaxis().SetTitleOffset(0.35)
                prim.GetYaxis().SetNdivisions(503)
                prim.GetYaxis().SetTitle('Pull')
                prim.GetYaxis().SetRangeUser(-3, 3)
                break

        canvas.cd(3)
        plotpadF = ROOT.TPad("plotpadF", "top pad", 0.0, 0.21, 1.0, 1.0)
        ROOT.SetOwnership(plotpadF, False)
        plotpadF.SetBottomMargin(0.00)
        plotpadF.SetRightMargin(0.04)
        plotpadF.SetLeftMargin(0.16)
        plotpadF.Draw()
        ratiopadF = ROOT.TPad("ratiopadF", "bottom pad", 0.0, 0.0, 1.0, 0.21)
        ROOT.SetOwnership(ratiopadF, False)
        ratiopadF.SetTopMargin(0.00)
        ratiopadF.SetRightMargin(0.04)
        ratiopadF.SetBottomMargin(0.5)
        ratiopadF.SetLeftMargin(0.16)
        ratiopadF.SetTickx(1)
        ratiopadF.SetTicky(1)
        ratiopadF.Draw()
        if plotpadF != ROOT.TVirtualPad.Pad():
            plotpadF.cd()
        fFrame.Draw()
        ratiopadF.cd()
        fFrame2.Draw()
        prims = ratiopadF.GetListOfPrimitives()
        for prim in prims:
            if 'frame' in prim.GetName():
                prim.GetXaxis().SetLabelSize(0.19)
                prim.GetXaxis().SetTitleSize(0.21)
                prim.GetXaxis().SetTitleOffset(1.0)
                prim.GetXaxis().SetLabelOffset(0.03)
                prim.GetYaxis().SetLabelSize(0.19)
                prim.GetYaxis().SetLabelOffset(0.006)
                prim.GetYaxis().SetTitleSize(0.21)
                prim.GetYaxis().SetTitleOffset(0.35)
                prim.GetYaxis().SetNdivisions(503)
                prim.GetYaxis().SetTitle('Pull')
                prim.GetYaxis().SetRangeUser(-3, 3)
                break

        # save
        out = ROOT.TFile.Open(outFName, 'RECREATE')
        # workspace is not readable due to RooCMSShape
        # for now, just don't write
        # self._w.Write('{}_workspace'.format(self._name),
        #              ROOT.TObject.kOverwrite)
        canvas.Write('{}_Canv'.format(self._name), ROOT.TObject.kOverwrite)
        resPass.Write('{}_resP'.format(self._name), ROOT.TObject.kOverwrite)
        resFail.Write('{}_resF'.format(self._name), ROOT.TObject.kOverwrite)
        statTests.Write('{}_statTests'.format(self._name),
                        ROOT.TObject.kOverwrite)
        for hKey in self._hists:
            self._hists[hKey].Write('{}_{}'.format(self._name, hKey),
                                    ROOT.TObject.kOverwrite)
        out.Close()
        canvas.Print(outFName.replace('.root', '.png') if not fitSignalOnly else outFName.replace('.root', '_signalFit.png'))

    def fit_resolution (self, outFName, mcTruth=False, fitSignalOnly=False, st='', shift=''):
    
        if 'SCB' in st:
            DOCRYSTALBALL = True
            DOCRUIJFF = False
            DODOUBLECB = False   
        elif 'cruijff' in st:		
            DOCRUIJFF = True
            DOCRYSTALBALL = False
            DODOUBLECB = False
        elif 'DCB' in st:
            DODOUBLECB = True
            DOCRYSTALBALL = False
            DOCRUIJFF = False
        fit_min = self._fitRangeMin
        fit_max = self._fitRangeMax
        if mcTruth:
            a="gen"
        else:
            a=""        
        ROOT.gSystem.Load("./RooCruijff_cxx.so")
        ROOT.gSystem.Load("./RooDCBShape_cxx.so")
        if not mcTruth:
            datahist=ROOT.RooDataHist("hPName"+a,"hPName"+a,ROOT.RooArgList(self._w.var(self._fitVar)),self._hists['Pass'])
            getattr(self._w,'import')(datahist,ROOT.RooCmdArg())
        else:
            genhist=ROOT.RooDataHist("hPName"+a,"hPName"+a,ROOT.RooArgList(self._w.var(self._fitVar)),self._hists['GenPass'])
            getattr(self._w,'import')(genhist,ROOT.RooCmdArg())
        if 'BinUp' in shift:
            nDOF = (fit_max-fit_min)/0.25
        elif 'BinDown' in shift:
            nDOF = (fit_max-fit_min)/1.0
        else:
            nDOF = (fit_max-fit_min)/0.5
        
        if DOCRYSTALBALL:
            funct = ROOT.TF1("crystal","crystalball",fit_min,fit_max)
            funct.SetLineColor(ROOT.kRed)   
            nDOF = nDOF-3 
            bw = self._w.pdf("bw")
            cb = self._w.pdf("cb")
            self._w.var(self._fitVar).setRange(fit_min,fit_max)
            self._w.var(self._fitVar).setRange('fit_Range',fit_min,fit_max)
            self._w.var(self._fitVar).setBins(2000,"cache")
            self._w.var(self._fitVar).setMin("cache",0)
            self._w.var(self._fitVar).setMax("cache",1000);## need to be adjusted to be higher than limit setting
            sigpdf = ROOT.RooFFTConvPdf("sig"+a,"sig"+a,self._w.var(self._fitVar),bw,cb)
            getattr(self._w,'import')(sigpdf,ROOT.RooCmdArg())
          
            fitResult = self._w.pdf("sig"+a).fitTo(self._w.data("hPName"+a), ROOT.RooFit.Save(), ROOT.RooFit.Range("fit_Range"), ROOT.RooFit.Minos(ROOT.kFALSE), ROOT.RooFit.SumW2Error(ROOT.kFALSE))
        elif DOCRUIJFF:
            nDOF = nDOF-3
            bw = self._w.pdf("bw")
            cb = self._w.pdf("cb")
            self._w.var(self._fitVar).setRange(fit_min,fit_max)
            self._w.var(self._fitVar).setRange('fit_Range',fit_min,fit_max)
            self._w.var(self._fitVar).setBins(2000,"cache")
            self._w.var(self._fitVar).setMin("cache",0)
            self._w.var(self._fitVar).setMax("cache",1000); ## need to be adjusted to be higher than limit setting
            sigpdf = ROOT.RooFFTConvPdf("sig"+a,"sig"+a,self._w.var(self._fitVar),bw,cb)
            getattr(self._w,'import')(sigpdf,ROOT.RooCmdArg())
            fitResult = self._w.pdf("sig"+a).fitTo(self._w.data("hPName"+a),ROOT.RooFit.Save(), ROOT.RooFit.Range("fit_Range"), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kFALSE))
        elif DODOUBLECB:
            nDOF = nDOF-4
            self._w.var("nR").setVal(1)
            bw = self._w.pdf("bw")
            cb = self._w.pdf("cb")
            self._w.var(self._fitVar).setRange(fit_min,fit_max)
            self._w.var(self._fitVar).setRange('fit_Range',fit_min,fit_max)
            self._w.var(self._fitVar).setBins(2000,"cache")
            self._w.var(self._fitVar).setMin("cache",0)
            self._w.var(self._fitVar).setMax("cache",1000); ## need to be adjusted to be higher than limit setting
            sigpdf = ROOT.RooFFTConvPdf("sig"+a,"sig"+a,self._w.var(self._fitVar),bw,cb)
            getattr(self._w,'import')(sigpdf, ROOT.RooCmdArg())
            fitResult = self._w.pdf("sig"+a).fitTo(self._w.data("hPName"+a),ROOT.RooFit.Save(), ROOT.RooFit.Range("fit_Range"), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kFALSE))
	
        chi2 = ROOT.RooChi2Var("bla"+a,"blubb"+a,self._w.pdf("sig"+a),self._w.data("hPName"+a)).getVal()
   
        c1 = ROOT.TCanvas("c1","c1",700,700)
        c1.cd()	
        plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
        style =tdrstyle.setTDRStyle()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetTitleXOffset(1.45)
        ROOT.gStyle.SetPadLeftMargin(0.2)	
        ROOT.gStyle.SetTitleYOffset(2)			
        plotPad.UseCurrentStyle()
        plotPad.Draw()	
        plotPad.cd()
        
        if DODOUBLECB or DOCRYSTALBALL or DOCRUIJFF:
            if 'BinUp' in shift:
                self._w.var(self._fitVar).setBins(int((fit_max-fit_min)/0.25))
            elif 'BinDown' in shift: 
                self._w.var(self._fitVar).setBins(int(fit_max-fit_min))
            else:
                self._w.var(self._fitVar).setBins(int((fit_max-fit_min)/0.5))
            frame = self._w.var(self._fitVar).frame(ROOT.RooFit.Title('Invariant mass of dimuon pairs'))
            frame.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
            frame.GetYaxis().SetTitle("Events")
            ROOT.RooAbsData.plotOn(self._w.data('hPName'+a), frame, ROOT.RooFit.Name("hPName"+a))
            self._w.pdf('sig'+a).plotOn(frame, ROOT.RooFit.Name("sig"+a))
            frame.Draw()
            chi2 = frame.chiSquare("sig"+a,"hPName"+a) 
        else:
            h.GetXaxis().SetTitle("m_{ll} [GeV]")
            h.SetLineColor(kBlack)
            h.GetXaxis().SetRangeUser(fit_min,fit_max)
            h.SetMarkerStyle(20)
            h.SetMarkerSize(0.7)	
            h.Draw("E")
            if DOCRYSTALBALL or DOCRUIJFF or DODOUBLECB:
                funct.Draw("SAME")
            else:
                gaus.Draw("SAME")
        
        
        nDOFforWS = ROOT.RooRealVar('nDOF'+a,'nDOF'+a,nDOF )
        getattr(self._w,'import')(nDOFforWS, ROOT.RooCmdArg())	
        chi2forWS = ROOT.RooRealVar('chi2'+a,'chi2'+a,chi2*nDOF )
        getattr(self._w,'import')(chi2forWS, ROOT.RooCmdArg())			
        latex = ROOT.TLatex()
        latex.SetTextFont(42)
        latex.SetTextAlign(31)
        latex.SetTextSize(0.04)
        latex.SetNDC(True)
        latexCMS = ROOT.TLatex()
        latexCMS.SetTextFont(61)
        latexCMS.SetTextSize(0.055)
        latexCMS.SetNDC(True)
        latexCMSExtra = ROOT.TLatex()
        latexCMSExtra.SetTextFont(52)
        latexCMSExtra.SetTextSize(0.03)
        latexCMSExtra.SetNDC(True)
        
        latex.DrawLatex(0.95, 0.96, "(13 TeV)")
        
        cmsExtra = "Preliminary" 
        latexCMS.DrawLatex(0.78,0.88,"CMS")
        yLabelPos = 0.84
        latexCMSExtra.DrawLatex(0.78,yLabelPos,"%s"%(cmsExtra))
        
        latexFit1 = ROOT.TLatex()
        latexFit1.SetTextFont(42)
        latexFit1.SetTextSize(0.035)
        latexFit1.SetNDC(True)
        for i,eta in enumerate(self._abseta):     
            for j,pt in enumerate(self._pt):
                if "abseta_%i_pt_%i"%(i+1,j+1) in self._name:
                    latexFit1.DrawLatex(0.25, 0.84, "%i GeV < p_{T} < %i GeV \n  %0.1f <eta< %0.1f" %(self._pt[j],self._pt[j+1] ,self._abseta[i],self._abseta[i+1])) 
       
        latexFit = ROOT.TLatex()
        latexFit.SetTextFont(42)
        latexFit.SetTextSize(0.030)
        latexFit.SetNDC(True)        
        latexFit.DrawLatex(0.25, 0.74,"%s = %5.3g #pm %5.3g GeV"%("mean bias",self._w.var("mean").getVal(),self._w.var("mean").getError()))
        if "SCB" in st:
            latexFit.DrawLatex(0.25, 0.7,"%s = %5.3g #pm %5.3g GeV"%("#sigma",self._w.var("sigma").getVal(),self._w.var("sigma").getError()))
            latexFit.DrawLatex(0.25, 0.66,"%s = %5.3g #pm %5.3g"%("alphaL",self._w.var("alphaL").getVal(),self._w.var("alphaL").getError()))
            latexFit.DrawLatex(0.25, 0.62,"%s = %5.3g #pm %5.3g"%("nL",self._w.var("nL").getVal(),self._w.var("nL").getError()))
        elif "cruijff" in st:
            latexFit.DrawLatex(0.25, 0.7,"%s = %5.3g #pm %5.3g GeV"%("#sigma",self._w.var("sigma").getVal(),self._w.var("sigma").getError()))
            latexFit.DrawLatex(0.25, 0.66,"%s = %5.3g #pm %5.3g"%("alphaL",self._w.var("alphaL").getVal(),self._w.var("alphaL").getError()))
            latexFit.DrawLatex(0.25, 0.62,"%s = %5.3g #pm %5.3g"%("alphaR",self._w.var("alphaR").getVal(),self._w.var("alphaR").getError()))
        
        elif "DCB" in st:
            latexFit.DrawLatex(0.25, 0.7,"%s = %5.3g #pm %5.3g GeV"%("#sigma",self._w.var("sigma").getVal(),self._w.var("sigma").getError()))
            latexFit.DrawLatex(0.25, 0.66,"%s = %5.3g #pm %5.3g"%("alphaL",self._w.var("alphaL").getVal(),self._w.var("alphaL").getError()))
            latexFit.DrawLatex(0.25, 0.62,"%s = %5.3g #pm %5.3g"%("alphaR",self._w.var("alphaR").getVal(),self._w.var("alphaR").getError()))
            latexFit.DrawLatex(0.25, 0.58,"%s = %5.3g #pm %5.3g"%("nL",self._w.var("nL").getVal(),self._w.var("nL").getError()))
            latexFit.DrawLatex(0.25, 0.54,"%s = %5.3g #pm %5.3g"%("nR",self._w.var("nR").getVal(),self._w.var("nR").getError()))
        			
        latexFit.DrawLatex(0.25, 0.5, "#chi^{2}/ndf = %5.3f / %2.0f = %4.2f" %(chi2*nDOF,nDOF,chi2))
      
        plotDir = os.path.join("fitResults",st,shift)
        os.makedirs(plotDir, exist_ok=True)
        if mcTruth:
            plotPath = os.path.join(plotDir,self._name+"gen")
            c1.Print('{}.pdf'.format(plotPath))
        else:
            plotPath = os.path.join(plotDir,self._name)
            c1.Print('{}.pdf'.format(plotPath))
        print("Done Fitting"+a)
        if not mcTruth:
            out = ROOT.TFile.Open(outFName, 'RECREATE')
   
            c1.Write('{}_Canv'.format(self._name), ROOT.TObject.kOverwrite)

     
            fitResult.Write('{}_fitResult'.format(self._name),ROOT.TObject.kOverwrite)
            out.Close()
   
        else:

            out = ROOT.TFile.Open(outFName, 'UPDATE')
            c1.Write('{}_Canvgen'.format(self._name), ROOT.TObject.kOverwrite)
            fitResult.Write('{}_fitResultgen'.format(self._name),ROOT.TObject.kOverwrite)
            out.Close()
