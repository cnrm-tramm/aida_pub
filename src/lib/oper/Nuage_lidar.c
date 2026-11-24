/****************************************************
*
* OPERATOR     Calcul des bases, peaks et top des couches nuageuses  
*              à partir d'un profil lidar PrF.
*
* VERSION        1.0
*
* ARGUMENTS    IN   float[]  PrF       -      data 1D
*              IN   int      NbCol     -      Nombre de colonne du tableau PrF
*              IN   float    Thr1      -      
*              IN   float    Thr2      -      
*              IN   float[]  z         -      altitude de mesure des Pr2
*              IN   Int      zmin      m      Altitude min extrapolation
*
*              OUT  int      flag      -      flag présence couche(s) nuageuse(s)
*              OUT  float    bases     m      tableau altitudes de la base des couches nuageuses
*              OUT  float    peak      m      tableau altitudes du sommet des couches nuageuses
*              OUT  float    top       m      tableau altitudes du sommet max des couches nuageuses
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
OP_Nuage_lidar (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  int Thr1, Thr2, Zmin, NbCol;
  PyObject *pArgs, *pFunc;
  PyObject *pValue;
  double base[NbVal][6];
  
  npy_intp dims2[2];

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.Nuage_lidar", "Nuage_lidar");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(5);
  PyErr_Print();
  NbCol = *(int*)ArgList[1];
  Thr1 = *(int*)ArgList[2];
  Thr2 = *(int*)ArgList[3];
  Zmin = *(int*)ArgList[5];

  dims2[0] = NbVal;   
  dims2[1] = NbCol; 
  (void) sprintf (DiagExec, "Nuage_lidar, %lu echant., creation de %d %d %d %d ",
		  NbVal, NbCol, Zmin, Thr1, Thr2);

  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 3, pValue);

  PyTuple_SetItem(pArgs, 1, PyFloat_FromDouble(Thr1));
  PyTuple_SetItem(pArgs, 2, PyFloat_FromDouble(Thr2));
  PyTuple_SetItem(pArgs, 4, PyFloat_FromDouble(Zmin));
  
  /* on appelle la fonction python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();
/*  PyObject_Print(pValue, stderr, 0);*/

  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[6], 4);


  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc); 


  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_Nuage_lidar (oper * optr)
{
  strcpy (optr->Nom, "Nuage_lidar");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2019-05-28 09:00:00 +0100 (Mar. 28 Mai 2019) $";
  optr->fctptr = OP_Nuage_lidar;
  optr->NbArg = 10;		/* doit rester inf. a FIL_MAX_ARG */

  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";

  /* Nbcol*/
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "any";
  optr->Arg_Car[1].famille = "any";

  /* Thr1*/
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].famille = "any";

  /* Thr2*/
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT; 
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].famille = "any";

  /* liste altitudes */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "*";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].famille = "any";

  /* zmin */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_I32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any"; 
  optr->Arg_Car[5].unite = "m";
  optr->Arg_Car[5].famille = "any";

  /* vecteur sortie */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "6";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "m";
  optr->Arg_Car[6].famille = "\"altitude\"";
  optr->Arg_Car[6].name = "\"Altitude du sommet des nuages\"";
  optr->Arg_Car[6].en_name = "\"Top cloud layer altitude\"";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "6";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "m";
  optr->Arg_Car[7].famille = "\"altitude\"";
  optr->Arg_Car[7].name = "\"Altitude base des nuages\"";
  optr->Arg_Car[7].en_name = "\"Base cloud layer altitude";
  optr->Arg_Car[7].misval = "$Arg1.misval";

  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "6";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "m";
  optr->Arg_Car[8].famille = "\"altitude\"";
  optr->Arg_Car[8].name = "\"Altitude des nuages\"";
  optr->Arg_Car[8].en_name = "\"Cloud altitude\"";
  optr->Arg_Car[8].misval = "$Arg1.misval";

  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "1";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "without";
  optr->Arg_Car[9].famille = "\"controle\"";
  optr->Arg_Car[9].name = "\"Flag presence couche nuageuse\"";
  optr->Arg_Car[9].en_name = "\"Cloud indicator flag\"";
  optr->Arg_Car[9].misval = "$Arg1.misval";

}
