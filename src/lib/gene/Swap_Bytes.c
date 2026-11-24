/* -*- coding: utf-8 -*- 
 * vim:fileencoding=utf-8 
 */

/*
 *  Ensemble de fonctions pour échanger des octets.
 *
 */

/** Échange de 2 octets dans un (ou plusieurs) groupe(s) de 16 bits.
 *
 * @param ptr : pointeur vers le (ou les) groupe de 16 bits.
 * @param len : indique le nbre de groupe de 16 bits,
 * pas le nombre d'octets !
*/
void
swap_2_bytes (void *ptr, int len)
{
  register char *c_ptr = ptr;
  register char c_tmp;
  register int i;

  for (i = 0; i < len; i++)
    {
      c_tmp = c_ptr[0];
      c_ptr[0] = c_ptr[1];
      c_ptr[1] = c_tmp;
      c_ptr += 2;
    }
}

/** Change l'ordre des 4 octets dans un (ou plusieurs) groupe(s) de 32 bits.
 * 
 * @param ptr : pointeur vers le (ou les) groupe de 32 bits.
 * @param len : indique le nbre de groupe de 32 bits,
 * pas le nombre d'octets !
 */
void
swap_4_bytes (void *ptr, int len)
{
  register char *c_ptr = ptr;
  register char c_tmp;
  register int i;

  for (i = 0; i < len; i++)
    {
      c_tmp = c_ptr[0];
      c_ptr[0] = c_ptr[3];
      c_ptr[3] = c_tmp;
      c_tmp = c_ptr[1];
      c_ptr[1] = c_ptr[2];
      c_ptr[2] = c_tmp;
      c_ptr += 4;
    }
}

/** Change l'ordre des 8 octets dans un (ou plusieurs) groupe(s) de 64 bits.
 * 
 * @param ptr : pointeur vers le (ou les) groupe de 64 bits.
 * @param len : indique le nbre de groupe de 64 bits,
 * pas le nombre d'octets !
 */
void
swap_8_bytes (void *ptr, int len)
{
  register char *c_ptr = ptr;
  register char c_tmp;
  register int i;

  for (i = 0; i < len; i++)
    {
      c_tmp = c_ptr[0];
      c_ptr[0] = c_ptr[7];
      c_ptr[7] = c_tmp;
      c_tmp = c_ptr[1];
      c_ptr[1] = c_ptr[6];
      c_ptr[6] = c_tmp;
      c_tmp = c_ptr[2];
      c_ptr[2] = c_ptr[5];
      c_ptr[5] = c_tmp;
      c_tmp = c_ptr[3];
      c_ptr[3] = c_ptr[4];
      c_ptr[4] = c_tmp;

      c_ptr += 8;
    }
}
