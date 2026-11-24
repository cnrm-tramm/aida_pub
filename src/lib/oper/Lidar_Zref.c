/****************************************************
*
* OPERATOR       Lidar_Zref.c   FUNCTION  ANSI-C
*
* PURPOSE 	 Determination de l'altitude max reference
* 		 pouyr l'inversion du signal lidar 
*
* DESCRIPTION     
*
* VERSION        1.0
*
* ARGUMENTS    IN   float  x    	            Lidar signal P.R2 (1D)
* 	       IN   int    z            m 	    altitudes above the ground level (in meters)
* 	       IN   int    nb_z         without     number of altitude (array_dim)
*              IN   float  z1   	m	    minimal altitude for reference altitude (in meters)
*              IN   float  z2   	m	    maximal altitude for reference altitude (in meters)
*              IN   floar  step       		    step 
*
*              OUT  float  zref     m	    Altitude maximale de reference 
*
* ENTRY            
*                 
* SUBPROGRAMS    
* 		Lidar_Zref.py
*
* FILES   
*
* REFERENCES   
* 		Utilise un code développée dans la filiere BASIC du LOA (Ph. Goloub)
* 		Code transformé par Python par CNRM/GMEI/TRAMM
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
OP_Lidar_Zref (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  int Nbcol;
  PyObject *pArgs, *pValue, *pFunc;
  
  npy_intp dims2[2];

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.Lidar_Zref", "Lidar_Zref");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(5);
  PyErr_Print();
  Nbcol = *(int*)ArgList[2];

  /* x */
  dims2[0] = NbVal; 
  dims2[1] = Nbcol;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* z */
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);

  /* z1 */
  pValue = PyFloat_FromDouble(*(float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 2, pValue);

  /* z2 */
  pValue = PyFloat_FromDouble(*(float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 3, pValue);
  
  /* step */
  pValue = PyFloat_FromDouble(*(int *)ArgList[5]);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();

  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[6], 1 );
  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc); 


  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_Lidar_Zref (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Lidar_Zref");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Lidar_Zref;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */
   
  i = 0;
  /* X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "optique";

  /* Z */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = "atltitude";

  /* nb_z */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* z1*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = "";

   /* z2*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = "";

 /* step */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

 
  /* zref */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = "\"altitude\"";
  optr->Arg_Car[i].name = "\"Altitude de reference maximale\"";
  optr->Arg_Car[i].en_name = "\"Max reference altitude\"";
  optr->Arg_Car[i].misval = "$Arg1.misval";

}
