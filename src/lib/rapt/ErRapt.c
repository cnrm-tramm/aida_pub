#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <locale.h>

#include <gene.h>

#include "ErRapt.h"

extern int errno;
/* static int errapt; */
int errapt;

#define LEN_CHAINE_ERREUR	120

/**    Returns a pointer to a message describing the error
 * corresponding to the argument errnum.
 */
char *
strerrapt (const int errnum)
{
  static char vide[LEN_CHAINE_ERREUR];
  static char *STR_ERRNO;
  static char *STR_EINVAL;
  static char *STR_EBADF;
  static char *STR_EOPEN;
  static char *STR_EREAD;
  static char *STR_EWRITE;
  static char *STR_ENOMEM;
  static char *STR_EMMAP;
  static char *STR_EFFORMAT;
  static char *STR_EFFMT_SHORT;
  static char *STR_EFFMT_START;
  static char *STR_EFFMT_HLEN_NEG;
  static char *STR_EFFMT_HLEN_SEP;
  static char *STR_EFFMT_HDR_END;
  static char *STR_ENOPOS;
  static char *STR_EBADID;
  static char *STR_EBADACFT;
  static char *STR_EBADFMT;
  static char *STR_EBADYSTR;
  static char *STR_EBADNSTR;
  static char *STR_ENEGFREQ;
  static char *STR_EBADATYC;
  static char *STR_EBADVECNAM;
  static char *STR_ENOTAFILE;
  static char *STR_ENOTYOURS;
  static char *STR_ENOREAD;
  static char *STR_ENOWRITE;
  static char *STR_EBADEND;
  static char *STR_SHORTPATH;

  char *locale_msg;
  static int locale_code = 0;

  if (locale_code == 0)
    {
      locale_msg = setlocale (LC_MESSAGES, "");
      if (!strncmp (locale_msg, "fr", 2))
	locale_code = 1;
      else
	locale_code = 2;
    }

  if (locale_code == 1)
    {
      STR_ERRNO = "Erreur systeme :";
      STR_EINVAL = "Argument incorrect";
      STR_EBADF = "Mauvais descripteur de fichier";
      STR_EOPEN = "echec ouverture :";
      STR_EREAD = "echec lecture :";
      STR_EWRITE = "echec ecriture :";
      STR_ENOMEM = "echec allocation memoire :";
      STR_EMMAP = "Echec de projection en memoire :";
      STR_EFFORMAT = "Mauvais format de fichier";
      STR_EFFMT_SHORT = "Fichier trop court";
      STR_EFFMT_START =
	"fichier de format incorrect : ne commence pas par \"VECT-DATA\"";
      STR_EFFMT_HLEN_NEG = "fichier incorrect : longueur d'en-tete negative";
      STR_EFFMT_HLEN_SEP =
	"Fichier de format incorrect : manque '\\n' apres HDR_LEN";
      STR_EFFMT_HDR_END =
	"Fichier de format incorrect :  \"FIN_HDR\" manquant";
      STR_ENOPOS = "Impossible de placer le curseur en debut de fichier";
      STR_EBADID = "Longueur de Acq_Id ! = 6 ou 8 !!!";
      STR_EBADACFT = "Plate-forme inconnue";
      STR_EBADFMT = "Format de donnees inconnu";
      STR_EBADYSTR = "Sous-chaine annee incorrecte dans un Acq_ID";
      STR_EBADNSTR = "Sous-chaine Num_Acq incorrecte dans un Acq_ID";
      STR_ENEGFREQ = "Frequence negative";
      STR_EBADATYC = "Aida_type_Code non valable";
      STR_EBADVECNAM = "Le nom du vecteur ne correspond pas aun nom demande";
      STR_ENOTAFILE = "Ceci n'est pas un fichier ordinaire";
      STR_ENOTYOURS = "Ce fichier ne vous appartient pas";
      STR_ENOREAD = "Pas de droit de lecture";
      STR_ENOWRITE = "Pas de droit d'ecriture";
      STR_EBADEND =
	"Pas pu determiner l'orientation memoire (le boutisme) de cette machine";
      STR_SHORTPATH = "Chaine trop courte pour une fonction xxx2Path";
    }
  else
    {
      STR_ERRNO = "System error :";
      STR_EINVAL = "Invalid argument";
      STR_EBADF = "Bad file descriptor";
      STR_EOPEN = "open failed :";
      STR_EREAD = "read failed :";
      STR_EWRITE = "write failed :";
      STR_ENOMEM = "memory allocation failed :";
      STR_EMMAP = "memory mapping failed :";
      STR_EFFORMAT = "Error in file format";
      STR_EFFMT_SHORT = "File too short";
      STR_EFFMT_START = "Bad file format : not starting with \"VECT-DATA\"";
      STR_EFFMT_HLEN_NEG = "Bad file : negative header length";
      STR_EFFMT_HLEN_SEP = "Bad file format : missing '\\n' after HDR_LEN";
      STR_EFFMT_HDR_END = "Bad file format : missing \"FIN_HDR\"";
      STR_ENOPOS = "Unable to position to beginning of file";
      STR_EBADID = "Length of Acq_Id ! = 6 OR 8 !!!";
      STR_EBADACFT = "Unrecognised platform.";
      STR_EBADFMT = "Unrecognised data format.";
      STR_EBADYSTR = "Bad year substring in Acq_ID";
      STR_EBADNSTR = "Bad Num_Acq substring in Acq_ID";
      STR_ENEGFREQ = "Negative Frequency";
      STR_EBADATYC = "Invalid Aida_type_Code";
      STR_EBADVECNAM = "Vector name doesn't match requested name";
      STR_ENOTAFILE = "Not a regular file.";
      STR_ENOTYOURS = "Not your file.";
      STR_ENOREAD = "No read permission.";
      STR_ENOWRITE = "No write permission.";
      STR_EBADEND = "unable to determine endianness of this machine";
      STR_SHORTPATH = "A xxx2Path function was given a too short string";
    }


  switch (errnum)
    {
    case RAPT_ERRNO:
      strcpy (vide, STR_ERRNO);
      strcat_sur (vide, LEN_CHAINE_ERREUR, strerror (errno));
      return vide;
    case RAPT_EINVAL:
      return STR_EINVAL;
    case RAPT_EBADF:
      return STR_EBADF;
    case RAPT_EOPEN:
      strcpy (vide, STR_EOPEN);
      strcat_sur (vide, LEN_CHAINE_ERREUR, strerror (errno));
      return vide;
    case RAPT_EREAD:
      strcpy (vide, STR_EREAD);
      strcat_sur (vide, LEN_CHAINE_ERREUR, strerror (errno));
      return vide;
    case RAPT_EWRITE:
      strcpy (vide, STR_EWRITE);
      strcat_sur (vide, LEN_CHAINE_ERREUR, strerror (errno));
      return vide;
    case RAPT_ENOMEM:
      strcpy (vide, STR_ENOMEM);
      strcat_sur (vide, LEN_CHAINE_ERREUR, strerror (errno));
      return vide;
    case RAPT_EMMAP:
      strcpy (vide, STR_EMMAP);
      strcat_sur (vide, LEN_CHAINE_ERREUR, strerror (errno));
      return vide;
    case RAPT_EFFORMAT:
      return STR_EFFORMAT;
    case RAPT_EFFMT_SHORT:
      return STR_EFFMT_SHORT;
    case RAPT_EFFMT_START:
      return STR_EFFMT_START;
    case RAPT_EFFMT_HLEN_NEG:
      return STR_EFFMT_HLEN_NEG;
    case RAPT_EFFMT_HLEN_SEP:
      return STR_EFFMT_HLEN_SEP;
    case RAPT_EFFMT_HDR_END:
      return STR_EFFMT_HDR_END;
    case RAPT_ENOPOS:
      return STR_ENOPOS;
    case RAPT_EBADID:
      return STR_EBADID;
    case RAPT_EBADACFT:
      return STR_EBADACFT;
    case RAPT_EBADFMT:
      return STR_EBADFMT;
    case RAPT_EBADYSTR:
      return STR_EBADYSTR;
    case RAPT_EBADNSTR:
      return STR_EBADNSTR;
    case RAPT_ENEGFREQ:
      return STR_ENEGFREQ;
    case RAPT_EBADATYC:
      return STR_EBADATYC;
    case RAPT_EBADVECNAM:
      return STR_EBADVECNAM;
    case RAPT_ENOTAFILE:
      return STR_ENOTAFILE;
    case RAPT_ENOTYOURS:
      return STR_ENOTYOURS;
    case RAPT_ENOREAD:
      return STR_ENOREAD;
    case RAPT_ENOWRITE:
      return STR_ENOWRITE;
    case RAPT_EBADEND:
      return STR_EBADEND;
    case RAPT_SHORTPATH:
      return STR_SHORTPATH;
    default:
      sprintf (vide, "errapt=%d", errnum);
      return vide;
    }
}

/** Print a message describing current RAPT error status.
 *
 *    perrapt() writes a message to the standard error output, describing
 * the last error encountered during a call to a function of the RAPT library.
 * The argument string s is printed first, followed by a colon,  a blank, 
 * the message, and a new-line, just as the standard library function "perror" does.
 *
 *      The error number is taken from the external variable errapt (and errno if
 * a system error is detected). Those variables are set when errors occur but not
 * cleared when non-erroneous calls are made.
 *
 *      The contents of the messages are identical to those returned by 
 * the strerrapt() function with errapt as the argument.
 *
 *      If given a NULL string, the perrapt() function prints only the 
 * message and a new-line.
 */
void
perrapt (const char *s)
{
  if (s != NULL)
    {
      (void) fprintf (stderr, "%s: ", s);
    }

  (void) fprintf (stderr, "%s\n", strerrapt (errapt));

}
