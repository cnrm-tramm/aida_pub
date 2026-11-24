#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Production des fichiers NetCDF a partir de fichiers vecteurs 

usage : prod_CDF.py JJMMAAAA(début) JJMMAAAA(fin) -c fic_config -v num_version
     ou prod_CDF.py ACQID(début) ACQID(fin) -c fic_config -v num_version

Description des champs du fichier de config :

section [GENERAL]
(*) = obligatoire 
    plateforme : nom AIDA de la plateforme (exemple : toulouse-flux), (*) si JJMMAAAA en argument   
    reftime (*) : nom du vecteur de reference temporelle (tous les vecteurs doivent avoir la même)
    coordinates : Elaboration d'un fichier netcdf trajectoire (liste des vecteurs utilisés pour trajectoire lat, lon, alti)
    base_nom_fic_out (*), version(*), processing_level et format_date_nom_fic_out : servent à construire le nom du fichier de 
sortie sous la forme 
                <base_nom_fic_out>_<date>_<processing_level>_V<version>.nc
            ou  <base_nom_fic_out>_<date>_<acqid>_<processing_level>_V<version>.nc
    base_temps_fic_out(*) :  jour ou periode 
    dimension : Dimension de la variable time Unlimited ou Limited (Unlimited par défaut).
                Mettre à Unlimited pour pouvoir concaténer plusieurs fichiers après.

    convention_datation = debut, milieu, fin (fin par defaut)

Les autres champs sont optionnels et sont retranscrit tels quels
dans le fichier NetCDF. Mais la norme (voir : http://cfconventions.org/latest.html) 
propose de mettre les champs suivants :

    title = (description du jeu de données)  
    creator_name =  (contact)  
    creator_institution =
    institution = 
    source =  (ex : surface observations) 
    history = 
    summary =
    comment =

On peut aussi mettre des champs qui ne sont pas dans la norme

doi = 
version = 

une section par parametre [PARAM0] ... contenant :
    nom : nom du parametre en langage anglais, français, ...
    nom_vecteur : nom du fichier vecteur

Les vecteurs 1D sont acceptés.

Le standard_name CF est déterminé automatiquement à parir du nom
du vecteur, de sa famille, ...

...
Exemple de fichier config :

[GENERAL]
plateforme = toulouse-flux
reftime = rft_time_REG_%1800 
version= 1.00
base_nom_fic_out = CNRM_MTO_L2A-30min-Mean 
format_date_nom_fic_out = %Y-%m-%d
base_temps_fic_out = jour 

title =  Meteopole-Flux Meterological Data  
creator_institution = CNRM,Univesité de Toulouse, Météo-France, CNRS, Toulouse, France
institution = CNRM,Univesité de Toulouse, Météo-France, CNRS, Toulouse, France
source = surface observation
creator_email = A RENSEIGNER
creator_name = xxx@yyy.zz

[SOIL_HEAT_FLUX]
nom =  Soil Heat Flux 
nom_vecteur = flx_phi0_moy_c2_v3_%60_Met_%1800 

[SWUP]
nom = Upward short wave radiation  
nom_vecteur  = ray_rgm_cnr1_c2_%60_Met_%1800 

"""

import argparse
import os
import sys
import datetime as dt
import configparser
import re
import subprocess as sub


import numpy as np
 

#from netCDF4 import Dataset
import netCDF4 as nc

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA
from AIDA_name_to_CF_name import AIDA_name_to_CF_name
from AcqId import *

#------------------------------------------------------

def is_varname_CF_OK ( varname ) :
    """
    Teste si le nom de la variable est conforme à la norme CF
    qui accepte les lettres, nombres, et underscore
    """
    
    liste_alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    varname_u = varname.upper() 

    if ( varname_u[0] not in liste_alpha ) :
        return(False)

    ret = True
    for c in varname_u[1:] :
        if (c.isdigit() or (c in liste_alpha) or c=='_'):
            ret=True
        else :
            ret=False
            break
    return(ret)
    
#------------------------------------------------------

def AIDAtype_to_NetCDFtype ( AIDA_format ) :
    """ 
    Fait la correspondance entre le type AIDA et le type NetCDF
    """

    f = AIDA_format.lower()

    type_netCDF = { 'ieeefloat_32' : 'f4',
            'string' : 'S32' , 'int_16' : 'f4', 'int_32': 'f4' }

    if not f in type_netCDF.keys() : 
        print ( '-+- ATTENTION format {} non connu de prod_CDF'.format(AIDA_format) )   
        print ( '-+-    Utilisation format par defaut : "f4".' )   
        return ("f4")

    return ( type_netCDF[f] ) 


#------------------------------------------------------
def decode_bornes ( bornes_vect ):
    """
    decode le champ bornes d'un vecteur 2D et renvoie une liste de tuple
    """
    s=bornes_vect.replace("(","").replace(")","")
    l=s.split(";")
    liste_bornes = np.array( [ ( float(x.split(',')[0]), float(x.split(',')[1]) ) for x in l ] )
    
    return liste_bornes

#------------------------------------------------------
def init_tab_data (dim_array) :
    """
    initialise un np.array vide mais formé en fonction de dim_array au sens AIDA 
    """
    if dim_array == 1 :
        data = np.empty ( 0 )
    else :
        data = np.empty ( (0,  dim_array ))

    return data

def construit_nom_vecteur ( str_vect, acq ) :

    # Cas où le nom de vecteur comporte un choix  récupérer
    # dans un fichier de config CHOIX_PARAM_NETCDF.
    # nom_vecteur = xxx(section_choix)xxxxx
    deb_choix=str_vect.find("${")
    if deb_choix < 0 :
        return(str_vect)

    fin_choix=str_vect.find("}")
    
    if fin_choix >= 0 and fin_choix > deb_choix + 1 :
        decoupe_nom_vecteur = re.split('[${}]',str_vect)

    if len(decoupe_nom_vecteur) > 3 :
        fic_choix="CHOIX_PARAM_NETCDF"
        choix= configparser.ConfigParser()
        choix.read(fic_choix)
        section = decoupe_nom_vecteur[2]
        try :
            choix_vecteur = choix.get(section,str(acq))
        except  configparser.NoOptionError :
            print("+++ ERREUR : Pas de choix pour la section {} pour l'acqid {}".format(section, str(acq)))
            sys.exit(-1)

        nom_vect = decoupe_nom_vecteur[0] + choix_vecteur + decoupe_nom_vecteur[3]
        return (nom_vect)
    else :
        return(str_vect)


def construit_comment ( str_comment, acq ) :

    # Cas où le commentaire dépend de l'acqid  récupérer
    # dans un fichier de config CHOIX_PARAM_NETCDF.
    # le commentaire

    if str_comment.startswith("${") and  str_comment.endswith("}") :
        decoupe_str_comment = re.split('[${}]',str_comment)
        fic_choix="CHOIX_PARAM_NETCDF"
        choix= configparser.ConfigParser()
        choix.read(fic_choix)
        section = decoupe_str_comment[2]
        cle = str(acq) +"_c"
        try :
            acq_comment = choix.get(section,cle)
        except  configparser.NoOptionError :
            print("+++ ERREUR : Pas de commentaire pour la section {} pour l'acqid {}".format(section, str(acq)))
            sys.exit(-1)

        return (acq_comment)
    else :
        return(str_comment)

def recup_source_vect_cal( nom_vecteur,str_acqid):
    """ recupere la liste des capteurs utilisé pour creer le vecteur considéré
     pour cela recupere la liste des vecteurs cal qui on servi a fabriquer le vecteur acqid 
     puis on recherche la liste des parametres manufacturer et model du champ sensor """

    # recuperation de la famille du vecteur out
    source_instru=[]
    #liste des vecteurs cal utilisés pour produire le vecteur
    base_output = 'GenGraphVect.' + os.getenv('USER')
    prog=os.path.join(AH,"bin","gengraphvect.py -a {} -n 4 -o png -s asc -f {} {}".format(str_acqid,base_output,nom_vecteur))
    s=sub.run(prog,shell=True,capture_output=True,encoding='iso-8859-15')
    liste_lvect=s.stdout.lstrip().split('\n')
    #print("liste_vect associe a {}:{}".format(nom_vecteur,liste_lvect))
    debut=True
    for lvect in liste_lvect:
        if 'Vecteur' in lvect:
            source = ""
            vect=(lvect.lstrip().split(' '))[1]
            #On recupere directement l'attribut du vecteur via aida
            dhdr=AIDA.Vector(str_acqid,vect, attributes_only=True)
            for key, ligne in dhdr.attributes.items():
                st=ligne.split(':')
                if (st[0] == 'sensor') or (st[0] == 'transducer' and source == "" ) or (st[0] == 'instrument' and source=="") :
                    if len(st) >=4:
                        source="{} : {}: {}".format(st[1],st[2],st[3])
                    elif len(st) >=3:
                            source="{} : {}".format(st[1],st[2])
                    elif len(st) >=2:
                            source="{} ".format(st[1])
                    else:
                            source=":"
                        
                    if source not in source_instru :
                         source_instru.append(source)

    return(source_instru)


#------------------------------------------------------
def ecrit_fic_CDF(id_dataset, nomfic, dict_acqid_var, dict_vect_var, reftime, time_bounds, config, acq_meta, version ) : 
    """
    nomfic : nom du fichier NetCDF
    time : liste de datetime
    time_bounds (tableau 2D): limites de l'intervalle de temps representatif de l'echantillon en secondes
                              depuis le début OOH
    dict_vect_var : dictionnaire contenant un dictionnaire attributes et un tableau de data 
    avec la  variable NetCDF comme clef
    """
     # ouverture du fichiers NetCDF  
    root_cdf = nc.Dataset(nomfic , 'w', format='NETCDF4')
    try :
        dimension = config.get('GENERAL','dimension')
        if dimension == "Limited" :
            time = root_cdf.createDimension('time', size=len(reftime))
        else :
            time = root_cdf.createDimension('time', None)
    except :
        time = root_cdf.createDimension('time', None)

    level = root_cdf.createDimension('level', 2)
    string_leng = root_cdf.createDimension('string_length', 100)

    # attributs generaux 
    # on retranscrit dans le NetCDF tous les attributs fournis dans le fichier de config
    options_non_attributs=['plateforme', 'reftime', 'version', 'base_nom_fic_out', 'base_temps_fic_out', 'format_date_nom_fic_out', 'dimension', 'remplace_vecteur_absent', 'convention_datation','idaeris','date_publication','client_template']
    options_generales =  config.options('GENERAL')

    liste_attributs_CDF = [ s for s in options_generales if s not in options_non_attributs ] 
    #for s in options_non_attributs : 
    #    if s in liste_attributs_CDF :
    #        liste_attributs_CDF.remove(s)

    # cas particulier pour description et data_sources utilisés à la place de
    # title et institution. On garde le cas pour la compatibilité des anciens
    # fichiers de config
    if "creator_name"  in liste_attributs_CDF :
        root_cdf.creator_name = config.get('GENERAL','creator_name') 
        liste_attributs_CDF.remove('creator_name')
    else :
        creator_name = "EXEMPLES"
        root_cdf.creator_name = creator_name
    if "creator_email"  in liste_attributs_CDF :
        root_cdf.creator_email = config.get('GENERAL','creator_email') 
        liste_attributs_CDF.remove('creator_email')
    else :
        creator_email = "EXEMPLES@mail.fr"
        root_cdf.creator_email = creator_email
    if 'data_sources' in liste_attributs_CDF :
        root_cdf.institution = config.get('GENERAL','data_sources') 
        liste_attributs_CDF.remove('data_sources')
    if 'description' in liste_attributs_CDF :
        root_cdf.title = config.get('GENERAL','description') 
        liste_attributs_CDF.remove('description')
    if 'acqid' in liste_attributs_CDF and config.get('GENERAL','acqid') != "Null" :
        acq_id = config.get('GENERAL','acqid') 
        root_cdf.acqid = acq_id
        liste_attributs_CDF.remove('acqid')
    else :
        if ( base_temps_fic_out != "periode" ):
            acq_id = acq_meta.get_field_value("IDENTIFICATION","acq_id")
            if 'coordinates' in liste_attributs_CDF  :
                root_cdf.flight_id = acq_id
            else :
                root_cdf.acqid = acq_id
        else :
            root_cdf.acqid = str(dict_acqid_var["acqid_deb"]) + "-" + str(dict_acqid_var["acqid_fin"])
    if 'processing_level' in liste_attributs_CDF :
        root_cdf.processing_level = config.get('GENERAL','processing_level')  
        liste_attributs_CDF.remove('processing_level')
    if 'coordinates' in liste_attributs_CDF :
        if ( base_temps_fic_out == "periode" ):
            print("+++ Erreur les attributs [GENERAL] coordinates et base_temps_fic_out=periode sont incompatibles.")
            sys.exit(-1)
        lst_param_traj = config.get('GENERAL','coordinates')
        root_cdf.coordinates = lst_param_traj
        liste_attributs_CDF.remove('coordinates')
        root_cdf.featureType = "Trajectory"
        #  pour coller au format trajectoire simple il faut ajouter
        # la variable trajectory qui contient l'ID du vol :
        var = root_cdf.createVariable ( "trajectory", 'S1', ('string_length')) 
        var.cf_role = "trajectory_id"
        var[:] = nc.stringtochar(np.array(["acqid="+acq_id], 'S100'))
    
        date_vol = acq_meta.get_date_acq()
        root_cdf.flight_date = date_vol.strftime('%Y-%m-%d')
        liste_attributs_CDF.remove('date_vol')
   
        date_dec = acq_meta.get_horaire('decollage')
        root_cdf.time_take_off = date_dec.strftime('%Y-%m-%dT%H:%M:%SZ')
        liste_attributs_CDF.remove('decollage')
  
        date_att = acq_meta.get_horaire('atterrissage')
        root_cdf.time_landing = date_att.strftime('%Y-%m-%dT%H:%M:%SZ')
        liste_attributs_CDF.remove('atterrissage')
    else :
        lst_param_traj = []

    if 'geospatial_lat_min' in liste_attributs_CDF :
        lat_min_cfg = np.float64(config.get('GENERAL','geospatial_lat_min'))  
        liste_attributs_CDF.remove('geospatial_lat_min')
    else :
        lat_min_cfg = np.nan
    if 'geospatial_lat_max' in liste_attributs_CDF :
        lat_max_cfg = np.float64(config.get('GENERAL','geospatial_lat_max'))  
        liste_attributs_CDF.remove('geospatial_lat_max')
    else :
        lat_max_cfg = np.nan
    if 'geospatial_lon_min' in liste_attributs_CDF :
        lon_min_cfg = np.float64(config.get('GENERAL','geospatial_lon_min'))  
        liste_attributs_CDF.remove('geospatial_lon_min')
    else :
        lon_min_cfg = np.nan
    if 'geospatial_lon_max' in liste_attributs_CDF :
        lon_max_cfg = np.float64float(config.get('GENERAL','geospatial_lon_max'))  
        liste_attributs_CDF.remove('geospatial_lon_max')
    else :
        lon_max_cfg = np.nan
    if 'geospatial_lon_max' in liste_attributs_CDF :
        lon_max_cfg = np.float64float(config.get('GENERAL','geospatial_lon_max'))  
        liste_attributs_CDF.remove('geospatial_lon_max')
    else :
        lon_max_cfg = np.nan

    if "conventions"  in liste_attributs_CDF :
        root_cdf.Conventions = config.get('GENERAL','conventions') 
        liste_attributs_CDF.remove('conventions')
    else :
        root_cdf.Conventions = 'CF-1.8, ACDD'

    lat_min_traj = dict_acqid_var["lat_plt"]
    lat_max_traj = dict_acqid_var["lat_plt"]
    lon_min_traj = dict_acqid_var["lon_plt"]
    lon_max_traj = dict_acqid_var["lon_plt"]

    for attribut in liste_attributs_CDF :
        root_cdf.setncattr(attribut, config.get('GENERAL', attribut )  )

    root_cdf.id = id_dataset
    root_cdf.product_version = config.get('GENERAL','version')  
    #root_cdf.Conventions = 'CF-1.8, ACDD'
    root_cdf.time_coverage_start = dict_acqid_var["time_start"]
    root_cdf.time_coverage_end = dict_acqid_var["time_end"]
    if dict_acqid_var["time_resolution"] is not None :
        root_cdf.time_coverage_resolution = dict_acqid_var["time_resolution"]
#    root_cdf.creationdate = dt.datetime.today().isoformat() 
    root_cdf.date_created = dt.datetime.today().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    root_cdf.date_modified = dt.datetime.today().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    root_cdf.source_config = config.get('GENERAL','source_config')  

    # ecriture du temps 
    dt0 = reftime[0].replace(hour=0, minute=0, second=0, microsecond=0)
    var = root_cdf.createVariable ( "time", 'f8', ('time',)) 
    var.units = "seconds since {} 00:00 UTC".format(dt0.strftime("%Y-%m-%d") )
    var.standard_name =  "time" 
    var.long_name =  "time UTC" 
    var.calendar = 'standard'
    var[:] = [ (t - dt0).total_seconds()  for t in reftime ]
    
    # ecriture des bornes temporelles
    # les bornes ne sont pas datées. Elles sont en nombre
    # de secondes depuis 00h.
    # Dans le cas où on ecrit un fichier NetCDF qui couvre
    # une periode de plusieurs jours il faut ajouter 86400*nbjour
    # aux bornes temporelles correspondant à chaque jour
    if  len(time_bounds) !=0 : 
        var.bounds = "time_bnds"
        var = root_cdf.createVariable ( "time_bnds", 'f8', ('time','level')) 
        var[:] = time_bounds[:,:]

    liste_param =  config.sections()
    liste_param.remove('GENERAL')
    for param in liste_param:
        if param=="METADATA_AERIS":
            liste_param.remove('METADATA_AERIS')
    #try: 
        #liste_param.remove('METADATA_AERIS')
    #except Exception as e:
        #print("--- pas de section METADATA_AERIS:{}".format(e))

    for p in liste_param :

        if dict_vect_var[p]["attributes"]['misval'] == "" :
            dict_vect_var[p]["attributes"]['misval'] = np.nan 

        nom_vecteur_ini = config.get(p, "nom_vecteur") 
        nomvar = p 

        nom_vecteur =  construit_nom_vecteur ( nom_vecteur_ini, acqid )

        try :
            dim_array = int( dict_vect_var[p]["attributes"]["dim_array"] )
        except :
            dim_array = 1


        type_netcdf = AIDAtype_to_NetCDFtype ( dict_vect_var[p]["attributes"]["format"] )  


        if dim_array <= 1 : 
            #var = root_cdf.createVariable ( p  , type_netcdf, ('time',), fill_value= dict_vect_var[p]["attributes"]['misval'] ) 
            var = root_cdf.createVariable ( p  , type_netcdf, ('time',), fill_value= np.nan) 
        else :
            # cas d'un tableau de données 2D
            # creation d'un dimension et d'une donnée pour les bornes
            nom_dim = p+'_class'
            root_cdf.createDimension( nom_dim, dim_array)

            var = root_cdf.createVariable ( nom_dim, 'f4', (nom_dim,)) 
            var.units = dict_vect_var[p]["attributes"]['unit_bornes'] 
            var.bounds = nom_dim+"_bnds"
            try : 
                var.long_name =  config.get(p, 'bornes_name')
            except :
                pass
            liste_bornes = AIDA.strBornes_to_array ( dict_vect_var[p]["attributes"]['bornes'] )            
            
            tab_bornes_sup = np.array( [ x[1] for x in  liste_bornes[0] ] )
            var[:] = tab_bornes_sup

            # creation de bounds pour les bornes du tableau
            var = root_cdf.createVariable ( nom_dim+"_bnds" , 'f4', (nom_dim,'level'))  
            var[:] =  np.array( liste_bornes[0] )

#            var =  root_cdf.createVariable ( p  , 'f4', ('time',nom_dim), fill_value= dict_vect_var[p]["attributes"]['misval'] ) 
            var =  root_cdf.createVariable ( p  , 'f4', ('time',nom_dim), fill_value= np.nan ) 

        # ecriture des meta-données de la variable
        if dict_vect_var[p]["attributes"]['unit'].lower().strip() != "without" :
            var.units = dict_vect_var[p]["attributes"]['unit']
        var.long_name =  config.get(p, 'nom')

        if dict_vect_var[p]["attributes"]['comment']!="":
            var.comment= dict_vect_var[p]["attributes"]['comment']
        if dict_vect_var[p]["attributes"]['valid_min']!="":
            var.valid_min= dict_vect_var[p]["attributes"]['valid_min']
        if dict_vect_var[p]["attributes"]['valid_max']!="":
            var.valid_max= dict_vect_var[p]["attributes"]['valid_max']
        if dict_vect_var[p]["attributes"]['valid_range']!="":
            #var.valid_range= str(dict_vect_var[p]["attributes"]['valid_range'])
            var.setncattr_string("valid_range",dict_vect_var[p]["attributes"]['valid_range'])



        
        # 18/01/2022 : on supprime l'écriture de thesaurus et instrument
        # s'ils ne sont pas définis (to be defined).
        # De plus, thesaurus n'est pas un attribut normalise, il faut
        # utiliser plutôt keywords 

        #try :
        #    var.thesaurus =  config.get(p, 'thesaurus' )
        #except configparser.NoOptionError :
        #    var.thesaurus =  "to be defined"

        #try:
        #    var.instrument = config.get(p, 'instrument' )
        #except configparser.NoOptionError :
        #    var.instrument =  "to be defined"

        var.origin = nom_vecteur  
        if (len(lst_param_traj) > 0) and (p not in lst_param_traj) :
            var.coordinates = lst_param_traj

        source=""
        try :
            source=config.get(p, "source") 
            print(" source dans le fichier de config, pas de recherche dans les vecteurs.")
            var.source=source
        except configparser.NoOptionError as e:
#            print("+ :{}: recherche des parametres sensor issus du vecteur {}:{}".format(e,nom_vecteur, source))
            lst_source=recup_source_vect_cal( nom_vecteur,str(acqid))
            source = ""
            for src in lst_source :
                source="{}; {}".format(source,src)

            if len(source) > 0 :
               var.source=source[1:]
            else :
               var.source=source
        except Exception as e:
            print("ERR lecture param:{} du vecteur {}:{}" .format(p,nom_vecteur,e))
                


        try : 
            CF_name = config.get(p, "standard_name" )
        except  configparser.NoOptionError :
            try :
                CF_name = config.get(p, "nom_CF" )
            except  configparser.NoOptionError :
                CF_name =  AIDA_name_to_CF_name ( nom_vecteur )

        if CF_name :
            # TODO : il faudrait tester si le CF est correct par rapport à la table des noms CF
            var.standard_name = CF_name
        else :
            print("-+- Attention standard_name non determine pour {}:{}\n".format(p, nom_vecteur))

        if p in lst_param_traj :
            if CF_name == "latitude" :
                lat_min_traj = np.nanmin(dict_vect_var[p]["data"])
                lat_max_traj = np.nanmax(dict_vect_var[p]["data"])

            if CF_name == "longitude" :
                lon_min_traj = np.nanmin(dict_vect_var[p]["data"])
                lon_max_traj = np.nanmax(dict_vect_var[p]["data"])

        try : 
            commentaire = config.get(p, "comment" )
            var.comment = construit_comment( commentaire, acqid)
        except  configparser.NoOptionError :
            pass 

        # association d'une (ou de plusieurs) variable(s) auxillaire(s)
        try : 
            var_auxiliere =  config.get(p, "variables_auxillaires")
            list_var_auxiliere = var_auxiliere.split(' ')
            for vara in list_var_auxiliere :
                if ( vara not in liste_param) :
                    print ("ERREUR : Dans Variable {}, {} demandée, mais n'existe pas.".format(p, var_auxiliere))
                    return 2
            var.ancillary_variables = config.get(p, "variables_auxillaires")
        except :
            pass

        # variables auxillaires en tant que flag (valeurs possibles et légende)
        try :
            flag_meanings = config.get(p, "flag_meanings")
            flag_values = config.get(p, "flag_values")
            nb_meanings = len(flag_meanings.split(' '))
            nb_values = len(flag_values.split(' '))
            if ( nb_values == nb_meanings ) :
                var.flag_meanings = config.get(p, "flag_meanings")
                var.flag_values = config.get(p, "flag_values")
            else :
                print("WARNNING : FLAG {} , nb_values != nb_meanings {} !+ {} ".format(nom_vecteur, nb_values, nb_meanings))
                return 1
        except :
            pass

        var [:] = dict_vect_var[p]["data"]

        print("--- vecteur :  {} nom param : {} N mesures : {}".format(nom_vecteur,  var.long_name, len(var) )) 

    if lon_min_cfg is not np.nan :
        root_cdf.geospatial_lon_min = lon_min_cfg
    elif lon_min_traj is not np.nan :
        root_cdf.geospatial_lon_min = lon_min_traj
    if lat_max_cfg is not np.nan :
        root_cdf.geospatial_lon_max = lon_max_traj
    elif lon_max_traj is not np.nan :
        root_cdf.geospatial_lon_max = lon_max_traj

    if lat_min_cfg is not np.nan :
        root_cdf.geospatial_lat_min = lat_min_cfg
    elif lat_min_traj is not np.nan :
        root_cdf.geospatial_lat_min = lat_min_traj
    if lat_max_cfg is not np.nan :
        root_cdf.geospatial_lat_max = lat_max
    elif lat_max_traj is not np.nan :
        root_cdf.geospatial_lat_max = lat_max_traj

    root_cdf.close() 
    return 0


def cree_time_conv ( time_bounds, conv ) :
   """
   cree un tableau time à partir des time_bounds et de la convention de datation (debu, milieu, fin)
   """ 

   d = { "debut": [1., 0.],
         "milieu": [0.5, 0.5],
         "fin": [0., 1.] }

   time = d[conv][0]* time_bounds[:,0] + d[conv][1]*time_bounds[:,1]

   return(time)



#------------------ PROG PRINCIPAL ---------------------

# décodage des arguments

parser = argparse.ArgumentParser()
parser.add_argument("prod_deb", help="date de début sous forme JJMMAAAA") 
parser.add_argument("prod_fin", help="date de fin sous forme JJMMAAAA") 
parser.add_argument('-r','--rep_out', help='nom du repertoire de sortie')
parser.add_argument('-c','--config', required = True, help='chemin complet du fichier de config')
parser.add_argument('-v','--version', required = False, help='numéro de version des fichiers à produire')

args=parser.parse_args()

# Récupération arguments 

rep_out=args.rep_out
if rep_out is(None):
    rep_out="./"
    print ("--- Ecriture des fichiers sur le repertoire courant:{}".format(rep_out))
else:
    print ("--- Ecriture des fichiers sur repertoire: {}".format(rep_out))

fic_config = args.config

#Lecture du fichier de config 

config = configparser.ConfigParser(interpolation=None)
config.read(fic_config)

# ajout nom du fichier de config dans config
try :
    config['GENERAL']['source_config'] = fic_config
except :
    pass

# Récupération des arguments début et fin de traitement

try :
    abrev_plt = AIDA.AIDA_nom_long_to_abrev( config.get('GENERAL','plateforme') ) 
    dt_deb = dt.datetime.strptime( args.prod_deb, "%d%m%Y" )
    dt_fin = dt.datetime.strptime( args.prod_fin, "%d%m%Y" )
    acqid_deb = AcqId( plateforme=abrev_plt, date= dt_deb) 
    acqid_fin = AcqId( plateforme=abrev_plt, date= dt_fin) 
except ValueError :
    try : 
        acqid_deb = AcqId(args.prod_deb)
        acqid_fin = AcqId(args.prod_fin)
        dt_deb = acqid_deb.acqid_to_date()
        dt_fin = acqid_fin.acqid_to_date()
        plateforme, annee, num = AIDA.ID_to_full(str(acqid_deb))
        abrev_plt = AIDA.AIDA_nom_long_to_abrev(plateforme) 
    except ValueError :
        print("+++ ERREUR argument début ou fin de prod incorrecte""") 
        sys.exit(1) 

if ( str(acqid_deb)[0:2] != str(acqid_fin)[0:2] ) :
    print("+++ ERREUR : Acqid_deb et acqid_fin doivent etre de la même plate-forme !")
    sys.exit(1) 

if ( acqid_deb >  acqid_fin ) :
    print("+++ ERREUR : acqid_deb doit précéder acqid_fin")
    sys.exit(1) 

# Récupération informations fichier config, section GENERAL

try : 
    version =  config.get('GENERAL','version') 
    prefixe_nomfic = config.get('GENERAL', 'base_nom_fic_out')
    base_temps_fic_out = config.get('GENERAL','base_temps_fic_out').strip() 
    nom_vecteur_temps=config.get('GENERAL','reftime') 
except  configparser.NoOptionError as m :
    print("+++ Erreur config : {}".format(m))
    sys.exit(-1)

if args.version is not None :
    version = args.version
 
if config.has_option('GENERAL', 'format_date_nom_fic_out') :
    format_date_fic_out = config.get('GENERAL', 'format_date_nom_fic_out')
else :
    format_date_fic_out = "%Y%m%d"

if config.has_option('GENERAL', 'remplace_vecteur_absent') :
    REMPLACE_VECTEUR_ABSENT = config.get('GENERAL', 'remplace_vecteur_absent') 
else :
    REMPLACE_VECTEUR_ABSENT = False 

if config.has_option('GENERAL', 'processing_level') :
    Level_data = config.get('GENERAL', 'processing_level') 
else :
    Level_data = "-1"

if config.has_option('GENERAL', 'convention_datation') :
    convention_datation = config.get('GENERAL', 'convention_datation') 
else :
    convention_datation = 'fin' 

if config.has_option('GENERAL', 'organisation_name') :
    organisation = config.get('GENERAL', 'organisation_name')
else:
    organisation=""

FIC_JOUR = True
if ( base_temps_fic_out == "periode" ):
    FIC_JOUR=False
else :
    FIC_JOUR=True


liste_param = config.sections()
liste_param.remove('GENERAL')
for param in liste_param:
    if param=="METADATA_AERIS":
        liste_param.remove('METADATA_AERIS')
#try: 
    #liste_param.remove('METADATA_AERIS')
#except Exception as e:
    #print("--- pas de section METADATA_AERIS:{}".format(e))

# Récupération info plateforme
try :
    lat_plt, lon_plt, alti_plt = AIDA.decode_position_plf(abrev_plt)
except :
    lat_plt = np.nan
    lon_plt = np.nan
    alti_plt = np.nan

# controle des noms de variables

for p in liste_param :
    if not is_varname_CF_OK ( p ) :
        print ( "-++ Attention : le nom de variable {} n'est pas conforme CF".format(p) ) 
        print ( "-++ Voir #2.3 sur https://cfconventions.org/Data/cf-conventions/cf-conventions-1.8/cf-conventions.html " ) 

#------ debut boucle sur les acqid


dict_vect_var={}
dt_time=[]
time_bounds=np.empty((0,2))
acqid = acqid_deb
acq_meta = {}
flg_fin = 0
flg_deb = 0
days_since_start = -1
while  ( acqid <= acqid_fin ): 
    days_since_start += 1
    dict_acqid_var={}
    dict_acqid_var["abrev_plt"]= abrev_plt
    dict_acqid_var["lat_plt"]= lat_plt
    dict_acqid_var["lon_plt"]= lon_plt
    dict_acqid_var["alti_plt"]= alti_plt
    dt_acq = acqid.acqid_to_date()
    dt_courant = dt.datetime(dt_acq.year, dt_acq.month, dt_acq.day, 0,0,0)
# traitement du temps time_bounds = np.empty( (len(time), 2) ) 
    try:
        nom_vecteur_temps=config.get('GENERAL','reftime') 
        vect_time = AIDA.Vector( str(acqid), config.get('GENERAL','reftime') ) 
        if ( flg_deb == 0 ) :
            dict_acqid_var["time_start"]= (dt_courant + dt.timedelta(seconds= vect_time.data[0])).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            S_time_start =  dict_acqid_var["time_start"]
            dict_acqid_var["acqid_deb"]= str(acqid)
            S_acqid_deb = dict_acqid_var["acqid_deb"]
            if ( base_temps_fic_out == "periode" ):
                flg_deb = 1
        else :
            dict_acqid_var["time_start"]= S_time_start
            dict_acqid_var["acqid_deb"]= S_acqid_deb

        dict_acqid_var["time_end"]= (dt_courant + dt.timedelta(seconds= vect_time.data[-1])).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        dict_acqid_var["acqid_fin"]= str(acqid)
    except IOError as m :
        print("-+- ATTENTION : probleme lecture vecteur temps:{}  pour l'acqid {}: {}".format( nom_vecteur_temps,acqid,m )) 
        acqid = acqid +1 
        continue 
    except Exception as e :
        print( config.get('GENERAL','reftime') )
        print("-+- ERREUR lecture acqid={}: {}".format(acqid,e))
        acqid = acqid +1 
        continue 

    nb_val_time = len(vect_time.data)
    # lecture des bornes du temps si defini dans l'entête
    freq_ech=vect_time.attributes["freq_ech"]
    if float(freq_ech) != 0 :
        time_ech = 1./float(freq_ech)
        dict_acqid_var["time_resolution"] = "PT{:f}S".format(time_ech)
    else :
        dict_acqid_var["time_resolution"] = None


    tb = AIDA.time_to_data_bnds(str(acqid), nom_vecteur_temps)

    time_conv = cree_time_conv ( tb, convention_datation )
    dt_time.extend ( [ dt_courant + dt.timedelta(seconds= t) for t in time_conv ] )
    if not FIC_JOUR :
        time_bounds = np.append ( time_bounds, tb+(days_since_start*86400), axis = 0 )
    else :
        time_bounds = np.append ( time_bounds, tb, axis = 0 )

    if ( base_temps_fic_out == "mobile"  or  base_temps_fic_out == "jour" ):
        try :
            acq_meta = AIDA.Inf(str(acqid))
        except AIDA.AidaError as err_info:
            message = "Attention Acqid non valid !"
            print(message)
        except KeyError as err_info:
            message = "Attention Acqid non valid !"
            print(message)

# lecture de tous les  vecteurs
# on les range dans un dict ayant pour clefs liste_param
    for p in liste_param :

        nom_vecteur_ini = config.get(p, "nom_vecteur") 
        nomvar = p 

        nom_vecteur =  construit_nom_vecteur ( nom_vecteur_ini, acqid )

        # on initialise d'abord la structure de données
        # avec les attributs d'un vecteur présent sur la période
        # et un tableau de données vide mais correctement formé.
        if p not in list(dict_vect_var.keys())  :
            dict_vect_var[p]= {"attributes": None, "data" : None}
            acq = acqid_deb
            while  ( acq <= acqid_fin ):
                try :
                    v = AIDA.Vector ( str(acq), nom_vecteur, attributes_only=True )
                    dict_vect_var[p]["attributes"] = v.attributes
                    break
                except IOError as m :
                    acq = acq + 1

            if dict_vect_var[p]["attributes"] is None :
                print("-+- ATTENTION : Le vecteur {} n'existe pas sur cette période".format(nom_vecteur))
                print("-+- On remplace par des valeurs manquantes")
                config.set('GENERAL', 'comment', '{} not available for this period'.format(p) )
                dict_vect_var[p]["attributes"]={}
                dict_vect_var[p]["attributes"]["misval"]= np.nan 
                dict_vect_var[p]["attributes"]["format"]= 'ieeefloat_32' 

                try : 
                    dict_vect_var[p]["attributes"]["unit"]= config.get(p, 'unit') 
                except configparser.NoOptionError :
                    dict_vect_var[p]["attributes"]["unit"]= ""
                try :
                    dict_vect_var[p]["attributes"]["dim_array"]= config.get(p, 'dim_array') 
                except  configparser.NoOptionError :
                    dict_vect_var[p]["attributes"]["dim_array"]= 1

            try : 
                dict_vect_var[p]["attributes"]["unit"]= config.get(p, 'unit') 
            except configparser.NoOptionError :
                pass

            try : 
                dict_vect_var[p]["attributes"]["valid_range"]= config.get(p, 'valid_range') 
            except configparser.NoOptionError as e:
                #print("WARN: pas de valid_max dans la section {}:e".format(e,p))
                dict_vect_var[p]["attributes"]["valid_range"]= ""
            try : 
                dict_vect_var[p]["attributes"]["valid_min"]= config.get(p, 'valid_min') 
            except configparser.NoOptionError as e:
                #print("WARN: pas de valid_min dans la section {}:e".format(e,p))
                dict_vect_var[p]["attributes"]["valid_min"]= ""
            try : 
                dict_vect_var[p]["attributes"]["valid_max"]= config.get(p, 'valid_max') 
            except configparser.NoOptionError as e:
                #print("WARN: pas de valid_max dans la section {}:e".format(e,p))
                dict_vect_var[p]["attributes"]["valid_max"]= ""
            try : 
                dict_vect_var[p]["attributes"]["comment"]= config.get(p, 'comment') 
            except configparser.NoOptionError as e:
                #print("WARN: pas de commentaire dans la section {}:e".format(e,p))
                dict_vect_var[p]["attributes"]["comment"]= ""
            try :
                dim_array = int(  dict_vect_var[p]["attributes"]["dim_array"] )
            except :
                dim_array = 1
            dict_vect_var[p]["data"] = init_tab_data(dim_array)

        # on peut maintenant lire les données et remplir la structure de
        # donnees dict_vect_var

        try : 
            vecteur = AIDA.Vector ( str(acqid), nom_vecteur )
            nb_data = len(vecteur.data) 
            dict_vect_var[p]["data"] = np.append (  dict_vect_var[p]["data"], vecteur.data, axis =0 )
        except IOError as m :
            if REMPLACE_VECTEUR_ABSENT and p in list(dict_vect_var.keys()) :
                print("-+- ATTENTION : probleme lecture vecteur {}".format( nom_vecteur )) 
                print("-+- On remplace par des valeurs manquantes")
                dim_array =  int(  dict_vect_var[p]["attributes"]["dim_array"] )
                nb_data = len(vect_time.data)
                if dim_array == 1 :
                    data = np.full( len(vect_time.data),  np.nan )
                else :
                    data = np.full ( (len(vect_time.data), dim_array ) , np.nan )

                dict_vect_var[p]["data"] = np.append (  dict_vect_var[p]["data"], data, axis =0 )
            else :
                print("+++ ERREUR: {}".format(m))
                print("+++ Pas de remplacement des vecteurs absents. On ne peut pas continuer comme ca !")
                sys.exit(-1)



        if (nb_data > 0 and nb_data != nb_val_time): 
            print(f"+++ ERREUR : Nb de valeurs différentes dans le " +\
                  f"vecteur temps '{vect_time.attributes['#hdr_name']}' et " +\
                  f"dans '{p}'")
            sys.exit(-1)


    if FIC_JOUR :
        if ( base_temps_fic_out == "mobile" ):
            if ( Level_data == "-1"  ):
                DATASET = "{}".format(prefixe_nomfic)
                FIC_CDF_OUT = os.path.join(rep_out,"{}_{}_{}_V{}.nc".format(prefixe_nomfic, dt_courant.strftime(format_date_fic_out), str(acqid),version ))
            else :
                DATASET = "{}_{}".format(prefixe_nomfic, Level_data)
                FIC_CDF_OUT = os.path.join(rep_out,"{}_{}_{}_{}_V{}.nc".format(prefixe_nomfic, dt_courant.strftime(format_date_fic_out), str(acqid), Level_data,version ))
        else :
            if ( Level_data == "-1"  ):
                DATASET = "{}".format(prefixe_nomfic)
                FIC_CDF_OUT = os.path.join(rep_out,"{}_{}_V{}.nc".format(prefixe_nomfic, dt_courant.strftime(format_date_fic_out), version ))
            else :
                DATASET = "{}_{}".format(prefixe_nomfic, Level_data)
                FIC_CDF_OUT = os.path.join(rep_out,"{}_{}_{}_V{}.nc".format(prefixe_nomfic, Level_data, dt_courant.strftime(format_date_fic_out), version ))

        # ecriture d'un fichier par jour
        cr = ecrit_fic_CDF( DATASET, FIC_CDF_OUT, dict_acqid_var, dict_vect_var, dt_time, time_bounds, config, acq_meta, version )
        if ( cr == 0 ) :
            print("--- Ecriture {} OK".format(FIC_CDF_OUT))
        else :
            print("+++ Ecriture {} NOK".format(FIC_CDF_OUT))


        for p in list(dict_vect_var.keys()) :
            try :
                dim_array = int( dict_vect_var[p]["attributes"]["dim_array"] )
            except :
                dim_array = 1
            dict_vect_var[p]["data"] = init_tab_data(dim_array)
                
        dt_time=[]
        time_bounds=np.empty((0,2))

#        time_bounds=[]


    acqid = acqid +1 

# fin de boucle sur les acqid

if not FIC_JOUR :
    # ecriture d'un fichier NetCDF pour toute la periode
    if ( Level_data == "-1"  ):
        DATASET = "{}".format(prefixe_nomfic)
        FIC_CDF_OUT = os.path.join(rep_out,"{}_{}_{}_V{}.nc".format(prefixe_nomfic, dt_deb.strftime(format_date_fic_out), dt_fin.strftime(format_date_fic_out),version ))
    else:
        DATASET = "{}_{}".format(prefixe_nomfic, Level_data)
        FIC_CDF_OUT = os.path.join(rep_out,"{}_{}_{}_{}_V{}.nc".format(prefixe_nomfic, dt_deb.strftime(format_date_fic_out), dt_fin.strftime(format_date_fic_out),Level_data,version ))
    cr = ecrit_fic_CDF(DATASET,  FIC_CDF_OUT, dict_acqid_var, dict_vect_var, dt_time, time_bounds, config, acq_meta, version )
    if ( cr == 0 ) :
        print("--- Ecriture {} OK".format(FIC_CDF_OUT))
    else :
        print("+++ Ecriture {} NOK".format(FIC_CDF_OUT))


