/*
 *
 * $Log: not supported by cvs2svn $
 * Revision 1.8  2007/11/29 11:38:39  bruno_PIGUET
 * Corrections de doc.
 *
 * Revision 1.7  2007/11/29 10:39:37  bruno_PIGUET
 * Mise en forme commentaires.
 *
 * Revision 1.6  2004/05/27 14:33:55  mequigno
 * Initialisation du pointeur sur integer *NbOpt présent dans la liste d'arguments passés à la fonction EclatLdc().
 *
 * Revision 1.5  2002/02/04 09:04:22  piguet
 * correction d'un probleme bizarre : fichier tronqué, manque
 * le "}" final.
 *
 * Revision 1.4  2002/01/15 15:36:20  piguet
 * Correction "rapide" du bug signalé précédement.
 *
 * Revision 1.3  2000/06/14 14:45:21  piguet
 * Signalement d'un bug potentiel :
 *    la fonction EclatLdc renvoie l'adresse d'une variable
 * locale, même pas déclarée en "static".
 *
 * Revision 1.2  97/02/17  16:05:05  16:05:05  piguet (Bruno PIGUET)
 * cosmetique
 * 
 *
 *****************************************************************************
 */



#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define	TRUE	1
#define FALSE	0
#define MAX_ARG_LENGTH	60


char *
SaveOptArg (char mapile[][MAX_ARG_LENGTH],
	    int *nb_champs)
{
  int i, tailleopt;
  char *tabstr;

  /* Je determine la taille a allouer. */
  tailleopt = 0;
  for (i = 0; i < *nb_champs; i++)
    {
      tailleopt = tailleopt + strlen (mapile[i]) + 1;
    }
  tailleopt = tailleopt + 1;

  /* J'alloue pour une option et son (ses) argument(s). */
  if ((tabstr = malloc (tailleopt)) == NULL)
      (void) fprintf (stderr, "Erreur, allocation impossible\n");

  /* Je range l'option et son (ses) argument(s). */
  strcpy (tabstr, mapile[0]);
  for (i = 1; i < *nb_champs; i++)
    {
      strcat (tabstr, " ");
      strcat (tabstr, mapile[i]);
    }
  *nb_champs = 0;
  mapile = NULL;
  return (tabstr);
}


/** Décode la ligne de commande (ldc) et renvoie un tableau de 
 * de chaines caracteres du type :
 *			option_1 [arguments_eventuels]
 *			     	    ...
 *			  [*]	 [arguments_eventuels]
 *				    ...
 *			option_n [arguments_eventuels]
 *
 *		Dans le cas ou un argument est entre en ldc sans option 
 *		préalable - cas ou il se trouve juste derriere le programme -
 *		une "*" remplace l'option dans le tableau de carateres.
 *
 *		Si deux options se suivent sans être séparées par un espace,
 *		la routine arrête le traitement par exit(0).
 *
 * APPEL		char **EclatLdc(int argc, char *argv[], int *nbropt)
 *
 * @param nb_arg : nombre d'arguments en ldc (typiquement, argc)
 * @param list : liste des arguments en ldc (typiquement, argv)
 * @param NbOpt : le nombre d'options trouvées par la routine.
 *
 * \return Un tableau de pointeurs sur caractères.
 *
 */
char **
EclatLdc (int nb_arg,
	  char **list,
	  int *NbOpt)
{
  char str_tmp[MAX_ARG_LENGTH], argum[100];
  char pile[500][MAX_ARG_LENGTH];
  static char *TabTriee[500];
  char *ptr;
  int i, f_pile_pleine, nbchamps;

  f_pile_pleine = FALSE;

  *NbOpt = 0;

  for (i = 1; i < nb_arg; i++)
    {
      (void) strcpy (argum, list[i]);
      if (argum[0] == '-')
	{
	  /* Nouvelle option, mais pas la premiere => on emmagasine les parametres
	     deja traites. */
	  if (f_pile_pleine)
	    {
	      TabTriee[*NbOpt] = NULL;
	      TabTriee[*NbOpt] = SaveOptArg (pile, &nbchamps);
	      *NbOpt = *NbOpt + 1;
	      f_pile_pleine = FALSE;
	    }

	  /* J'empile la nouvelle option ou la premiere. */
	  nbchamps = 0;
	  strncpy (pile[nbchamps], &argum[1], 1);
	  pile[nbchamps][1] = '\0';
	  nbchamps++;
	  f_pile_pleine = TRUE;

	  if (strlen (argum) > 2)
	    {
	      /* On refuse le cas ou deux options seraient "collees". Ex -b-h */
	      strcpy (str_tmp, &argum[1]);
	      ptr = NULL;
	      if ((ptr = strchr (str_tmp, '-')) != NULL)
		{
		  (void) fprintf (stderr,
				  "\nEclatLdc : les deux options %s doivent separees par un espace.\n\n"
				  ,argum);
		  exit (0);
		}
	      /* J'empile un argument "colle" a son option. */
	      (void) strcpy (pile[nbchamps], &argum[2]);
	      nbchamps++;
	    }
	  /* Si toute la liste des arguments est passee, je range ... */
	  if (i >= nb_arg - 1)
	    {
	      TabTriee[*NbOpt] = NULL;
	      TabTriee[*NbOpt] = SaveOptArg (pile, &nbchamps);
	      *NbOpt = *NbOpt + 1;
	    }
	}
      else
	{
	  /* J'empile un argument. */
	  (void) strcpy (pile[nbchamps], argum);
	  nbchamps++;

	  /* Dans le cas ou le premier argument de la ldc n'est pas une option, */
	  /* on ecrit le caractere "*" a la place de l'option.                 */
	  if (i == 1)
	    {
	      (void) strcpy (pile[nbchamps - 1], "* ");
	      (void) strcat (pile[nbchamps - 1], argum);
	      TabTriee[*NbOpt] = NULL;
	      TabTriee[*NbOpt] = SaveOptArg (pile, &nbchamps);
	      *NbOpt = *NbOpt + 1;
	      f_pile_pleine = FALSE;
	    }

	  /* Si toute la liste des arguments est passee, je range ... */
	  if ((i >= nb_arg - 1) && (f_pile_pleine))
	    {
	      TabTriee[*NbOpt] = NULL;
	      TabTriee[*NbOpt] = SaveOptArg (pile, &nbchamps);
	      *NbOpt = *NbOpt + 1;
	    }
	}			/* fin else "-" */
    }				/* fin for (i = 1; i < nb_arg; i++) */
  return (TabTriee);
  /* Attention !! */
  /*  warning: function returns address of local variable */
  /* But it works, since the variable is declared "static" */
  /*  Is it really needed ? */
}
