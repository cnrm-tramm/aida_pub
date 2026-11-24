/*
 * Fonctions de chargement des operateurs contenus dans une "shared lib"
 */
#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600
#define _XOPEN_SOURCE_EXTENDED

#include <stdlib.h>
#include <string.h>
#ifdef __hpux
/* Pour HP-UX sur 32 bits */
#include <dl.h>
#else
/* La SVR4 standard dynamic loading API (HP-UX 64-bit, Linux, ...) */
#include <stdio.h>
#include <unistd.h>
#include <dlfcn.h>
#endif

#include "struct_oper.h"

#include <Python.h>
#include <numpy/arrayobject.h>


#ifndef __hpux
/* definition d'un substitut de structure shl_symbol, qui sera utilisée par les fonctions. */
typedef struct
{
  void (*value) (oper *);
  char *name;
}
shl_symbol;
#endif

#include <errno.h>
#include "load_oper.h"

extern int errno;


#ifndef __hpux
/** 
* @brief remplace la fonction shl_getsymbols() sur les
* systèmes où elle est absente.
* 
* @param PathLib
* @param lib_handle
* @param memory
* @param symbols
* 
* @return 
*/
static int
emulation_de_shl_getsymbols (const char *const PathLib,
			     void *lib_handle,
			     void *(*memory) (), shl_symbol ** symbols)
{
#define NM_OUTPUT_MAX_LEN (128)
#define NM_INVOCATION "/usr/bin/nm -g"
  FILE *tuyau_ptr;
  char buf[NM_OUTPUT_MAX_LEN];
  char *cptr;
  char *error_str;
  char *commande_str;
  size_t nb_entry = 0;
  size_t taille_tab_symb, len;
  int cod_ret;
  void *tmp_void_ptr;
  void (*tmp_fct_ptr) (oper *);	/* declare tmp_fct_ptr as pointer to function of pointer to oper, returning void */

  /* Un p'tit coup de popen sur le résultat de nm */

  commande_str = malloc (strlen (NM_INVOCATION) + strlen (PathLib) + 2);
  strcpy (commande_str, NM_INVOCATION);
  strcat (commande_str, " ");
  strcat (commande_str, PathLib);

  tuyau_ptr = popen (commande_str, "r");
  free (commande_str);
  commande_str = NULL;
  if (tuyau_ptr == NULL)
    {
      return -1;
    }
  taille_tab_symb = 200;
  *symbols = malloc (sizeof (**symbols) * taille_tab_symb);
  if (*symbols == NULL)
    {
      fprintf (stderr,
	       "Not enough memory to allocate list of symbols(%lu)\n",
	       taille_tab_symb);
    }
  while (fgets (buf, BUFSIZ, tuyau_ptr) != NULL)
    {
      /* recherche, dans la ligne, un mot */
      /* correspondant à OP_* ou ID_*     */
      cptr = strstr (buf, "OP_");
      if (cptr == NULL)
	{
	  cptr = strstr (buf, "ID_");
	}
      if (cptr != NULL)
	{
	  if ((cptr == buf)
	      || (*(cptr - 1) == ' ')
	      || (*(cptr - 1) == '|') || (*(cptr - 1) == '\t'))
	    {
	      /* Tout va bien, on est en début de mot */
	      /* Cherchons la fin  */
	      len = strcspn (cptr, " \t|\n");
	      *(cptr + len) = 0;
	      /* Verifier qu'il reste de la place dans le tableau de shl_symbol */
	      if (nb_entry >= taille_tab_symb)
		{
		  taille_tab_symb += 100;
		  *symbols = realloc (*symbols,
				      sizeof (**symbols) * taille_tab_symb);
		  if (*symbols == NULL)
		    {
		      fprintf (stderr,
			       "Not enough memory to allocate list of symbols(%lu)\n",
			       taille_tab_symb);
		    }
		}
	      /* appeler dlsym(cptr); pour connaître l'adresse de du symbole. */
	      (*symbols)[nb_entry].name = strdup (cptr);
	      /* On tombe ici sur un conflit de standards, entre POSIX qui
	       * définit  dlsym comme renvoyant un "void *", et ISO-C qui
	       * interdit de caster un void* vers un pointeur sur fonction.
	       * Espérons que POSIX évoluera et que dlsym renverra bientôt vraiment un 
	       * pointeur sur fonction, puique tel est son rôle. 
	       * cf http://www.opengroup.org/onlinepubs/009695399/functions/dlsym.html 
	       * La méthode directe :
	       * (*symbols)[nb_entry].value = (void (*)(oper *)) dlsym (lib_handle, cptr);
	       * ne marche pas. */
	      /* On cast "à la sauvage" */
	      tmp_void_ptr = dlsym (lib_handle, cptr);
	      /* le memcpy qui outrepasse l'interdiction */
	      memcpy (&tmp_fct_ptr, &tmp_void_ptr, sizeof (tmp_void_ptr));
	      /* l'affectation tant désirée */
	      (*symbols)[nb_entry].value = tmp_fct_ptr;

	      error_str = dlerror ();
	      if (error_str != NULL)
		{
		  fputs (error_str, stderr);
		  exit (1);
		}
	      nb_entry++;
	    }
	}
    }
  cod_ret = pclose (tuyau_ptr);
  if ((cod_ret == -1) || (cod_ret >= 127))
    {
      /* erreur quelconque */
      return -1;
    }
  return nb_entry;
}
#endif

/** Return string describing error code.
 *
 * This function returns a string describing the
 * error code passed in the argument NumErreur.
 *
 * @param NumErreur : Errorr code.
 * @return A string describing the error.
 */
const char *
OPLD_erreur (int NumErreur)
{
  switch (NumErreur)
    {
    case OPLD_ERROR:
      return strerror (errno);
      break;
    case OPLD_INVVAL:
      return ("Invalid parameter value");
      break;
    case OPLD_NOTFOUND:
      return ("File not found");
      break;
    case OPLD_NOACCESS:
      return ("Couldn't access file");
      break;
    case OPLD_NOMEM:
      return ("Memory allocation error");
      break;
    case OPLD_NOTALIB:
      return ("Bad library file format");
      break;
    }
  return NULL;
}

/** frees memory and nullify the pointer 
 *
 */
#ifdef __hpux
static void
delete_symb_list (struct shl_symbol **symb_list_ptr, size_t Nb_symb)
{
  struct shl_symbol *cur_symb;
  free (*symb_list_ptr);
  *symb_list_ptr = NULL;
#else
static void
delete_symb_list (shl_symbol ** symb_list_ptr, size_t Nb_symb)
{
  size_t i;
  shl_symbol *symbols;
  symbols = *((shl_symbol **) symb_list_ptr);
  for (i = 0; i < Nb_symb; i++)
    {
      if (symbols[i].name != NULL)
	{
	  free (symbols[i].name);
	  symbols[i].name = NULL;
	}
    }
  free (*symb_list_ptr);
  *symb_list_ptr = NULL;
#endif
}

/** Loads a library of operators.
 *
 *  An operator corresponds to three functions :
 *        operator (itself)
 *        OP_operator (standardized interface function)
 *        ID_operator (description function)
 *
 * @param PathLib : path to the library to load.
 * @param liste : pointer to an array of operator descriptor(s).
 *   This array will be malloc()'ed by the function, and must be
 *   freed by the user (function Free_Liste_Oper () ).
 *
 * \Return the number of operator loaded, or a negative
 * error code.
 */
int
Init_Liste_Oper_dyn (const char *const PathLib, oper ** liste)
{
  int Nb_symb, i, ii, iii;
  int NbOP_, Nb_vrai_oper;
  char *Nom_desc_oper;
#ifdef __hpux
  long poubelle = 0;
  shl_t lib_handle;
  struct shl_symbol *symb_list, *cur_symb, *cherche_symb;
#else
  shl_symbol *symb_list, *cur_symb, *cherche_symb;
  void *lib_handle;
#endif
  void (*IDfuncPtr) (oper *);
  oper *OpPtr;

  if (PathLib == NULL)
    {
      return (OPLD_INVVAL);
    }
#ifdef __hpux
  lib_handle = shl_load (PathLib, BIND_IMMEDIATE | BIND_VERBOSE, poubelle);
  if (lib_handle == NULL)
    {
      switch (errno)
	{
	case ENOENT:
	  return OPLD_NOTFOUND;
	  break;
	case EACCES:
	  return OPLD_NOACCESS;
	  break;
	case ENOMEM:
	  return OPLD_NOMEM;
	  break;
	case ENOEXEC:
	  return OPLD_NOTALIB;
	  break;
	default:
	  return OPLD_ERROR;
	  break;
	}
    }
#else
  lib_handle = dlopen (PathLib, RTLD_NOW);
  if (!lib_handle)
    {
      fputs (dlerror (), stderr);
      exit (1);
    }
#endif

#ifdef __hpux
  Nb_symb = shl_getsymbols (lib_handle, TYPE_PROCEDURE, EXPORT_SYMBOLS,
			    malloc, &symb_list);
  if (Nb_symb < 0)
    {
      return OPLD_ERROR;
    }
#else
  Nb_symb = emulation_de_shl_getsymbols (PathLib, lib_handle, malloc,
					 &symb_list);
  if (Nb_symb < 0)
    {
      perror ("");
      fputs (dlerror (), stderr);
    }
#endif

  NbOP_ = 0;
  for (i = 0, cur_symb = symb_list; i < Nb_symb; cur_symb++, i++)
    {
      if ((strncmp (cur_symb->name, "OP_", 3) == 0)
	  && (strlen (cur_symb->name) > 3))
	NbOP_++;
    }


  /* On alloue un de plus pour la structure vide, a la fin.. */
  *liste = malloc ((NbOP_ + 1) * sizeof (oper));
  if (*liste == NULL)
    {
      delete_symb_list (&symb_list, Nb_symb);
      return (OPLD_NOMEM);
    }

  Nb_vrai_oper = 0;
  for (i = 0, cur_symb = symb_list; i < Nb_symb; cur_symb++, i++)
    {
      if ((strncmp (cur_symb->name, "OP_", 3) == 0)
	  && (strlen (cur_symb->name) > 3))
	{
	  Nom_desc_oper = strdup (cur_symb->name);
	  if (Nom_desc_oper == NULL)
	    return OPLD_NOMEM;
	  Nom_desc_oper[0] = 'I';
	  Nom_desc_oper[1] = 'D';
	  for (ii = 0, cherche_symb = symb_list; ii < Nb_symb;
	       cherche_symb++, ii++)
	    {
	      if (strcmp (cherche_symb->name, Nom_desc_oper) == 0)
		{
		  break;	/* On arrete la recherche... */
		}
	    }
	  if (ii >= Nb_symb)
	    {
	      /* Pas de fonction ID_xxx correspondante a OP_xxx  */
	      fprintf (stderr, "%s non trouve \n", Nom_desc_oper);
	    }
	  else
	    {
	      /* On a trouve la fonction ID_xxx. On l'execute...
	       * Mais d'abord, une sage initialisation vide.    */
	      OpPtr = &((*liste)[Nb_vrai_oper]);
	      strcpy (OpPtr->Nom, "");
	      OpPtr->Version = "";
	      OpPtr->Date = "";
	      OpPtr->type = OPERTYP_NONE;
	      OpPtr->fctptr = NULL;
	      OpPtr->repl_oper = NULL;
	      OpPtr->repl_cause = NULL;
	      OpPtr->misval_auto = 1;	/* Attention : par defaut, c'est automatique.. */
	      OpPtr->NbArg = 0;
	      for (iii = 0; iii < FIL_MAX_ARG; iii++)
		{
		  OpPtr->Arg_Car[iii].direction = DIR_NONE;
		  OpPtr->Arg_Car[iii].categorie = CAT_UNKNOWN;
		  OpPtr->Arg_Car[iii].typ = ATYC_UNDEF;
          OpPtr->Arg_Car[iii].array_shape = NULL;
		  OpPtr->Arg_Car[iii].array_dim = NULL;
		  OpPtr->Arg_Car[iii].bornes = NULL;
		  OpPtr->Arg_Car[iii].unit_bornes = NULL;
		  OpPtr->Arg_Car[iii].unite = NULL;
		  OpPtr->Arg_Car[iii].name = NULL;
		  OpPtr->Arg_Car[iii].type_sample = NULL;
		  OpPtr->Arg_Car[iii].sample = NULL;
		  OpPtr->Arg_Car[iii].ref_time = NULL;
		  OpPtr->Arg_Car[iii].NbVal = NULL;
		  OpPtr->Arg_Car[iii].famille = NULL;
		  OpPtr->Arg_Car[iii].misval = NULL;
		  OpPtr->Arg_Car[iii].name = NULL;
		  OpPtr->Arg_Car[iii].en_name = NULL;
		}
	      /* Il me ne semble pas inutile de preciser que la ligne
	       * suivante caste le pointeur "value" en un pointeur sur
	       * fonction prenant un oper * en argument et ne produisant
	       * rien (void), ce qui, Oh Chance !!, est precisement
	       * le type de IDfuncPtr.
	       */
	      IDfuncPtr = (void (*)(oper *)) cherche_symb->value;
	      /* Et maintenant, y'a plus qu'a executer cette fonction */
	      (*IDfuncPtr) (&((*liste)[Nb_vrai_oper]));
	      Nb_vrai_oper++;
	    }
	  free (Nom_desc_oper);
	}
    }

  /* Et on utilise une structure vide comme marqueur de fin */
  strcpy ((*liste)[Nb_vrai_oper].Nom, "");
  (*liste)[Nb_vrai_oper].fctptr = NULL;
  (*liste)[Nb_vrai_oper].NbArg = -1;

  /* On n'oublie pas de liberer la memoire utilisee.  */
  delete_symb_list (&symb_list, Nb_symb);

  return Nb_vrai_oper;
}

/**    Frees an array of operator descriptor previously
 * allocated by Init_Liste_Oper_dyn.
 **/
void
Free_Liste_Oper (oper ** liste)
{
  oper *Oper;

  if (*liste == NULL)
    return;

  Oper = *liste;
  while (Oper->NbArg != -1)
    {
      Oper++;
    }
#ifdef __hpux
#else
  /* appeler dlclose () ? */
#endif
  free (*liste);
  *liste = NULL;
}

PyObject* import_py_oper ( char *module, char *oper )
  {
  PyObject *pModule, *pFunc;

  /* fonction de chargement d'un operateur en Python 
   * module : nom du module qui contient la fonction
   * oper : nom de la fonction a importer
   */

  PyRun_SimpleString("import sys");
  PyRun_SimpleString("import os");
  PyRun_SimpleString("AH = os.getenv(\'AIDA_HOME\')");
  PyRun_SimpleString("PYTHON_X_Y = \"python%d.%d\" % (sys.version_info[0], sys.version_info[1])");
  PyRun_SimpleString("sys.path.append(os.path.join(AH, \'lib\', PYTHON_X_Y))");

  pModule = PyImport_ImportModule(module);

  /*fprintf (stderr, "import module\n");*/
  if (pModule == NULL)
     {
      fprintf(stderr, "+++ Erreur importation module Python %s \n", module);
      PyErr_Print();
     }

  pFunc = PyObject_GetAttrString(pModule, oper);
  if (pFunc == NULL)
     {
      fprintf(stderr, "+++ Erreur importation fonction %s dans module %s \n", oper, module );
      PyErr_Print();
     }

  /*fprintf (stderr, "import fonction\n");*/
  /*PyObject_Print(pFunc, stderr, 0);*/ 
  Py_DECREF(pModule);

  return pFunc;
  }

int PyObject_to_ArgList ( PyObject *py_o, float **ArgList, int nbarg )
  {
   /*
    * recupere les données dans un PyObject resultat d'un programme Python
    * et les met dans le tableau ArgList 
    *
    * PyObject peut-etre un Tuple (Python retourne plusieurs arguments)
    * ou un PyObject simple (Python retourne 1 seul argument)
    *
    * py_o : PyObject retourne par le programme Python
    * Arglist : tableau qui contient les adresses des tableaux resultats
    * nbarg : le nombre de tableau resultat (= nombre de vecteurs produits par l'operateur
    */
   int i, nret;
   PyObject *ret[15];

   if ( PyTuple_Check(py_o) == 1)
     {
	nret = (int)PyTuple_Size(py_o);

	if (nret != nbarg ) 
	   {
	    fprintf(stderr, "+++ Nombre d'argument retournes par la fonction Python != de celui retourne par l'operateur nret=%d nbarg=%d\n",nret,nbarg);
	    return -1;
           }

	for (i=0; i < nret; i++)
	  {
	    ret[i] = PyTuple_GetItem(py_o, (Py_ssize_t)i);
  	    PyObject_2_Ctab_float ( ret[i] , (float*)(*ArgList) );
	    ArgList++;
	  }

      }
   else 
      {
	if (nbarg != 1 ) 
	   {
	    fprintf(stderr, "+++ Nombre d'argument retournes par la fonction Python != de celui retourne par l'operateur  nbarg=%d\n",nbarg);
	    return -1;
           }
  	PyObject_2_Ctab_float ( py_o , (float*)(*ArgList) );
      }

   return 0;
  }

int PyObject_2_Ctab_float ( PyObject *py_o, float *Ctab ) 
   /* Transforme un PyObject simple (pas un Tuple) en tableau de float */

   {
    int i;
    long k, len_data;
    double *data;
   
    PyArrayObject* obj = PyArray_GETCONTIGUOUS( (PyArrayObject*) py_o );
    data = (double*) obj ->data;


    len_data=1;
    for ( i= 0; i < (obj->nd); i++ )
     {
      len_data = len_data * obj->dimensions[i];
     }

    for (k=0; k < len_data; k++)
      {
	  *Ctab = (float)*data;
	  Ctab++;
	  data++;
      }

    Py_DECREF(obj);
    return 0;

  }

