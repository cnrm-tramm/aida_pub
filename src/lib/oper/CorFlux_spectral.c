/****************************************************
*
* OPERATOR       CorFlux_spectral.c   FUNCTION  ANSI-C
*
* PURPOSE 	 
*
*    Compute spectral correction and corrected flux
*    with cospectra and transfer function of the measurements system
*
* DESCRIPTION     
*
* VERSION        1.0
*
* ARGUMENTS     
*	IN      float	cospectre 		without 	ideal cospectrum [nfreq]
*    	IN	float  	nfreq	   		without 	number of requencies ($Arg1.array_dim)
*    	IN	float  	freq	   		without 	frequencies ($Arg1.bornes)
*	IN	float	fonction_transfert	without 	transfer function of the measurement system
*	IN	float	flux			W/m2		flux to be corrected
*
*	OUT	float	flux_cor		W/m2		corrected flux
*       OUT	float 	cor_spectrale		without 	spectral correction
*
* ENTRY            
*                 
* SUBPROGRAMS    
* 	
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
OP_CorFlux_spectral (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  int Nbcol;
  PyObject *pArgs, *pValue, *pFunc;
  float *bornes;
  
  npy_intp dims1[1];
  npy_intp dims2[2];

  Py_Initialize();
  import_array();

  Nbcol = *(int*)ArgList[1];

  /* on récupére le tableau de bornes à partir de ArgListe[2] */

  bornes = (float *)malloc( sizeof(float)*Nbcol*2);
 
  pFunc = import_py_oper ( "AIDA", "strBornes_to_array");

  pArgs = PyTuple_New(1);
  pValue = PyUnicode_FromString((char*)ArgList[2]);
  PyTuple_SetItem(pArgs, 0, pValue);

  pValue = PyObject_CallObject(pFunc, pArgs);
  codret=PyObject_to_ArgList ( pValue, &bornes, 1 );
  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);

  /* chargement de l'operateur Python */
  pFunc = import_py_oper ( "old_calcul.CorFlux_spectral", "CorFlux_spectral");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(4);
  PyErr_Print();


  /*nf */
  dims2[0] = Nbcol; 
  dims2[1] = 2; 
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, bornes);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* cospectre */
  dims2[0] = NbVal; 
  dims2[1] = Nbcol;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 1, pValue);

  /* fonction de transfert */
  dims2[0] = NbVal; 
  dims2[1] = Nbcol;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 2, pValue);

  /* flux */
  dims1[0]=NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 3, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  /*PyObject_Print(pValue, stderr, 0);*/

  if ( PyErr_Occurred() != NULL )  
    {
     PyErr_Print();
     return OP_FAIL;
    }


  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[5], 2 );

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc); 

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;


}

void
ID_CorFlux_spectral (oper * optr)
{
  int i;
  strcpy (optr->Nom, "CorFlux_spectral");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_CorFlux_spectral;
  optr->NbArg = 7;		/* doit rester inf. a FIL_MAX_ARG */
   
  i = 0;

  /* 0: cospectre */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* 1: nfreq */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* 2: freq */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_STRING;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* 3: fonction de transfert */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";
  
  /* 4: flux*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1" ;
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "W/m2";
  optr->Arg_Car[i].famille = "flux";

  /* 5: flux_cor  */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";  
  optr->Arg_Car[i].NbVal = "$Arg5.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg5.type_sample";
  optr->Arg_Car[i].sample = "$Arg5.sample";
  optr->Arg_Car[i].ref_time = "$Arg5.ref_time";
  optr->Arg_Car[i].unite = "$Arg5.unit";
  optr->Arg_Car[i].famille = "$Arg5.famille";
  optr->Arg_Car[i].name = "$Arg5.name + \" avec correction spectrale\"";
  optr->Arg_Car[i].en_name = "$Arg5.english_name + \"with spectral correction\"";
  optr->Arg_Car[i].misval = "$Arg5.misval";

  /* 6: correction spectrale  */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";  
  optr->Arg_Car[i].NbVal = "$Arg5.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg5.type_sample";
  optr->Arg_Car[i].sample = "$Arg5.sample";
  optr->Arg_Car[i].ref_time = "$Arg5.ref_time";
  optr->Arg_Car[i].unite = "without";
  optr->Arg_Car[i].famille = "\"controle\"";
  optr->Arg_Car[i].name = "\"Correction spectrale de \"+ $Arg5.name";
  optr->Arg_Car[i].en_name = "\"Spectral correction of \" + $Arg5.english_name";
  optr->Arg_Car[i].misval = "$Arg5.misval";

}
