#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
# on importe Gtk que si on a un display (on en a pas forcément un en mode batch)
if os.environ.get('DISPLAY'):
    import gi
    gi.require_version('Gtk', '3.0') 
    from gi.repository import Gtk # @UnresolvedImport
AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
PYTHON_LIB = os.path.join(AH, 'lib', PYTHON_X_Y)
sys.path.append(PYTHON_LIB)
# import des classes modele, vue et controle
from vista.modele import date as vd
from vista.modele import classes as vc
if os.environ.get('DISPLAY'): 
    from vista.vue import vistacrash, interface as vi
    from vista.controle import controles
from vista.vue import vistagraph as vg
from vista.vue.interface import version as vistaversion


# On parse la ligne de commande
parser = argparse.ArgumentParser()
parser.add_argument("-v","--version", help="affiche la version de vista", action="store_true")
parser.add_argument("-l","--list", help="affiche la liste des attributs configurables", action="store_true")
parser.add_argument("-c","--console", help="active la console vista", action="store_true")
parser.add_argument("-b","--batch", help="utilisation de vista en mode batch", action="store_true")
parser.add_argument("-f","--file", help="fichier de configuration .vista")
parser.add_argument("-s","--start", help="date de début : AAAAMMJJ(MISS) (à utiliser obligatoirement avec l'option --end)")
parser.add_argument("-e","--end", help="date de fin : AAAAMMJJ(MISS) (à utiliser obligatoirement avec l'option --start)")
parser.add_argument("-m","--month", help="mois : AAAAMM (option prioritaire sur --start et --end)")
parser.add_argument("-o","--output", help="fichier de sortie (.pdf | .png | .ps)")

args = parser.parse_args()

if args.batch != True : # mode intéractif
    # Version
    if args.version == True :
        print(("Vista {}".format(vistaversion)))
        sys.exit(1)

    # Modèle
    if args.list == True :
        document = vc.Document("DATA", "{}", vistaversion)
        print((document.getPrettyAttrs()))
        sys.exit(1)            
    if not os.environ.get('DISPLAY'):
        print("Erreur Vista : la variable d'environnement DISPLAY n'est pas positionnée.")
        sys.exit(1)        
    try :
        if args.file != None :
            document = vc.Document("FICHIER", args.file, vistaversion)
            if document.compatible == 1 :
                print((document.message))
            elif document.compatible == 2 :
                vi.VistaDialog(document.message)
                sys.exit(1)
        else :
            document = vc.Document("DATA", "{}", vistaversion)
        document.batch = False
    except RuntimeError as e :
        vi.VistaDialog(str(e))
        sys.exit(1)

    # Vue
    ui = vi.UiVista(document, args.console)

    # Controler
    ui.ctrl = controles.controler(ui)
    
    del document
    vistacrash.initialize(window=ui.window)
    Gtk.main()
    
else : # mode batch
        
    # fichier de config json
    if args.file is None :
        print("Erreur vista : l'option -f |--file FILE est obligatoire en mode batch")
        exit(1)
    else :
        try :
            document = vc.Document("FICHIER", args.file, vistaversion)
            if document.compatible == 1 :
                print((document.message))
            elif document.compatible == 2 :
                print(("Erreur vista : {}".format(document.message)))
                exit(1)
        except RuntimeError as e :
            print(("Erreur Vista : {}".format(str(e))))
            exit(1)
        gdocument = vg.Gdocument(document)
        
    # dates
    if args.month != None :
        if len(args.month) != 6 :
            print("Erreur vista : le format de l'option -m|--month MONTH doit être AAAAMM")
            exit(1)
        else :
            chnDate =  args.month+"01000000" 
            document.dateMois = chnDate
            document.dateDebut, document.dateFin = vd.debutFinMois(chnDate)
    elif args.start is None or args.end is None :
        print("Erreur vista : les options -s|--start START, -e|--end END et -m|--month MONTH ne sont pas compatibles.")
        exit(1)
    else :
        # date de debut
        if len(args.start) < 8 or len(args.start) > 14 :
            print("Erreur vista : l'option --start START n'est pas au bon format.")
            exit(1)
        else :
            chnDateDebut = args.start
            for i in range(len(args.start), 14) :
                chnDateDebut = chnDateDebut+"0"
            document.dateDebut = chnDateDebut
        # date de fin
        if len(args.end) < 8 or len(args.end) > 14 :
            print("Erreur vista : l'option --end END n'est pas au bon format.")
            exit(1)
        else :
            chnDateFin = args.end
            for i in range(len(args.end), 14) :
                chnDateFin = chnDateFin+"0"
            document.dateFin = chnDateFin
    # output ?
    ficOutput=None
    bTraceTermine = False
    if args.output != None :
        rac,ext =  os.path.splitext(args.output)
        if ext == "" :
            ficOutput = rac
        else :
            message = ""
            print("On trace en fonction de l'extension du fichier output.")
            if ext == ".pdf" :
                print("Création d'un document au format pdf.")
                document.updateData()
                message = gdocument.exportPdf(args.output)
            elif ext == ".png" :
                print("Création d'un document au format png.")
                document.updateData()
                message = gdocument.exportPng(args.output)
            elif ext == ".ps" :
                print("Création d'un document au format ps.")
                document.updateData()
                message = gdocument.exportPs(args.output)
            else :
                message = "l'option -o|--output OUTPUT n'a pas une extension supportée (.pdf, .png, .ps ou rien)"
            if message != "" :
                print(("Erreur vista : "+message))
                exit(1)
            else :
                bTraceTermine = True
                                                    
    if bTraceTermine == False :
        fmt = document.getValue("format")
        if ( fmt.find("pdf") != -1 ) :
            print("Création d'un document au format pdf.")
            document.updateData()
            message = gdocument.exportPdf(ficOutput)  
        if ( fmt.find("png") != -1 ) :
            print("Création d'un document au format png.")
            document.updateData()
            message = gdocument.exportPng(ficOutput)
        if ( fmt.find("ps") != -1 ) :
            print("Création d'un document au format ps.")
            document.updateData()
            message = gdocument.exportPs(ficOutput)
        if message != "" :
                print(("Erreur vista : "+message))    

