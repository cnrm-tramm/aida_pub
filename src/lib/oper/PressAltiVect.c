/*************************************************************************
*
* OPERATOR         PressAltiVect.c  FUNCTION ANSI-C
*
* PURPOSE          Calcul de la pression aux altitudes Z à partir des pressions P0 mesurées aux altitudes Z0.
*
* DESCRIPTION                     
*
* VERSION          1.0 
*
*
* ARGUMENTS  
*                IN   float   P0      hPa             Pressions au niveau Z0 
*                IN   float   Tv      Kelvin          Tempé virtuelle moyenne de la couche
*                IN   float   Z0      m               Altitudes correpondantes à P0 
*                IN   float   Z       m               Altitudes pour lesquelles on calcule P 
*                IN   float   rsurg                   "constante" r/g
*
*                OUT  float   P       same as P0      Pressions aux altitude Z 

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
/* #define _XOPEN_SOURCE 600
 * SB message à la compil : 
 *   /usr/include/python3.7m/pyconfig-64.h:1537: warning: « _XOPEN_SOURCE » redéfini
 *   #define _XOPEN_SOURCE 700
 *   PressAltiVect.c:38: note: ceci est l'emplacement d’une précédente définition
 *   #define _XOPEN_SOURCE 600
 */
#define _XOPEN_SOURCE 700


/* Le #define _HPUX_SOURCE n'est la que pour "voir" strdup */
#define _HPUX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"
#include "load_oper.h"
#include "unit_def.h"


#include <Python.h>
#include <numpy/arrayobject.h>


/* la fonction d'enrobage classique */

int
PressAltiVect (unsigned long NbValOut,
	   float *P0, 
	   float *Tv,
	   float *Z0, 
	   float *Z, 
	   float rsurg, 
	   float *P)
{
  int codret;
  PyObject *pArgs, *pValue, *pFunc;
  npy_intp dims1[1];
  int flag_info_tempe;
  float CtoK;

  /* Détermination automatique Kelvin/Celsius */
  flag_info_tempe = auto_tempe_unit (NbValOut, Tv, &CtoK);

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.PressAltiVect", "PressAltiVect");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  pArgs = PyTuple_New(6);
  PyErr_Print();

  /* P0 */
  dims1[0] = NbValOut; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, P0);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* Tv */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, Tv);
  PyTuple_SetItem(pArgs, 1, pValue);

  /*CtoK */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, &CtoK);
  PyTuple_SetItem(pArgs, 2, pValue);

  /* Z0 */
  dims1[0] = NbValOut;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, Z0);
  PyTuple_SetItem(pArgs, 3, pValue);

  /* Z */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, Z);
  PyTuple_SetItem(pArgs, 4, pValue);

  /* rsurg */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, &rsurg);
  PyTuple_SetItem(pArgs, 5, pValue);

  /* on appelle la fonction Python */
  pValue = PyObject_CallObject(pFunc, pArgs);

  /* 
   * On recupere le donnees dans un PyObject.
   * La récupération se fait forcement dans des tableaux de floats mais
   * on veut des donnees de type int en sortie :
   *   on utilise donc un tableau de float temporaire pour recuperer les donnees
   *   puis on le copie dans le tableau de sortie en int.
   */  
  codret=PyObject_to_ArgList ( pValue, (float **)&P, 1 );

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);

  return flag_info_tempe;
}


int
OP_PressAltiVect (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int CodRet;

  sprintf (DiagExec, "OP_PressAltiVect (%lu ech.), Z0=%f, Z= %f, R/g = %f", NbVal,
	   *((float *) ArgList[2]), *((float *) ArgList[3]), *((float *) ArgList[4]));

  CodRet = PressAltiVect (NbVal,
		      (float *) ArgList[0],
		      (float *) ArgList[1],
		      (float *) ArgList[2],
		      (float *) ArgList[3], 
		      *((float *) ArgList[4]), 
		      (float *) ArgList[5]);

  switch (CodRet)
    {
    case -1:
      strcat (DiagExec, "ERR : Tempé Ni Kelvin Ni Celsius");
      return OP_FAIL;
    case T_EN_K :
      strcat (DiagExec, "Unité Température reconnue : Kelvin;");
      return OP_OK;
    case T_EN_C :
      strcat (DiagExec, "Unité Température reconnue : Degrés Celsius");
      return OP_OK;
    case MANQUANTES :
      strcat (DiagExec, "Données de température manquantes");
      return OP_OK;
    default:
      strcat (DiagExec, "Erreur inattendue");
      return OP_FAIL;
    }
}

void
ID_PressAltiVect (oper * optr)
{
  strcpy (optr->Nom, "PressAltiVect");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_PressAltiVect;
  optr->NbArg = 6;

  /* P0 */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "1";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "hPa";

  /* Tv */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "Kelvin";

  /* Z0  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = VECTOR;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "m";

  /* Z */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "m";

  /* rsurg */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = NULL;
  optr->Arg_Car[4].sample = NULL;
  optr->Arg_Car[4].unite = "any";

  /* P */
  optr->Arg_Car[5].direction = DIR_OUT;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF32;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[5].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[5].sample = "$Arg1.sample";
  optr->Arg_Car[5].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[5].unite = "$Arg1.unit";
  optr->Arg_Car[5].name = " \"Pression calculee a partir de \" +$Arg1.name";
  optr->Arg_Car[5].en_name = " \"Pressure computed with \"+$Arg1.english_name";
  optr->Arg_Car[5].famille = " \"pression\" ";
}
