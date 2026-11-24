#ifndef STRUCT_OPER
#define STRUCT_OPER

/* 
 *  Pour pouvoir faire appel a sqrt() et finite(), il
 * faut inclure math.h, et, sur HPUX-11, definir _HPUX_SOURCE
 */
#ifndef _HPUX_SOURCE
#  define _HPUX_SOURCE
#endif
/* Pour pouvoir "voir" isfinite() en C ANSI avec gcc,
 * il faut définir _XOPEN_SOURCE avec un niveau >500
*/

#ifndef _XOPEN_SOURCE
#define _XOPEN_SOURCE 700
#endif

#include <math.h>
#include <sys/types.h>

#include <rapt.h>

#define FIL_MAX_ARG 60

typedef enum
  {
    CAT_UNKNOWN, VECTOR, COEFFICIENT
  }
CATEGORIE;


/* On definit ici un "Arg_profil" qui ressemble beaucoup
 * au "variable_profil", mais dont la pluspart des champs
 * sont des chaines de caracteres, afin de pouvoir contenir
 * des formules, qui seront interpretees.
 */

typedef enum
  {
    DIR_NONE, DIR_IN, DIR_OUT
  }
sens;

#define MAX_FCT_NAM 60

typedef struct
  {
    sens direction;
    CATEGORIE categorie;
    AIDA_TYPE_CODE typ;
    char *array_shape;
    char *array_dim;
    char *bornes;
    char *unit_bornes;
    char *unite;
    char *name;			/* Seulement pour les VECTOR, nom_long dans l'en-tete; */
    char *en_name;		/* version anglaise du champ précédent. */
    char *type_sample;		/* Seulement pour les VECTOR */
    char *sample;		/* Seulement pour les VECTOR */
    char *ref_time;		/* Seulement pour les VECTOR */
    char *time_bnds;		/* Seulement pour les VECTOR */
    char *famille;		/* Seulement pour les VECTOR */
    char *misval;	        /* Seulement pour les VECTOR */
    char *NbVal;	        /* Seulement pour les VECTOR */
  }
Arg_profil;

#define OPERTYP_NONE		0
#define OPERTYP_TIME_TRANSFORM		1
#define OPERTYP_FMT_TRANSFORM		2

typedef struct
  {
    char Nom[MAX_FCT_NAM+1];
    const char *Version;
    const char *Date;
    int type;
    const char *repl_oper;      /* Operateurs obsoletes : le nom du remplacant */
    const char *repl_cause;     /* Operateurs obsoletes : la cause du remplacement */
    /* Declaration de fctptr as pointer to function () returning int */
    int (*fctptr) (unsigned long, void *[], char *);
    int misval_auto;
    int NbArg;
    Arg_profil Arg_Car[FIL_MAX_ARG];
  }
oper;

/* Les codes de retour standard des fonctions OP_xxx */
#define OP_OK	0
#define OP_FAIL	-1

/* Des constantes qui peuvent servir
 * Elles sont definies dans "math.h" si on a "_INCLUDE_XOPEN_SOURCE"
 * On se les definit ici au cas ou ... */

#ifndef M_PI
#define M_PI          3.14159265358979323846
#endif

#ifndef K_T0
#define K_T0 (273.15)
#endif

#ifndef K_NaN
#define K_NaN (sqrt(-1.0))
#endif

#ifndef isfinite
#define isfinite(x) ((sizeof(x)==sizeof(float))?finite((double) x):finite(x))
#endif

/* Une structure utile à des fonctions de calcul
 * Et la définition de pointeur vers fonction renvoyant ce resultat
 * Nb_OK: nb de valeurs valides pour la periode, Nb_mnq:nb de valeurs < seuil nb_avant nb de valeurs avant , nb_calc_KO : nb de valeurs qui interdisenet le calcul. ex valeur negatives des moyennes harmonique
 */
typedef struct
{
  float value;
  unsigned long Nb_OK, Nb_mnq, Nb_avant, Nb_calc_KO;
} result_1_t;

typedef result_1_t (*calc_fct_ptr_t) (const float *, unsigned long,
				    unsigned long, const double *, double,
				    double);

/* Maurel 2020 : definition d'une structure globle pour pouvoir passer 
 * à fvb des meta-données des vecteusr resultats
 * qui sont calculées par l'operateur */
Arg_profil Meta_Out[FIL_MAX_ARG];


#endif
/*  du ifndef STRUCT_OPER */
