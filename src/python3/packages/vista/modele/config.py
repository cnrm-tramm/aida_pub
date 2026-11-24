#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
    ##################################### Config

    Dans vista on appelle config l'ensemble des attributs des éléments du document.
    Il s'agit par exemple de l'orientation d'une page, de la couleur d'un tracé, de l' épaisseur d'un trait, ...
    Les différents attributs sont décrits et stockés dans un dictionnaire.
    Cette config est sauvegardée au format json dans des fichiers suffixés '.vista'
 
    On définit une classe générique Config et une classe par type d'élément qui hérite de Config.
"""
class Config :
    """
        Classe qui définit une configuration
    """
    def __init__(self, config) :
        self.typeConfig = ""
        self.values = config
        self.desc = {}
        
    def check(self):
        """
            vérifie les valeurs de la config
        """
        for key in self.values :
            # parametre connu ?
            if not key in list(self.desc.keys()) :
                print(("Avertissement : le parametre {} n'est pas ou plus supporté par vista pour la config {}.".format(key, self.typeConfig)))
                continue
            # controle du type : on convertit le unicode en utf-8
            if isinstance(self.values[key], str):
                self.values[key] = self.values[key]
            if ( not type(self.values[key]) == type(self.desc[key]["default"]) ) :                
                print(("Erreur de config : le parametre {} de la config {} n'est pas de type {}.".format(key, self.typeConfig, type(self.desc[key]["default"]))))
                return False
            # controle de la valeur
            if self.desc[key]["authorized"] != None :
                if self.values[key] in self.desc[key]["authorized"] :
                    self.desc[key]["value"] = self.values[key]
                else :
                    print(("Erreur de config : le parametre {} de la config {} a une valeur non autorisée : {} .".format(key, self.typeConfig, self.values[key])))
                    print(("Liste des valeurs possibles : {}".format(self.desc[key]["authorized"])))
                    return False
            elif self.desc[key]["mixed"] != None :
                for f in self.values[key].split(',') :
                    if not f.strip() in self.desc[key]["mixed"] :
                        print(("Erreur de config : le parametre {} de la config {} a une valeur non autorisée : {} .".format(key, self.typeConfig, self.values[key])))
                        print(("Sont autorisées les combinaisons parmi les valeurs {}".format(self.desc[key]["mixed"])))
                        return False
                self.desc[key]["value"] = self.values[key]
            else :
                if  self.desc[key]["min"] != None :
                    if self.values[key] < self.desc[key]["min"] :
                        print(("Erreur de config : le parametre {} de la config {} a une valeur({}) inférieure au minimum autorisé({}).".format(key, self.typeConfig, self.values[key], self.desc[key]["min"])))
                        return False
                if  self.desc[key]["max"] != None :
                    if self.values[key] > self.desc[key]["max"] :
                        print(("Erreur de config : le parametre {} de la config {} a une valeur({}) supérieure au maximum autorisé({}).".format(key, self.typeConfig, self.values[key], self.desc[key]["max"])))
                        return False
            # affectation de la valeur
            # compatibilité matplotlib 1.3 -> 1.5 : * n'est plus permis pour le typeLigne, il faut 'None'
            if key == "typeLigne" and self.values[key] == '*' :
                self.values[key] = 'None'
            self.desc[key]["value"] = self.values[key]
            
        
        # affectation des valeurs par defaut à celles qui n'ont pas été positionnées
        for key in self.desc :
            if self.desc[key]["value"] is None :
                self.desc[key]["value"] = self.desc[key]["default"]
                
        return True    


"""
    ##################################### ConfigDocument
"""        
class ConfigDocument(Config):
    """
        Classe qui définit la configuration du document (hérite de Config)
    """
    def __init__(self, config) :
        Config.__init__(self, config)
        self.typeConfig = "document"
        self.desc = {
            "version_vista": {
                       "type" : "str",
                       "default" : "1.0.0",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Version de vista qui a généré le document.",
                       "serialize" : True
                       }, 
            "format": {
                       "type" : "str",
                       "default" : "pdf",
                       "authorized" : None,
                       "mixed" : ["pdf","png","ps"],
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Format(s) de sortie.",
                       "serialize" : True
                       }, 
            "dest_dir": {
                       "type" : "str",
                       "default" : "/var/tmp",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Répertoire ou seront crées les documents.",
                       "serialize" : True
                       },
            "dest_fic": {
                       "type" : "str",
                       "default" : "$CONFIG_$DATEDEBUT_$DATEFIN",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du fichier.\n\t\tMacros utilisables : \n\t\t\t$CONFIG = nom de la config\n\t\t\t$DATEDEBUT = date de début\n\t\t\t$DATEFIN = date de fin.",
                       "serialize" : True
                       },
            "pages" : {
                       "type" : "list",
                       "default" : [],
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "",
                       "serialize" : False
                       }
        }
        if not self.check() :
            raise RuntimeError("Erreur ConfigDocument : la config n'est pas correcte")


"""
    ##################################### ConfigPage
"""
class ConfigPage(Config):
    """
        Classe qui définit la configuration d'une page (hérite de Config)
    """
    def __init__(self, config) :
        Config.__init__(self, config)
        self.typeConfig = "page"
        self.desc = {
            "titre" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Titre de la page.\n\t\t\tMacros utilisables : \n\t\t\t\t$CONFIG = nom de la config\n\t\t\t\t$DATEDEBUT = date de début\n\t\t\t\t$DATEFIN = date de fin.",
                       "serialize" : True                
                       },
            "policeTitre" : {
                       "type" : "str",
                       "default" : "Sans 12",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Police du titre ex : \"Times New Roman, Italic 13.\"",
                       "serialize" : True   
                        },
            "orientation": {
                       "type" : "str",
                       "default" : "portrait",
                       "authorized" : ["portrait","landscape","horizontal", "vertical"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Orientation du document.",
                       "serialize" : True
                       },
            "logo": {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du fichier logo : si vide, pas de logo affiché.",
                       "serialize" : True
                       },
            "positionLogo": {
                       "type" : "str",
                       "default" : "hg",
                       "authorized" : ["hg","hd","bg","bd"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Position du logo : hd=haut droite, bg=bas gauche, ...",
                       "serialize" : True
                       },
            "autoAgencement" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Mise en page automatique.",
                       "serialize" : True                
                       },
            
            "graphiques" : {
                       "type" : "list",
                       "default" : [],
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "",
                       "serialize" : True
                       }
        }
        if not self.check() :
            raise RuntimeError("Erreur ConfigPage : la config n'est pas correcte")
        

"""
    ##################################### ConfigGraphique
"""            
class ConfigGraphique(Config):
    """
        Classe qui définit la configuration d'un graphique (hérite de Config)
    """
    def __init__(self, config) :
        Config.__init__(self, config)
        self.typeConfig = "graphique"
        self.desc = {
            "type" : {
                       "type" : "str",
                       "default" : "ST",
                       "authorized" : ["ST","PlotXY","Histo","Histo3D", "RDV","Hov"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Type de graphique : série temporelle, plotXY, histogramme, histogramme 3D, Rose des vents, Hovmöller",
                       "serialize" : True                
                       },
            "titre" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Titre du graphique.\n\t\tMacros utilisables : \n\t\t\t$CONFIG = nom de la config\n\t\t\t$DATEDEBUT = date de début\n\t\t\t$DATEFIN = date de fin.",
                       "serialize" : True                
                       },
            "policeTitre" : {
                       "type" : "str",
                       "default" : "Sans 12",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Police du titre ex : \"Times New Roman, Italic 13.\"",
                       "serialize" : True   
                        },
            "x": {
                       "type" : "int",
                       "default" : -1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : -1,
                       "max" : 100,
                       "value" : None,
                       "desc" : "Abscisse du coin haut-gauche du graphique dans la page [0,100]. L'origine du repère est en haut à gauche.",
                       "serialize" : True
                       },
            "y": {
                       "type" : "int",
                       "default" : -1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : -1,
                       "max" : 100,
                       "value" : None,
                       "desc" : "Ordonnée du coin haut-gauche du graphique dans la page [0,100]. L'origine du repère est en haut à gauche.",
                       "serialize" : True
                       },
            "width": {
                       "type" : "int",
                       "default" : -1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : -1,
                       "max" : 100,
                       "value" : None,
                       "desc" : "Largeur du graphique dans la page [0,100]",
                       "serialize" : True
                       },
            "height": {
                       "type" : "int",
                       "default" : -1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : -1,
                       "max" : 100,
                       "value" : None,
                       "desc" : "Hauteur du graphique dans la page [0,100]",
                       "serialize" : True
                       },
            "echelle" : {
                       "type" : "str",
                       "default" : "auto",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Echelle automatique pour l'axe des abscisses de gauche.",
                       "serialize" : True                
                       },
            "echelleAmplitude" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0.0,
                       "max" : 100.0,
                       "value" : None,
                       "desc" : "Amplitude de l'échelle pour l'axe des abscisses de gauche.",
                       "serialize" : True                
                       },
            "echelleMin" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Minimum de l'échelle pour l'axe des abscisses de gauche.",
                       "serialize" : True                
                       },
            "echelleMax" : {
                       "type" : "float",
                       "default" : 100.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Maximum de l'échelle pour l'axe des abscisses de gauche.",
                       "serialize" : True                
                       },
            "jourNuit" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Tracé des pavés grisés représentant les périodes de jour et de nuit.",
                       "serialize" : True                
                       },
            "moisAnnees" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Tracé des pavés rosés représentant les mois ou les années.",
                       "serialize" : True                
                       },                 
            "traces" : {
                       "type" : "list",
                       "default" : [],
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "",
                       "serialize" : False
                       },
            "x=y" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "\tTracé de la droite x=y.",
                       "serialize" : True                
                       },
            "echelleDroite" : {
                       "type" : "str",
                       "default" : "auto",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Echelle automatique pour l'axe de droite.",
                       "serialize" : True                
                       },
            "echelleAmplitudeDroite" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0.0,
                       "max" : 100.0,
                       "value" : None,
                       "desc" : "Amplitude de l'échelle pour l'axe de droite.",
                       "serialize" : True                
                       },
            "echelleMinDroite" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Minimum de l'échelle pour l'axe de droite.",
                       "serialize" : True                
                       },
            "echelleMaxDroite" : {
                       "type" : "float",
                       "default" : 100.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Maximum de l'échelle pour l'axe de droite.",
                       "serialize" : True                
                       },
                    
            "echelleBas" : {
                       "type" : "str",
                       "default" : "auto",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Echelle automatique pour l'axe du bas.",
                       "serialize" : True                
                       },
            "echelleAmplitudeBas" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0.0,
                       "max" : 100.0,
                       "value" : None,
                       "desc" : "Amplitude de l'échelle pour l'axe du bas.",
                       "serialize" : True                
                       },
            "echelleMinBas" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Minimum de l'échelle pour l'axe du bas.",
                       "serialize" : True                
                       },
            "echelleMaxBas" : {
                       "type" : "float",
                       "default" : 100.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Maximum de l'échelle pour l'axe du bas.",
                       "serialize" : True                
                       },
            "uniteGauche" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage de l'unité sur l'axe gauche.",
                       "serialize" : True                
                       },
            "uniteDroite" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage de l'unité sur l'axe droit.",
                       "serialize" : True                
                       },
            "uniteBas" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage de l'unité sur l'axe du bas.",
                       "serialize" : True                
                       },
            "labelsGauche" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage des labels sur l'axe gauche.",
                       "serialize" : True                
                       },
            "labelsDroite" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage des labels sur l'axe droit.",
                       "serialize" : True                
                       },
            "labelsBas" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage des labels sur l'axe du bas.",
                       "serialize" : True                
                       },
            "labelsGaucheHov" : {
                       "type" : "str",
                       "default" : "100%",
                       "authorized" : ["100%","75%","50%","25%","10%","Auto","Aucun"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Quantité de labels affichés sur l'axe gauche d'un graphique Hovmöller.",
                       "serialize" : True                
                       },
            
            "minHisto" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeur du minimum à tracer sous forme d'histogramme.",
                       "serialize" : True                
                       },
            "maxHisto" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeur du maximum à tracer sous forme d'histogramme.",
                       "serialize" : True                
                       },
            "infHisto" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "On trace la classe des valeurs inférieures au minimum.",
                       "serialize" : True                
                       },
            "supHisto" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "On trace la classe des valeurs supérieures au minimum.",
                       "serialize" : True                
                       },
            "amplitudeClassesHisto" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Amplitude des classes de l'histogramme.",
                       "serialize" : True                
                       },
            "nombreClassesHisto" : {
                       "type" : "int",
                       "default" : 10,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nombre de classes de l'histogramme.",
                       "serialize" : True                
                       },
            "azimut" : {
                       "type" : "int",
                       "default" : -60,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : -180,
                       "max" : 180,
                       "value" : None,
                       "desc" : "Azimut en degrés pour les histogramme 3D.",
                       "serialize" : True                
                       },
            "elevation" : {
                       "type" : "int",
                       "default" : 30,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : -180,
                       "max" : 180,
                       "value" : None,
                       "desc" : "Elevation en degrés pour les histogramme 3D.",
                       "serialize" : True                
                       },
            "largeurBarre" : {
                       "type" : "int",
                       "default" : 100,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 5,
                       "max" : 100,
                       "value" : None,
                       "desc" : "Largeur en % des barres pour les histogramme 3D.",
                       "serialize" : True                
                       },
            "epaisseurBarre" : {
                       "type" : "int",
                       "default" : 50,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 5,
                       "max" : 100,
                       "value" : None,
                       "desc" : "Epaisseur en % des barres pour les histogramme 3D.",
                       "serialize" : True                
                       },
            "legendeAida" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage du nom des vecteurs sur le côté du graphique.",
                       "serialize" : True                
                       },
            "grille" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage du nom des vecteurs sur le côté du graphique.",
                       "serialize" : True                
                       },
            "y=n" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Tracé de la droite y=n.",
                       "serialize" : True                
                       },
            "n" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeur de n pour la droite y=n",
                       "serialize" : True                
                       },
            "secteursRDV" : {
                       "type" : "int",
                       "default" : 16,
                       "authorized" : [4,8,12,16,18,24,32,36],
                       "mixed" : None,
                       "min" : 0,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nombre de secteurs de la rose des vents : 4,8,12,16,18,24,32 ou 36",
                       "serialize" : True                
                       },
            "typeRDV" : {
                       "type" : "int",
                       "default" : 0,
                       "authorized" : [0,1,2],
                       "mixed" : None,
                       "min" : 0,
                       "max" : None,
                       "value" : None,
                       "desc" : "Type de rose des vents : 0=contours, 1=barres, 2=boites",
                       "serialize" : True                
                       },
            "couleurRDV" : {
                       "type" : "int",
                       "default" : 0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0,
                       "max" : 11,
                       "value" : None,
                       "desc" : "Numéro de la palette de couleurs de la rose des vents (0-11).",
                       "serialize" : True                
                       },
            "reversePaletteRDV" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Inversion de la palette de couleur.",
                       "serialize" : True                
                       },
            "roseStandard" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Classes de la rose des vents météo standard :[1.5-3-7-12].",
                       "serialize" : True                
                       },

            "inverseAxeYHov" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Inversion de l'axe des ordonnées.",
                       "serialize" : True                
                       },
            
            "legendeVisible" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Affichage ou non de la légende sur le graphique.",
                       "serialize" : True                
                       },
            "policeLegende" : {
                       "type" : "str",
                       "default" : "Sans 12",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Police du titre ex : \"Times New Roman, Italic 13.\"",
                       "serialize" : True   
                        },
            "positionLegende": {
                       "type" : "str",
                       "default" : "0,0,0,0,0",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Position de la légende : type, x, y, dx, dy dans un repère normé (cf matplotlib.legend)",
                       "serialize" : True
                       },
            "ncolLegende" : {
                       "type" : "int",
                       "default" : 1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 1,
                       "max" : 20,
                       "value" : None,
                       "desc" : "Nombre de colonnes sur lequel est affiché la légende",
                       "serialize" : True                
                       },
            "norme" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Graphique de type histo normé (unité = pourcents).",
                       "serialize" : True                
                       },
            "groupe_liaison" : {
                       "type" : "int",
                       "default" : -1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Numéro du groupe de liaison associé au graphique : tous les graphiques appartenant au même groupe voient leurs données liées.",
                       "serialize" : True                
                       },
             "fitData" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Adapter l'intervalle de date du graphique aux données et non à des journées entières.",
                       "serialize" : True                
                       },
             "echelleLogGauche" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui","non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Utilisation d'un échelle logarithmique sur l'axe de gauche.",
                       "serialize" : True                
                       },
             "echelleLogDroite" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui","non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Utilisation d'un échelle logarithmique sur l'axe de droite.",
                       "serialize" : True                
                       },
             "echelleLogBas" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui","non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Utilisation d'un échelle logarithmique sur l'axe du bas.",
                       "serialize" : True                
                       },
             "decoupageActiver" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui","non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Activer le découpage temporel",
                       "serialize" : True                
                       },
             "decoupagePeriode" : {
                       "type" : "str",
                       "default" : "j",
                       "authorized" : ["j","m", "a"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Période utilisée pour le découpage temporel : jour(j), mois(m) ou année(a)",
                       "serialize" : True                
                       },
            "nombreJoursDecoupage" : {
                       "type" : "int",
                       "default" : 1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 1,
                       "max" : 100,
                       "value" : None,
                       "desc" : "Nombre de jours de la période de découpage (1-100).",
                       "serialize" : True                
                       },
            "couleurDecoupage" : {
                       "type" : "int",
                       "default" : 0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0,
                       "max" : 11,
                       "value" : None,
                       "desc" : "Numéro de la palette de couleurs du découpage temporel (0-11).",
                       "serialize" : True                
                       },
            "reversePaletteDecoupage" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Inversion de la palette de couleur du découpage temporel.",
                       "serialize" : True                
                       },
            "typeHov" : {
                       "type" : "str",
                       "default" : "auto",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.2.0 : Type du diagramme Hovmöller : auto(defaut), largeur(10%, 32%, ...), shading (plages de couleurs), iso(isolignes), iso-shading(iso+shading) .",
                       "serialize" : True                
                       },
            "couleurHov" : {
                       "type" : "int",
                       "default" : 0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0,
                       "max" : 12,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.2.0 : Numéro de la palette de couleurs du diagramme Hovmöller (0-11).",
                       "serialize" : True                
                       },
            "reversePaletteHov" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.2.0 : Inversion de la palette de couleur.",
                       "serialize" : True                
                       },
            "seuilAutoHov" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.2.0 : Seuillage automatique des couleurs : la palette couvre toute la gamme de valeurs.",
                       "serialize" : True                
                       },
            "seuilMinHov" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.2.0 : Valeur associée à la première couleur de la palette.",
                       "serialize" : True                
                       },
            "seuilMaxHov" : {
                       "type" : "float",
                       "default" : 100.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.2.0 : Valeur associée à la dernière couleur de la palette.",
                       "serialize" : True                
                       },
            "horsGammeVisibleHov" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.2.0 : Valeurs hors gamme visibles ou pas.",
                       "serialize" : True                
                       }    
        }
        if not self.check() :
            raise RuntimeError("Erreur ConfigGraphique : la config n'est pas correcte")


"""
    ##################################### ConfigTrace
"""            
class ConfigTrace(Config):
    """
        Classe qui définit la configuration d'un tracé (hérite de Config)
    """
    def __init__(self, config) :
        Config.__init__(self, config)
        self.typeConfig = "trace"
        self.desc = {
            "type" : {
                       "type" : "str",
                       "default" : "ST",
                       "authorized" : ["ST","PlotXY","Histo","Histo3D", "RDV","Hov"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Type de graphique : ST(série temporelle), PlotXY, Histo, Histo3D, RDV(rose des vents), Hovmöller",
                       "serialize" : True                
                       },         
            "plateforme" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom abrégé de la plateforme tracée en ordonnée.",
                       "serialize" : True                
                       },
            "parametre" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du paramètre tracé en ordonnée.",
                       "serialize" : True                
                       },
            "operateur" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : ['+', '-','*','/'],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Opérateur sur le paramètre en ordonnée.",
                       "serialize" : True                
                       },
            "operande_nombre" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Opérande sur le paramètre en ordonnée.",
                       "serialize" : True                
                       }, 
            "operande_plateforme" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Nom abrégé de la plateforme utilisée comme opérande en ordonnée.",
                       "serialize" : True                
                       },
            "operande_parametre" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Nom du paramètre utilisé comme opérande en ordonnée.",
                       "serialize" : True                
                       },                        
            "plateforme_x" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom abrégé de la plateforme tracée en abscisse (PlotXY).",
                       "serialize" : True                
                       },
            "parametre_x" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du paramètre tracé en abscisse (PlotXY).",
                       "serialize" : True                
                       },
            "operateur_x" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : ['+', '-','*','/'],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Opérateur sur le paramètre en absisse (PlotXY).",
                       "serialize" : True                
                       },
           "operande_nombre_x" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Opérande sur le paramètre en abscisse (PlotXY).",
                       "serialize" : True                
                       }, 
           "operande_plateforme_x" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Nom abrégé de la plateforme utilisée comme opérande en abscisse (PlotXY).",
                       "serialize" : True                
                       },
            "operande_parametre_x" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Obsolète depuis 4.0.0 -Nom du paramètre utilisé comme opérande en abscisse (PlotXY).",
                       "serialize" : True                
                       },                                    
            "couleur" : {
                       "type" : "str",
                       "default" : "#000000",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Couleur en hexadecimal #RRGGBB ou #RGB",
                       "serialize" : True                
                       },
            "typeLigne" : {
                       "type" : "str",
                       "default" : "-",
                       "authorized" : ['-','--',':','*','None'],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Type de ligne du tracé.",
                       "serialize" : True                
                       },
            "marqueur" : {
                       "type" : "str",
                       "default" : "None",
                       "authorized" : ['None', '+', 'o', 's','.','^'],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Type de marqueur associé au tracé.",
                       "serialize" : True                
                       },
            "epaisseur" : {
                       "type" : "int",
                       "default" : 1,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0,
                       "max" : 500,
                       "value" : None,
                       "desc" : "Epaisseur du tracé.",
                       "serialize" : True                
                       },
            "regression" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Tracé de la droite de régression.",
                       "serialize" : True                
                       },
            "minHisto" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeur du minimum à tracer sous forme d'histogramme.",
                       "serialize" : True                
                       },
            "maxHisto" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeur du maximum à tracer sous forme d'histogramme.",
                       "serialize" : True                
                       },
            "infHisto" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "On trace la classe des valeurs inférieures au minimum.",
                       "serialize" : True                
                       },
            "supHisto" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "On trace la classe des valeurs supérieures au minimum.",
                       "serialize" : True                
                       },
            "amplitudeClassesHisto" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Amplitude des classes de l'histogramme.",
                       "serialize" : True                
                       },
            "nombreClassesHisto" : {
                       "type" : "int",
                       "default" : 10,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nombre de classes de l'histogramme.",
                       "serialize" : True                
                       },
            "labelNombreHisto" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Label du nombre d'élément dans la classe.",
                       "serialize" : True                
                       },
            "labelPourcentHisto" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Label du pourcentage de la classe.",
                       "serialize" : True                
                       },
            "conditions" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Description des variables et conditions pour un affichage conditionnel :\n                description des variables##condition1(expression,couleur,type de trait,epaisseur)##...##condition_non_evaluable n\n                exemple (1 variable, 1 condition) : x=Tf:tpr_sol10cm_c4_cal_%60##x<20.0,#ff0000,-,2##non_evaluable,#000000,-,1",
                       "serialize" : True                
                       },
            "operation_x" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Description des variables et opération en abscisses (PlotXY):\n                description des variables##opération n\n                exemple (1 variable) : x=Tf:tpr_sol10cm_c4_cal_%60##y=x+1",
                       "serialize" : True                
                       },
            "operation_y" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Description des variables et opération en ordonnées :\n                description des variables##opération n\n                exemple (1 variable) : x=Tf:tpr_sol10cm_c4_cal_%60##y=x+1",
                       "serialize" : True                
                       },
            "legende" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Légende associée au tracé (défaut = plateforme:paramètre.",
                       "serialize" : True                
                       },
            "legendeVisible" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Indique si la légende du tracé est visible.",
                       "serialize" : True                
                       },
            "filtrageConditionnel" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Pour un affichage conditionnel, indique si les conditions servent de filtre pour les données.",
                       "serialize" : True                
                       },
            "cumul" : {
                       "type" : "int",
                       "default" : 0,
                       "authorized" : [0,1,2],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Fonction cumul : 0=pas de cumul, 1=cumul sans raz sur nan, 2=cumul avec raz sur nan.",
                       "serialize" : True               
                },
            "axe_y" : {
                       "type" : "int",
                       "default" : 2,
                       "authorized" : [0, 1, 2],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Axe des ordonnées sur lequel on veut afficher les données : 0=gauche 1=droit 2=auto",
                       "serialize" : True                
                       },
            "typeHov" : {
                       "type" : "str",
                       "default" : "auto",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Type du diagramme Hovmöller : auto(defaut), largeur(10%, 32%, ...), shading (plages de couleurs), iso(isolignes), iso-shading(iso+shading) .",
                       "serialize" : True                
                       },
            "couleurHov" : {
                       "type" : "int",
                       "default" : 0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : 0,
                       "max" : 12,
                       "value" : None,
                       "desc" : "Numéro de la palette de couleurs du diagramme Hovmöller (0-11).",
                       "serialize" : True                
                       },
            "reversePaletteHov" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Inversion de la palette de couleur.",
                       "serialize" : True                
                       },
            "seuilAutoHov" : {
                       "type" : "str",
                       "default" : "oui",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Seuillage automatique des couleurs : la palette couvre toute la gamme de valeurs.",
                       "serialize" : True                
                       },
            "seuilMinHov" : {
                       "type" : "float",
                       "default" : 0.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeur associée à la première couleur de la palette.",
                       "serialize" : True                
                       },
            "seuilMaxHov" : {
                       "type" : "float",
                       "default" : 100.0,
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeur associée à la dernière couleur de la palette.",
                       "serialize" : True                
                       },
            "horsGammeVisibleHov" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Valeurs hors gamme visibles ou pas.",
                       "serialize" : True                
                       },
            "quiverHov" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Activation du tracé quiver (profil de vent).",
                       "serialize" : True                
                       },
            "quiverModeUVHov" : {
                       "type" : "str",
                       "default" : "non",
                       "authorized" : ["oui", "non"],
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Activation du mode UV sinon DDFF pour le calcul du quiver (profil de vent).",
                       "serialize" : True                
                       },
            "plateformeQuiverHov" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom abrégé de la plateforme pour le tracé quiver en mode dd/ff.",
                       "serialize" : True                
                       },
            "parametre_dd_hov" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du paramètre dd pour le tracé quiver en mode dd/ff..",
                       "serialize" : True                
                       },
            "parametre_ff_hov" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du paramètre ff pour le tracé quiver en mode dd/ff..",
                       "serialize" : True                
                       },
            "parametre_u_hov" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du paramètre u pour le tracé quiver en mode u/v..",
                       "serialize" : True                
                       },
            "parametre_v_hov" : {
                       "type" : "str",
                       "default" : "",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Nom du paramètre v pour le tracé quiver en mode u/v..",
                       "serialize" : True                
                       },
            "echantillonHovQuiverX" : {
                       "type" : "str",
                       "default" : "100",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Echantillonnage des données quiver des graphiques hovmoller sur l'axe X.",
                       "serialize" : True                
                       },
            "echantillonHovQuiverY" : {
                       "type" : "str",
                       "default" : "100",
                       "authorized" : None,
                       "mixed" : None,
                       "min" : None,
                       "max" : None,
                       "value" : None,
                       "desc" : "Echantillonnage des données quiver des graphiques hovmoller sur l'axe Y.",
                       "serialize" : True                
                       }
            
        }
        if not self.check() :
            raise RuntimeError("Erreur ConfigTrace : la config n'est pas correcte")
            
        #
        # Compatibilité des graphiques Hovmoller depuis changement en v4.2.0 :
        # jusque là on autorisait un seul tracé dans un graphique hovmoller.
        # Les attributs associés au graphiques (type, couleur,...) basculent maintenant sur les tracés.
        #
        
        # Compatibilité des opérations depuis changement en v4.0.0
        # parametre en y
        operateur = self.desc["operateur"]["value"]
        if operateur != self.desc["operateur"]["default"] :
            operande_nombre = self.desc["operande_nombre"]["value"]
            operande_parametre = self.desc["operande_parametre"]["value"]
            operande_plateforme = self.desc["operande_plateforme"]["value"]
            if operande_nombre != self.desc["operande_nombre"]["default"] :
                str_operation = "##y{}{}".format(operateur, operande_nombre)
                self.desc["operande_nombre"]["value"] = self.desc["operande_nombre"]["default"]
            elif operande_parametre != self.desc["operande_parametre"]["default"] and operande_plateforme != self.desc["operande_plateforme"]["default"] :
                str_operation = "a={}:{}##y{}a".format(operande_plateforme, operande_parametre, operateur)
                self.desc["operande_parametre"]["value"] = self.desc["operande_parametre"]["default"]
                self.desc["operande_plateforme"]["value"] = self.desc["operande_plateforme"]["default"]                
            print(str_operation)
            self.desc["operation_y"]["value"] = str_operation
            self.desc["operateur"]["value"] = self.desc["operateur"]["default"]
        # parametre en x
        operateur_x = self.desc["operateur_x"]["value"]
        if operateur_x != self.desc["operateur_x"]["default"] :
            operande_nombre_x = self.desc["operande_nombre_x"]["value"]
            operande_parametre_x = self.desc["operande_parametre_x"]["value"]
            operande_plateforme_x = self.desc["operande_plateforme_x"]["value"]
            if operande_nombre_x != self.desc["operande_nombre_x"]["default"] :
                str_operation = "##y{}{}".format(operateur_x, operande_nombre_x)
                self.desc["operande_nombre_x"]["value"] = self.desc["operande_nombre_x"]["default"]
            elif operande_parametre_x != self.desc["operande_parametre_x"]["default"] and operande_plateforme_x != self.desc["operande_plateforme_x"]["default"] :
                str_operation = "a={}:{}##y{}a".format(operande_plateforme_x, operande_parametre_x, operateur_x)
                self.desc["operande_parametre_x"]["value"] = self.desc["operande_parametre_x"]["default"]
                self.desc["operande_plateforme_x"]["value"] = self.desc["operande_plateforme_x"]["default"]
            print(str_operation)
            self.desc["operation_x"]["value"] = str_operation
            self.desc["operateur_x"]["value"] = self.desc["operateur_x"]["default"]
                

