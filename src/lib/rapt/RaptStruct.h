#ifndef _RAPT_STRUCT_INCLUDED
#define _RAPT_STRUCT_INCLUDED

/*    Research
 *    Aircraft
 *    Processing
 *    Tools.
 *
 *   Ce fichier "include" contient les définitions de tous
 * les types standard d'AIDA, ainsi que des types manipulés
 * par la librairie RAPT. 
 *
 * Les structures propres à RAPT sont :
 *   Attribut : une structure servant à la liste chaînée des attributs :
 *                deux champs sont des pointeurs sur characteres.
 *                un champ est le pointeur vers la suite.
 *   Hdr_univ : pointeur sur pointeur sur attribut, qui servira à 
 *              stocker le début de chaque liste d'attribut.
 *
 *
 *      On définit ici trois sorte de noms :
 *  Les "ATYP_xxx" sont des typedef qui implémentent les
 *      types officiels AIDA à partir des types particuliers
 *      d'une machine.
 *  les "ATYC_..." font partie de l'enum AIDA_TYPE_CODE, et
 *      permettent de coder le type comme un simple entier.
 *  les "ATYN_..." qui sont les noms officiels de ces types.
 */

/* Pour les fonctions qui retournent un time_t.  */
#include <time.h>

/* Série de test pour inclure des fichiers .h qui
 * définissent des types dont on est sûrs de la taille.
 */
#if __STDC_VERSION__-0 >= 199901
  /* Ce test permet de choper plus de cas positifs, comme ceux où le
   *  compilo fournit un support C99, mais où la compatibilité stricte
   *  avec la norme est désactivée.
   * Le "-0" est là pour ne pas fâcher les vieux préprocesseurs (ne
   *  respectant pas la norme) qui remplacent un identificateur absent
   *  par rien (plutôt que par 0);
   * Source : Antoine Leca in fr.comp.lang.c, le ven 1 juin 2007.
   */
   #include <stdint.h>
#else
  #if defined(WIN32) || defined(OS2)
    typedef short int16_t;
    typedef unsigned short uint16_t;
    typedef int int32_t;
    typedef unsigned int uint32_t;
  #else
  /* inttypes.h fournit les définitions attendues sur HP-UX et gcc. 
   * Internet semble dire que c'est OK aussi pour AIX, sun, osf, et IRIX.
   * pour les BSD, il semblerait que ce soit <sys/types.h>  */
    #include <inttypes.h>
  #endif 
#endif 

/* Définitions spécifiques au format vecteur */
#define VECT_MAGIC            "VECT-DATA"
#define VECT_HDR_START        "\x02"
#define VECT_HDR_END          "\x0C\x03\x1A"
#define VECT_HDR_TXT_END      "FIN_HDR"

/* Définition de types AIDA */
typedef uint16_t ATYP_Q12;
typedef uint16_t ATYP_Q14;
typedef uint16_t ATYP_Q14S;
typedef uint16_t ATYP_Q16;
typedef uint32_t ATYP_Q32;
typedef unsigned char ATYP_UI8;
typedef char ATYP_I8;
typedef int16_t ATYP_I16;
typedef uint16_t ATYP_UI16;
typedef int32_t ATYP_I32;
typedef uint32_t ATYP_UI32;
typedef int64_t ATYP_I64;
typedef uint64_t ATYP_UI64;
typedef float ATYP_IF32;
typedef double ATYP_IF64;
typedef int ATYP_HF32;
typedef char *ATYP_STR;
typedef struct
{
  unsigned Mot_ARINC:32;
  unsigned datage:32;
}
ATYP_ARINC_SY429;

typedef char *ATYP_BC635_TIME;
typedef struct
  {
    short hh;
    short mm;
    short ss;
    short ms;
  }
ATYP_NCAR2D_TIME;

/* au 24/09/2009, on ne sait rien sur ces données, à part leur taille. */
typedef struct
{
    char b1;
    char b2;
    char b3;
    char b4;
}
ATYP_ICVPMS_TIME;

typedef void *ATYP_SPECIAL;

typedef union
  {
    ATYP_Q12 Quanta12;
    ATYP_Q14 Quanta14;
    ATYP_Q14S Quanta14_s;
    ATYP_Q16 Quanta16;
    ATYP_Q32 Quanta32;
    ATYP_I8  Int8;
    ATYP_UI8 UInt8;
    ATYP_I16 Int16;
    ATYP_UI16 UInt16;
    ATYP_I32 Int32;
    ATYP_UI32 UInt32;
    ATYP_I64 Int64;
    ATYP_UI64 UInt64;
    ATYP_IF32 Float32;
    ATYP_IF64 Float64;
    ATYP_HF32 HPFloat32;
    ATYP_STR String;
    ATYP_ARINC_SY429 SY429;
    ATYP_BC635_TIME BC635;
    ATYP_NCAR2D_TIME NCAR2D_TIME;
    ATYP_SPECIAL Special;
  }
ATYP_ALL;

typedef enum
  {
    ATYC_UNDEF,
    ATYC_Q12, ATYC_Q14, ATYC_Q16, ATYC_Q32,
    ATYC_I8, ATYC_UI8,
    ATYC_I16, ATYC_UI16,
    ATYC_I32, ATYC_UI32,
    ATYC_I64, ATYC_UI64,
    ATYC_IF32, ATYC_IF64,
    ATYC_HF32,
    ATYC_STRING,
    ATYC_ARINC_SY429,
    ATYC_BC635_TIME,
    ATYC_NCAR2D_TIME,
    ATYC_SPECIAL,
    ATYC_Q14S
  }
AIDA_TYPE_CODE;

/*   Les ATYC_LOCAL sont des macro qui donnent le "vrai" ATYC
 * correspondant aux types historiques du C (int, long, ..),
 * sur la machine actuelle, dont la taille peut varier.
 *   On peut les utiliser pour interfacer AIDA avec une 
 * fonction qui utilise ces types (par ex, pour les opérateurs),
 * mais il est déconseillé de les utiliser pour décrire un vecteur
 * car on aura un résultat différent d'une machine à l'autre.  */
#include <limits.h>
#if INT_MAX == 2147483647 && INT_MIN == -2147483648 && UINT_MAX == 4294967295 
	/* les "int" font 32 bits */
#define ATYC_LOCAL_INT ATYC_I32
#define ATYC_LOCAL_UINT ATYC_UI32
#endif

#if LONG_MAX == 2147483647 && LONG_MIN == -2147483648 && ULONG_MAX == 4294967295
	/* les "long" font 32 bits */
#define ATYC_LOCAL_LONG ATYC_I32
#define ATYC_LOCAL_ULONG ATYC_UI32
#elif LONG_MAX == 9223372036854775807L && LONG_MIN == (-LONG_MAX - 1L) && ULONG_MAX == 18446744073709551615UL
	/* les "long" font 64 bits */
#define ATYC_LOCAL_LONG ATYC_I64
#define ATYC_LOCAL_ULONG ATYC_UI64
#else
#error cannot handle local definition of "long"
#endif



#define ATYN_UNKNOWN              "unknown"
#define ATYN_Q12                  "Quanta_12_bits"
#define ATYN_Q14                  "Quanta_14_bits"
#define ATYN_Q14S                 "Quanta_14_bits_signe"
#define ATYN_Q16                  "Quanta_16_bits"
#define ATYN_Q32                  "Quanta_32_bits"
#define ATYN_I8                   "Int_8"
#define ATYN_UI8                  "U_Int_8"
#define ATYN_I16                  "Int_16"
#define ATYN_UI16                 "U_Int_16"
#define ATYN_I32                  "Int_32"
#define ATYN_UI32                 "U_Int_32"
#define ATYN_I64                  "Int_64"
#define ATYN_UI64                 "U_Int_64"
#define ATYN_IF32                 "Ieeefloat_32"
#define ATYN_IF64                 "Ieeefloat_64"
#define ATYN_HF32                 "Hpfloat_32"
#define ATYN_STR                  "String"
#define ATYN_ARINC_SY429          "Arinc_SY429"
#define ATYN_BC635_TIME           "BC635_Time"
#define ATYN_NCAR2D_TIME          "NCAR2D_Time"
#define ATYN_SPECIAL              "Special"

typedef struct attr_s
  {
    char *name;
    char *value;
    struct attr_s *next;
  }
attr;

typedef attr ** Hdr_univ;

#define MAX_NOM_PLATE_FORME	30
#define MAX_NOM_VECTOR		64

#endif /* _RAPT_STRUCT_INCLUDED */
