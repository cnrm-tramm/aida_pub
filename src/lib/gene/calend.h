extern int
gregor_bissextile (int annee);

extern int
nb_jour_annee (int annee);

extern int
date_to_JDA (int annee, int mois, int jour);

extern int
date_to_JDA_DnR (int annee, int mois, int jour);

extern void
JDA_to_date (int JDA, int *annee_p, int *mois_p, int *jour_p);
