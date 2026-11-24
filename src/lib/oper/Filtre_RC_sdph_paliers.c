/****************************************************
*
* OPERATOR       filtrage RC 
*
* PURPOSE       Numerical filtering similar to a electric RC circuit
*
* DESCRIPTION   Ce filtre est le même que Filtre_RC_sdph, mais il appelle ici une
*               fonction python qui applique le filtre sur des intervalles de temps définis
*               dans le vecteur temps passé en argument. Il est notamment utilisé pour le traitement
*               de la sonde turbulente sous ballon captif de 4M.
*
* VERSION        1.0
*
* ARGUMENTS    IN   float    data_in      any     donnée d'origine
*              IN   double   time_in      second  base de temps de data_in
*              IN   float    fe           Hz      fréquence d'entrée (data_in)
*              IN   float    fc           Hz      fréquence de coupure
*              IN   float    typ          any     type de filtre (0 = passe bas, 1= passe haut)
*              IN   double   time_paliers second  base de temps qui définit les paliers
*              IN   double   time_bnds    second  bornes de temps associées à time_paliers    
*
*              OUT  float    data_out  any    donnée filtrée
*
* ENTRY            
*                 
* SUBPROGRAMS    none
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
* AGREEMENT      The author wishes that .....
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
OP_Filtre_RC_sdph_paliers (unsigned long NbVal, void *ArgList[], char *DiagExec)
{
  int codret;
  unsigned long NbValOut;
  PyObject *pArgs, *pValue, *pFunc;
  float *result[2];
  float *data_float;
  float *codret_float;
  NbValOut = *((unsigned long *) ArgList[7]);
  
  npy_intp dims1[1];
  npy_intp dims2[2];

  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.Filtre_RC_sdph_paliers", "Filtre_RC_sdph_paliers");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  pArgs = PyTuple_New(6);
  PyErr_Print();

  /* data_in */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);
  PyErr_Print();

  /* Time_in */
  dims1[0] = NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);
  PyErr_Print();
  
  /* fe */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[2]);
  PyTuple_SetItem(pArgs, 2, pValue);
  PyErr_Print();

  /* fc */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);
  PyErr_Print();
  
  /* type */
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);
  PyErr_Print();

  /* Time_bnds */ 
  dims2[0] = NbValOut;
  dims2[1] = 2;  
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_DOUBLE, (double *)ArgList[6]);
  PyTuple_SetItem(pArgs, 5, pValue);
  PyErr_Print();
  
  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();

  /* 
   * On recupere le donnees contenues dans pValue.
   * La récupération se fait forcement dans des tableaux de floats.
   */ 
  data_float = malloc(NbVal * sizeof (float));
  codret_float = malloc(1 * sizeof (float));
  result[0] = data_float;
  result[1] = codret_float;
  PyObject_to_ArgList ( pValue, (float **)result, 2 );
  memcpy(ArgList[8], data_float, NbVal * sizeof (float));

  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);
  
  /*
   * Renseignement du Diagnostic
   */
  codret = (int)(*codret_float);

  switch (codret)
    {
    case 0:
      sprintf (DiagExec, "OK");
      fprintf(stderr, "RETURN OK\n");
      return OP_OK;
    case -1:
      fprintf (stderr, " Fréquence de coupure négative !!\n");
      sprintf (DiagExec, "ERR: Fréquence de coupure négative.");
      return OP_FAIL;
    case -2:
      fprintf (stderr, " Fréquence d'échantillonnage négative !!\n");
      sprintf (DiagExec, "ERR: Fréquence d'échantillonnage négative.");
      return OP_FAIL;
    case -3:
      fprintf (stderr,
               " Type doit égal à 0 (passe-bas) ou 1 (passe-haut) !!\n");
      sprintf (DiagExec,
               "ERR: Type doit égal à 0 (passe-bas) ou 1 (passe-haut).");
      return OP_FAIL;
    default:
      sprintf (DiagExec, "ERR: Erreur %d", codret);
      return OP_FAIL;
    }
}

void
ID_Filtre_RC_sdph_paliers (oper * optr)
{
  strcpy (optr->Nom, "Filtre_RC_sdph_paliers");
  optr->Version = "$Revision: 5097 $";
  optr->Date = "$Date: 2022-09-08 09:00:00 +0200 (Jeu. 08 Sept 2022) $";
  optr->fctptr = OP_Filtre_RC_sdph_paliers;
  optr->NbArg = 9;		/* doit rester inf. a FIL_MAX_ARG */

  /* data_in */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "*";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "any";
  optr->Arg_Car[0].famille = "any";
  
  /* Time_in */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = VECTOR;
  optr->Arg_Car[1].typ = ATYC_IF64;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[1].type_sample = "any";
  optr->Arg_Car[1].sample = "any";
  optr->Arg_Car[1].unite = "second";

  /* % fréquences d'entrée */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_IF32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].type_sample = "any";
  optr->Arg_Car[2].sample = "any";
  optr->Arg_Car[2].unite = "any";
  optr->Arg_Car[2].famille = "any";

  /* % fréquences de coupure */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT; 
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].type_sample = "any";
  optr->Arg_Car[3].sample = "any";
  optr->Arg_Car[3].unite = "any";
  optr->Arg_Car[3].famille = "any";

  /* % type de filtre */
  optr->Arg_Car[4].direction = DIR_IN;
  optr->Arg_Car[4].categorie = COEFFICIENT; 
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "1";
  optr->Arg_Car[4].type_sample = "any";
  optr->Arg_Car[4].sample = "any";
  optr->Arg_Car[4].unite = "any";
  optr->Arg_Car[4].famille = "any";

  /* 5: time_paliers */
  optr->Arg_Car[5].direction = DIR_IN;
  optr->Arg_Car[5].categorie = VECTOR;
  optr->Arg_Car[5].typ = ATYC_IF64;
  optr->Arg_Car[5].array_dim = "1";
  optr->Arg_Car[5].type_sample = "any";
  optr->Arg_Car[5].sample = "any";
  optr->Arg_Car[5].unite = "second";

  /* 6: time_bnds      */
  optr->Arg_Car[6].direction = DIR_IN;
  optr->Arg_Car[6].categorie = COEFFICIENT;
  optr->Arg_Car[6].array_dim = "1";
  optr->Arg_Car[6].typ = ATYC_STRING;
  optr->Arg_Car[6].type_sample = NULL;	/* sans signification pour COEFFICIENT */
  optr->Arg_Car[6].sample = NULL;
  optr->Arg_Car[6].unite = "any";
  
  /* 7: size_out */
  optr->Arg_Car[7].direction = DIR_IN;
  optr->Arg_Car[7].categorie = COEFFICIENT;
  optr->Arg_Car[7].typ = ATYC_LOCAL_ULONG;
  optr->Arg_Car[7].array_dim = "1";
  optr->Arg_Car[7].type_sample = "any";
  optr->Arg_Car[7].sample = "any";
  optr->Arg_Car[7].unite = "";

  /* vecteur sortie */
  optr->Arg_Car[8].direction = DIR_OUT;
  optr->Arg_Car[8].categorie = VECTOR;
  optr->Arg_Car[8].typ = ATYC_IF32;
  optr->Arg_Car[8].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[8].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[8].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[8].sample = "$Arg1.sample";
  optr->Arg_Car[8].unite = "$Arg1.unit";
  optr->Arg_Car[8].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[8].famille = "$Arg1.famille";
  optr->Arg_Car[8].bornes = "$Arg1.bornes";
  optr->Arg_Car[8].unit_bornes = "$Arg1.unit_bornes";
  optr->Arg_Car[8].misval = "$Arg1.misval";
  
}
