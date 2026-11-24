/****************************************************
*
* OPERATOR       Inv_Klett_sa.c   FUNCTION  ANSI-C
*
* PURPOSE 	 Inversion du singl Lidar par la methode de Klett pour
* 		 obtneirt l'AOD
*
* DESCRIPTION     
*
* VERSION        1.0
*
* ARGUMENTS    IN   float  x    	           Lidar signal P.R2  (1D) 
* 	       IN   float  gate_nbr     without	    Number of gate (array_dim)
* 	       IN   float  x_range_gate m  	    Range gate of the lidar (bornes de X) 
*              IN   float  z    	m	    Altitude of lidar date (1D) 
*              IN   float  beta_mol     m-1    	    Molecular backscatter coefficient
*              IN   float  flg_cld 	m	    Altitude of cloud (0 if no cloud)
*              IN   float  altitude_max m	    Maximum altitude to take in account  
*              IN   float  dist_min 	m	    Minimal distance of the lidar to take in account  
*              IN   float  beta_a_init	m-1     Initial value of Beta  
*              IN   float  sa	 	without     Value of sa  
*              IN   float  extrap_typ	without     Type of extrapolation ('cst' or 'lin' )  
*
*
*              OUT  float  Beta    m-1	    	    Aerosol Backscatter coefficent profile 
*              OUT  float  aod     without 	    Aerosol optical depth 
*
* ENTRY            
*                 
* SUBPROGRAMS    
* 		Inv_Klett_sa.py
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
OP_Inv_Klett_sa (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  int Nbcol;
  PyObject *pArgs, *pValue, *pFunc;
  float *bornes;
  
  npy_intp dims1[1], dims2[2];

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
  pFunc = import_py_oper ( "old_calcul.Inv_Klett_sa", "Inv_Klett_sa");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(10);
  PyErr_Print();

  dims1[0]=NbVal;

  /* x */
  dims2[0] = NbVal; 
  dims2[1] = Nbcol;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* x_range_gate */
  dims2[0] = Nbcol; 
  dims2[1] = 2;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, bornes);
  PyTuple_SetItem(pArgs, 1, pValue);

  dims2[0] = NbVal; 
  dims2[1] = Nbcol;   
  /* z */
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 2, pValue);

  /* beta_mol */
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 3, pValue);

  /* flg_cld */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[5]);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* alt_max */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[6]);
  PyTuple_SetItem(pArgs, 5, pValue);

  /* dist_min */
  pValue = PyFloat_FromDouble(*((float *)ArgList[7]));
  PyTuple_SetItem(pArgs, 6, pValue);

  /* Beta_au_init */
  pValue = PyFloat_FromDouble(*((float *)ArgList[8]));
  PyTuple_SetItem(pArgs, 7, pValue);
  
  /* sa */
  pValue = PyFloat_FromDouble(*((float *)ArgList[9]));
  PyTuple_SetItem(pArgs, 8, pValue);
  
  /* extrap_typ */
  pValue = PyUnicode_FromString((char*)ArgList[10]);
  PyTuple_SetItem(pArgs, 9, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();
  /*PyObject_Print(pValue, stderr, 0);*/

  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[11], 2 );

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc); 
  free(bornes);


  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_Inv_Klett_sa (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Inv_Klett_sa");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Inv_Klett_sa;
  optr->NbArg = 13;		/* doit rester inf. a FIL_MAX_ARG */
   
  i = 0;
  /*  0 : x */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "optique";

  /* 1 : NbCol */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* 2: x_range_gate */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_STRING;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";
  
  /* 3 : z*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "altitude";

  /* 4 : beta_mol*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "optique";

  /* 5 : flg_cld*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "without";
  optr->Arg_Car[i].famille = "";

  /* 6 : alt_max*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = "altitude";

 /* 7 : dist_min*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = "altitude";

/* 8 : beta_init */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "m-1";
  optr->Arg_Car[i].famille = "optique";

/* 9 : sa */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

/* 10: extrap_typ */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_STRING;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";


/* 11 : Beta */ 
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].unite = "m-1";
  optr->Arg_Car[i].famille = "\"optique\"";
  optr->Arg_Car[i].bornes = "$Arg1.bornes";
  optr->Arg_Car[i].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[i].name = "\"Coefficient de retrodiffusion des aerosols\"";
  optr->Arg_Car[i].en_name = "\"Aerosol backscatter coefficient\"";
  optr->Arg_Car[i].misval = "$Arg1.misval";

/* 12: aod */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[i].sample = "$Arg1.sample";
  optr->Arg_Car[i].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[i].unite = "without";
  optr->Arg_Car[i].famille = "\"optique\"";
  optr->Arg_Car[i].name = "\"Epaisseur optique des Aerosols\"";
  optr->Arg_Car[i].en_name = "\"Aerosol optical depth\"";
  optr->Arg_Car[i].misval = "$Arg1.misval";


}
