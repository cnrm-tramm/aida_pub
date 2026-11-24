/****************************************************
*
* OPERATOR       Profil_Diff_Mol_reel.c   FUNCTION  ANSI-C
*
* PURPOSE 	 Determintation du profil de diffusion moleculaire de
* 		 l'atmosphère dans une longueur d'onde donnee        
*
* DESCRIPTION     
*
* VERSION        1.0
*
* ARGUMENTS    
* 	       IN   float  X    	            Lidar signal  (1D)
* 	       IN   float  range_gate   m 	    Range gate of lidar (bornes de X)
* 	       IN   float  Zlid    	m           Altitudes du profil (1D)
* 	       IN   int    nb_z         without     Nombre de niveau du profil ( array_dim ) 
*              IN   float  T	   	C ou K	    Profil de temperature de l'air 
*              IN   float  P   		hPa	    Profil de pression atmosphérique 
*              IN   floar  lambda 	nm	    Longueur d'onde du signal diffuse 
*
*              OUT  float  a_mol     m-1	    Coefficient d'extinction moleculaire  (1D) 
*              OUT  float  b_mol     m-1	    Coefficient de retrodiffusion moleculaire  (1D) 
*              OUT  float  trayleigh without	    Coefficient de retrodiffusion moleculaire rayleigh  (1D) 
*              OUT  float  pr2_mol   Photons.m2	    Signal moleculaire retrodiffusé  (1D) 
*
*
* ENTRY            
*                 
* SUBPROGRAMS    
* 		Profil_Diff_Mol_reel.py
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
OP_Profil_Diff_Mol_reel (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  int Nbcol_lid, Nbcol_p;
  PyObject *pArgs, *pValue, *pFunc;
  float *bornes;
  
  npy_intp  dims2[2];

  Py_Initialize();
  import_array();

  Nbcol_lid = *(int*)ArgList[3];
  Nbcol_p = *(int*)ArgList[7];

  /* on récupére le tableau de bornes à partir de ArgListe[2] */

  bornes = (float *)malloc( sizeof(float)*Nbcol_lid*2);
 
  pFunc = import_py_oper ( "AIDA", "strBornes_to_array");

  pArgs = PyTuple_New(1);
  pValue = PyUnicode_FromString((char*)ArgList[1]);
  PyTuple_SetItem(pArgs, 0, pValue);

  pValue = PyObject_CallObject(pFunc, pArgs);
  codret=PyObject_to_ArgList ( pValue, &bornes, 1 );
  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);


  /* on appelle loperateur Python */

  pFunc = import_py_oper ( "old_calcul.Profil_Diff_Mol_reel", "Profil_Diff_Mol_reel");
  PyErr_Print();

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(6);
  PyErr_Print();

  /* bornes */
  dims2[0] = Nbcol_lid; 
  dims2[1] = 2;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, bornes);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* zlid */
  dims2[0] = NbVal; 
  dims2[1] = Nbcol_lid;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[2]);
  PyTuple_SetItem(pArgs, 1, pValue);

  /* z */
  dims2[0] = NbVal; 
  dims2[1] = Nbcol_p;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 2, pValue);

  /* Tz */
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[5]);
  PyTuple_SetItem(pArgs, 3, pValue);
  
  /* Pz */
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[6]);
  PyTuple_SetItem(pArgs, 4, pValue);
  
  /* lambda */
  pValue = PyFloat_FromDouble(*(float *)ArgList[8]);
  PyTuple_SetItem(pArgs, 5, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();
  /*PyObject_Print(pValue, stderr, 0);*/
  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[9], 4 );

  Py_DECREF(pFunc); 
  Py_DECREF(pArgs);
  Py_DECREF(pValue);
  free(bornes);

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;


}

void
ID_Profil_Diff_Mol_reel (oper * optr)
{
  strcpy (optr->Nom, "Profil_Diff_Mol_reel");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Profil_Diff_Mol_reel;
  optr->NbArg = 13;		/* doit rester inf. a FIL_MAX_ARG */
 
  /* X */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";
  optr->Arg_Car[0].famille = "optique";

  /* bornes */ 
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_STRING;
  optr->Arg_Car[1].array_dim = "";
  optr->Arg_Car[1].type_sample = "";
  optr->Arg_Car[1].sample = "";
  optr->Arg_Car[1].unite = "";
  optr->Arg_Car[1].famille = "";

  /* Zlid */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "*";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "m";
  optr->Arg_Car[2].famille = "altitude";

  /* nb_zlid */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "";
  optr->Arg_Car[3].type_sample = "";
  optr->Arg_Car[3].sample = "";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].famille = "";

  /* Z*/
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "";
  optr->Arg_Car[4].type_sample = "";
  optr->Arg_Car[4].sample = "";
  optr->Arg_Car[4].unite = "m";
  optr->Arg_Car[4].famille = "altitude";


  /* Tz*/
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "";
  optr->Arg_Car[5].type_sample = "";
  optr->Arg_Car[5].sample = "";
  optr->Arg_Car[5].unite = "K";
  optr->Arg_Car[5].famille = "temperature";

   /* Pz*/
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = VECTOR;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "";
  optr->Arg_Car[6].type_sample = "any";
  optr->Arg_Car[6].sample = "any";
  optr->Arg_Car[6].unite = "hPa";
  optr->Arg_Car[6].famille = "pression";
  
  /* nb_z */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_I32;
  optr->Arg_Car[7].array_dim = "";
  optr->Arg_Car[7].type_sample = "";
  optr->Arg_Car[7].sample = "";
  optr->Arg_Car[7].unite = "";
  optr->Arg_Car[7].famille = "";


 /* lambda */
  optr->Arg_Car[8].direction = DIR_IN;
  optr->Arg_Car[8].categorie = COEFFICIENT;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "";
  optr->Arg_Car[8].type_sample = "";
  optr->Arg_Car[8].sample = "";
  optr->Arg_Car[8].unite = "nm";
  optr->Arg_Car[8].famille = "";

 
  /* amol */
  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "m-1";
  optr->Arg_Car[9].famille = "\"optique";
  optr->Arg_Car[9].name = "\"Coefficient d'extinction moleculaire\"";
  optr->Arg_Car[9].en_name = "\"Molecular extinction coefficient\"";
  optr->Arg_Car[9].misval = "$Arg1.misval";


  /* bmol */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "m-1";
  optr->Arg_Car[10].famille = "\"optique\"";
  optr->Arg_Car[10].name = "\"Coefficient de retrodiffusion moleculaire\"";
  optr->Arg_Car[10].en_name = "\"Molecular backscatter coefficient\"";
  optr->Arg_Car[10].misval = "$Arg1.misval";

 /* t_rayleigh */
  optr->Arg_Car[11].direction = DIR_OUT;
  optr->Arg_Car[11].categorie = VECTOR;
  optr->Arg_Car[11].typ = ATYC_IF32;
  optr->Arg_Car[11].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[11].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[11].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[11].sample = "$Arg1.sample";
  optr->Arg_Car[11].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[11].unite = "without";
  optr->Arg_Car[11].famille = "\"optique\"";
  optr->Arg_Car[11].name = "\"Coefficient de retrodiffusion moleculaire rayleigh\"";
  optr->Arg_Car[11].en_name = "\"Rayleigh molecular backscatter profile coefficient\"";
  optr->Arg_Car[11].misval = "$Arg1.misval";

  /* pr2_mol */
  optr->Arg_Car[12].direction = DIR_OUT;
  optr->Arg_Car[12].categorie = VECTOR;
  optr->Arg_Car[12].typ = ATYC_IF32;
  optr->Arg_Car[12].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[12].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[12].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[12].sample = "$Arg1.sample";
  optr->Arg_Car[12].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[12].unite = "$Arg1.unit";
  optr->Arg_Car[12].famille = "\"optique\"";
  optr->Arg_Car[12].name = "\"Signal moleculaire retrodiffuse\"";
  optr->Arg_Car[12].en_name = "\"Molecular backscatter signal\"";
  optr->Arg_Car[12].misval = "$Arg1.misval";


}
