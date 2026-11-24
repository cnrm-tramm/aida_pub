/*************************************************************************
*
* OPERATOR         Comble_spline  FUNCTION ANSI-C
*
* PURPOSE          Remplace les valeurs manquantes par une interpolation par spline 
*
* DESCRIPTION   
*                  1 - Calcul de la représentation spline de la courbe du paramètre X
*                  2 - Remplacement des valeurs manquantes par la valeur de la spline en ces points
*                  
*
* VERSION          1.0 
*
*
* ARGUMENTS  
*            IN   float      X          Vecteur paramètre à combler
*            IN   int        l          Lissage (>=0, préconisé = 5)
*
*            OUT  float      Xc       	Parametre X dont les valeurs manquantes sont remplacées par une interpolation par spline.
*            OUT  float      Flag_Xc    Flag valant 1 pour les valeurs de X qui ont été remplacées, 0 pour les autres.   
*
* ENTRY        NONE
*        
* SUBPROGRAMS  NONE
*        
* REFERENCES   
*
* COPYRIGHT    Meteo-France
*	       Centre National de Recherches Meteorologiques 
*	       GMEI/ TRAMM
*	       42, av G. Coriolis
*	       31057 TOULOUSE cedex  
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
OP_Comble_spline (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  PyObject *pArgs, *pValue, *pValue2, *pFunc;
  
  npy_intp dims1[1];

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.Comble_spline", "Comble_spline");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  pArgs = PyTuple_New(2);
  PyErr_Print();

  /* x */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* lissage */
  dims1[0] = 1; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);
  /* on appelle la fonction Python */

  pValue2 = PyObject_CallObject(pFunc, pArgs);
  /* PyObject_Print(pValue, stderr, 1); */

  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */
  codret=PyObject_to_ArgList ( pValue2, (float **)&ArgList[2], 2 );

  Py_DECREF(pValue);
  Py_DECREF(pValue2);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);


  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_Comble_spline (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Comble_spline");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Comble_spline;
  optr->NbArg = 4;		/* doit rester inf. a FIL_MAX_ARG */
   
  i = 0;
  /* X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";

  /* lissage */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "NULL";
  optr->Arg_Car[i].sample = "NULL";
  optr->Arg_Car[i].unite = "any";

  /* Xc */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].unite = "$Arg1.unit";

  /* Flag_Xc */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  
}
