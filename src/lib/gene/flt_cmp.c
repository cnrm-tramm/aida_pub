/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8
 */

#include <limits.h>
#include <float.h>
#include <math.h>

/*  Pour savoir si un float "x" est assimilable à zéro, il faut avoir 
 * une idée de l'ordre de grandeur. Par exemple, cos(M_PI/2.) retourne
 * 6.12323e-17, ce qui est très petit devant 1, mais très grand devant
 * FLT_MIN. Ou, lorsqu'on travaille entre 10^20 et 10^30, une valeur de 100
 * devient assimilable à zéro.
 *
 * Donc, on définit une variable float_0_borne, qui est égale
 * à 5 * FLT_MIN par défaut, mais réglable par un appel
 * à set_float_zero_ODG
 */
static double float_0_borne = 5. * FLT_MIN;

/**  Définit la borne max des valeurs assimilés a zéro 
 *  en fonction de l'ordre de grandeur des valeurs qui
 *  seront testées.
 * \param ODG : l'ordre de grandeur
 *
 *  */
void
set_float_zero_ODG (float ODG)
{
  float ODG_pos;

  ODG_pos = fabs (ODG);
  if (ODG_pos > 5 * 1.e10 * FLT_MIN)
    {
      float_0_borne = ODG_pos * 1e-10;
    }
  else
    {
      float_0_borne = 5. * FLT_MIN;
    }
}

/** Indique si x est assimilable à zéro, avec la précision
 * de l'ordre de grandeur actuel (cf. set_float_zero_ODG() )
 *
 * \param x : le nombre à tester.
 *
 * \return 0 ou 1
 * 
 */
int
almost_zero_flt (double x)
{
  return (fabs (x) < float_0_borne) ? 1 : 0;
}

/** Indique si x est assimilable à zéro, avec la précision d'un double
 *
 * \param x : le nombre à tester.
 *
 * \return 0 ou 1
 * 
 */
int
almost_zero_dbl (double x)
{
  return (fabs (x) < 5. * DBL_MIN) ? 1 : 0;
}

/**  Compare X et Y, avec une tolerance spécifiée
 *
 * \param x : le premier nombre à tester.
 * \param y : le second nombre à tester.
 * \param toler : la tolérance absolue (pas proportionnelle à x ou y).
 *
 *  \return : 1 si x > y, -1 si x < y, 0 si x ~= y, avec la tolerance demandea
 */
int
toler_cmp_flt (double x, double y, double toler)
{
  if (almost_zero_flt (x) && almost_zero_flt (y))
    return 0;
  if (x - y > toler)
    return 1;
  if (x - y < -toler)
    return -1;
  return 0;
}

/**  Compare X et Y, avec une precision relative quelconque.
 *
 * \param x : le premier nombre à tester.
 * \param y : le second nombre à tester.
 * \param rel_prec : la precision relative du test
 *
 *  \return : 1 si x > y, -1 si x < y, 0 si x ~= y, à la précision demandee
 */
int
approx_cmp_flt (double x, double y, double rel_prec)
{
  if (almost_zero_flt (x) && almost_zero_flt (y))
    return 0;
  if (x - rel_prec * fabs (x) > y + rel_prec * fabs (y))
    return 1;
  if (x + rel_prec * fabs (x) < y - rel_prec * fabs (y))
    return -1;
  return 0;
}

/**  Compare X et Y, avec la precision relative des flottants.
 *
 * \param x : le premier nombre à tester.
 * \param y : le second nombre à tester.
 *
 *  \return : 1 si x > y, -1 si x < y, 0 si x ~= y, à la précision d'un float
 */
int
almost_cmp_flt (double x, double y)
{
  static double relative_precision = 5. * FLT_EPSILON;

  return approx_cmp_flt (x, y, relative_precision);
}

/**  Indique si X et Y sont approximativement égaux (avec une certaine tolerance)
 *
 * \param x : le premier nombre à tester.
 * \param y : le second nombre à tester.
 * \param toler : la tolerance acceptée.
 *
 * \return 1 si quasi-égalité, 0 sinon.
 */
int
toler_equal_flt (double x, double y, double toler)
{
  return toler_cmp_flt (x, y, toler) ? 0 : 1;
}

/**  Indique si X et Y sont égaux (à la précision des floats) 
 *
 * \param x : le premier nombre à tester.
 * \param y : le second nombre à tester.
 *
 * \return 1 si quasi-égalité, 0 sinon.
 */
int
almost_equal_flt (double x, double y)
{
  return (almost_cmp_flt (x, y)) ? 0 : 1;
}

/**  Indique si X et Y sont approximativement égaux (à une précision 
 *    relative donnée) 
 *
 * \param x : le premier nombre à tester.
 * \param y : le second nombre à tester.
 * \param rel_prec : precision relative
 *
 * \return 1 si quasi-égalité, 0 sinon.
 */
int
approx_equal_flt (double x, double y, double rel_prec)
{
  return approx_cmp_flt (x, y, rel_prec) ? 0 : 1;
}

