/*
 *  Programme de création des fichiers (LaTeX) de documentation
 * des opérateurs, à partir des fonctions d'auto-description
 * (les ID_xxx).
 */

#define _POSIX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#ifndef PATH_MAX
#define PATH_MAX 1023
#endif

#include <gene.h>
#include <rapt.h>
#include <oper.h>
#include <load_oper.h>

/** 
 * @brief Fournit les noms (chaîne de caract. ) des types
 * standard connus de AIDA, sous la forme utilisée dans 
 * la documentation. 
 *
 * Cette fonction est très semblable à AidaTypNom de la bibliothèque
 * rapt, mais produit un résultat plus adapté à la documentation.
 * 
 * @param typ un type de variable, sous la forme d'un code interne à AIDA.
*/
const char *
DocTypNom (const AIDA_TYPE_CODE typ)
{
  switch (typ)
    {
    case ATYC_I32:
      return "int";
    case ATYC_IF32:
      return "float";
    case ATYC_IF64:
      return "double";
    default:
      return AidaTypNom (typ);
    }
}

char *
DocCatNom (const CATEGORIE categorie)
{
  switch (categorie)
    {
    case CAT_UNKNOWN:
      return "Undefined";
    case VECTOR:
      return "Vecteur";
    case COEFFICIENT:
      return "Coeff.";
    default:
      return "BUG-";
    }
}

/**   Ecrit, sur le "fichier" stream, la chaine de 
 * caractère *s, en encodant les caractères 
 * de commande de LaTeX.
 */
int
LaTeX_fputs (const char *s, FILE * stream)
{
  int cod_ret, i;

  if ((s == NULL) || (stream == NULL))
    return -1;			/*  mettre errno à EBADF ?  */

  i = 0;
  while (*s != 0)
    {
      switch (*s)
	{
	case '#':
	case '$':
	case '%':
	case '~':
	case '&':
	case '^':
	case '_':
	case '\\':
	case '{':
	case '}':
	  /* On n'écrit que le caractère d'échappement. */
	  cod_ret = putc ('\\', stream);
	  if (cod_ret == EOF)
	    return EOF;
	  i++;			/* SURTOUT PAS de break. */
	default:
	  cod_ret = putc (*s, stream);
	  if (cod_ret == EOF)
	    return EOF;
	  i++;
	}
      s++;
    }
  return i;
}

void
EcritCodageComment (FILE * of)
{
  /* Les chaînes de caractères suivantes ont des accents
   * explicitement codés en ISO-8859-15 ("latin9"), qui
   * est le codage de toutes les docs AIDA. 
   *   Le jour d'un éventuel passage à l'utf-8, penser à faire
   * les modifications en conséquence.
   *  En latin-9, les "é" sont le caractère 233, codés par \xe9 (ou \351) 
   *  En utf-8, les "é" sont codés par \xc3\xa9 (ou \303\251)
   *  En latin-9, les "ô" sont le caractère 244, codés par \xf4 (ou \364) 
   *  En utf-8, les "ô" sont codés par \xc3\xb4 (ou \303\264)
   */

  const char *message =
    "%% Dans ce fichier, les \351ventuels accents sont cod\351s\n"
    "%% en ISO-8859-15 (aka latin9)\n"
    "%% La ligne suivante donne trois exemples \n"
    "%% e accent aigu : \351, e accent grave : \350, e-dans-l'o : \275\n";

  (void) fprintf (of, "%s", message);
}

void
EcritDebutTabArg (FILE * of, const sens direction)
{
  char *commentstr, *titrestr;

  switch (direction)
    {
    case DIR_NONE:
      commentstr = "BUG : dir inconnue";
      titrestr = "Bug : dir inconnue";
      break;
    case DIR_IN:
      commentstr = "ENTREES";
      titrestr = "Entr\\'ees";
      break;
    case DIR_OUT:
      commentstr = "SORTIES";
      titrestr = "Sorties";
      break;
    default:
      commentstr = "BUG dir hors-gamme";
      titrestr = "Bug dir hors-gamme";
    }
  (void) fprintf (of, "%s%s%s%s\n", "%", "%%%%", commentstr, "%%%%");
  (void) fprintf (of, "%s\n", "\\begin{tabarg}");
  (void) fprintf (of, "%s%s%s\n", "\\multicolumn{3}{l}{\\titretab {",
		  titrestr, "}}\\\\");
  (void) fprintf (of, "%s\n", "\\hline");
}

void
EcritLigneTabArg (FILE * of, const int NumArg, const Arg_profil Arg_Car)
{
  (void) fprintf (of, "\\$Arg%d & ", NumArg + 1);
  (void) fprintf (of, "%s, ", DocCatNom (Arg_Car.categorie));
  (void) fprintf (of, "%s", "\\texttt{");
  (void) fprintf (of, "%s", DocTypNom (Arg_Car.typ));
  if (Arg_Car.array_dim != NULL)
    {
      if (strcmp (Arg_Car.array_dim, "1"))
	(void) fprintf (of, "[%s]", Arg_Car.array_dim);
    }
  (void) fprintf (of, "%s", "} ");
  (void) fprintf (of, "%s", "& ");
  (void) fprintf (of, "%s", "blabla (");
  (void) LaTeX_fputs (Arg_Car.unite, of);
  (void) fprintf (of, "%s", ")\\\\");
  (void) fprintf (of, "\n");
}

void
CreateStdDocFile (const char *DocFileName, const char *NomOper)
{
  FILE *of;

  of = fopen (DocFileName, "w");
  if (of == NULL)
    {
      perror (DocFileName);
      return;
    }
  (void) fprintf (of, "%s\n%s\n", "%%%%%", "%");
  EcritCodageComment (of);
  (void) fprintf (of, "%s%s%s\n", "\\section{", "INCONNU", "}");
  (void) fputs ("\n", of);
  (void) fprintf (of, "%s%s%s%s", "\\itemstyle{", "Op\\'erateur~:", "} ",
		  "\\operfmt{");
  (void) LaTeX_fputs (NomOper, of);
  (void) fprintf (of, "%s\n", "}");
  (void) fprintf (of, "%s", "\\index{");
  (void) LaTeX_fputs (NomOper, of);
  (void) fprintf (of, "%s\n", "}");
  (void) fputs ("\n", of);
  (void) fprintf (of, "%s%s%s%s\n", "%", "%%%%", "OBJET", "%%%%");
  (void) fprintf (of, "%s%s%s\n", "\\itemstyle{", "Objet~:", "}");
  (void) fprintf (of, "%s\n", "INCONNU");
  (void) fputs ("\n", of);
  (void) fprintf (of, "%s%s%s%s\n", "%", "%%%%", "ARGUMENTS", "%%%%");
  (void) fprintf (of, "%s\n", "\\bigskip");
  (void) fprintf (of, "%sarguments/%s.args.tex%s\n", "\\input{", NomOper,
		  "}");
  (void) fprintf (of, "\n");
  (void) fprintf (of, "%s%s%s%s\n", "%", "%%%%", "FORMULE", "%%%%");
  (void) fprintf (of, "%s%s%s\n", "\\itemstyle{", "Formule", "}");
  (void) fprintf (of, "\n");
  (void) fprintf (of, "%sformules/%s.frm.tex%s\n", "\\input{", NomOper, "}");
  (void) fprintf (of, "\n");
  (void) fprintf (of, "%s%s%s%s\n", "%", "%%%%", "AUTEUR", "%%%%");
  (void) fprintf (of, "%s%s%s\n", "\\itemstyle{", "Auteur~:", "}");
  (void) fprintf (of, "%s\n", "CNRM/GMEI/TRAMM");
  (void) fprintf (of, "\n");
  (void) fprintf (of, "%s%s%s%s\n", "%", "%%%%", "REFERENCE", "%%%%");
  (void) fprintf (of, "%s%s%s\n", "\\itemstyle{", "R\\'ef\\'erences~:", "}");
  (void) fprintf (of, "%s\n", "INCONNU");
  fclose (of);
}

void
CreateArgDocFile (FILE * DocFile, const oper * Oper)
{
  int flag_in, flag_out;
  int j;

  /* Le tableau des entrées */
  flag_in = 0;
  for (j = 0; j < Oper->NbArg; j++)
    {
      if (Oper->Arg_Car[j].direction == DIR_IN)
	{
	  if (!flag_in)
	    {
	      EcritDebutTabArg (DocFile, DIR_IN);
	      flag_in = 1;
	    }
	  EcritLigneTabArg (DocFile, j, Oper->Arg_Car[j]);
	}
    }
  (void) fprintf (DocFile, "%s\n", "\\end{tabarg}");
  (void) fprintf (DocFile, "\n");

  /* Puis le tableau des sorties */
  (void) fprintf (DocFile, "%s\n", "\\medskip");
  flag_out = 0;
  for (j = 0; j < Oper->NbArg; j++)
    {
      if (Oper->Arg_Car[j].direction == DIR_OUT)
	{
	  if (!flag_out)
	    {
	      EcritDebutTabArg (DocFile, DIR_OUT);
	      flag_out = 1;
	    }
	  EcritLigneTabArg (DocFile, j, Oper->Arg_Car[j]);
	}
    }
  (void) fprintf (DocFile, "%s\n", "\\end{tabarg}");

}

void
CreateFrmDocFile (const char *DocFileName, const char *NomOper)
{
  FILE *of;

  if (DocFileName == NULL)
    {
      return;
    }
  of = fopen (DocFileName, "w");
  if (of == NULL)
    {
      perror (DocFileName);
      return;
    }

  if (NomOper != NULL)
    {
      (void) fprintf (of, "%s%s\n", "%% Formule de l'operateur : ", NomOper);
    }
  else
    {
      (void) fprintf (of, "%s\n",
		      "%% UNDEFINED NAME. There's a bug somewhere.");
    }
  EcritCodageComment (of);
  (void) fprintf (of, "%s\n", "\\[");
  (void) fprintf (of, "%s\n", "Resultat = a-b. \\Zeta");
  (void) fprintf (of, "%s\n", "\\]");
  (void) fprintf (of, "\n");
  fclose (of);
}

int
main (int argc, char *argv[])
{
  oper *Liste_oper;
  int CodRet;
  int i, NbOper, NbEcrit;
  char DocPath[PATH_MAX + 1];
  char *OperDocPath;
  char *ArgOperDocPath;
  char *FrmOperDocPath;
  char OperLibPath[PATH_MAX + 1];
  char DocFileName[PATH_MAX + 1];
  FILE *DocFile;
  char *EnvStr, *Env_AIDA;
  struct stat buf;

  CodRet = AidaGetEnv ("AIDA_LIB", &EnvStr);
  switch (CodRet)
    {
    case 2:			/* Le cas normal : $AIDA_HOME+(ext.) */
      break;
    case 0:			/* Le cas ou une var d'envir. spécifique existe. */
      fprintf (stderr,
	       "WARN : On utilisera les librairies de %s (indiqué par AIDA_LIB)\n",
	       EnvStr);
      fprintf (stderr, "       au lieu de $AIDA_HOME/lib\n");
      break;
    case -1:
      perrapt (argv[0]);
      break;
    default:
      fprintf (stderr, "WARN : pour %s, %s\n", "AIDA_LIB",
	       GetEnvMsg (CodRet));
    }
  strncpy (OperLibPath, EnvStr, PATH_MAX);
  OperLibPath[PATH_MAX - 1] = 0;
  strncat (OperLibPath, "/liboper.sl", PATH_MAX);
  free (EnvStr);
  
  Env_AIDA = getenv ("AIDA_HOME");
  if (Env_AIDA == NULL)
    {
      fprintf(stderr, "+++ Pas d'environnemnt AIDA. On ne peut rien faire \n");
      exit(-1);
    }
  else  
    {
     strcpy (DocPath,Env_AIDA);
     strcat ( DocPath,"/src/doc" );
    }
  fprintf(stderr,"--- Repertoire destination de la doc : %s\n",DocPath); 
       
  CodRet = CheckDirExist (DocPath, DIR_FORCE);
  if (CodRet == 0)
    {
      fprintf (stderr,
	       "Le répertoire de doc (%s) n'existe pas, et il n'est pas possible de le créer !\n",
	       DocPath);
      perror (NULL);
      exit (-1);
    }
  OperDocPath = malloc (strlen (DocPath) + strlen ("/oper") + 1);
  strcpy (OperDocPath, DocPath);
  strcat (OperDocPath, "/oper");
  fprintf(stderr,"--- Repertoire des operateurs : %s\n",OperDocPath); 

  CodRet = CheckDirExist (OperDocPath, DIR_FORCE);
  if (CodRet == 0)
    {
      fprintf (stderr,
	       "Le répertoire de doc des opérateurs (%s) n'existe pas, et il n'est pas possible de le créer !\n",
	       OperDocPath);
      perror (NULL);
      exit (-1);
    }

  ArgOperDocPath = malloc (strlen (OperDocPath) + strlen ("/arguments") + 1);
  strcpy (ArgOperDocPath, OperDocPath);
  strcat (ArgOperDocPath, "/arguments");
  if (CodRet == 0)
    {
      fprintf (stderr,
	       "Le répertoire des argumenst des opérateurs (%s) n'existe pas, et il n'est pas possible de le créer !\n",
	       ArgOperDocPath);
      perror (NULL);
      exit (-1);
    }

  FrmOperDocPath = malloc (strlen (OperDocPath) + strlen ("/formules") + 1);
  strcpy (FrmOperDocPath, OperDocPath);
  strcat (FrmOperDocPath, "/formules");

  NbOper = Init_Liste_Oper_dyn (OperLibPath, &Liste_oper);
  if (NbOper < 0)
    {
      (void) fprintf (stderr,
		      "%s: Impossible de charger la bibliotheque d'operateurs %s \n",
		      argv[0], OperLibPath);
      (void) fprintf (stderr, "---%s---\n", OPLD_erreur (NbOper));
      /* CloseLog (); */
      exit (4);
    }
  else
    {
      (void) fprintf (stdout,
		      "+++ %s : %d opérateurs chargés\n", argv[0], NbOper);
    }

  NbEcrit = 0;
  for (i = 0; i < NbOper; i++)
    {
      /* 1- le fichier de doc complète de l'opérateur */
      strcpy (DocFileName, OperDocPath);
      strcat (DocFileName, "/");
      strcat (DocFileName, Liste_oper[i].Nom);
      strcat (DocFileName, ".tex");
      CodRet = stat (DocFileName, &buf);
      if (CodRet == -1)
	if (errno == ENOENT)
	  {
	    CreateStdDocFile (DocFileName, Liste_oper[i].Nom);
	    NbEcrit++;
	  }

      /* 2- le fichier "include" de description des arguments */
      strcpy (DocFileName, ArgOperDocPath);
      strcat (DocFileName, "/");
      strcat (DocFileName, Liste_oper[i].Nom);
      strcat (DocFileName, ".args.tex");
      CodRet = stat (DocFileName, &buf);
      if (CodRet == -1)
	if (errno == ENOENT)
	  {
	    DocFile = fopen (DocFileName, "w");
	    if (DocFile != NULL)
	      {
		EcritCodageComment (DocFile);
		CreateArgDocFile (DocFile, &(Liste_oper[i]));
		fclose (DocFile);
	      }
	    else
	      {
		perror (DocFileName);
	      }
	  }

      /* 3- le fichier "include" contenant la formule */
      strcpy (DocFileName, FrmOperDocPath);
      strcat (DocFileName, "/");
      strcat (DocFileName, Liste_oper[i].Nom);
      strcat (DocFileName, ".frm.tex");
      CodRet = stat (DocFileName, &buf);
      if (CodRet == -1)
	if (errno == ENOENT)
	  CreateFrmDocFile (DocFileName, Liste_oper[i].Nom);

    }

  (void) fprintf (stdout,
		  "+++ %s : %d opérateurs, %d nouveaux fichiers-doc écrits\n",
		  argv[0], i, NbEcrit);
  Free_Liste_Oper (&Liste_oper);

  free (FrmOperDocPath);
  free (OperDocPath);
  free (ArgOperDocPath);
  return EXIT_SUCCESS;
}
