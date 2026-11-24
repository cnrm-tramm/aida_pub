/****************************************************
*
* OPERATOR     Covar_XY_max.c   FUNCTION  ANSI-C
*
* PURPOSE      	Calcul des covariances et correlations entre 2 vecteurs, avec maximisation de la covariance
*
* DESCRIPTION  	Ce opérateur calcule les covariances et correlations sur des périodes
*		de temps consécutives définies par l'utilisateur.   
*		A la difference de l'operateur Covar_XY : il calcule la covariance dans 
*		tous les cas et fournit le nombre de secondes ayant servies au calcul.
*
* VERSION       $Revision: 5097 $
*
* ARGUMENTS   IN   float  x    		Any    				premier vecteur
*             IN   float  y    		Any    				second vecteur
*             IN   float  Fe   		s-1				fréquence d'échantillonnage des données	
*             IN   float  Tint	 	s				Temps d'intégration pour le calcul du flux	
*             IN   float  tlag_min	s				Borne minimale de variation du décalage temporel pour le calcul du maximum de covariance
*             IN   float  tlag_max	s				Borne maximale de variation du décalage temporel pour le calcul du maximum de covariance
*
*             OUT  float  Cov_xy        x's unit * Y's unit            	Covariance 
*             OUT  float  Cor_xy        none		               	Correlation
*             OUT  float  Nbsec_valid   s                              	nombre de secondes valides sur lequel la covariance a été calculée 
*             OUT  float  tlag   	s                              	decalage temporel au maximum de covariance 
*
* REFERENCES
*
*
* COPYRIGHT     Meteo-France
*
*#########################################################################*/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <limits.h>
#include <stdlib.h>

#include "thermo.h"

#include "struct_oper.h"
#include "load_oper.h"

#include <Python.h>
#include <numpy/arrayobject.h>


/* la fonction d'enrobage classique */

int
OP_Covar_XY_max (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  unsigned long NbVal_out;
  PyObject *pArgs, *pValue, *pFunc;
  npy_intp  dims[1];
  int NCar;

  Py_Initialize();
  import_array();


  NCar = sprintf (DiagExec, "Covar_XY_max : (%ld echant.) ", NbVal) ;
  if (NCar < 0)
    NCar = 0;
  DiagExec += NCar;


  /* on appelle l operateur Python */

  pFunc = import_py_oper ( "old_calcul.Covar_XY_max", "Covar_XY_max");
  PyErr_Print();

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(6);

  /*X*/
  dims[0] = NbVal;   
  pValue = PyArray_SimpleNewFromData(1, dims, NPY_FLOAT,(float *)ArgList[0] );
  PyTuple_SetItem(pArgs, 0, pValue);

  /*Y*/
  dims[0] = NbVal;   
  pValue = PyArray_SimpleNewFromData(1, dims, NPY_FLOAT,(float *)ArgList[1] );
  PyTuple_SetItem(pArgs, 1, pValue);

  /*Fe*/
  pValue = PyFloat_FromDouble(*(float *)ArgList[2]);
  PyTuple_SetItem(pArgs, 2, pValue);

  /*Tint*/
  pValue = PyFloat_FromDouble(*(float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);

  /* tlagmin */
  pValue = PyFloat_FromDouble(*(float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* tlagmax */
  pValue = PyFloat_FromDouble(*(float *)ArgList[5]);
  PyTuple_SetItem(pArgs, 5, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();
  /*PyObject_Print(pValue, stderr, 0);*/
  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[6], 4 );

  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;

}

void
ID_Covar_XY_max (oper * optr)
{
  int i;

  strcpy (optr->Nom, "Covar_XY_max");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Covar_XY_max;
  optr->NbArg = 10;
  optr->misval_auto = 1;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";

  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";

  for (i = 2; i <= 5; i++)
    {
      optr->Arg_Car[i].direction = DIR_IN;
      optr->Arg_Car[i].categorie = COEFFICIENT;
      optr->Arg_Car[i].array_dim = "1";
      optr->Arg_Car[i].typ = ATYC_IF32;
      optr->Arg_Car[i].unite = "any";
      optr->Arg_Car[i].type_sample = NULL;
      optr->Arg_Car[i].sample = NULL;
    }

  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "1./$Arg4";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg7.sample";
  optr->Arg_Car[6].unite = "$Arg1.unit*$Arg2.unit";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  optr->Arg_Car[6].famille = "\"auto\"";
  optr->Arg_Car[6].name = "\"Covariance  \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[6].en_name = "\"Covariance  \" + $Arg1.english_name + \".\" + $Arg2.english_name";

  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "1./$Arg4";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg8.sample";
  optr->Arg_Car[7].unite = "$Arg1.unit*$Arg2.unit";
  optr->Arg_Car[7].misval = "$Arg1.misval";
  optr->Arg_Car[7].famille = "\"auto\"";
  optr->Arg_Car[7].name = "\"Correlation  \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[7].en_name = "\"Correlation  \" + $Arg1.english_name + \".\" + $Arg2.english_name";

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "1";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "1./$Arg4";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg9.sample";
  optr->Arg_Car[8].unite = "second";
  optr->Arg_Car[8].misval = "$Arg1.misval";
  optr->Arg_Car[8].famille = "\"controle\"";
  optr->Arg_Car[8].name = "\"Nombre de secondes pour le calcul de la covariance : \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[8].en_name = "\"Number of seconds in calculation of covariance  : \" + $Arg1.english_name + \".\" + $Arg2.english_name";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal/($Arg3*$Arg4)";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "1./$Arg4";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time+\"_Med_\"+$Arg10.sample";
  optr->Arg_Car[9].unite = "second";
  optr->Arg_Car[9].misval = "$Arg1.misval";
  optr->Arg_Car[9].famille = "\"controle\"";
  optr->Arg_Car[9].name = "\"Decalage temporel au maximum de covariance \" + $Arg1.name + \".\" + $Arg2.name";
  optr->Arg_Car[9].en_name = "\"Timelag to maximize covariance  : \" + $Arg1.english_name + \".\" + $Arg2.english_name";



}
