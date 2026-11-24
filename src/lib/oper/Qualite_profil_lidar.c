/****************************************************
*
* OPERATOR     calcul index de qualité du profil
*
* VERSION        1.0
*
* ARGUMENTS    IN   float[]  PrF       -      signal filtré du lildar
*              IN   float[]  Pr_mol    -      profil de diffusion moleculaire de l'atmosphère dans une longueur d'onde donnee 
*              IN   float[]  z         m      altitudes of lidar gate 
*              IN   float    zref      m      reference altitude for molecular signal 

*              OUT  float    qualindex m      quality index for each profiles
*
* ENTRY            
*                 
* SUBPROGRAMS    none
*
* FILES   
*
* REFERENCES   
*
* CHANGES               
*                
*
* COPYRIGHT      Meteo-France
*
* AGREEMENT      The author wishes that .....
*#########################################################################*/

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
OP_Qualite_profil_lidar (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  int NbCol;
  PyObject *pArgs, *pValue, *pFunc;
  npy_intp dims1[2];
  npy_intp dims2[1];

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.Qualite_profil_lidar", "Qualite_profil_lidar");
//  PyObject_Print(pFunc, stderr, 0);

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(4);
  PyErr_Print();
  NbCol = *(int*)ArgList[2];

  dims1[0] = NbVal;   
  dims1[1] = NbCol; 
  dims2[0] = NbVal;   
  (void) sprintf (DiagExec, "Qualite_profil_lidar, %lu echant., et %d colonnes ",
		  NbVal, NbCol);
  pValue = PyArray_SimpleNewFromData(2, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);

  pValue = PyArray_SimpleNewFromData(2, dims1, NPY_FLOAT, (float *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);

  pValue = PyArray_SimpleNewFromData(2, dims1, NPY_FLOAT, (float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 2, pValue);

  pValue = PyArray_SimpleNewFromData(1, dims2, NPY_FLOAT, (float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 3, pValue);

/*  PyObject_Print(pArgs, stderr, 0);
 */
  
  /* on appelle la fonction python */
  pValue = PyObject_CallObject(pFunc, pArgs);

  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */
  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[5], 1);

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc); 

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_Qualite_profil_lidar (oper * optr)
{
  strcpy (optr->Nom, "Qualite_profil_lidar");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2019-05-28 09:00:00 +0100 (Mar. 28 Mai 2019) $";
  optr->fctptr = OP_Qualite_profil_lidar;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Pr_mol*/
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "*";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any"; 
  optr->Arg_Car[1].famille = "any";

  /* NbCol*/
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].famille = "any";

  /* altitude */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "*";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].famille = "any";

  /* zref */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any"; 
  optr->Arg_Car[4].unite = "m";
  optr->Arg_Car[4].famille = "any";

  /* vecteur sortie */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "without";
  optr->Arg_Car[5].famille = "\"flag\"";
  optr->Arg_Car[5].name = "\"Qualite du signal lidar\"";
  optr->Arg_Car[5].en_name = "\"Quality of lidar signal\"";
  optr->Arg_Car[5].misval = "$Arg1.misval";
  
}
