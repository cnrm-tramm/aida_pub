/****************************************************
*
* LIBRARY      oper_util.c   FUNCTIONS   ANSI-C
*
* PURPOSE      Fonctions utilles à la mécanique des opérateurs.
*
* DESCRIPTION  
*
*
* VERSION      $revision:$
*
* ARGUMENTS   
*
* ENTRY        int
*              
* SUBPROGRAMS   
*
* FILES        
*
* REFERENCES  
*
* CHANGES      
*
* COPYRIGHT    Meteo-France
*
* AGREEMENT    The author wishes that .....
*#########################################################################*/
#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "struct_oper.h"
#include "load_oper.h"
#include <Python.h>
#include <numpy/arrayobject.h>


/** 
* @brief Ecrit un intervalle de temps (éventuellement vide)
* dans une chaîne de caractères.
* 
* @param DiagString la chaine dans laquelle ecrire. On suppose qu'elle 
* est assez grande...
* @param nom le nom du paramètre
* @param data le tableau de données du paramètre
* @param nb_data le nombre d'éléments du tableau.
*/
char *
ecrit_bornes_temps (char *DiagString, const char *nom, double *data,
		    size_t nb_data)
{
  int NCar = 0;

  switch (nb_data)
    {
    case 0:
      NCar = sprintf (DiagString, "%s vide, ", nom);
      break;
    case 1:
      NCar = sprintf (DiagString, "%s unique : %g, ", nom, data[0]);
      break;
    default:
      NCar = sprintf (DiagString, "%s in [%g, %g], ", nom,
		      data[0], data[nb_data - 1]);
    }
  return DiagString + NCar;
}

/** 
* @brief Retourne la dimension n à partir d'une chaîne décrivant le array_shape
* d'un tableau de data, -1 si la dimension n'existe pas.
* 
* @param array_shape la chaine qui décrit les dimensions du tableau de data (ex : 14,7)
* @param dim_num l'entier qui donne le numéro de la dimension (1 à n)
*/
int
get_dimension_n (const char *array_dim, int dim_num)
{
  char *token, *str_tmp;
  int i = 1;
  int dim = -1;
  str_tmp = strdup(array_dim);
  if (str_tmp != NULL) {
    token = strtok (str_tmp,",");
    while (token != NULL)
       {
         if ( i == dim_num )
           dim = atoi(token);
         token = strtok (NULL, ",");
         i++; 
       }
    free(str_tmp);  
  }

  return dim;
}

/** 
* @brief Effectue un calcul en utilisant time_bnds.
* 
* @param NbVal nombre de valeurs de la donnée d'entrée
* @param ArgList liste des arguments de l'opérateur
* @param DiagExec chaîne de diagnostic
* @param NomOper nom de l'opérateur appelant
* @param ChaineArgSup chaine supplementaire contenant 1 ou plusieurs floats separes par des: seuil1:seuil2: .... 
* @param IndexOut: index final de la liste des param (nb_param_sup = IndexOut-6)
* @param NomFonction nom de la fonction à exécuter
*/
int
fait_calcul_tps_bnds (unsigned long NbVal, void *ArgList[], int IndexOut,  char *DiagExec, char *NomOper, char *NomFonction, char *ChaineArgSup)
{
  int codret;
  int NCar;
  PyObject *pArgs, *pValue, *pFunc;
  unsigned long NbValOut;
  npy_intp dims1[1];
  npy_intp dims2[2];
  float *result[3];
  float *data_float;
  float *codret_float;
  float *tab_stat_float;
  int NbParamArgSup,NbParamIn;

  NbValOut = *((unsigned long *) ArgList[5]);
  NbParamArgSup = IndexOut-6;
  NbParamIn = IndexOut;

  /*
   * Initialisation des structures python
   */
  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.StatEch_tps_bnds", "fait_calcul_tps_bnds");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  /*pArgs = PyTuple_New(6);*/
  pArgs = PyTuple_New(7);
  PyErr_Print();

  /* X_in */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);
  PyErr_Print();

  /* Time_in */
  dims1[0] = NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);
  PyErr_Print();

  /* Tolerance manquant */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[2]);
  PyTuple_SetItem(pArgs, 2, pValue);
  PyErr_Print();

  /* Time_out */
  dims1[0] = NbValOut;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);
  PyErr_Print();

  /* Time_bnds */ 
  dims2[0] = NbValOut;
  dims2[1] = 2;
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_DOUBLE, (double *)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);
  PyErr_Print();

  /* function */
  dims1[0] = strlen(NomFonction)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, NomFonction);
  PyTuple_SetItem(pArgs, 5, pValue);
  PyErr_Print();

  /* ChaineArgSup */
  dims1[0] = strlen(ChaineArgSup)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, ChaineArgSup);
  PyTuple_SetItem(pArgs, 6, pValue);
  PyErr_Print();

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();

  /* 
   * On recupere le donnees contenues dans pValue.
   * La récupération se fait forcement dans des tableaux de floats.
   */ 
  data_float = malloc(NbValOut * sizeof (float));
  codret_float = malloc(1 * sizeof (float));
  tab_stat_float = malloc(3 * sizeof (float));
  result[0] = data_float;
  result[1] = codret_float;
  result[2] = tab_stat_float;
  codret=PyObject_to_ArgList ( pValue, (float **)result, 3 );

  /* Debug
  for (i=0; i<NbValOut; i++) {
     fprintf(stderr,"%f\n",(float)(data_float)[i]);
  }    
  fprintf(stderr,"CODRET : %f\n", codret_float[0]);
  fprintf(stderr,"TAB_STAT : %f %f %f\n", tab_stat_float[0], tab_stat_float[1], tab_stat_float[2]);
  */
  /*memcpy(ArgList[6], data_float, NbValOut * sizeof (float));*/
  memcpy(ArgList[IndexOut], data_float, NbValOut * sizeof (float));

  /*
   * Renseignement du Diagnostic
   */
  NCar = sprintf (DiagExec, "%s (%lu ech), ", NomOper, NbVal);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_orig in [%g,%g] ", 
                 ((double *) ArgList[1])[0],
                 ((double *) ArgList[1])[NbVal-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_dest in [%g,%g] ", 
                 ((double *) ArgList[4])[0],
                 ((double *) ArgList[4])[(NbValOut*2)-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, " nb_resu=%lu ", *((unsigned long *) ArgList[5]));
  DiagExec += NCar;
  codret = (int)codret_float[0];
  if (codret == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[1])[NbVal - 1],
	       ((double *) ArgList[4])[0]);
    }
  else if (codret == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[1])[0],
	       ((double *) ArgList[4])[(NbValOut)*2 - 1]);
    }
  else
    {
      sprintf (DiagExec,
	       "OK:%d val. en sortie,  (OK:%d, 0:%d, pas_assez:%d).",
	       codret, (int)tab_stat_float[0], (int)tab_stat_float[1], (int)tab_stat_float[2]);
    }


  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);

  return(codret);
}


/*3 vecteurs en entree un vecteur en sortie*/
int
fait_calcul_tps_bnds_1couche (unsigned long NbVal, void *ArgList[], int IndexOut,  char *DiagExec, char *NomOper, char *NomFonction, char *ChaineArgSup)
{
  int codret;
  int NCar;
  PyObject *pArgs, *pValue, *pFunc;
  unsigned long NbValOut;
  npy_intp dims1[1];
  npy_intp dims2[2];
  float *result[3];
  float *data_float;
  float *codret_float;
  float *tab_stat_float;
  int NbParamArgSup,NbParamIn;

  NbValOut = *((unsigned long *) ArgList[7]);
  NbParamArgSup = IndexOut-6;
  NbParamIn = IndexOut;

  /*
   * Initialisation des structures python
   */
  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.HbnMoyInvEch_tps_bnds", "fait_calcul_hbn_moy_tps_bnds");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  /*pArgs = PyTuple_New(6);*/
  pArgs = PyTuple_New(9);
  PyErr_Print();

  /* X_in_1 */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);
  PyErr_Print();

  /* X_in_2 */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 1, pValue);
  PyErr_Print();

  /* X_in_2 */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 2, pValue);
  PyErr_Print();

  /* Time_in */
  dims1[0] = NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[1]);
  PyTuple_SetItem(pArgs, 3, pValue);
  PyErr_Print();

  /* Tolerance manquant */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[2]);
  PyTuple_SetItem(pArgs, 4, pValue);
  PyErr_Print();

  /* Time_out */
  dims1[0] = NbValOut;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[3]);
  PyTuple_SetItem(pArgs, 5, pValue);
  PyErr_Print();

  /* Time_bnds */ 
  dims2[0] = NbValOut;
  dims2[1] = 2;
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_DOUBLE, (double *)ArgList[4]);
  PyTuple_SetItem(pArgs, 6, pValue);
  PyErr_Print();

  /* function */
  dims1[0] = strlen(NomFonction)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, NomFonction);
  PyTuple_SetItem(pArgs, 7, pValue);
  PyErr_Print();

  /* ChaineArgSup */
  dims1[0] = strlen(ChaineArgSup)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, ChaineArgSup);
  PyTuple_SetItem(pArgs, 8, pValue);
  PyErr_Print();

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();

  /* 
   * On recupere le donnees contenues dans pValue.
   * La récupération se fait forcement dans des tableaux de floats.
   */ 
  data_float = malloc(NbValOut * sizeof (float));
  codret_float = malloc(1 * sizeof (float));
  tab_stat_float = malloc(3 * sizeof (float));
  result[0] = data_float;
  result[1] = codret_float;
  result[2] = tab_stat_float;
  codret=PyObject_to_ArgList ( pValue, (float **)result, 3 );

  /* Debug
  for (i=0; i<NbValOut; i++) {
     fprintf(stderr,"%f\n",(float)(data_float)[i]);
  }    
  fprintf(stderr,"CODRET : %f\n", codret_float[0]);
  fprintf(stderr,"TAB_STAT : %f %f %f\n", tab_stat_float[0], tab_stat_float[1], tab_stat_float[2]);
  */
  /*memcpy(ArgList[6], data_float, NbValOut * sizeof (float));*/
  memcpy(ArgList[IndexOut], data_float, NbValOut * sizeof (float));

  /*
   * Renseignement du Diagnostic
   */
  NCar = sprintf (DiagExec, "%s (%lu ech), ", NomOper, NbVal);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_orig in [%g,%g] ", 
                 ((double *) ArgList[3])[0],
                 ((double *) ArgList[3])[NbVal-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_dest in [%g,%g] ", 
                 ((double *) ArgList[6])[0],
                 ((double *) ArgList[6])[(NbValOut*2)-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, " nb_resu=%lu ", *((unsigned long *) ArgList[5]));
  DiagExec += NCar;
  codret = (int)codret_float[0];
  if (codret == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[3])[NbVal - 1],
	       ((double *) ArgList[6])[0]);
    }
  else if (codret == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[3])[0],
	       ((double *) ArgList[6])[(NbValOut)*2 - 1]);
    }
  else
    {
      sprintf (DiagExec,
	       "OK:%d val. en sortie,  (OK:%d, 0:%d, pas_assez:%d).",
	       codret, (int)tab_stat_float[0], (int)tab_stat_float[1], (int)tab_stat_float[2]);
    }


  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);

  return(codret);
}

int
fait_calcul_tps_bnds_3couches (unsigned long NbVal, void *ArgList[], int IndexOut,  char *DiagExec, char *NomOper, char *NomFonction, char *ChaineArgSup)
{
  int codret;
  /*int cod1,cod2,cod3;*/
  int NCar;
  PyObject *pArgs, *pValue, *pFunc;
  unsigned long NbValOut;
  npy_intp dims1[1];
  npy_intp dims2[2];
  float *result[9];
  float *data1_float,*data2_float,*data3_float;
  float *codret1_float,*codret2_float,*codret3_float;
  float *tab1_stat_float,*tab2_stat_float,*tab3_stat_float;

  NbValOut = *((unsigned long *) ArgList[7]);

  /*
   * Initialisation des structures python
   */
  Py_Initialize();
  import_array();

  pFunc = import_py_oper ( "old_calcul.HbnMoyInvEch_tps_bnds", "fait_calcul_tps_bnds_3couches");

  /* on remplit PyObject de type tuple avec les arguments d'entrees */
  pArgs = PyTuple_New(9);
  PyErr_Print();

  /* X_in */
  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[0]);
  PyTuple_SetItem(pArgs, 0, pValue);
  PyErr_Print();

  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[1]);
  PyTuple_SetItem(pArgs, 1, pValue);
  PyErr_Print();

  dims1[0] = NbVal; 
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_FLOAT, (float *)ArgList[2]);
  PyTuple_SetItem(pArgs, 2, pValue);
  PyErr_Print();

  /* Time_in */
  dims1[0] = NbVal;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[3]);
  PyTuple_SetItem(pArgs, 3, pValue);
  PyErr_Print();

  /* Tolerance manquant */
  dims1[0] = 1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_INT, (int *)ArgList[4]);
  PyTuple_SetItem(pArgs, 4, pValue);
  PyErr_Print();

  /* Time_out */
  dims1[0] = NbValOut;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_DOUBLE, (double *)ArgList[5]);
  PyTuple_SetItem(pArgs, 5, pValue);
  PyErr_Print();

  /* Time_bnds */ 
  dims2[0] = NbValOut;
  dims2[1] = 2;
  pValue = PyArray_SimpleNewFromData(2, dims2, NPY_DOUBLE, (double *)ArgList[6]);
  PyTuple_SetItem(pArgs, 6, pValue);
  PyErr_Print();

  /* function */
  dims1[0] = strlen(NomFonction)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, NomFonction);
  PyTuple_SetItem(pArgs, 7, pValue);
  PyErr_Print();

  /* ChaineArgSup */
  dims1[0] = strlen(ChaineArgSup)+1;
  pValue = PyArray_SimpleNewFromData(1, dims1, NPY_CHAR, ChaineArgSup);
  PyTuple_SetItem(pArgs, 8, pValue);
  PyErr_Print();

  pValue = PyObject_CallObject(pFunc, pArgs);
  PyErr_Print();

  /* 
   * On recupere le donnees contenues dans pValue.
   * La récupération se fait forcement dans des tableaux de floats.
   */ 
  data1_float = malloc(NbValOut * sizeof (float));
  data2_float = malloc(NbValOut * sizeof (float));
  data3_float = malloc(NbValOut * sizeof (float));

  codret1_float = malloc(1 * sizeof (float));
  codret2_float = malloc(1 * sizeof (float));
  codret3_float = malloc(1 * sizeof (float));
  tab1_stat_float = malloc(3 * sizeof (float));
  tab2_stat_float = malloc(3 * sizeof (float));
  tab3_stat_float = malloc(3 * sizeof (float));

  result[0] = data1_float;
  result[1] = data2_float;
  result[2] = data3_float;
  result[3] = codret1_float;
  result[4] = codret2_float;
  result[5] = codret3_float;
  result[6] = tab1_stat_float;
  result[7] = tab2_stat_float;
  result[8] = tab3_stat_float;
  codret=PyObject_to_ArgList ( pValue, (float **)result, 9 );
  PyErr_Print();

  memcpy(ArgList[IndexOut], data1_float, NbValOut * sizeof (float));
  memcpy(ArgList[IndexOut+1], data2_float, NbValOut * sizeof (float));
  memcpy(ArgList[IndexOut+2], data3_float, NbValOut * sizeof (float));
     
  PyErr_Print();

  /*
   * Renseignement du Diagnostic
   */
      
  NCar = sprintf (DiagExec, "%s (%lu ech), ", NomOper, NbVal);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_orig in [%g,%g] ", 
                 ((double *) ArgList[3])[0],
                 ((double *) ArgList[3])[NbVal-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, "time_dest in [%g,%g] ", 
                 ((double *) ArgList[6])[0],
                 ((double *) ArgList[6])[(NbValOut*2)-1]);
  DiagExec += NCar;
  NCar = sprintf (DiagExec, " nb_resu=%lu ", *((unsigned long *) ArgList[7]));
  DiagExec += NCar;
  /*cod1=(int)codret1_float[0];
  cod2=(int)codret2_float[0];
  cod3=(int)codret3_float[0];*/
  if ( (int)codret1_float[0] == -1 ||  (int)codret2_float[0] == -1 || (int)codret3_float[0] == -1 )
      codret=-1;
  else 
    if ( (int)codret1_float[0] == -2 ||  (int)codret2_float[0] == -2 || (int)codret3_float[0] == -2 )
      codret=-2;
    else
        codret= (int)codret1_float[0] ;
  if (codret == -1)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas pour un des vecteurs de sortie, "
	       "Le dernier temps d'origine (%g) est avant le premier temps demandé (%g)",
	       ((double *) ArgList[3])[NbVal - 1],
	       ((double *) ArgList[6])[0]);
    }
  else if (codret == -2)
    {
      sprintf (DiagExec, "Les 2 periodes de temps ne se chevauchent pas pour un des vecteurs de sortie, "
	       "Le premier temps d'origine (%g) est apres le dernier temps demandé (%g)",
	       ((double *) ArgList[3])[0],
	       ((double *) ArgList[6])[(NbValOut)*2 - 1]);
    }
  else
    {
      sprintf (DiagExec,
	       "OK1:%d val. en sortie,  (OK:%d, 0:%d, pas_assez:%d). , OK2:%d val. en sortie,  (OK:%d, 0:%d, pas_assez:%d). , OK3:%d val. en sortie,  (OK:%d, 0:%d, pas_assez:%d).",
	       codret, (int)tab1_stat_float[0], (int)tab1_stat_float[1], (int)tab1_stat_float[2],
	       codret, (int)tab2_stat_float[0], (int)tab2_stat_float[1], (int)tab2_stat_float[2],
	       codret, (int)tab3_stat_float[0], (int)tab3_stat_float[1], (int)tab3_stat_float[2]);
    }


  Py_DECREF(pValue);
  Py_DECREF(pArgs);
  Py_DECREF(pFunc);

  return(codret);
}

