#!/usr/bin/env python3

"""
Created on 23 mai 2019

@author: CNRM/GMEI/TRAMM
"""

import logging
import re


class format_latex :
    # Liste des controles
    controles_liste = []


    @classmethod
    def suppr_carac_speciaux(cls, text, trace_me=False):
        """
        Remplace le code latex par les caracteres adaptés
        (Après tests, cette méthode bien que peu esthétique et la plus rapide)
        """
        if trace_me:
            logging.debug(f":::: suppr_carac_speciaux : DEBUT : text = >>>{text}<<<")
        result = text
        result = result.replace("&","  ").replace("\\tt ","").replace("}","").replace("\\textbf","").replace("\\sf","").replace("\\newline","\n")
        result = result.replace("$","").replace("{","").replace("\\textit","").replace("\\\\","").replace("\\%","%").replace("\\leq",u"\u2264")
        result = result.replace("^2",u"\u00B2").replace("\\texttt","").replace("\\vdots",u"\u22EE").replace("^\\circ",u"\u00B0")
        result = result.replace("\\_","_").replace("\\c c",u"\u00E7").replace("\\_","_").replace("\\c c",u"\u00E7").replace("\\item","- ")
        result = result.replace("\\sin","sin").replace("\\cos","cos").replace("\\beginitemize","").replace("\\tanenditemize","")
        result = result.replace("\\hline","____________").replace("\\begincenter","").replace("\\endcenter","").replace("\\endtabular","")

        result = result.replace("\\`a",u"\u00E0").replace("\\'e",u"\u00E9").replace("\\`e",u"\u00E8").replace("\\^e",u"\u00EA").replace("\\`u",u"\u00F9")
        result = result.replace("\\^o",u"\u00F4").replace("\\¨i",u"\u00EF").replace("\\^i",u"\u00EE").replace("\\^a",u"\u00E2").replace("\\alpha",u"\u03B1")
        result = result.replace("\\theta",u"\u03B8").replace("\\upsilon",u"\u03C5").replace("\\beta",u"\u03B2").replace("\\vartheta",u"\u03B8")
        result = result.replace("\\pi",u"\u03C0").replace("\\phi ",u"\u03C6").replace("\\gamma",u"\u03B3").replace("\\iota",u"\u03B9").replace("\\delta",u"\u03B4")
        result = result.replace("\\kappa",u"\u03BA").replace("\\rho",u"\u03C1").replace("\\chi",u"\u03C7").replace("\\epsilon",u"\u03B5").replace("\\lambda",u"\u03BB")
        result = result.replace("\\zeta",u"\u03B6").replace("\\omega",u"\u03C9").replace("\\sigma",u"\u03C3").replace("\\mu",u"\u03BC").replace("\\psi",u"\u03C8")
        result = result.replace("\\eta",u"\u03B7").replace("\\xi",u"\u03BE").replace("\\tau",u"\u03C4").replace("\\Lambda",u"\u039B").replace("\\Gamma",u"\u0393")
        result = result.replace("\\Upsilon",u"\u03A5").replace("\\Xi",u"\u039E").replace("\\Delta",u"\u2206").replace("\\Psi",u"\u03A8").replace("\\Sigma",u"\u03A3")
        result = result.replace("\\Pi",u"\u03A0").replace("\\Theta",u"\u0398").replace("\\Omega",u"\u03A9").replace("\\\"\\i","ï")
        result = result.replace("\\rangle",u"\u3009").replace("\\Uparrow",u"\u21D1").replace("\\rbrack","]").replace("\\lbrack","[").replace("\\uparrow",u"\u2191")
        result = result.replace("\\ge",u"\u2265").replace("\\Vert",u"\u2551").replace("\\vert",u"|").replace("\\updownarrow",u"\u2195").replace("\\langle",u"\u3008")
        result = result.replace("\\sum",u"\u2211").replace("\\gg",">>").replace("\\ll","<<").replace("\\equiv",u"\u2261").replace("\\geq",u"\u2265")
        result = result.replace("\\prod",u"\u220F").replace("\\]","").replace("\\[","").replace("\\beginarrayc","").replace("\\Phi",u"\u03A6")
        result = result.replace("\\endarray","").replace("\\overlineu","u¯").replace("\\overlinev","v¯").replace("\\overlinew","w¯")
        result = result.replace("\\overlinex","x¯").replace("\\overlinev'w'","v¯w¯").replace("\\over","\\").replace("^\\bullet",u"\u2022")

        result = re.sub( r"\\begintabular.*\n", "",result)

        # Pour éviter que "<" et ">" soit pris comme une balise (donc crash)
        result = result.replace("<",u"\u3008").replace(">",u"\u3009")

        # format fraction spécial
        for x in range(result.count("\\frac")):
            text = result.split("\\frac",1)
            result = text[0]+text[1][0]+"/"+text[1][1:]

        return result

