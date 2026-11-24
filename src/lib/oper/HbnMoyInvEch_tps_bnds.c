/*************************************************************************
*
* OPERATOR      HbnMoyInvEch_tps_bnds  FUNCTION ANSI-C
*
* PURPOSE       Calcul des moyennes sur 30 minutes des 3 couches de hbn , si le nombre de couches reste constant sur la période et échantillonnage d'une variable sur une autre base de temps en tenant compte du time_bnds. 
*
* DESCRIPTION   
*               Cette fonction échantillonne une variable "Var_1","Var_2" et "Var_3"
*                   qui sont datées par le vecteur temps "time_in" sur une 
*                   autre base de temps "time_out" définissant un "time_bnds".
*               La variable resultat est "Var_out_1","Var_out_2","Var_out_3".	
*               On ne fait aucune supposition sur la régularité de
*                   l'échantillonnage des 2 variables. Cette fonction peut
*                   donc servir, par exemple, à transformer une serie temporelle
*                   asynchrone en une série régulière.
*               On suppose que time_in est "à peu près" trié par ordre
*                   croissant.
*                  
*
* VERSION       1.0 
*
*
* ARGUMENTS     IN  float   Var_in_1          any       variable de départ a échantillonner
* ARGUMENTS     IN  float   Var_in_2          any       variable de départ a échantillonner
* ARGUMENTS     IN  float   Var_in_3          any       variable de départ a échantillonner
*               IN  double  time_in         second    base de temps de départ
*               IN  int     tolerance_mnq             Nombre mini de valeur pour accepter 
*                                                     de faire le calcul (mettre 0 pour faire
*                                                     le calcul meme si un seul point !)
*               IN  double  time_out        second    base de temps d'arrivée
*               IN  double  time_bnds       second    bornes de temps associées à time_out
*               IN  int     size_out        any       Nb de valeurs dans la base de temps d'arrivée
*               IN  double  val_inv         any       valeur à invalider pour calculer les moyennes
*               IN  double  val_replac      any       valeur de remplacement pour les valeurs égales à val_inv
*               IN  double  tolerance_inv   any       tolerance (pourcentage entre 0 et 1) de valeurs invalides acceptables pour calculer la moyenne
*
*               OUT float   Var_out_1         same as   variable "Var_in" échantillonnée sur la base "time_out"
*               OUT float   Var_out_2        same as   variable "Var_in" échantillonnée sur la base "time_out"
*               OUT float   Var_out_3       same as   variable "Var_in" échantillonnée sur la base "time_out"
*
* ENTRY         NONE
*        
* SUBPROGRAMS   NONE
*        
* REFERENCES   
*
* COPYRIGHT     Meteo-France
*	            Centre National de Recherches Meteorologiques 
*	            GMEI/ TRAMM
*	            42, av G. Coriolis
*	            31057 TOULOUSE cedex  
*
*
*############################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "load_oper.h"

#include <Python.h>
#include <numpy/arrayobject.h>

/* la fonction d'enrobage classique */
int
OP_HbnMoyInvEch_tps_bnds (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  char chaine_arg_sup[80];
  int index_out;

  sprintf( chaine_arg_sup, "%f:%f:%f",*((float *)ArgList[8]), *((float *)ArgList[9]), *((float *)ArgList[10])); 

  index_out=11;
  codret = fait_calcul_tps_bnds_3couches(NbVal, ArgList, index_out, DiagExec, "HbnMoyInvEch_tps_bnds", "calcule_moy_3couches",chaine_arg_sup);
  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_HbnMoyInvEch_tps_bnds (oper * optr)
{
  strcpy (optr->Nom, "HbnMoyInvEch_tps_bnds");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2020-12-17 12:35:40 +0100 (jeu. 17 mars 2020) $";
  optr->fctptr = OP_HbnMoyInvEch_tps_bnds;
  optr->NbArg = 14;		/* doit rester inf. a FIL_MAX_ARG */
   
  /* 1: X_in_1 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: X_in_2 */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* 3: X_in_3 */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: time_in */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "second";

  /* 5: Tolerance manquant */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 6: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 7: time_bnds      */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  /* 8: size_out */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "";

  /* 9: val_inv */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "";

 /* 10: val_replac */
  optr->Arg_Car[9].direction = DIR_IN;
  optr->Arg_Car[9].categorie = COEFFICIENT;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].type_sample = "any";
  optr->Arg_Car[9].sample = "any";
  optr->Arg_Car[9].unite = "";

 /* 11: tolerance_inv */
  optr->Arg_Car[10].direction = DIR_IN;
  optr->Arg_Car[10].categorie = COEFFICIENT;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].type_sample = "any";
  optr->Arg_Car[10].sample = "any";
  optr->Arg_Car[10].unite = "";

  /* 12: X_out_1 */
  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[11].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[11].sample = "$Arg6.sample";
  optr->Arg_Car[11].ref_time = " $Arg6.nom ";
  optr->Arg_Car[11].unite = "$Arg1.unit";
  optr->Arg_Car[11].famille = "$Arg1.famille";
  optr->Arg_Car[11].misval = "$Arg1.misval";
  optr->Arg_Car[11].name = "\"Moyenne hors valeurs invalides de \"+$Arg1.name + \" synchronisé sur \" + $Arg6.name + \" sans changement de couches\"";
  optr->Arg_Car[11].en_name = "\"Mean by period without invalid values of \"+$Arg1.english_name + \" synchronised on \" + $Arg6.english_name +\" without change of layers\"";

  /* 13: X_out_2 */
  optr->Arg_Car[12].direction = DIR_OUT;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[12].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[12].sample = "$Arg6.sample";
  optr->Arg_Car[12].ref_time = " $Arg6.nom ";
  optr->Arg_Car[12].unite = "$Arg1.unit";
  optr->Arg_Car[12].famille = "$Arg1.famille";
  optr->Arg_Car[12].misval = "$Arg1.misval";
  optr->Arg_Car[12].name = "\"Moyenne hors valeurs invalides de \"+$Arg2.name + \" synchronisé sur \" + $Arg6.name + \" sans changement de couches\"";
  optr->Arg_Car[12].en_name = "\"Mean without invalid values of \"+$Arg2.english_name + \" synchronised on \" + $Arg6.english_name +\" without change of layers\"";

  /* 14: X_out_3 */
  optr->Arg_Car[13].direction = DIR_OUT;
  optr->Arg_Car[13].categorie = VECTOR;
  optr->Arg_Car[13].typ = ATYC_IF32;
  optr->Arg_Car[13].array_dim = "1";
  optr->Arg_Car[13].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[13].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[13].sample = "$Arg6.sample";
  optr->Arg_Car[13].ref_time = " $Arg6.nom ";
  optr->Arg_Car[13].unite = "$Arg1.unit";
  optr->Arg_Car[13].famille = "$Arg1.famille";
  optr->Arg_Car[13].misval = "$Arg1.misval";
  optr->Arg_Car[13].name = "\"Moyenne hors valeurs invalides de \"+$Arg3.name + \" synchronisé sur \" + $Arg6.name + \" sans changement de couches\"";
  optr->Arg_Car[13].en_name = "\"Mean without invalid values of \"+$Arg3.english_name + \" synchronised on \" + $Arg6.english_name +\" without change of layers\"";
}
