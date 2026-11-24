/****************************************************
*
* LIBRARY      unit.c   FUNCTIONS   ANSI-C
*
* PURPOSE      Fonctions de detection automatique d'unités
*
* DESCRIPTION  
*
*
* VERSION      1.0
*
* ARGUMENTS   
*
* ENTRY        int
*              auto_tempe_unit (const unsigned long ndata, float *data, float *const)
*
*              const char *
*              unit_raconte (int flag_unit)
*
*              int
*              unitconvert (char *str_from, char *str_to, double *pente, double *intercept)
*
*              int
*              reconnait_deg_rad (const char *unit)
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
#define _XOPEN_SOURCE_EXTENDED
#define _HPUX_SOURCE

#include <math.h>
#include <strings.h>		/* pour strcasecmp */
#include <stdio.h>

#include <udunits2.h>

#include <gene.h>		/* Pour OteDebut() et OteFin() */

#include "struct_oper.h"
#include "unit_def.h"

#ifndef K_T0
#define K_T0 273.15
#endif

/* Une variable visible par les différentes fonctions de ce fichier */
static ut_system *unitSystem = NULL;

/** 
* @brief Détermine empiriquement si une série de
* valeur peut être des Kelvin ou des degrés Celsius
* mesurés dans l'atmosphère.
*      Les degrés Celsius doivent être entre -273.15 et 100
*      Les Kelvins doivent être supérieurs à 100
*
* @param ndata : Le nombre de données dans la série.
* @param data : pointeur vers la première donnée
* @param konst : La constante de conversion à ajouter
*           aux valeurs pour obtenir des Kelvins (0 ou 273.15)
* 
* @return un entier indiquant l'unité reconnue.
*/
int
auto_tempe_unit (const unsigned long ndata, const float *data, float *konst)
{
  unsigned long i, j;
  int flag_info;
  int definie;
  int nb_data_C, nb_data_K;
  int n_data_calcul;

  definie = 0;
  nb_data_C = 0;
  nb_data_K = 0;
  if ( ndata < 20 )
  {
     n_data_calcul = 1;
  }
  else
  {
     n_data_calcul = ndata/14;
  }

  for (i = 0; i < ndata; i=i+n_data_calcul)
  {
    if (!isfinite (data[i]))
	  continue;
    if (data[i] < -273.15)
	  continue;
    if (data[i] > 373.15)
	  continue;
    else
	{
	  if (data[i] < 100)
          nb_data_C++;
	  else
          nb_data_K++;
	}
  }


  if (nb_data_C >=  nb_data_K )
    {
      *konst = K_T0;
      flag_info = T_EN_C;
      definie = 1;
    }
  else
    {
      *konst = 0.;
      flag_info = T_EN_K;
      definie = 1;
    }

  if (!definie)
    {
      /* On n'a pas réussi à reconnaitre l'unité. Alors, de facon arbitraire
         on considère la Tempe en Kelvin (pas de conversion) */
      *konst = 0.;
      flag_info = MANQUANTES;
    }

  return flag_info;
}

/** Donne un message correspondant à un code 
 * de reconnaissance de gamme de température.
 *
 * \return : une chaine de caractère
 *
 */
const char *
unit_raconte (int flag_unit)
{
  switch (flag_unit)
    {
    case -1:
      return "ERR : Tempé Ni Kelvin Ni Celsius";
    case T_EN_K:
      return "Unité Température reconnue : Kelvin";
    case T_EN_C:
      return "Unité Température reconnue : Degrés Celsius";
    case MANQUANTES:
      return "Impossible reconnaître Température : Données Manquantes";
    default:
      return "Erreur inattendue";
    }
}

/** Ce qu'il faut faire a la fin pour udunits.
 * 
 */
static void
libere_unit ()
{
  ut_free_system (unitSystem);
}

/** decrit une erreur d'analyse d'unite
 */
void
print_error_ut_parse (const char *qualif_unite, const char *unit_str)
{
  switch (ut_get_status ())
    {
    case UT_UNKNOWN:
      (void) fprintf (stderr, "Unite %s (%s) inconnue\n", qualif_unite,
		      unit_str);
      break;
    case UT_SYNTAX:
      (void) fprintf (stderr, "Unite %s (%s) incomprehensible\n",
		      qualif_unite, unit_str);
      break;
    default:
      (void) fprintf (stderr, "Erreur (%d) dans ut_parse(%s)\n",
		      ut_get_status (), unit_str);
    }
}


/** Donne les coefficients d'un polynome de premier
 * degré permettant de convertir une unité en une autre.
 *
 * \return 
 *      - 0 : unites equivalentes
 *      - 1 : unites differentes
 *      - 2 : erreur passage arguments
 */
int
unitconvert (char *str_from, char *str_to, double *pente, double *intercept)
{
  cv_converter *converter;
  ut_unit *ut_unit_from, *ut_unit_to;
  const double x1 = 128.0;
  int CodRet;

  if ((str_from == NULL) || (str_to == NULL) || (pente == NULL)
      || (intercept == NULL))
    return -2;

  /* Premier test sans passer par udunits sur les unites passes en arguments.
   * Ce qui veut dire qu'on accepte de "convertir" des zertyuiop en zertyuiop
   */
  OteDebut (str_from, " \t");
  OteFin (str_from, " \t\n");
  OteDebut (str_to, " \t");
  OteFin (str_to, " \t\n");

  if (!strcasecmp (str_from, str_to))
    {
      *pente = 1.0;
      *intercept = 0.0;
      return 0;
    }

  if (unitSystem == NULL)
    {
      unitSystem = ut_read_xml (NULL);
      if (unitSystem == NULL)
	{
	  (void) fprintf (stderr,
			  "+++ WARN : Impossible d'initialiser le traitement des unites.\n");
	  CodRet = ut_get_status ();
	  switch (CodRet)
	    {
	    case UT_OPEN_ARG:
	      (void) fprintf (stderr,
			      "\tPas pu ouvrir le fichier d'unite explicite.\n");
	      perror ("\t");
	      break;
	    case UT_OPEN_ENV:
	      (void) fprintf (stderr,
			      "\tPas pu ouvrir le fichier d'unite $UDUNITS2_XML_PATH.\n");
	      perror ("\t");
	      break;
	    case UT_OPEN_DEFAULT:
	      (void) fprintf (stderr,
			      "\tPas pu ouvrir le fichier d'unite de l'installation.\n");
	      perror ("\t");
	      break;
	    case UT_PARSE:
	      (void) fprintf (stderr,
			      "\tErreur pendant analyse du fichier d'unites.\n");
	      break;
	    case UT_OS:
	      (void) fprintf (stderr,
			      "\tErreur systeme pendant lecture du fichier d'unites.\n");
	      perror ("\t");
	      break;
	    default:
	      (void) fprintf (stderr, "\tCode erreur = %d\n", CodRet);
	    }

	  *pente = 0.0 / 0.0;	/* NaN */
	  *intercept = 0.0 / 0.0;
	  return -1;
	}
      if (atexit (libere_unit) != 0)
	{
	  fprintf (stderr, "--- cannot set exit function\n");
	  /* Mais c'est pas grave pour l'execution, on continue quand même */
	}
    }

  ut_unit_from = ut_parse (unitSystem, str_from, UT_ASCII);
  if (ut_unit_from == NULL)
    {
      print_error_ut_parse ("origine", str_from);
      ut_free_system (unitSystem);
      return -1;
    }

  ut_unit_to = ut_parse (unitSystem, str_to, UT_ASCII);
  if (ut_unit_to == NULL)
    {
      print_error_ut_parse ("destination", str_to);
      ut_free(ut_unit_from);
      ut_free_system (unitSystem);
      return -1;
    }

  /*  This function returns a non-zero value if conversion is possible;
   *  otherwise, 0 is returned */
  CodRet = ut_are_convertible (ut_unit_from, ut_unit_to);
  if ((CodRet == UT_BAD_ARG) || (CodRet == UT_NOT_SAME_SYSTEM) ||
      (CodRet == UT_SUCCESS))
    {
      ut_free(ut_unit_from);
      ut_free(ut_unit_to);
      (void) fprintf (stderr,
		      "Unites d'origine (%s) et de destination (%s) incompatibles\n",
		      str_from, str_to);
      return -1;
    }
  converter = ut_get_converter (ut_unit_from, ut_unit_to);
  ut_free(ut_unit_from);
  ut_unit_from = NULL;
  ut_free(ut_unit_to);
  ut_unit_to = NULL;
  if (converter == NULL)
    {
      (void) fprintf (stderr,
		      "Pas pu obtenir un convertisseur de udunits2\n");
      return -2;
    }

  *intercept = cv_convert_double (converter, 0.0);
  *pente = (cv_convert_double (converter, x1) - *intercept) / x1;

  cv_free (converter);
  converter = NULL;

  return 0;
}

/** 
 * @brief Fonction simpliste de reconnaissance
 * d'une unité angulaire.
 * 
 * @param unit : chaine de caractère indiquant une unité angulaire
 *
 * @return : UNIT_IS_DEGREE pour degres,
 *   UNIT_IS_RADIAN pour radians,
 *   UNIT_IS_UNKNOWN pour inconnu.
 */
int
reconnait_deg_rad (const char *unit)
{
  int Flag_unit = UNIT_IS_UNKNOWN;

  if (unit == NULL)
    return UNIT_IS_UNKNOWN;

  if (!strcasecmp (unit, "degree") || !strcasecmp (unit, "degre")
      || !strcasecmp (unit, "deg"))
    {
      Flag_unit = UNIT_IS_DEGREE;
    }
  else if (!strcasecmp (unit, "rad") || !strcasecmp (unit, "radian"))
    {
      Flag_unit = UNIT_IS_RADIAN;
    }
  else
    {
      Flag_unit = UNIT_IS_UNKNOWN;
    }

  return Flag_unit;
}

/** 
 * @brief 
 * 
 * @param unit : chaine de caractère indiquant une unité "kt" ou "m/s"
 *
 * @return : 1 pour kt,  0 pour m/s, -1 pour inconnu.
 */
int
reconnait_kt_ms (const char *unit)
{
  int Flag_unit = -1;

  /* Ignorer les espaces en debut de chaine. */
  while ((*unit == ' ') || (*unit == '\t'))
    unit++;

  if (!strcasecmp (unit, "kt") || !strcasecmp (unit, "knot"))
    {
      Flag_unit = 1;
    }
  else if (!strcasecmp (unit, "m/s") || !strcasecmp (unit, "meter/second") ||
	   !strcasecmp (unit, "m/sec") ||
	   !strcasecmp (unit, "m s-1") || !strcasecmp (unit, "m.s-1") ||
	   !strcasecmp (unit, "meter second-1")
	   || !strcasecmp (unit, "meter.second-1"))
    {
      Flag_unit = 0;
    }
  else
    {
      Flag_unit = -1;
    }

  return Flag_unit;
}
