#!/usr/bin/env python3

from tkinter import *
import os

def Affiche_information(text_affiche,couleur) :
    fen1 = Tk()
    fen1.title("Message.")
    Label(fen1, text=text_affiche, bg=couleur,height = 5).pack()
    Button(fen1, text='OK', command = fen1.destroy).pack()
    fen1.mainloop()

def test_presence_applicatif(appl) :
    cmd = "which " + appl + " > /dev/null"
    Retour_cmd = os.system(cmd)

    if Retour_cmd != 0 :
        return(1)
    else :
        return(0)

def test_presence_repertoire(rept) :
    if os.path.exists(rept) == True :
        return(0)
    else :
        return(1)

def ecrit_fic_config(event) :

    if Saisie_visu.get() != "" :
        retour=test_presence_applicatif(Saisie_visu.get())
        if retour != 0 :
            texte = "Applicatif " + Saisie_visu.get() + " non connu!\n " +\
                            "saisir autre applicatif ou vide pour applicatif par d\u00E9faut"
            Affiche_information(texte,"red")
            return(-1)       

    if Saisie_visu_ps.get() != "" :
        retour=test_presence_applicatif(Saisie_visu_ps.get())
        if retour != 0 :
            texte = "Applicatif " + Saisie_visu_ps.get() + " non connu!\n " +\
                "saisir autre applicatif ou vide pour applicatif par d\u00E9faut"
            Affiche_information(texte,"red")
            return(-1)       

    if Saisie_rep_sav.get() != "" :
        retour=test_presence_repertoire(Saisie_rep_sav.get())
        if retour != 0 :
            texte = "Le r\u00E9pertoire " + Saisie_rep_sav.get() + " n'existe pas!\n " +\
                "saisir autre r\u00E9pertoire ou vide pour r\u00E9pertoire par d\u00E9faut"
            Affiche_information(texte,"red")
            return(-1)       

    nom_fic_config=AH + "/config/gengraphvect.cfg"
    try :
        fic_conf = open(nom_fic_config,"w")
        fic_conf.write("couleur_info_capteur=" + var_chaine.get()+"\n")
        fic_conf.write("couleur_vecteur_init=" + var_vect0.get()+"\n")
        fic_conf.write("couleur_vecteur_inter=" + var_vect1.get()+"\n")
        fic_conf.write("couleur_vecteur_etudie=" + var_vectF.get()+"\n")
        fic_conf.write("couleur_fonction_noeud=" + var_Fonc.get()+"\n")
        fic_conf.write("couleur_fonction_texte=" + var_FoncT.get()+"\n")
        if Saisie_visu.get() == "" :
            fic_conf.write( "appl_visu_graphe=eog"+"\n")
        else :
            fic_conf.write( "appl_visu_graphe=" + Saisie_visu.get()+"\n")

        if Saisie_visu_ps.get() == "" :
            fic_conf.write( "appl_visu_ps=gv"+"\n")
        else :
            fic_conf.write( "appl_visu_ps=" + Saisie_visu_ps.get()+"\n")

        if Saisie_rep_sav.get() == "" :
            fic_conf.write( "rep_sav=/tmp"+"\n")
        else :
            fic_conf.write( "rep_sav=" + Saisie_rep_sav.get()+"\n")

        fic_conf.flush()
    except :
        texte = "Probl\u00E8me \u00E9criture fichier de config!"
        Affiche_information(texte,"red")
    else :
        texte = "Ecriture fichier de config : OK"
        Affiche_information(texte,"skyblue1")
    fic_conf.close()

def initialise(flg) :
    global var_chaine
    global var_vect0
    global var_vect1
    global var_vectF
    global var_Fonc
    global var_FoncT

    var_chaine = StringVar()
    var_vect0 = StringVar()
    var_vect1 = StringVar()
    var_vectF = StringVar()
    var_Fonc = StringVar()
    var_FoncT = StringVar()

    cr_lit = lit_fic_preference()
    
    if cr_lit != 0 :
        var_chaine.set(liste_couleur[1])
        var_vect0.set(liste_couleur[2])
        var_vect1.set(liste_couleur[3])
        var_vectF.set(liste_couleur[0])
        var_Fonc.set(liste_couleur[5])
        var_FoncT.set(liste_couleur[4])
    else :
        var_chaine.set(config_couleur["couleur_info_capteur"][:-1])
        var_vect0.set(config_couleur["couleur_vecteur_init"][:-1])
        var_vect1.set(config_couleur["couleur_vecteur_inter"][:-1])
        var_vectF.set(config_couleur["couleur_vecteur_etudie"][:-1])
        var_Fonc.set(config_couleur["couleur_fonction_noeud"][:-1])
        var_FoncT.set(config_couleur["couleur_fonction_texte"][:-1])


def lit_fic_preference() :
    global AH
    global appl_visu_graphe
    global appl_visu_ps
    global repertoire_sav
    global config_couleur
    config_couleur = {}
    nom_fic_config = AH + "/config/gengraphvect.cfg"

    appl_visu_graphe = "eog"
    appl_visu_ps = "gv"
    repertoire_sav = "/tmp"

    try :
        fic_conf = open(nom_fic_config,"r")
    except IOError:
        print("Utilisation valeurs defaut")
        return(1)
    else :
        for line_config in fic_conf:
            info_param = line_config.split("=")
            config_couleur[info_param[0]] = info_param[1]
        appl_visu_graphe = config_couleur['appl_visu_graphe'][0:-1]
        appl_visu_ps = config_couleur['appl_visu_ps'][0:-1]
        try :
            repertoire_sav = config_couleur['rep_sav'][0:-1]
        except :
                print("rep sav par defaut : " + repertoire_sav)
        return(0)

def reset_cou():
    global fond_chaine
    global fond_vect0
    global fond_vect1
    global fond_vectF
    global fond_Fonc
    global fond_FoncT

    var_chaine.set(liste_couleur[1])
    var_vect0.set(liste_couleur[2])
    var_vect1.set(liste_couleur[3])
    var_vectF.set(liste_couleur[0])
    var_Fonc.set(liste_couleur[5])
    var_FoncT.set(liste_couleur[4])

    fond_chaine.itemconfigure(rect_chaine, fill= var_chaine.get())
    fond_vect0.itemconfigure(rect_vect0, fill= var_vect0.get())
    fond_vect1.itemconfigure(rect_vect1, fill= var_vect1.get())
    fond_vectF.itemconfigure(rect_vectF, fill= var_vectF.get())
    fond_Fonc.itemconfigure(rect_Fonc, fill= var_Fonc.get())
    fond_FoncT.itemconfigure(rect_FoncT, fill= var_FoncT.get())

def change_cou(event):
    global fond_chaine
    global fond_vect0
    global fond_vect1
    global fond_vecte
    global fond_Fonc
    global fond_FoncT

    fond_chaine.itemconfigure(rect_chaine, fill= var_chaine.get())
    fond_vect0.itemconfigure(rect_vect0, fill= var_vect0.get())
    fond_vect1.itemconfigure(rect_vect1, fill= var_vect1.get())
    fond_vectF.itemconfigure(rect_vectF, fill= var_vectF.get())
    fond_Fonc.itemconfigure(rect_Fonc, fill= var_Fonc.get())
    fond_FoncT.itemconfigure(rect_FoncT, fill= var_FoncT.get())
    print(Saisie_visu.get())

global fond_chaine
global fond_vect0
global fond_vect1
global fond_vectF
global fond_Fonc
global fond_FoncT
global var_chaine
global var_vect0
global var_vect1
global var_vectF
global var_Fonc
global var_FoncT
global AH


AH = os.getenv('AIDA_HOME')
if not AH:
    print("FATAL : AIDA_HOME non defini", file=sys.stderr)
liste_couleur=('salmon1','palegreen1','lightblue2','white','brown','yellow1','blue','red','orange','black','gray50','gray60','gray70','gray80','gray90','beige','purple','orchid','azure','ivory','lavender')


Fp=Tk()
Fp.title("Configuration applicatif gengraph.")
Fp.minsize(width=400, height=300)
Fp.maxsize(width=600, height=500)
Fp.resizable(width=YES, height=YES)
Fp.configure(bg="lightblue2")
F_couleur=LabelFrame(Fp, text="Choix couleurs.")
F_couleur.configure(bg="lightblue2", width=400, height=300)
F_action=LabelFrame(Fp,bg="lightblue2", text="Action")
F_saisie=LabelFrame(Fp, bg="lightblue2", text="Divers")

initialise(0)
visu_graphe=StringVar()
visu_graphe.set(appl_visu_graphe)
visu_ps=StringVar()
visu_ps.set(appl_visu_ps)
rep_sav=StringVar()
rep_sav.set(repertoire_sav)
Button(F_action, text='Quitter', command = Fp.destroy).pack(side=LEFT)
validOK = Button(F_action, text='Valider')
validOK.pack(side=LEFT)
validOK.bind('<Button-1>',ecrit_fic_config)
Button(F_action, text='reset', command = reset_cou).pack(side=LEFT)
F_action.pack(side=BOTTOM)

F_saisie_image=Frame(F_saisie, bg="lightblue2")
Label(F_saisie_image,bg="linen",text="application \u00E9diteur d'image",width=25, justify = RIGHT).pack(side=LEFT)
Saisie_visu = Entry(F_saisie_image, textvariable=visu_graphe, justify = LEFT, relief="sunken", borderwidth=5)
Saisie_visu.pack(side=LEFT)
F_saisie_image.pack(side=TOP)

F_saisie_ps=Frame(F_saisie, bg="lightblue2")
Label(F_saisie_ps, bg="ivory",text="application \u00E9diteur postscript",width=25, justify = RIGHT).pack(side=LEFT)
Saisie_visu_ps = Entry(F_saisie_ps, textvariable=visu_ps, justify = LEFT, relief="sunken", borderwidth=5)
Saisie_visu_ps.pack(side=LEFT)
F_saisie_ps.pack(side=TOP)

F_rep_sav=Frame(F_saisie, bg="lightblue2")
Label(F_rep_sav, bg="ivory",text="R\u00E9pertoire sauvegarde par d\u00E9faut",width=25, justify = RIGHT).pack(side=LEFT)
Saisie_rep_sav = Entry(F_rep_sav, textvariable=rep_sav, justify = LEFT, relief="sunken", borderwidth=5)
Saisie_rep_sav.pack(side=LEFT)
F_rep_sav.pack(side=TOP)
F_saisie.pack(side=BOTTOM)

F_couleur_chaine=Frame(F_couleur)
F_couleur_chaine.configure(bg="lightblue2",width=500, height=40)
Label(F_couleur_chaine, bg="linen", text="Chaine Mesure",width=13).pack(side=LEFT)
option_couleur_chaine= OptionMenu(F_couleur_chaine, var_chaine,*liste_couleur, command=change_cou)
option_couleur_chaine.pack(side=LEFT)
fond_chaine = Canvas(F_couleur_chaine, width=100, height=30, background='red')
try :
    rect_chaine=fond_chaine.create_rectangle(0,0,100,30, fill=var_chaine.get())
except TclError :
    print("ERREUR : %s couleur non connue!, utilisation couleur par defaut." % (var_chaine.get()))
    var_chaine.set(liste_couleur[1])
    rect_chaine=fond_chaine.create_rectangle(0,0,100,30, fill=var_chaine.get())
fond_chaine.pack(side=RIGHT, expand=1, anchor="e")
F_couleur_chaine.pack(side=TOP, fill="both")

F_couleur_vect0=Frame(F_couleur)
F_couleur_vect0.configure(bg="lightblue2",width=500, height=40)
Label(F_couleur_vect0,bg="linen", text="Vecteur initiale",width=13).pack(side=LEFT)
option_couleur_vect0= OptionMenu(F_couleur_vect0, var_vect0,*liste_couleur,command=change_cou)
option_couleur_vect0.pack(side="left")
fond_vect0 = Canvas(F_couleur_vect0, width=100, height=30, background='red')
F_couleur_vect0.pack(side=TOP, fill="both")
fond_vect0.pack(side=RIGHT)
try :
    rect_vect0=fond_vect0.create_rectangle(0,0,100,30, fill=var_vect0.get())
except TclError :
    print("ERREUR : %s couleur non connue!, utilisation couleur par defaut." % (var_vect0.get()))
    var_vect0.set(liste_couleur[2])
    rect_vect0=fond_vect0.create_rectangle(0,0,100,30, fill=var_vect0.get())

F_couleur_vect1=Frame(F_couleur)
F_couleur_vect1.configure(bg="lightblue2",width=500, height=40)
Label(F_couleur_vect1, bg="linen",text="Vecteur inter",width=13).pack(side=LEFT)
option_couleur_vect1= OptionMenu(F_couleur_vect1, var_vect1,*liste_couleur,command=change_cou)
option_couleur_vect1.pack(side="left")
fond_vect1 = Canvas(F_couleur_vect1, width=100, height=30, background='red')
F_couleur_vect1.pack(side=TOP, fill="both")
fond_vect1.pack(side=RIGHT)
try :
    rect_vect1=fond_vect1.create_rectangle(0,0,100,30, fill=var_vect1.get())
except TclError :
    print("ERREUR : %s couleur non connue!, utilisation couleur par defaut." % (var_vect1.get()))
    var_vect1.set(liste_couleur[3])
    rect_vect1=fond_vect1.create_rectangle(0,0,100,30, fill=var_vect1.get())

F_couleur_vectF=Frame(F_couleur)
F_couleur_vectF.configure(bg="lightblue2",width=500, height=40)
Label(F_couleur_vectF, bg="linen",text="Vecteur final",width=13).pack(side=LEFT)
option_couleur_vectF= OptionMenu(F_couleur_vectF, var_vectF,*liste_couleur,command=change_cou)
option_couleur_vectF.pack(side="left")
fond_vectF = Canvas(F_couleur_vectF, width=100, height=30, background='red')
F_couleur_vectF.pack(side=TOP, fill="both")
fond_vectF.pack(side=RIGHT)
try :
    rect_vectF=fond_vectF.create_rectangle(0,0,100,30, fill=var_vectF.get())
except TclError :
    print("ERREUR : %s couleur non connue!, utilisation couleur par defaut." % (var_vectF.get()))
    var_vectF.set(liste_couleur[0])
    rect_vectF=fond_vectF.create_rectangle(0,0,100,30, fill=var_vectF.get())

F_couleur_Fonc=Frame(F_couleur)
F_couleur_Fonc.configure(bg="lightblue2",width=500, height=40)
Label(F_couleur_Fonc,bg="linen", text="Fonction cadre",width=13).pack(side=LEFT)
option_couleur_Fonc= OptionMenu(F_couleur_Fonc, var_Fonc,*liste_couleur,command=change_cou)
option_couleur_Fonc.pack(side="left")
fond_Fonc = Canvas(F_couleur_Fonc, width=100, height=30, background='red')
F_couleur_Fonc.pack(side=TOP, fill="both")
fond_Fonc.pack(side=RIGHT)
try :
    rect_Fonc=fond_Fonc.create_rectangle(0,0,100,30, fill=var_Fonc.get())
except TclError :
    print("ERREUR : %s couleur non connue!, utilisation couleur par defaut." % (var_Fonc.get()))
    var_Fonc.set(liste_couleur[5])
    rect_Fonc=fond_Fonc.create_rectangle(0,0,100,30, fill=var_Fonc.get())

F_couleur_FoncT=Frame(F_couleur)
F_couleur_FoncT.configure(bg="lightblue2",width=500, height=40)
Label(F_couleur_FoncT,bg="linen", text="Fonction texte",width=13).pack(side=LEFT)
option_couleur_FoncT= OptionMenu(F_couleur_FoncT, var_FoncT,*liste_couleur,command=change_cou)
option_couleur_FoncT.pack(side="left")
fond_FoncT = Canvas(F_couleur_FoncT, width=100, height=30, background='red')
F_couleur_FoncT.pack(side=TOP, fill="both")
fond_FoncT.pack(side=RIGHT)
try :
    rect_FoncT=fond_FoncT.create_rectangle(0,0,100,30, fill=var_FoncT.get())
except TclError :
    print("ERREUR : %s couleur non connue!, utilisation couleur par defaut." % (var_FoncT.get()))
    var_FoncT.set(liste_couleur[4])
    rect_FoncT=fond_FoncT.create_rectangle(0,0,100,30, fill=var_FoncT.get())

F_couleur.pack(side=TOP)
Fp.mainloop()

