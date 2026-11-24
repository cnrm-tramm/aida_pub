/*************************************************************************
*
* OPERATOR      PresenceNuageEch_tps_bnds  FUNCTION ANSI-C
*
* PURPOSE        Vérifie la présence d'au moins 1 top < val_seuil sur 30 minutes pour 3 couches de hbn et échantillonnage du résultat sur la base de temps 30 mn donnée par time_bnds. 
*
* DESCRIPTION   
*               Cette fonction échantillonne une variable "Var_1","Var_2" et "Var_3"
*                   qui sont datées par le vecteur temps "time_in" sur une 
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
*               IN  double  val_inv         any       valeur invalidée pour calculer les moyennes seuillées
*
*               OUT float   Var_out_         same as   variable "Var_in" échantillonnée sur la base "time_out"
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

int
fait_calcul_pres_nuage_tps_bnds (unsigned long NbVal, void *ArgList[], int IndexOut,  char *DiagExec, char *NomOper, char *NomFonction, char *ChaineArgSup)
{
  int codret;
  int NCar;
  PyObject *pArgs, *pValue, *pFunc;
  unsigned long NbValOut;
  npy_intp dims1[1];
  npy_intp dims2[2];
  float *result[3];
  float *data1_float;
  float *codret1_float;
  float *tab1_stat_float;

  NbValOut = *((unsigned long *) ArgList[7]);

  /*
   * Initialisation des structures python
   */
  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.PresenceNuageEch_tps_bnds", "fait_calcul_pres_nuage_tps_bnds");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  pArgs = PyTuple_New(9);
  PyErr_Print();

  /* X_in */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);
  PyErr_Print();

  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);
  PyErr_Print();

  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[2]);
  PyTuple_SetItem(pArgs, 2, pValue);
  PyErr_Print();

  /* Time_in */
  dims1[0] = NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);
  PyErr_Print();

  /* Tolerance manquant */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);
  PyErr_Print();

  /* Time_out */
  dims1[0] = NbValOut;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[5]);
  PyTuple_SetItem(pArgs, 5, pValue);
  PyErr_Print();

  /* Time_bnds */ 
  dims2[0] = NbValOut;
  dims2[1] = 2;
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_DOUBLE, (double *)ArgList[6]);
  PyTuple_SetItem(pArgs, 6, pValue);
  PyErr_Print();

  /* function */
  dims1[0] = strlen(NomFonction)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, NomFonction);
  PyTuple_SetItem(pArgs, 7, pValue);
  PyErr_Print();

  /* ChaineArgSup */
  dims1[0] = strlen(ChaineArgSup)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, ChaineArgSup);
  PyTuple_SetItem(pArgs, 8, pValue);
  PyErr_Print();

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();

  /* 
   * On recupere le donnees contenues dans pValue.
   * La récupération se fait forcement dans des tableaux de floats.
   */ 
  data1_float = malloc(NbValOut * sizeof (float));

  codret1_float = malloc(1 * sizeof (float));
  tab1_stat_float = malloc(3 * sizeof (float));

  result[0] = data1_float;
  result[1] = codret1_float;
  result[2] = tab1_stat_float;
  codret=PyObject_to_ArgList ( pValue, (float **)result, 3 );
  PyErr_Print();

  memcpy(ArgList[IndexOut], data1_float, NbValOut * sizeof (float));
     
  PyErr_Print();

  /*
   * Renseignement du Diagnostic
   */
      
  NCar = sprintf (DiagExec, "%s (%lu ech), ", NomOper, NbVal);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_orig in [%g,%g] ", 
                 ((double *) ArgList[3])[0],
                 ((double *) ArgList[3])[NbVal-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_dest in [%g,%g] ", 
                 ((double *) ArgList[6])[0],
                 ((double *) ArgList[6])[(NbValOut*2)-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, " nb_resu=%lu ", *((unsigned long *) ArgList[7]));
  DiagExec += NCar;
  if ( (int)codret1_float[0] == -1 )
      codret=-1;
  else 
    if ( (int)codret1_float[0] == -2 )
      codret=-2;
    else
        codret= (int)codret1_float[0] ;
  if (codret == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas pour un des vecteurs de sortie, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[3])[NbVal - 1],
	       ((double *) ArgList[6])[0]);
    }
  else if (codret == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas pour un des vecteurs de sortie, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[3])[0],
	       ((double *) ArgList[6])[(NbValOut)*2 - 1]);
    }
  else
    {
      sprintf (DiagExec,
	       "OK1:%d val. en sortie,  (OK:%d, 0:%d, pas_assez:%d). ",
	       codret, (int)tab1_stat_float[0], (int)tab1_stat_float[1], (int)tab1_stat_float[2]);
    }


  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);

  return(codret);
}


/* la fonction d'enrobage classique */
int
OP_PresenceNuageEch_tps_bnds (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  char chaine_arg_sup[80];
  int index_out;

  index_out=9;
  sprintf( chaine_arg_sup, "%f",*((float *)ArgList[8])); 

  codret = fait_calcul_pres_nuage_tps_bnds(NbVal, ArgList, index_out, DiagExec, "PresenceNuageEch_tps_bnds", "calcule_presence_nuage",chaine_arg_sup);
  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_PresenceNuageEch_tps_bnds (oper * optr)
{
  strcpy (optr->Nom, "PresenceNuageEch_tps_bnds");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2020-12-17 12:35:40 +0100 (jeu. 17 mars 2020) $";
  optr->fctptr = OP_PresenceNuageEch_tps_bnds;
  optr->NbArg = 10;		/* doit rester inf. a FIL_MAX_ARG */
   
  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "";

  /* 2: time_in */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF64;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "second";

  /* 3: Tolerance manquant */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* 4: time_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 5: time_bnds      */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";

  /* 6: size_out */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "";

  /* 7: val_inv */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "";

  /* 8: X_out */
  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg6.NbVal";	/* ou $Arg6.value */
  optr->Arg_Car[9].type_sample = "$Arg6.type_sample";
  optr->Arg_Car[9].sample = "$Arg6.sample";
  optr->Arg_Car[9].ref_time = " $Arg6.nom ";
  optr->Arg_Car[9].unite = "percent";
  optr->Arg_Car[9].famille = "$Arg1.famille";
  optr->Arg_Car[9].misval = "$Arg1.misval";
  optr->Arg_Car[9].name = "\"Pourcentage de presence d'au moins une valeur de \" + $Arg1.name + \" ou \" + $Arg2.name + \" ou \" + $Arg3.name + \" et inferieure a un seuil sur la periode\"";
  optr->Arg_Car[9].en_name = "\"Percent of presence at least one value of \" + $Arg1.english_name + \" or \" + $Arg2.english_name + \" or \" + $Arg3.english_name + \" inferior at a threhold during the periode \"";
}
