#include "RaptStruct.h"
#include "ErRapt.h"

/*
 *   Cette fonction fournit les noms (chaîne de caract. ) des types
 * standard connus de AIDA.
 *   Techniquement, c'est rien qu'un "case" très bête (tout le boulot
 * est fait par la définition des ATYN, ATYC,...), mais c'est mieux
 * que ce soit dans une seule fonction d'une seule librairie.
 *
 */

char *
AidaTypNom (const AIDA_TYPE_CODE typ)
{
  switch (typ)
    {
    case ATYC_UNDEF:
      return "Undefined";
    case ATYC_Q12:
      return ATYN_Q12;
    case ATYC_Q14:
      return ATYN_Q14;
    case ATYC_Q14S:
      return ATYN_Q14S;
    case ATYC_Q16:
      return ATYN_Q16;
    case ATYC_Q32:
      return ATYN_Q32;
    case ATYC_I8:
      return ATYN_I8;
    case ATYC_UI8:
      return ATYN_UI8;
    case ATYC_I16:
      return ATYN_I16;
    case ATYC_UI16:
      return ATYN_UI16;
    case ATYC_I32:
      return ATYN_I32;
    case ATYC_UI32:
      return ATYN_UI32;
    case ATYC_I64:
      return ATYN_I64;
    case ATYC_UI64:
      return ATYN_UI64;
    case ATYC_IF32:
      return ATYN_IF32;
    case ATYC_IF64:
      return ATYN_IF64;
    case ATYC_HF32:
      return ATYN_HF32;
    case ATYC_ARINC_SY429:
      return ATYN_ARINC_SY429;
    case ATYC_BC635_TIME:
      return ATYN_BC635_TIME;
    case ATYC_NCAR2D_TIME:
      return ATYN_NCAR2D_TIME;
    case ATYC_STRING:
      return ATYN_STR;
    case ATYC_SPECIAL:
      return ATYN_SPECIAL;
    default:
      errapt = RAPT_EBADATYC;
      return ATYN_UNKNOWN;
    }
}
