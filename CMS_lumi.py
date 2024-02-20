import ROOT as rt

# CMS_lumi
#   Initiated by: Gautier Hamel de Monchenault (Saclay)
#   Translated in Python by: Joshua Hardenbrook (Princeton)
#   Updated by:   Dinko Ferencek (Rutgers)
#

cmsText = "CMS"
cmsTextFont = 61

writeExtraText = True
extraText = "Preliminary"
extraTextFont = 52

lumiTextSize = 0.6
lumiTextOffset = 0.2

cmsTextSize = 0.75
cmsTextOffset = 0.1

relPosX = 0.045
relPosXAlt = 0.115
relPosY = 0.035
relExtraDY = 1.2

extraOverCmsTextSize = 0.76

lumi = ""

drawLogo = False


def CMS_lumi(pad, era, iPosX):
    outOfFrame = False
    if (iPosX//10 == 0):
        outOfFrame = True

    alignY_ = 3
    alignX_ = 2
    if (iPosX//10 == 0):
        alignX_ = 1
    if (iPosX == 0):
        alignY_ = 1
    if (iPosX//10 == 1):
        alignX_ = 1
    if (iPosX//10 == 2):
        alignX_ = 2
    if (iPosX//10 == 3):
        alignX_ = 3
    align_ = 10*alignX_ + alignY_

    H = pad.GetWh()
    W = pad.GetWw()
    L = pad.GetLeftMargin()
    T = pad.GetTopMargin()
    R = pad.GetRightMargin()
    B = pad.GetBottomMargin()

    pad.cd()

    # find correct sqrt(s) from era
    sqrtS = {
    '2016': '13 TeV', 
    '2017': '13 TeV',
    '2018': '13 TeV',
    '2022': '13.6 TeV',
    '2023': '13.6 TeV',
    }

    lumiText = ''
    for year in sqrtS:
        if year in era:
            lumiText = lumi + ' (' + sqrtS[year] + ')'

    latex = rt.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(rt.kBlack)

    extraTextSize = extraOverCmsTextSize*cmsTextSize

    latex.SetTextFont(42)
    latex.SetTextAlign(31)
    latex.SetTextSize(lumiTextSize*T)

    latex.DrawLatex(1-R, 1-T+lumiTextOffset*T, lumiText)

    if outOfFrame:
        latex.SetTextFont(cmsTextFont)
        latex.SetTextAlign(11)
        latex.SetTextSize(cmsTextSize*T)
        latex.DrawLatex(L, 1-T+lumiTextOffset*T, cmsText)

    pad.cd()

    posX_ = 0
    if (iPosX % 10 <= 1):
        posX_ = L + relPosX*(1-L-R)
    elif (iPosX % 10 == 2):
        posX_ = L + 0.5*(1-L-R)
    elif (iPosX % 10 == 3):
        posX_ = 1-R - relPosX*(1-L-R)

    posY_ = 1-T - relPosY*(1-T-B)

    if not outOfFrame:
        if drawLogo:
            posX_ = L + 0.045*(1-L-R)*W/H
            posY_ = 1-T - 0.045*(1-T-B)
            xl_0 = posX_
            yl_0 = posY_ - 0.15
            xl_1 = posX_ + 0.15*H/W
            yl_1 = posY_
            CMS_logo = rt.TASImage("CMS-BW-label.png")
            pad_logo = rt.TPad("logo", "logo", xl_0, yl_0, xl_1, yl_1)
            pad_logo.Draw()
            pad_logo.cd()
            CMS_logo.Draw("X")
            pad_logo.Modified()
            pad.cd()
        else:
            latex.SetTextFont(cmsTextFont)
            latex.SetTextSize(cmsTextSize*T)
            latex.SetTextAlign(align_)
            latex.DrawLatex(posX_, posY_, cmsText)
            if writeExtraText:
                latex.SetTextFont(extraTextFont)
                latex.SetTextAlign(align_)
                latex.SetTextSize(extraTextSize*T)
                latex.DrawLatex(
                    posX_,
                    posY_ - relExtraDY*cmsTextSize*T,
                    extraText
                )
    elif writeExtraText:
        posX_ = L + relPosXAlt*(1-L-R)
        posY_ = 1 - T + lumiTextOffset*T

        latex.SetTextFont(extraTextFont)
        latex.SetTextSize(extraTextSize*T)
        latex.SetTextAlign(align_)
        latex.DrawLatex(posX_, posY_, extraText)

    pad.Update()
