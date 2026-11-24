/****************************************************
*
* OPERATOR       FT_analytique_Moncrieff.c   FUNCTION  ANSI-C
*
* PURPOSE 	 
* 	  Compute analytic transfert function of the eddy-covariance measuremnt system
*
* DESCRIPTION     
*
* VERSION        1.0
*
* ARGUMENTS     
*       IN   	float 	nfreq   without Number of frequency (array_dim
*	IN	string 	hp_lp 	without type analaytic FT 
* 	       				( 'HP': high-pass only, 'LP' : low-pass only, 'HPLP' : high-pass and low-pass ) 
*	IN	float	fe 	Hz	sample frequency 
*	IN	float	tint 	s	integration duration 
*       IN 	string	type1 	without type of instrument 1
*       IN 	string	type2 	without	type of instrument 2
*       IN	float	hsep 	m 	horizontal separation between instruments 1 and 2
*       IN	float	vsep 	m	vertical separation between instruments 1 and 2 (m)
*       IN 	string	type_hp	without	type of fluctuation computing method ( 'ba': block average, 'rm' : moyenne glissante )
*       IN 	float	tauf 	s	time constant of running-mean  
*       IN	float	u_moy	m/s	wind speed 
*
*	OUT  	float	TF	without	Transfert function 
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
OP_FT_analytique_Moncrieff (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int i, codret;
  int nbornes;
  PyObject *pArgs, *pValue, *pFunc, *py_o;
  PyObject *type, *value, *traceback;
  int LEN_B=28;
  char *msg_err, *bornes, str[LEN_B];
  double *data;
  
  npy_intp dims1[1];

  Py_Initialize();
  import_array();


  /* chargement de l'operateur Python */
  pFunc = import_py_oper ( "old_calcul.FT_analytique_Moncrieff", "FT_analytique_Moncrieff");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */

  pArgs = PyTuple_New(11);
  PyErr_Print();

  /*nfreq */
  pValue = PyFloat_FromDouble(*((float *)ArgList[0]));
  PyTuple_SetItem(pArgs, 0, pValue);

  /* hf_bf */
  pValue = PyUnicode_FromString((char*)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);

  /* fe */
  pValue = PyFloat_FromDouble(*((float *)ArgList[2]));
  PyTuple_SetItem(pArgs, 2, pValue);

  /*tint*/
  pValue = PyFloat_FromDouble(*((float *)ArgList[3]));
  PyTuple_SetItem(pArgs, 3, pValue);

  /* type 1 */
  pValue = PyUnicode_FromString((char*)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* type 2 */
  pValue = PyUnicode_FromString((char*)ArgList[5]);
  PyTuple_SetItem(pArgs, 5, pValue);

  /* hsep */
  pValue = PyFloat_FromDouble(*((float *)ArgList[6]));
  PyTuple_SetItem(pArgs, 6, pValue);

  /* vsep */
  pValue = PyFloat_FromDouble(*((float *)ArgList[7]));
  PyTuple_SetItem(pArgs, 7, pValue);

  /* type_hp */
  pValue = PyUnicode_FromString((char*)ArgList[8]);
  PyTuple_SetItem(pArgs, 8, pValue);

  /* tauf */
  pValue = PyFloat_FromDouble(*((float *)ArgList[9]));
  PyTuple_SetItem(pArgs, 9, pValue);

  /* u_moy */
  dims1[0]=NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[10]);
  PyTuple_SetItem(pArgs, 10, pValue);

  /* on appelle la fonction Python */

  pValue = PyObject_CallObject(pFunc, pArgs);
  /*PyObject_Print(pValue, stderr, 0);*/

  /* traitement erreur fonction Python */
  if ( PyErr_Occurred() != NULL )  
    {
     PyErr_Fetch(&type, &value, &traceback);
     PyObject* repr = PyObject_Repr(value);
     PyObject* str = PyUnicode_AsEncodedString(repr, "utf-8", "~E~");
     msg_err = PyBytes_AS_STRING(str);
     fprintf(stderr, "+++ %s\n", msg_err );
     Py_DECREF(repr); 
     Py_DECREF(str); 
     Py_DECREF(type); 
     Py_DECREF(value); 
     Py_DECREF(traceback); 
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
  
  Meta_Out[11].bornes = bornes ;

  /* on recupere le donnees dans pValue qui est un PyObject 
   * pour les mettre dans ArgList */

  py_o = PyTuple_GetItem(pValue,(Py_ssize_t)1);
  codret=PyObject_to_ArgList ( py_o, (float **)&ArgList[11], 1 );

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc); 

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;

}

void
ID_FT_analytique_Moncrieff (oper * optr)
{
  int i;
  strcpy (optr->Nom, "FT_analytique_Moncrieff");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_FT_analytique_Moncrieff;
  optr->NbArg = 12;		/* doit rester inf. a FIL_MAX_ARG */
   
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

  /*  hp_lp */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_STRING;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /*  fe  */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* tint */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* type 1 */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_STRING;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* type 2 */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_STRING;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

 /*  hsep  */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* vsep */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* type_hp */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_STRING;
  optr->Arg_Car[i].array_dim = "*";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

  /* tauf */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "";
  optr->Arg_Car[i].type_sample = "";
  optr->Arg_Car[i].sample = "";
  optr->Arg_Car[i].unite = "";
  optr->Arg_Car[i].famille = "";

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

/* fonction de transfert */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF32;
  optr->Arg_Car[i].array_dim = "$Arg1";  
  optr->Arg_Car[i].bornes = "";
  optr->Arg_Car[i].NbVal = "$Arg11.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg11.type_sample";
  optr->Arg_Car[i].sample = "$Arg11.sample";
  optr->Arg_Car[i].ref_time = "$Arg11.ref_time";
  optr->Arg_Car[i].unite = "without";
  optr->Arg_Car[i].famille = "\"controle\"";
  optr->Arg_Car[i].name = "\"Fonction de transfert analytique du systeme selon Moncrieff 1997\"";
  optr->Arg_Car[i].en_name = "\"Transfert function of measrement system from Moncrieff 1997\"";
  optr->Arg_Car[i].misval = "$Arg11.misval";


}
