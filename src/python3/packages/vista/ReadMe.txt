########### Package Vista ############


Vista est conçu selon le pattern modèle-vue-controle.

Arborescence
------------

modele : gère toute la partie données

    classes.py
        contient les classes utilisées pour les données. Le modèle de données est arborescent :
            Document
                |_ Pages(s)
                     |_ Graphique(s)
                            |_ Trace(s)

    config.py
        dans vista on appelle config l'ensemble des attributs des éléments du document. (c'est historique, lié au fait que les premières specs
        de vista ne parlaient pas d'ihm mais uniquement de création de fichiers de config de documents pdf ou png).
        Il s'agit par exemple de l'orientation d'une page, de la couleur d'un tracé, de l' épaisseur d'un trait, ...
        Les différents attributs sont décrits et stockés dans un dictionnaire.
        Cette config est sauvegardée au format json dans des fichiers suffixés '.vista'
        On définit une classe générique Config et une classe par type d'élément qui hérite de Config (ConfigDocument, ConfigPage, ...)

    date.py
        module qui contient des fonctions qui font des opérations sur les dates. 
        vistadate est de forme AAAAMMJJHHMMSS
    

vue : gère toute la partie affichage

    interface.py
        contient le code de l'ihm (Gtk3) dans la classe UiVista. L'interface 'statique' est construite avec glade (fichier vista.glade)

    vistagraph.py
        contient le code d'affichage des graphiques (matplotlib). Les classes graphiques ont un modèle arborescent :
            Gdocument
                |_ Gpages(s)
                     |_ Ggraphique(s)
                            |_ Gtrace(s)
        Pour les graphiques et les traces, des classes spécialisées héritent de Ggraphique et Gtrace (GgraphiqueST, GgraphiqueHisto, GgraphiquePlotXY,...
        GtraceST, GtraceHisto, GtracePlotXY,...)

    vistarose.py
        module spécifique aux roses des vents, trouvé sur le web et légèrement adapté

    vistaagencement.py
        module qui gère l'ihm d'agencement des graphiques dans une page.

    vistacrash.py
        module qui affiche une boite de dialogue en cas de plantage avec traceback.

        
controle : gère la dynamique de linterface

    controles.py
        la classe Controles positionne les callbacks sur les widgets.


config : contient les éléments de configuration du logiciel

    vecteurs : pour chaque plateforme contient l'ensemble des noms des vecteurs possibles.


icons : contient les icones utilisés par vista


doc : contient les fichiers utilisés pour la documentation urilisateur en ligne. Cette doc est affichée dans vista via la librairie WebKit2
      qui permet d'afficher du html/css


main.py : programme principal (renommé vista sous $AIDA_HOME/bin par le makefile).
          Il construit le modèle la vue et le controle et lance la main_loop Gtk.
          Il gère aussi le mode "batch", sans interface : il construit alors juste le modèle et lance un tracé au format souhaité. (pas de code particulier
          pour ça, on change juste le backend).


Protocole d'ajout d'une propriété à un élément
----------------------------------------------

1 - Ajouter la définition de la propriété dans le fichier modele/config.py dans la classe correspondant à l'élément (ConfigDocument, ConfigPage, ...)
2 - Ajouter les éléments d'interface pour modifier cette propriété dans le fichier vue/vista.glade en utilisant le logiciel glade
3 - Positionner les callbacks sur les widgets dans le fichier controle/controles.py (définier la fonction callback par ex onMyButtonPress et positionner le
    callback sur le widget avec un connect). Les callbacks sont regroupés par éléments (Document, Page, Graphique ou Trace). Dans ce callback, on met généralement 
    à jour l'objet Config associé à l'élément.
4 - Mettre à jour la fonction d'update de l'interface associée à l'élément dans controle/controles.py (updateUiDocument, updateUiPage, updateUiGraphique, ...) : 
    cette fonction est appelée à chaque fois que l'on sélectionne un élément dans le treeview pour mettre à jour l'interface de configuration de l'élément en bas à gauche dans l'ihm.


Installation du package
-----------------------

make install sous $AIDA_HOME/src/python3
Le main "vista" est installé sous $AIDA_HOME/bin
Le package est installé sous $AIDA_HOME/lib/python3.x vista



