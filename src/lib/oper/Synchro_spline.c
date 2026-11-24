/****************************************************
*
* OPERATOR       Synchro_spline.c   FUNCTION  ANSI-C
*
* PURPOSE 	 
* 		Synchroniser un parametre sur une autre base de temps
*		par interpolation par spline
*
* DESCRIPTION     
*
* VERSION        1.0
*
* ARGUMENTS    
* 	       IN   float  X    	            Variable a interpoler 
* 	       IN   double time			    Temps de X
* 	       IN   double time_dest		    Temps destination
* 	       IN   float  decal		    decalage temporel à appliquer (s) 
* 	       IN   string unit_x		    unite de X ( "degres" ou "radians" ou "any" )
* 	       IN   int				    taille X_sync ($Arg2.NbVal)
*
*              OUT  float  X_sync     		    X synchronisé sur time_dest 
*
* ENTRY            
*                 
* SUBPROGRAMS    
* 		Synchro_sline.py
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
* AGREEMENT      
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
OP_Synchro_spline (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  unsigned long NbVal_out;
  PyObject *pArgs, *pValue, *pFunc;
  
  npy_intp  dims[1];

  Py_Initialize();
  import_array();


  /* on appelle loperateur Python */

  pFunc = import_py_oper ( "old_calcul.Synchro_spline", "Synchro_spline");
  PyErr_Print();

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(5);
  PyErr_Print();

  /*X*/
  dims[0] = NbVal;   
  pValue = PyArray_SimpleNewFromData(1, dims, NPY_FLOAT,(float *)ArgList[0] );
  PyTuple_SetItem(pArgs, 0, pValue);

  /*time*/
  dims[0] = NbVal;   
  pValue = PyArray_SimpleNewFromData(1, dims, NPY_DOUBLE,(double *)ArgList[1] );
  PyTuple_SetItem(pArgs, 1, pValue);

  NbVal_out = *((unsigned long *)ArgList[5]); 
  /*time_dest*/
  dims[0] = NbVal_out;   
  pValue = PyArray_SimpleNewFromData(1, dims, NPY_DOUBLE,(double *)ArgList[2] );
  PyTuple_SetItem(pArgs, 2, pValue);

  /* decal */
  pValue = PyFloat_FromDouble(*(float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);

  /* unit_x */
  pValue = PyUnicode_FromString((char*)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();
  /*PyObject_Print(pValue, stderr, 0);*/
  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[6], 1 );

  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;


}

void
ID_Synchro_spline (oper * optr)
{
  strcpy (optr->Nom, "Synchro_spline");
  optr->Version = "";
  optr->Date = "";
  optr->fctptr = OP_Synchro_spline;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */
 
  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].famille = "any";

  /* time_X */ 
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";
  optr->Arg_Car[1].famille = "temps";

  /* time_dest */ 
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF64;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "second";
  optr->Arg_Car[2].famille = "temps";


  /* decal*/
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "";
  optr->Arg_Car[3].type_sample = "";
  optr->Arg_Car[3].sample = "";
  optr->Arg_Car[3].unite = "second";
  optr->Arg_Car[3].famille = "";

   /* unit */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_STRING;
  optr->Arg_Car[4].array_dim = "";
  optr->Arg_Car[4].type_sample = "";
  optr->Arg_Car[4].sample = "";
  optr->Arg_Car[4].unite = "";
  optr->Arg_Car[4].famille = "";

  /* NbVal_out */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[5].array_dim = "";
  optr->Arg_Car[5].type_sample = "";
  optr->Arg_Car[5].sample = "";
  optr->Arg_Car[5].unite = "";
  optr->Arg_Car[5].famille = "";

  /* X_sync */
  optr->Arg_Car[6].direction = DIR_OUT;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "$Arg3.array_dim";
  optr->Arg_Car[6].NbVal = "$Arg3.NbVal";
  optr->Arg_Car[6].type_sample = "$Arg3.type_sample";
  optr->Arg_Car[6].sample = "$Arg3.sample";
  optr->Arg_Car[6].ref_time = "$Arg3.nom";
  optr->Arg_Car[6].unite = "$Arg1.unit";
  optr->Arg_Car[6].famille = "$Arg1.famille";
  optr->Arg_Car[6].name = "$Arg1.name";
  optr->Arg_Car[6].en_name = "$Arg1.english_name";
  optr->Arg_Car[6].misval = "$Arg1.misval";

}
