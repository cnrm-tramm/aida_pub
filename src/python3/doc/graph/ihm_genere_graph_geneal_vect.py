#!/usr/bin/env python3

import os
import pwd
import configparser
from subprocess import Popen, PIPE
from tkinter import *

def who_am_i():
    """ Essaie de savoir qui on est, dans tous les cas...
    """
    try:
        user = pwd.getpwuid(os.getuid())[0]
    except Exception:
        try:
            user = os.environ.get("USER")
        except Exception:
            user = os.getlogin()
    return user

def lance_config() :
    """ Lance l'ihm de saisie des preferencese.
    """
    graphe.config(state = "disable")
    visu.config(state = "disable")
    cr_lance_config = os.system("ihm_config_graph_geneal_vect.py")
    print("SORTIE")
    if cr_lance_config == 0 :
        lit_fic_preference()

def lit_fic_preference() :
    """ Lecture du fichier de config si il existe,
        et initialisation des preferences.
    """
    global AH
    global appl_visu_graphe
    global appl_visu_ps
    global repertoire_sav
    config_couleur = {}
    nom_fic_config = AH + "/config/gengraphvect.cfg"
    repertoire_sav = "/tmp"

    appl_visu_graphe = "xdg-open"
    appl_visu_ps = "xdg-open"

    try :
        fic_conf = open(nom_fic_config,"r")
    except IOError:
        commente.insert(END,"INFORMATION : Pas de fichier de config, utilisation des donn\u00E9es par d\u00E9faut")
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
        commente.insert(END,"INFORMATION : Lecture du fichier de config : OK.")

def affiche_aide (nom_fic_doc) :
    """ Affiche la doc utilisateur du programme
        La docutentation est en pdf.
        Utilise l'applicatif xpdf ou evince ou acroread
    """

    visual_pdf=["xpdf","evince","acroread"]
    for visu in visual_pdf :
        cmd = "which " + visu + " > /dev/null"
        Retour_cmd = os.system(cmd)

        if Retour_cmd != 0 :
            print("Utilitaire " + visu + " absent.")
        else :
            ## cmd_visu = visu + " " + AH + "/doc/oper/" + nom_fic_doc + "&"
            cmd_visu = visu + " " + AH + "/doc/" + nom_fic_doc + "&"
            os.system(cmd_visu)
            break

     
def effacer_log () :
    """ Efface le contenu de la fenetre log.
    """
    commente.delete(0, END)

def sav_repertoire (event) :
    """ sauvegarde le repertoire selectionne
    """
    
    global  irep

    irep = repertoire.curselection()
    rep_en_cours = repertoire.get(irep)

def lit_repertoire (event) :
    """ Recherche la liste des repertoires dans
        un repertoire selectionne
    """

    index = repertoire.curselection()
    rep = repertoire.get(index)
    if rep == ".." :
        rep2 = repertoire.get(1)
        index = rep2.rfind("/")
        if index == 0 :
            rep = "/"
        else :
            rep = rep2[0:index]
    try :
        liste_data = os.listdir(rep)
        liste_data.sort()
    except OSError: 
        commente.insert(END, "ERREUR : R\u00E9pertoire interdit")
    else :
        repertoire.delete(0, END)
        repertoire.insert(END,"..")
        repertoire.insert(END, rep)
        for dir in liste_data :
            if dir[0] != "." and os.path.isdir(os.path.join(rep, dir)) :
                repertoire.insert(END, os.path.join(rep, dir))
            repertoire.selection_set(first=1)

def filtre_vecteur (event) :
    """ filtre les vecteurs a partir d'une requete
    """

    vecteur.delete(0, END)
    index = periode.curselection()
    PER = periode.get(index)
    liste_data = os.listdir(EP_DATA +"/" + PLATF + "/" + AN  + "/" + PER)
    liste_data.sort()
    list_recherche = Cher_vect.get().split("*")
    NB_CHER = len(list_recherche)
    for vect in liste_data :
        if vect[0] != "." :
            ln_car = len(list_recherche[0])
            if list_recherche[0] == vect[0:ln_car] :
                ln_car = len(list_recherche[NB_CHER-1])
                if len(list_recherche) == 2 :
                    if list_recherche[NB_CHER-1] == vect[-ln_car-4:-4] :
                        vecteur.insert(END, vect[:-4])
                if len(list_recherche) == 3 :
                    if  list_recherche[NB_CHER-1] == vect[-ln_car-4:-4] \
                                    and list_recherche[1] in vect :
                        vecteur.insert(END, vect[:-4])

def visu_graphe () :
    """ Lance la visualisation du graphe sur l'ecran
    """

    user = who_am_i()
    Niveau_graphe =  var.get()
    sens_graphe = var3.get()
    Niveau_in = Niveau_graphe[0:1]
    if Niveau_in >= "4" :
        nomfic = VECTEUR + "." + user
        nomficext = VECTEUR + "." + user + ".asc"
    else :
        nomfic = VECTEUR + "." + user
        nomficext = VECTEUR + "." + user + "." + var2.get()

    prg = "gengraphvect.py -a "
    arg =  acq_id + " -n "+ Niveau_in + " -o " + var2.get() + " -s " + sens_graphe + " -f " + nomfic + " " + VECTEUR
    cmd = prg + arg 
    print(cmd)
    retour = Popen(cmd, stderr=PIPE, shell=True)
    f_out, f_err = retour.communicate()

    if "ERREUR" not in f_err.decode():
        if Niveau_in >= "4" :
#            commente.insert(END,"Liste vecteurs sur stderr.")
            os.system("(gedit " + repertoire_sav + "/" + nomficext + " 2> /dev/null;rm -f " + repertoire_sav + "/" +  VECTEUR + ".asc)")
        elif "fig" in var2.get() :
            os.system("(xfig " + repertoire_sav + "/" + nomficext + " 2> /dev/null;rm -f " + repertoire_sav + "/" + VECTEUR + "_n" + Niveau_in + "*.*)")
        elif var2.get() == "ps" :
            os.system("(" + appl_visu_ps + " " + repertoire_sav + "/" + nomficext + " 2> /dev/null)")
        else :
            os.system("(" + appl_visu_graphe + " " + repertoire_sav + "/" + nomficext + " 2> /dev/null)")
        os.system("rm -f /tmp/" +  VECTEUR + ".dot")

    f_err_ligne = f_err.decode().split("\n")
    for ligne in f_err_ligne :
        commente.insert(END, ligne)

def donne_nom_graphe () :
    """ Cree une boite de dialogue pour demander le nom
        de sauvegarde et repertoire de depot du graphe
    """
    global repertoire
    global HOME
    global nom_fichier
    global Fsav

    HOME = os.getenv('HOME')
    if not HOME:
        print("FATAL : $HOME non d\u00E9fini", file=sys.stderr)
        sys.exit(100)

# recuperation des repertoire sous $HOME
    liste_data = os.listdir(HOME)
    liste_data.sort()

    Niveau_graphe =  var.get()
    Niveau_in = Niveau_graphe[0:1]

# Trace de la boite de dialogue enregistrement
    Fsav = Toplevel()
    Fsav.title("Sauvegarde dans un fichier.")
    Fsav.minsize(width=300, height=300)
    Fsav.maxsize(width=400, height=300)
    Fsav.resizable(width=YES, height=NO)
    Fsav.configure(bg="lightblue2")

   # Recherche repetoire
    Fsav_rep = LabelFrame(Fsav, text="Choix repertoire.")
    Fsav_rep.configure(bg="lightblue2")
    repertoire = Listbox(Fsav_rep)
    scrollbar_rep = Scrollbar(Fsav_rep)
    repertoire.config(yscrollcommand=scrollbar_rep.set,  width=40)
    scrollbar_rep.config(command=repertoire.yview)
    repertoire.pack(side=LEFT)
    scrollbar_rep.pack(side=LEFT, fill=Y)
    Fsav_rep.pack()
    repertoire.bind("<Double-Button-1>", lit_repertoire)

    Fsav_nom_fic = LabelFrame(Fsav, text="Choix fichier.")
    Fsav_nom_fic.configure(bg="lightblue2")
    nom_fichier = Entry(Fsav_nom_fic, justify = LEFT, \
                    relief="sunken", borderwidth=5, width=40)
    nom_fichier.pack(side=LEFT)
    nom_fichier.bind("<Button-1>", sav_repertoire)
    if Niveau_in == "4" :
        nomfic = VECTEUR
    else :
        nomfic = VECTEUR + "_n" + Niveau_in + "_" +  var3.get() 
#        nomfic = VECTEUR + "_n" + Niveau_in
    nom_fichier.insert(0, nomfic)
    Fsav_nom_fic.pack()

    Fsav_action = LabelFrame(Fsav, text="Choix Action.")
    Fsav_action.configure(bg="lightblue2")

    Button(Fsav_action, text="Quitter", command=Fsav.destroy).pack(side=LEFT)
    Button(Fsav_action, text="Lancer", command=lance_graphe).pack(side=LEFT)
    Fsav_action.pack()

    repertoire.insert(END, "..")
    repertoire.insert(END, HOME)
    for dir in liste_data :
        if dir[0] != "." and os.path.isdir(os.path.join(HOME, dir)) :
            repertoire.insert(END, os.path.join(HOME, dir))
        repertoire.selection_set(first=1)


def lance_graphe () :
    """ Lance la creation du graphe dans un fichier
    """
    global nom_fichier
    global Fsav

    try :
        index = repertoire.curselection()[0]
        rep = repertoire.get(index)
    except IndexError:
        if ( irep ) > 0 :
            index = irep
            rep = repertoire.get(index)
#            commente.insert(END, u"ATTENTION : S\u00E9lectionner un r\u00E9pertoire de d\u00E9pot")
        else :
            rep = HOME

    nom_fic = nom_fichier.get()
    sens_graphe = var3.get()
    Niveau_graphe =  var.get()
    Niveau_in = Niveau_graphe[0:1]

    if int(Niveau_in) >= 4 :
        ext_fic = "asc"
    else :
        ext_fic = var2.get() 

    prg = "gengraphvect.py -a "
    arg =  acq_id + " -n "+ Niveau_in + " -o " + var2.get() + " -s " + sens_graphe + " -f " + nom_fic + " " + VECTEUR
    cmd = prg + arg
    file = VECTEUR + "_n"+Niveau_in+"."+ ext_fic
    print(cmd)
    if nom_fic != "" :
        nomfic = rep + "/" + nom_fic 
    else :
        commente.insert(END,"INFORMATION : Utilisation nomenclature par d\u00E9faut")
        nomfic = rep + "/" + file
    cmt_sav = "INFORMATION : Cr\u00E9tion du fichier : " + nomfic
    commente.insert(END, cmt_sav)
    retour = Popen(cmd, stderr=PIPE, shell=True)
    f_out, f_err = retour.communicate()
    commente.insert(END, f_err)
    os.system("rm -f /tmp/" +  VECTEUR + ".dot")
    os.system("mv -f " + repertoire_sav + "/" + nom_fic + "." + ext_fic + " " + nomfic + "." + ext_fic)
    F_term = Toplevel()
    F_term.title("Information.")
    F_term.configure(bg="lightblue2")
    Label(F_term, text='Elaboration terminee', bg="lightblue2", fg='black' ).pack(padx=10, pady=10)
    quit = Button(F_term, text='Quitter', command = F_term.destroy)
    quit.pack()
    Fsav.destroy()

    
def recup_vecteur(event):
    """  Selectionne le vecteur a etudier
    """
    global VECTEUR
    index = vecteur.curselection()
    try :
        VECTEUR = vecteur.get(index)
    except TclError:
        commente.insert(END, "ATTENTION : Fen\u00EAtre non active.")
    else :
        visu.config(state = "normal")
        graphe.config(state = "normal")

def recup_periode(event):
    """ Recherche les vecteurs disponibles pour un acq_id donnee
    """
    global PER
    vecteur.delete(0, END)
    index = periode.curselection()
    try : 
        PER = periode.get(index)
    except TclError:
        commente.insert(END, "ATTENTION : Fen\u00EAtre non active.")
    else :
        path_TO_acqid()
        liste_data = os.listdir(EP_DATA +"/" + PLATF + "/" + AN  + "/" + PER)
        liste_data.sort()
        for vect in liste_data :
            if vect[0] != "." :
                vecteur.insert(END, vect[:-4])
        Cher_vect.config(state = "normal")
        visu.config(state = "disable")
        graphe.config(state = "disable")

def recup_annee(event):
    """ Recherche les periodes pour une plateforme et annee donnees
    """
    global AN

    nb_rep_rejete = 0
    periode.delete(0, END)
    vecteur.delete(0, END)
    index = annee.curselection()
    try : 
        AN = annee.get(index)
    except TclError:
        commente.insert(END, "ATTENTION : Fen\u00EAtre non active.")
    else :
        liste_data = os.listdir(EP_DATA +"/" + PLATF + "/" + AN)
        liste_data.sort()
        for per in liste_data :
            try :
                pertmp = int(per)
            except ValueError:
                nb_rep_rejete = nb_rep_rejete + 1
#                print >> sys.stderr, u"R\u00E9pertoire rejet\u00E9, pas une p\u00E9riode"
            else :
                periode.insert(END, per)
        Cher_vect.config(state = "disable")
        graphe.config(state = "disable")
        visu.config(state = "disable")
        if ( nb_rep_rejete > 0 ) :
            cmt = "INFORMATION : " + PLATF + "/" + AN + " : " + str(nb_rep_rejete) + " p\u00E9riode(s) rejet\u00E9e(s), pas un entier"
            commente.insert(END, cmt)

def recup_platform(event):
    """ Recherche les annee pour une plateforme donnee
    """
    global PLATF

    nb_rep_rejete = 0
    annee.delete(0, END)
    periode.delete(0, END)
    vecteur.delete(0, END)
    index = plateforme.curselection()
    try :
        PLATF = plateforme.get(index)
    except TclError:
        commente.insert(END, "ATTENTION : Fen\u00EAtre non active.")
    else :
        liste_data = os.listdir(EP_DATA +"/" + PLATF)
        liste_data.sort()
        for yyyy in liste_data :
            try :
                aaaa = int(yyyy)
            except ValueError:
                nb_rep_rejete = nb_rep_rejete + 1
#                print >> sys.stderr, u"Repertoire rejet\u00E9, pas une ann\u00E9e"
            else :
                annee.insert(END, yyyy)
        graphe.config(state = "disable")
        visu.config(state = "disable")
        Cher_vect.config(state = "disable")
        if ( nb_rep_rejete > 0 ) :
            cmt = "INFORMATION : " + PLATF + " : " + str(nb_rep_rejete) + " r\u00E9pertoire(s) rejet\u00E9(s), pas une ann\u00E9e"
            commente.insert(END, cmt)

def path_TO_acqid():
    """ Renvoie l identifiant acq_id en fonction du repertoire de depot
    """
    global acq_id

    abrv = ""
    acq_id = ""
    PROFIL=os.getenv('AIDA_PROFIL', '')
    path = os.path.join (os.getenv ('AIDA_HOME'), 'profils', PROFIL, 'plate-formes')

    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg_file = open(path, encoding="ISO-8859-1")
    cfg.readfp(cfg_file)
    for section in cfg.sections():
        if  PLATF == section :
            abrv = cfg.get(section, 'abrev') 
            break
                       
    acq_id = abrv + AN[2:4] + PER
    cmt = "INFORMATION : acq_id utilis\u00E9 : " + acq_id 
    commente.insert(END, cmt)


global commente
global AH

# Trace de la boite de dialogue pere
#-----------------------------------

Fp = Tk()
Fp.title("Elaboration Arbre G\u00E9n\u00E9alogique d'un vecteur.")
Fp.minsize(width=800, height=300)
Fp.maxsize(width=1000, height=500)
Fp.resizable(width=YES, height=YES)
Fp.configure(bg="lightblue2")

# Creation de la barre de menu
#-----------------------------
MENU1 = Menu(Fp)
# Creation du menu fichier:
FICHIER = Menu(MENU1, tearoff=0)
MENU1.add_cascade(label="Fichier", menu=FICHIER)
FICHIER.add_command(label="configuration", command=lance_config)
FICHIER.add_command(label="Quitter", command=Fp.quit)
AIDE = Menu(MENU1, tearoff=0)
MENU1.add_cascade(label="Aide", menu=AIDE)
nom_doc="genere_graph_geneal_vect_utilisateur.pdf"
AIDE.add_command(label="Doc Utilisateur", command=lambda : affiche_aide("genere_graph_geneal_vect_utilisateur.pdf"))
AIDE.add_command(label="Doc Technique", command=lambda : affiche_aide("genere_graph_geneal_vect_technique.pdf"))
# afficher le menu
Fp.config(menu=MENU1)

# Creation des frames de Fp 
#--------------------------
F_VECT = LabelFrame(Fp, text="Choix Vecteur.")
F_VECT.configure(bg="lightblue2")

F_TYPE_GRAPHE = LabelFrame(Fp, text="Choix Graphe.")
F_TYPE_GRAPHE.configure(bg="lightblue2")

F_ACTION = LabelFrame(Fp, text="Choix Action.")
F_ACTION.configure(bg="lightblue2")

F_COMMENT = LabelFrame(Fp, text="Log.")
F_COMMENT.configure(bg="orange")

# Creation des listbox pour la frame choix vecteur
#-------------------------------------------------
#listbox des plateformes
plateforme = Listbox(F_VECT, selectmode=SINGLE, exportselection=0)
SCROLLBAR_PLTF = Scrollbar(F_VECT)
plateforme.config(yscrollcommand=SCROLLBAR_PLTF.set,  width=20)
SCROLLBAR_PLTF.config(command=plateforme.yview)

#listbox des annees
annee = Listbox(F_VECT, selectmode=SINGLE, exportselection=0)
SCROLLBAR_ANNEE = Scrollbar(F_VECT)
annee.config(yscrollcommand=SCROLLBAR_ANNEE.set,  width=15)
SCROLLBAR_ANNEE.config(command=annee.yview)

#listbox des periodes de mesures
periode = Listbox(F_VECT, selectmode=SINGLE, exportselection=0)
SCROLLBAR_PERIODE = Scrollbar(F_VECT)
periode.config(yscrollcommand=SCROLLBAR_PERIODE.set, width=15)
SCROLLBAR_PERIODE.config(command=periode.yview)

#listbox des vecteurs
vecteur = Listbox(F_VECT, selectmode=SINGLE, exportselection=0)
SCROLLBAR_VECT = Scrollbar(F_VECT)
vecteur.config(yscrollcommand=SCROLLBAR_VECT.set, width=30)
SCROLLBAR_VECT.config(command=vecteur.yview)

# Creation des boutons pour la frame choix graphe
#------------------------------------------------
liste_type_graphe = ["0", "1", "2", "3", "4"]
liste_type_graphe = ["0 : Vecteurs + Capteurs",\
                "1 : Vecteurs + Fonctions",\
                "2 = 1 + Arguments",\
                "3 = 2 + Capteurs",\
                "4 : capteurs uniquement (ascii)",\
                "9 : Liste vecteurs "]
var = StringVar()
var.set(liste_type_graphe[0])
option_graphe = OptionMenu(*(F_TYPE_GRAPHE, var) + \
                tuple(liste_type_graphe))

liste_type_sortie = ["png", "gif", "svg", "ps","fig"]
var2 = StringVar()
var2.set(liste_type_sortie[0])
option_sortie = OptionMenu(*(F_TYPE_GRAPHE, var2) + \
                tuple(liste_type_sortie))

liste_sens_graphe = ["asc", "desc"]
var3 = StringVar()
var3.set(liste_sens_graphe[0])
option_sens = OptionMenu(*(F_TYPE_GRAPHE, var3) + \
                tuple(liste_sens_graphe))

# Creation des boutons pour la frame choix action
#------------------------------------------------
# bouton quitter
quitter = Button(F_ACTION, text='Quitter', command = Fp.destroy)

# bouton visualisation graphe
visu = Button(F_ACTION, text='Visualiser', command = visu_graphe)

# bouton tracer graphe
graphe = Button(F_ACTION, text='Sauvegarder', command = donne_nom_graphe)

# bouton effacer log
efface_log = Button(F_ACTION, text='Effacer log', command = effacer_log)

# Creation de la listbox de la frame log
#---------------------------------------
#listbox des logs
commente = Listbox(F_COMMENT, selectmode=SINGLE, exportselection=0)
SCROLLBAR_COMMENT = Scrollbar(F_COMMENT)
commente.config(yscrollcommand=SCROLLBAR_COMMENT.set, width=100)
SCROLLBAR_COMMENT.config(command=commente.yview)

# Mise en forme de la boite de dialogue
#--------------------------------------

plateforme.pack(side=LEFT)
SCROLLBAR_PLTF.pack(side=LEFT, fill=Y)
annee.pack(side=LEFT)
SCROLLBAR_ANNEE.pack(side=LEFT, fill=Y)
periode.pack(side=LEFT)
SCROLLBAR_PERIODE.pack(side=LEFT, fill=Y)
vecteur.pack(side=LEFT)
SCROLLBAR_VECT.pack(side=LEFT, fill=Y)
Label(F_VECT, text="Recherche vecteur :", font = ("Arial", 10,"italic")).pack(side=TOP, expand=1, anchor="s")
Cher_vect = Entry(F_VECT, justify = CENTER, relief="sunken", borderwidth=5)
Cher_vect.pack(side=LEFT, expand=1, anchor="n")
Cher_vect.bind('<Return>' , filtre_vecteur)
Cher_vect.config(state = "disable")

Label(F_TYPE_GRAPHE, text="sens graphe ").pack(side=LEFT, padx=3)
option_sens.pack(side=LEFT, ipadx=2)
Label(F_TYPE_GRAPHE, text="type graphe ").pack(side=LEFT, padx=3)
option_graphe.pack(side=LEFT, ipadx=2)
Label(F_TYPE_GRAPHE, text="format sortie ").pack(side=LEFT, padx=3)
option_sortie.pack(side=LEFT, ipadx=2)

quitter.pack(side=LEFT, padx=10, pady=10, ipadx=10)
visu.pack(side=LEFT, padx=10, pady=10, ipadx=10)
visu.config(state = "disable")
graphe.pack(side=LEFT, padx=10, pady=10, ipadx=10)
graphe.config(state = "disable")
efface_log.pack(side=LEFT, padx=10, pady=10, ipadx=10)

commente.pack(side=LEFT, padx=0, pady=10, ipadx=10)
SCROLLBAR_COMMENT.pack(side=LEFT, fill=Y, padx=0, pady=10, ipadx=0 )

F_VECT.pack()
F_TYPE_GRAPHE.pack()
F_ACTION.pack()
F_COMMENT.pack()

plateforme.bind("<<ListboxSelect>>", recup_platform )
annee.bind("<<ListboxSelect>>", recup_annee )
periode.bind("<<ListboxSelect>>", recup_periode )
vecteur.bind("<<ListboxSelect>>", recup_vecteur )

# Declaration et initialisation des variables globales

AH = os.getenv('AIDA_HOME')
if not AH:
    cmt = "ERREUR : AIDA_HOME non d\u00E9fini"
    cmt2 = "       Quitter, initialiser la variable AIDA_HOME avant de relancer l'application."
    AH = " "
    print("FATAL : AIDA_HOME non d\u00E9fini", file=sys.stderr)
    commente.insert(END, cmt)
    commente.insert(END, cmt2)
else :
    EP_DATA = os.getenv('AIDA_DATA')
    if EP_DATA is None :
        EP_DATA = AH + "/data"

    lit_fic_preference()

# recuperation de la liste des plateformes existantes sous AIDA_HOME/data
    liste_data = os.listdir(EP_DATA)
    liste_data.sort()

    for pltf in liste_data :
        plateforme.insert(END, pltf)

# Recherche de l'utilitaire dot pour tracer l'arbre
cmd = "which dot > /dev/null"
Retour_cmd = os.system(cmd)

if Retour_cmd != 0 :
    cmt = "ERREUR : L'utilitaire dot (de Graphviz) absent."
    cmt2 = "       Quitter, installer dot ( Information sur http://www.graphviz.org/.)"
    print("---------------------------------------------------", file=sys.stderr)
    print(" FATAL ERREUR : L'utilitaire dot (de Graphviz) \
doit-etre install\u00E9 sur votre serveur.", file=sys.stderr)
    print(" Information sur http://www.graphviz.org/.", file=sys.stderr)
    print("---------------------------------------------------", file=sys.stderr)
    commente.insert(END, cmt)
    commente.insert(END, cmt2)
    plateforme.config(state = "disable")

Fp.mainloop()
