/* Pour les definitions de GENE_BIG_ENDIAN, ... */
#include "gene.h"

/** Teste l'ordre des octets d'une machine.
 *
 *  \return 
 *     -  GENE_BIG_ENDIAN si "Big Endian"
 *     -  GENE_LITTLE_ENDIAN si "Little Endian"
 *     -  GENE_UNDEF_ENDIAN si l'algorithme n'a pas trouvé
 *
 *   Petit commentaire perso :
 *     Cet algorithme ne me semble pas absolument
 * correct : en effet, rien ne garantit que
 * adr(c[1]) = adr(c[0]) + 1 ....
 *  Bon, en pratique, il a marche sur tous les
 * machines/compilateurs que j'ai essayé.
 */

int
Endianness ()
{
  union
    {
      long l;
      char c[sizeof (long)];
    }
  u;

  u.l = 1;
  if (u.c[0] == 1)
    return GENE_LITTLE_ENDIAN;
  else if (u.c[sizeof (long) - 1] == 1)
      return GENE_BIG_ENDIAN;
  else
    return GENE_UNDEF_ENDIAN;
}
