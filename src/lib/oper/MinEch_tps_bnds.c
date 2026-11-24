/*************************************************************************
*
* OPERATOR      MinEch_tps_bnds  FUNCTION ANSI-C
*
* PURPOSE       Moyenne et échantillonnage d'une variable sur une autre base
*               de temps en tenant compte du time_bnds. 
*
* DESCRIPTION   
*               Cette fonction échantillonne une variable "Var_in"
*                   qui est datée par le vecteur temps "time_in" sur une 
*                   autre base de temps "time_out" définissant un "time_bnds".
*               La variable resultat est "Var_out".	
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
* ARGUMENTS     IN  float   Var_in          any       variable de départ a échantillonner
*               IN  double  time_in         second    base de temps de départ
*               IN  int     tolerance_mnq             Nombre mini de valeur pour accepter 
*                                                     de faire le calcul (mettre 0 pour faire
*                                                     le calcul meme si un seul point !)
*               IN  double  time_out        second    base de temps d'arrivée
*               IN  double  time_bnds       second    bornes de temps associées à time_out
*               IN  int     size_out        any       Nb de valeurs dans la base de temps d'arrivée
*
*               OUT float   Var_out         same as   variable "Var_in" échantillonnée sur la base "time_out"
*					                        Var_in    	
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
OP_MinEch_tps_bnds (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  char chaine_arg_sup[80];
  int index_out;

  index_out=6;
  sprintf( chaine_arg_sup, "") ; 

  codret = fait_calcul_tps_bnds(NbVal, ArgList, index_out, DiagExec, "MinEch_tps_bnds", "calcule_min",chaine_arg_sup);
  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_MinEch_tps_bnds (oper * optr)
{
  strcpy (optr->Nom, "MinEch_tps_bnds");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2020-12-17 12:35:40 +0100 (jeu. 17 mars 2020) $";
  optr->fctptr = OP_MinEch_tps_bnds;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */
   
  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* 3: Tolerance manquant */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 4: time_out */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  /*optr->Arg_Car[3].NbVal = "$Arg4.NbVal";*/	/* ou $Arg6.value */
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "second";

  /* 5: time_bnds      */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].typ = ATYC_STRING;
  optr->Arg_Car[4].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  /* 6: size_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "";

  /* 7: X_out */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg4.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[6].type_sample = "$Arg4.type_sample";
  optr->Arg_Car[6].sample = "$Arg4.sample";
  optr->Arg_Car[6].ref_time = " $Arg4.nom ";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].name = "\"Minimum de \" +$Arg1.name + \" sur \" + $Arg4.name";
  optr->Arg_Car[6].en_name ="\"Minimum of \"+$Arg1.english_name + \" on \" + $Arg4.english_name";
}
