/*
 * Il existe certaines fonctions pour lesquelles
 * cextract n'extrait pas le prototype.
 *
 * Ces prototypes sont donc ecrits dans ce fichier,
 * de facon non-automatique.
 *
 * Le programme qui en ont besoin devront donc faire
 * un #include "thermo_extra.h"
 */
extern void (*ew_function (const char *formule_name)) (const float, float *);
