/****************************************************
*
* OPERATOR       Cospectre_Chaleur_Moncrieff97.c   FUNCTION  ANSI-C
*
* PURPOSE 	 
* 		 Compute analytic heat cospectrum by Moncrieff 97
*
* DESCRIPTION     
*
* VERSION        1.0
*
* ARGUMENTS     
* 	       IN   float      	nfreq   without Number of frequency (array_dim)
* 	       IN   float     	z 	m  	Measurement height
*              IN   float 	d 	m    	Displacement height
*              IN   float       L 	m  	Monin-Obhukov length
*	       IN   float 	u_moy 	m/s 	wind speed
*
*	       OUT  float  cospectrum 		Heat cospectrum 
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
* A system to measure surface fluxes of momentum, sensible heat,
* water vapour and carbon dioxide
* J.B. Moncrieff, J.M. Massheder, H. de Bruin, J. Elbers, T. Friborg,  B.
* Heusinkveld, P. Kabat, S. Scott, H. Soegaard, A. Verhoef
* Journal of Hydrology 188-189 (1997) 589-611
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
OP_Cospectre_Chaleur_Moncrieff97 (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int i, codret;
  int nbornes;
  PyObject *pArgs, *pValue, *pFunc, *py_o;
  int LEN_B=28;
  char *bornes, str[LEN_B];
  double *data;
  
  npy_intp dims1[1];

  Py_Initialize();
  import_array();


  /* chargement de l'operateur Python */
  pFunc = import_py_oper ( "old_calcul.Cospectre_Chaleur_Moncrieff97", "Cospectre_Chaleur_Moncrieff97");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(5);
  PyErr_Print();

  /*nfreq */
  pValue = PyFloat_FromDouble(*((float *)ArgList[0]));
  PyTuple_SetItem(pArgs, 0, pValue);

  /* z */
  pValue = PyFloat_FromDouble(*((float *)ArgList[1]));
  PyTuple_SetItem(pArgs, 1, pValue);

  /*d*/
  pValue = PyFloat_FromDouble(*((float *)ArgList[2]));
  PyTuple_SetItem(pArgs, 2, pValue);

  dims1[0]=NbVal;
  /* L */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);

  /* u_moy */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  /*PyObject_Print(pValue, stderr, 0);*/
  if ( PyErr_Occurred() != NULL )  
    {
     PyErr_Print();
     return OP_FAIL;
    }

  /* recuperation des bornes */

  py_o = PyTuple_GetItem(pValue, (Py_ssize_t)0);
  PyArrayObject* obj = PyArray_GETCONTIGUOUS( (PyArrayObject*) py_o );
  data = (double*) obj ->data;

  nbornes = obj->dimensions[0];

  bornes = (char *)malloc( (nbornes*LEN_B +1 )*sizeof(char) );
  strcpy( bornes,  "");
  for ( i=0; i< nbornes-1; i++) 
     {
      sprintf(str,"(%.6e,%.6e);", data[i], data[i]);
      strcat ( bornes, str );
     }
  sprintf(str,"(%.6e,%.6e)", data[nbornes-1], data[nbornes-1]);
  strcat ( bornes, str );

  /* renseigne la structure globale Meta_Out pour que fvb puisse écrire ces bornes
   * dans le vecteur résultat
   */
  
  Meta_Out[5].bornes = bornes ;

  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  py_o = PyTuple_GetItem(pValue, 1);
  codret=PyObject_to_ArgList ( py_o, (float **)&ArgList[5], 1 );

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc); 

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;

}

void
ID_Cospectre_Chaleur_Moncrieff97 (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Cospectre_Chaleur_Moncrieff97");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Cospectre_Chaleur_Moncrieff97;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */
   
  i = 0;
  /*  nfreq */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /*  z */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /*  d  */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* L */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "m";
  optr->Arg_Car[i].famille = "turbulence";
  
  /*  u_moy*/
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "m/s";
  optr->Arg_Car[i].famille = "vent";

/* cospectre */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "$Arg1";  
  optr->Arg_Car[i].bornes = "";
  optr->Arg_Car[i].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg4.type_sample";
  optr->Arg_Car[i].sample = "$Arg4.sample";
  optr->Arg_Car[i].ref_time = "$Arg4.ref_time";
  optr->Arg_Car[i].unite = "without";
  optr->Arg_Car[i].famille = "\"turbulence\"";
  optr->Arg_Car[i].name = "\"Cospectre analytique de chaleur selon Moncrieff 1997\"";
  optr->Arg_Car[i].en_name = "\"Heat analytic cospectrum Moncrieff 1997\"";
  optr->Arg_Car[i].misval = "$Arg4.misval";


}
