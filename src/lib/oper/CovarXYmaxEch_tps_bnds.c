/*************************************************************************
*
* OPERATOR      CovarXYmax_tps_bnds  FUNCTION ANSI-C
*
* PURPOSE       Calcul d'une covaraince max et échantillonnage d'une variable sur une autre base
*               de temps en tenant compte du time_bnds. 
*
* DESCRIPTION  	Ce opérateur calcule les covariances et correlations sur des périodes
*		        de temps définies par l'utilisateur. (attribut time_bnds du vecteur temps associé). 
*		        A la difference de l'operateur Covar_XY : il calcule la covariance dans 
*		        tous les cas et fournit le nombre de secondes ayant servies au calcul.
*                  
*
* VERSION       1.0 
*
*
* ARGUMENTS     IN   float   x    		    Any    		premier vecteur
*               IN   float   y    		    Any    		second vecteur
*               IN   double  time_in        second      base de temps de départ
*               IN   int     tolerance_mnq              nombre mini de valeur pour accepter 
*                                                           de faire le calcul (mettre 0 pour faire
*                                                           le calcul meme si un seul point !)
*               IN   double  time_out       second      base de temps d'arrivée
*               IN   double  time_bnds      second      bornes de temps associées à time_out
*               IN   int     size_out       any         nb de valeurs dans la base de temps d'arrivée
*               IN   float   tlag_min	    s			borne minimale de variation du décalage temporel pour le
*                                                           calcul du maximum de covariance
*               IN   float   tlag_max	    s			borne maximale de variation du décalage temporel pour le
*                                                           calcul du maximum de covariance
*
*               OUT  float   Cov_xy         x's unit * Y's unit     Covariance 
*               OUT  float   Cor_xy         none		            Correlation
*               OUT  float   Nbsec_valid    s           nombre de secondes valides sur lequel la covariance
*                                                           a été calculée 
*               OUT  float   tlag   	    s           décalage temporel au maximum de covariance   	
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
OP_CovarXYmax_tps_bnds (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  unsigned long NbVal_out;
  unsigned long NbValOut;
  int NCar;
  PyObject *pArgs, *pValue, *pFunc;
  npy_intp dims1[1];
  npy_intp dims2[2];
  float *result[6];
  float *data_cov;
  float *data_corr;
  float *data_nbsec;
  float *data_lag;
  float *codret_float;
  float *tab_stat_float;
  NbValOut = *((unsigned long *) ArgList[6]);

  /*
   * Initialisation des structures python
   */
  Py_Initialize();
  import_array();

  /* on appelle l operateur Python */

  pFunc = import_py_oper ( "old_calcul.CovarXYmax_tps_bnds", "CovarXYmax_tps_bnds");
  PyErr_Print();

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(8);

  /*X*/
  dims1[0] = NbVal;   
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT,(float *)ArgList[0] );
  PyTuple_SetItem(pArgs, 0, pValue);

  /*Y*/
  dims1[0] = NbVal;   
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT,(float *)ArgList[1] );
  PyTuple_SetItem(pArgs, 1, pValue);

  /* Time_in */
  dims1[0] = NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[2]);
  PyTuple_SetItem(pArgs, 2, pValue);
  PyErr_Print();

  /* Tolerance manquant */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);
  PyErr_Print();

  /* Time_out */
  dims1[0] = NbValOut;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);
  PyErr_Print();

  /* Time_bnds */ 
  dims2[0] = NbValOut;
  dims2[1] = 2;
  
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_DOUBLE, (double *)ArgList[5]);
  PyTuple_SetItem(pArgs, 5, pValue);
  PyErr_Print();

  /* tlagmin */
  pValue = PyFloat_FromDouble(*(float *)ArgList[7]);
  PyTuple_SetItem(pArgs, 6, pValue);

  /* tlagmax */
  pValue = PyFloat_FromDouble(*(float *)ArgList[8]);
  PyTuple_SetItem(pArgs, 7, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();

  /* 
   * On recupere le donnees contenues dans pValue.
   * La r\E9cup\E9ration se fait forcement dans des tableaux de floats.
   */ 
  data_cov = malloc(NbValOut * sizeof (float));
  data_corr = malloc(NbValOut * sizeof (float));
  data_nbsec = malloc(NbValOut * sizeof (float));
  data_lag = malloc(NbValOut * sizeof (float));
  codret_float = malloc(1 * sizeof (float));
  tab_stat_float = malloc(3 * sizeof (float));
  result[0] = data_cov;
  result[1] = data_corr;
  result[2] = data_nbsec;
  result[3] = data_lag;
  result[4] = codret_float;
  result[5] = tab_stat_float;
  codret=PyObject_to_ArgList ( pValue, (float **)result, 6 );

  memcpy(ArgList[9], data_cov, NbValOut * sizeof (float));
  memcpy(ArgList[10], data_corr, NbValOut * sizeof (float));
  memcpy(ArgList[11], data_nbsec, NbValOut * sizeof (float));
  memcpy(ArgList[12], data_lag, NbValOut * sizeof (float));

  /*
   * Renseignement du Diagnostic
   */
  NCar = sprintf (DiagExec, "%s (%lu ech), ", "CovarXYmax_tps_bnds", NbVal);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_orig in [%g,%g] ", 
                 ((double *) ArgList[1])[0],
                 ((double *) ArgList[1])[NbVal-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_dest in [%g,%g] ", 
                 ((double *) ArgList[4])[0],
                 ((double *) ArgList[4])[(NbValOut*2)-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, " nb_resu=%lu ", *((unsigned long *) ArgList[5]));
  DiagExec += NCar;
  codret = (int)codret_float[0];
  if (codret == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demand\E9 (%g)",
	       ((double *) ArgList[1])[NbVal - 1],
	       ((double *) ArgList[4])[0]);
    }
  else if (codret == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demand\E9 (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[4])[(NbValOut)*2 - 1]);
    }
  else
    {
      sprintf (DiagExec,
	       "OK:%d val. en sortie,  (OK:%d, 0:%d, pas_assez:%d).",
	       codret, (int)tab_stat_float[0], (int)tab_stat_float[1], (int)tab_stat_float[2]);
    }


  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;

}

void
ID_CovarXYmax_tps_bnds (oper * optr)
{
  strcpy (optr->Nom, "CovarXYmax_tps_bnds");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2020-12-17 12:35:40 +0100 (jeu. 17 mars 2020) $";
  optr->fctptr = OP_CovarXYmax_tps_bnds;
  optr->NbArg = 13;		/* doit rester inf. a FIL_MAX_ARG */
   
  /* 1: X_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* 2: Y_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "";

  /* 3: time_in */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "second";

  /* 4: Tolerance manquant */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "";

  /* 5: time_out */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF64;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "second";

  /* 6: time_bnds      */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].typ = ATYC_STRING;
  optr->Arg_Car[5].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[5].sample = NULL;
  optr->Arg_Car[5].unite = "any";

  /* 7: size_out */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "";

 /* 8: tlag_min */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "";

 /* 9: tlag_max */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].type_sample = "any";
  optr->Arg_Car[8].sample = "any";
  optr->Arg_Car[8].unite = "";

 /* 10: covariance */
  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg5.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg5.type_sample";
  optr->Arg_Car[9].sample = "$Arg5.sample";
  optr->Arg_Car[9].ref_time = "$Arg5.nom";
  optr->Arg_Car[9].unite = "$Arg1.unit*$Arg2.unit";
  optr->Arg_Car[9].misval = "$Arg1.misval";
  optr->Arg_Car[9].famille = "\"auto\"";
  optr->Arg_Car[9].name = "\"Covariance  \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[9].en_name = "\"Covariance  \" + $Arg1.english_name + \".\" + $Arg2.english_name";

 /* 11: correlation */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "1";
  optr->Arg_Car[10].NbVal = "$Arg5.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg5.type_sample";
  optr->Arg_Car[10].sample = "$Arg5.sample";
  optr->Arg_Car[10].ref_time = "$Arg5.nom";
  optr->Arg_Car[10].unite = "$Arg1.unit*$Arg2.unit";
  optr->Arg_Car[10].misval = "$Arg1.misval";
  optr->Arg_Car[10].famille = "\"auto\"";
  optr->Arg_Car[10].name = "\"Correlation  \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[10].en_name = "\"Correlation  \" + $Arg1.english_name + \".\" + $Arg2.english_name";

 /* 12: nombre de secondes valides */
  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "1";
  optr->Arg_Car[11].NbVal = "$Arg5.NbVal";
  optr->Arg_Car[11].type_sample = "$Arg5.type_sample";
  optr->Arg_Car[11].sample = "$Arg5.sample";
  optr->Arg_Car[11].ref_time = "$Arg5.nom";
  optr->Arg_Car[11].unite = "second";
  optr->Arg_Car[11].misval = "$Arg1.misval";
  optr->Arg_Car[11].famille = "\"controle\"";
  optr->Arg_Car[11].name = "\"Nombre de secondes pour le calcul de la covariance : \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[11].en_name = "\"Number of seconds in calculation of covariance  : \" + $Arg1.english_name + \".\" + $Arg2.english_name";

/* 13: décalage au max de covariance */
  optr->Arg_Car[12].direction = DIR_OUT;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "1";
  optr->Arg_Car[12].NbVal = "$Arg5.NbVal";
  optr->Arg_Car[12].type_sample = "$Arg5.type_sample";
  optr->Arg_Car[12].sample = "$Arg5.sample";
  optr->Arg_Car[12].ref_time = "$Arg5.nom";
  optr->Arg_Car[12].unite = "second";
  optr->Arg_Car[12].misval = "$Arg1.misval";
  optr->Arg_Car[12].famille = "\"controle\"";
  optr->Arg_Car[12].name = "\"Decalage temporel au maximum de covariance \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[12].en_name = "\"Timelag to maximize covariance  : \" + $Arg1.english_name + \".\" + $Arg2.english_name";

}
