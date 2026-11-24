/*************************************************************************
*
* OPERATOR         Flag_to_percent  FUNCTION ANSI-C
*
* PURPOSE          A partir d'un vecteur de flags et de sa base de temps,
*                  calcule le pourcentage d'une valeur de flag donnee sur une base de temps donnee. 
*
* DESCRIPTION   
*                  Pour chaque periode de la nouvelle base de temps, on compte le nombre de flags
*                  correspondant a la valeur de flag passee dans le vecteur d'entree et on calcule le 
*                  pourcentage.
*                  
*
* VERSION          1.0 
*
*
* ARGUMENTS  
*            IN   int      X          Variable flag d'entree
*            IN   float      Tx         Variable temps associe a X
*            IN   int      f          Valeur du flag a evaluer
*            IN   float      Ty         Variable temps associe a Y
*            IN   int      NbVarY        Dimension de Y ($Arg4.NbVal)
*
*            OUT  float      Y       	Variable Y contenant le pourcentage de f sur chaque periode

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
OP_Flag_to_percent (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  PyObject *pArgs, *pValue, *pFunc;
  unsigned long *NbValOut;
  npy_intp dims1[1];
  float *data_float;
  int i;

  NbValOut = (unsigned long *) ArgList[4];

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.Flag_to_percent", "Flag_to_percent");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  pArgs = PyTuple_New(4);
  PyErr_Print();

  /* X */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);

  /* Tx */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);

  /* f */
  dims1[0] = 1; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[2]);
  PyTuple_SetItem(pArgs, 2, pValue);
  /* on appelle la fonction Python */

  /* Ty */
  dims1[0] = *NbValOut;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);

  pValue = PyObject_CallObject(pFunc, pArgs);

  /* 
   * On recupere le donnees dans un PyObject.
   * La récupération se fait forcement dans des tableaux de floats mais
   * on veut des donnees de type int en sortie :
   *   on utilise donc un tableau de float temporaire pour recuperer les donnees
   *   puis on le copie dans le tableau de sortie en int.
   */  
  data_float = malloc(*NbValOut * sizeof (float));
  codret=PyObject_to_ArgList ( pValue, (float **)&data_float, 1 );
  for (i=0; i<*NbValOut; i++) {
     ((int *)(ArgList[5]))[i] = (int) ((float *)(data_float))[i];
  }

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);
  free(data_float);

  if (codret == -1)
     return OP_FAIL;
  else 
     return OP_OK;
}

void
ID_Flag_to_percent (oper * optr)
{
  int i;
  strcpy (optr->Nom, "Flag_to_percent");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2013-03-25 13:23:40 +0100 (lun. 25 mars 2013) $";
  optr->fctptr = OP_Flag_to_percent;
  optr->NbArg = 6;		/* doit rester inf. a FIL_MAX_ARG */
   
  i = 0;
  /* X */
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";

  /* Tx */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";

  /* f */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = COEFFICIENT;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "NULL";
  optr->Arg_Car[i].sample = "NULL";
  optr->Arg_Car[i].unite = "any";

  /* Ty */
  i++;
  optr->Arg_Car[i].direction = DIR_IN;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_IF64;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].type_sample = "any";
  optr->Arg_Car[i].sample = "any";

  /* NbValOut */
  i++;
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT;
  optr->Arg_Car[4].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "";

  /* Y */
  i++;
  optr->Arg_Car[i].direction = DIR_OUT;
  optr->Arg_Car[i].categorie = VECTOR;
  optr->Arg_Car[i].typ = ATYC_I32;
  optr->Arg_Car[i].array_dim = "1";
  optr->Arg_Car[i].NbVal = "$Arg4.NbVal";
  optr->Arg_Car[i].type_sample = "$Arg4.type_sample";
  optr->Arg_Car[i].sample = "$Arg4.sample";
  optr->Arg_Car[i].ref_time = "$Arg4.nom";
  optr->Arg_Car[i].unite = "$Arg1.unit";
}
