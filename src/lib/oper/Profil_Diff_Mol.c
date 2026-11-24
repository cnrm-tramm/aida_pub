/****************************************************
*
* OPERATOR       Profil_Diff_Mol.c   FUNCTION  ANSI-C
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
* 	       IN   float  Z    	m           Altitudes du profil (1D)
* 	       IN   int    nb_z         without     Nombre de niveau du profil ( array_dim ) 
*              IN   float  T0   	C ou K	    Temperature de l'air au niveau de la mer 
*              IN   float  P0   	hPa	    Pression atmosphérique  au niveau de la mer 
*              IN   floar  lambda 	nm	    Longueur d'onde du signal diffuse 
*
*              OUT  float  a_mol     ?	    Signal moleculaire diffusé  (1D) 
*              OUT  float  b_mol     ?	    Signal moleculaire diffusé  (1D) 
*              OUT  float  trayleigh     ?	    Signal moleculaire diffusé  (1D) 
*              OUT  float  pr2_mol     ?	    Signal moleculaire diffusé  (1D) 
*
*
* ENTRY            
*                 
* SUBPROGRAMS    
* 		Profil_Diff_Mol.py
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
OP_Profil_Diff_Mol (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  int Nbcol;
  PyObject *pArgs, *pValue, *pFunc;
  float *bornes;
  
  npy_intp  dims2[2];

  Py_Initialize();
  import_array();

  Nbcol = *(int*)ArgList[3];

  /* on récupére le tableau de bornes à partir de ArgListe[2] */

  bornes = (float *)malloc( sizeof(float)*Nbcol*2);
 
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

  pFunc = import_py_oper ( "old_calcul.Profil_Diff_Mol", "Profil_Diff_Mol");
  PyErr_Print();

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(5);
  PyErr_Print();

  /* bornes */
  dims2[0] = Nbcol; 
  dims2[1] = 2;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, bornes);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* z */
  dims2[0] = NbVal; 
  dims2[1] = Nbcol;   
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_FLOAT, (float *)ArgList[2]);
  PyTuple_SetItem(pArgs, 1, pValue);

  /* T0 */
  pValue = PyFloat_FromDouble(*(float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 2, pValue);

  /* P0 */
  pValue = PyFloat_FromDouble(*(float *)ArgList[5]);
  PyTuple_SetItem(pArgs, 3, pValue);
  
  /* lambda */
  pValue = PyFloat_FromDouble(*(float *)ArgList[6]);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();
  /*PyObject_Print(pValue, stderr, 0);*/
  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  codret=PyObject_to_ArgList ( pValue, (float **)&ArgList[7], 4 );

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
ID_Profil_Diff_Mol (oper * optr)
{
  strcpy (optr->Nom, "Profil_Diff_Mol");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Profil_Diff_Mol;
  optr->NbArg = 11;		/* doit rester inf. a FIL_MAX_ARG */
 
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

  /* Z */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "*";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "m";
  optr->Arg_Car[2].famille = "altitude";

  /* nb_z */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "";
  optr->Arg_Car[3].type_sample = "";
  optr->Arg_Car[3].sample = "";
  optr->Arg_Car[3].unite = "";
  optr->Arg_Car[3].famille = "";

  /* T0*/
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "";
  optr->Arg_Car[4].type_sample = "";
  optr->Arg_Car[4].sample = "";
  optr->Arg_Car[4].unite = "K";
  optr->Arg_Car[4].famille = "";

   /* P0*/
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = COEFFICIENT;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "hPa";
  optr->Arg_Car[5].famille = "";

 /* lambda */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].typ = ATYC_IF32;
  optr->Arg_Car[6].array_dim = "";
  optr->Arg_Car[6].type_sample = "";
  optr->Arg_Car[6].sample = "";
  optr->Arg_Car[6].unite = "nm";
  optr->Arg_Car[6].famille = "";

 
  /* amol */
  optr->Arg_Car[7].direction = DIR_OUT;
  optr->Arg_Car[7].categorie = VECTOR;
  optr->Arg_Car[7].typ = ATYC_IF32;
  optr->Arg_Car[7].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[7].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[7].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[7].sample = "$Arg1.sample";
  optr->Arg_Car[7].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[7].unite = "m-1";
  optr->Arg_Car[7].famille = "\"optique";
  optr->Arg_Car[7].name = "\"Coefficient d'extinction moleculaire\"";
  optr->Arg_Car[7].en_name = "\"Molecular extinction coefficient\"";
  optr->Arg_Car[7].misval = "$Arg1.misval";


  /* bmol */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].unite = "m-1";
  optr->Arg_Car[8].famille = "\"optique\"";
  optr->Arg_Car[8].name = "\"Coefficient de retrodiffusion moleculaire\"";
  optr->Arg_Car[8].en_name = "\"Molecular backscatter coefficient\"";
  optr->Arg_Car[8].misval = "$Arg1.misval";

 /* t_rayleigh */
  optr->Arg_Car[9].direction = DIR_OUT;
  optr->Arg_Car[9].categorie = VECTOR;
  optr->Arg_Car[9].typ = ATYC_IF32;
  optr->Arg_Car[9].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[9].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[9].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[9].sample = "$Arg1.sample";
  optr->Arg_Car[9].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[9].unite = "without";
  optr->Arg_Car[9].famille = "\"optique\"";
  optr->Arg_Car[9].name = "\"Coefficient de retrodiffusion moleculaire rayleigh\"";
  optr->Arg_Car[9].en_name = "\"Rayleigh molecular backscatter profile coefficient\"";
  optr->Arg_Car[9].misval = "$Arg1.misval";

  /* pr2_mol */
  optr->Arg_Car[10].direction = DIR_OUT;
  optr->Arg_Car[10].categorie = VECTOR;
  optr->Arg_Car[10].typ = ATYC_IF32;
  optr->Arg_Car[10].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[10].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[10].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[10].sample = "$Arg1.sample";
  optr->Arg_Car[10].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[10].unite = "$Arg1.unit";
  optr->Arg_Car[10].famille = "\"optique\"";
  optr->Arg_Car[10].name = "\"Signal moleculaire retrodiffuse\"";
  optr->Arg_Car[10].en_name = "\"Molecular backscatter signal\"";
  optr->Arg_Car[10].misval = "$Arg1.misval";




}
