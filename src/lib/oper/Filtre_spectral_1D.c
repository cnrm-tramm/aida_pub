/****************************************************
*
* OPERATOR       filtrage de fréquences et extrapolation
*               basse couche pour le traitement des données 1D. 
*
* VERSION        1.0
*
* ARGUMENTS    IN   float[]  LnPr2     -      data 1D
*              IN   float    A         %      0 < A < 1  % fréquences filtrées
*              IN   Int      zmin      m      Altitude fin extrapolation  
*              IN   Str      typ_ext         Type extralopatikon "cst" ou "lin"
*
*              OUT  float    LnPr2_FE        Data lidar filtrées et extrapolées
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
OP_Filtre_spectral_1D (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  long i, j;
  int Nbcol, Zmin;
  float Filt;
  PyObject *pArgs, *pValue, *pFunc;
 
  
  npy_intp dims1[2];

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.Filtre_spectral_1D", "Filtre_spectral_1D");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(5);
  PyErr_Print();
  Nbcol = *(int*)ArgList[1];
  Zmin = *(int*)ArgList[4];
  Filt = *(float*)ArgList[2];

  dims1[0] = NbVal; 
  dims1[1] = Nbcol;   
  (void) sprintf (DiagExec, "Filtre_apectral, %lu echant., creation de %d",
		  NbVal, Nbcol);
  pValue = PyArray_SimpleNewFromData(2, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);
  PyTuple_SetItem(pArgs, 1, PyFloat_FromDouble(Filt));
  PyTuple_SetItem(pArgs, 2, PyUnicode_FromString((char*)ArgList[3]));
  PyTuple_SetItem(pArgs, 3, PyFloat_FromDouble(Zmin));
  PyTuple_SetItem(pArgs, 4, PyUnicode_FromString((char*)ArgList[5]));
/*  PyObject_Print(pArgs, stderr, 0);*/
  
  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
/*  PyObject_Print(pValue, stderr, 0);*/

  /* on recupere le donnees dans rValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, &ArgList[6], 1 );

  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);


  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_Filtre_spectral_1D (oper * optr)
{
  strcpy (optr->Nom, "Filtre_spectral_1D");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2019-04-17 09:00:00 +0100 (Mer. 17 Avril 2019) $";
  optr->fctptr = OP_Filtre_spectral_1D;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */

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

  /* % fréquences filtrées*/
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT; 
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].famille = "any";

  /* liste altitudes */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_STRING;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].famille = "any";

  /* zmin */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_I32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any"; 
  optr->Arg_Car[4].unite = "m";
  optr->Arg_Car[4].famille = "any";

  /* type extrapolation */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_STRING;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "any";
  optr->Arg_Car[5].famille = "any";

  /* vecteur sortie */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[6].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[6].sample = "$Arg1.sample";
  optr->Arg_Car[6].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].bornes = "$Arg1.bornes";
  optr->Arg_Car[6].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[6].name = "";
  optr->Arg_Car[6].en_name = "";
  optr->Arg_Car[6].misval = "$Arg1.misval";
  
}
