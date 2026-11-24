#!/usr/bin/env python3

"""
Fonctions d'analyse des instructions d'un .fil
"""

import sys
import os
import logging
import ast      # Abstract Syntax Trees
import re
import numpy as np


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import Constantes

# Constantes
# ----------
# pour permettre à eval de remplacer par exemple 'Ra/g' par sa valeur,
# "importer" les constantes AIDA en variables locales
locals().update(Constantes.AIDA_Csts)


class Ast_fil(ast.NodeVisitor):
    """ Classe NodeVisitor pour AST sur les .fil.
        Ajout de la variable 'self.called_funcs' qui permet de mémoriser
        la liste des noms de fonction trouvés par AST.
    """
    def __init__(self):
        super().__init__()

        # liste des noms de fonction trouvés par AST
        self.called_funcs = set()

    def visit_Expr(self, node):
        self.generic_visit(node)

    def visit_Call(self, node):
        def visit_func(node):
            if type(node) == ast.Name:
                return node.id
            elif type(node) == ast.Attribute:
                # Recursion on series of calls to attributes.
                func_name = visit_func(node.value)
                func_name += "." + node.attr
                return func_name
            elif type(node) == ast.Str:
                return node.s
            elif type(node) == ast.Subscript:
                return node.value.id

        func = node.func
        func_name = visit_func(func)
        self.called_funcs.add(func_name)


    def visit_Assign(self, node):
        g = self.generic_visit(node)


def protect_dollars(lines):
    """ Retourne toutes les lignes reçues après avoir enclos entre ''
        chaque variable commençant par un $.
    """
    # protection de toutes les variables $xxx par : "$xxx"
    pattern = re.compile('(\$[\w.^$]+)')
    return [ pattern.sub(r"'\1'", line.strip()) for line in lines ]


def protect_specials(lines, mode=None):
    """ Retourne toutes les lignes reçues après avoir enclos entre ''
        chaque variable contenant des caractères spéciaux : _%:.@
        'regex \w <=> [a-zA-Z0-9_]

        :param str() mode      : si l'instruction est une signature (comme le
                                 fait EDIFIL), 'protect_specials' ne protège
                                 pas bien l'instructruction.
                                 => mode permet d'adapter le code...
    """
    # protection de toutes les variables contenant des caractères spéciaux
    if not mode:
        pattern = r'([a-z][\w%:@.]*[_:@.%][\w%:@.]*)(?=[,\s\)])(?!\s*\()'
    elif mode == "edifil":
        pattern = r'([a-zA-Z][\w%:@.]*[_:@.%][\w%:@.]*)(?=[,\s\)])(?!\s*\()'
    else:
        raise Exception ("protect_specials ne sait pas traiter le mode {mode}")
    return [ re.sub(pattern, r"'\1'", line, flags=re.IGNORECASE)
             for line in lines ]


def protect_0int(lines, mode=None):
    """ Retourne toutes les lignes reçues après avoir enclos entre ''
        chaque variable qui ressemble à un int mais commence par 0 (ex : 0067).

        :param str() mode      : si l'instruction est une signature (comme le
                                 fait EDIFIL), 'protect_specials' ne protège
                                 pas bien l'instructruction.
                                 => mode permet d'adapter le code...
    """
    pattern = r'([,\(]\s*)(0\d+)\s*(?=[,\)])'
    return [ re.sub(pattern, r"\1'\2'", line) for line in lines ]


def check_fil(filename, lines, oper_c_names, oper_py_names, logger=None):
    """ Vérifie la syntaxe générale du .fil avec AST.

        Lève une exception en cas de problème.

        :param str    filename     : nom du fichier (juste pour message
                                     d'erreur)
        :param list()    lines        : liste de toutes les lignes du .fil.
        :param list()    oper_c_names : liste des noms d'opérateur C.
        :param list()    oper_py_names: liste des noms d'opérateur Python.
        :param logging() logger       : objet de log
    """
    if not logger:
        logger = logging.getLogger(__name__)

    try:
        logger.log(logging.RUN, "check_fil")
    except Exception as e:
        logger.info("==== check_fil : DEBUT")

    ast_fil = Ast_fil()

    nb_err = 0
    protected_dollars  = protect_dollars(lines)
    protected_specials = protect_specials(protected_dollars)
    protected_specials = protect_0int(protected_specials)
    for i, line in enumerate(protected_specials, 1):
        if len(line) > 0 and line[0] != '#' and '$$' in line:
            # ça passe pour :
            # Ech_tps_impos (rft_time_campbel11_%60, ctl_tint_c1_cal_%60, 60., rft_time_REG_%60, $$Arg4.NbVal, ctl_tint_c1_Eti_%60)
            # mais ça ne passera peut-être pas toujours...
            nb_err = nb_err + 1
            logger.error(f"ERREUR DE SYNTAXE ('$$') : {lines[i-1].strip()}")

        try:
            tree = ast.parse(line)
        except SyntaxError as e:
            nb_err = nb_err + 1
            # mettre en concordence le n° de ligne et le nom du fichier
            # dans le message de l'exception
            e.lineno   = i
            e.filename = filename
            logger.error(f"ERREUR DE SYNTAXE : {lines[i-1].strip()}\n--> {e}")
        else:
            ast_fil.visit(tree)

    if nb_err:
        raise Exception (f"{nb_err} erreur(s) de syntaxe à corriger...")


    for fct_name in ast_fil.called_funcs:
        if not fct_name in oper_c_names  and \
           not fct_name in oper_py_names:
            try:
                eval_fct = eval(fct_name)
            except NameError as e:
                nb_err = nb_err + 1
                logger.warning(f"l'opérateur '{fct_name}' est inconnu...")

    if nb_err:
        raise Exception (f"{nb_err} nom(s) d'opérateur à corriger...")


def parse_instruction(instruction, mode=None):
    """ Parse l'instruction ADC ou FVB ou EDIFIL reçue.

        :param str instruction : instruction ADC lue.
        :param str mode        : si l'instruction est une signature (comme le
                                 fait EDIFIL), 'protect_specials' ne protège
                                 pas bien l'instructruction.
                                 => mode permet d'adapter le code...

        :return: oper_name, args_brut, args_opt, args_HDR
        :rtype : str()    , list()   , dict()  , dict()
    """
    # protéger les nom de vecteur, les variable $ etc
    protected_dollars  = protect_dollars([ instruction ])
    protected_specials = protect_specials(protected_dollars, mode)
    protected_specials = protect_0int(protected_specials)

    # faire faire l'analyse par AST
    try:
        tree = ast.parse(protected_specials[0])
    except SyntaxError as e:
        # troncquer la fin du message "(<unknown>, line 1)" qui dérange edifil
        raise Exception(str(e).split('(')[0])

    if not tree.body:
        return None, None, None, None


    # ranger les arguments de la commande selon leur destination
    oper_name = None
    args_brut = list()
    args_opt  = None
    args_HDR  = None
    if type(tree.body[0]) == ast.Expr:

        # opérateur
        oper_name = tree.body[0].value.func.id

        # arguments
        for i, arg in enumerate(tree.body[0].value.args):
            brut = ast.get_source_segment(protected_specials[0], arg)

            # enlever les ' de protection, s'il y en a
            if "'" in brut:
                brut = brut.replace("'", '')

            if mode != 'edifil':
                # supprimer les '0' qui pourraient avoir été donnés
                # devant un int (ex : 0067)
                if brut.isdigit() and brut != '0':
                    brut = brut.lstrip('0')

                # cas amusant où brut = 'x' => x = eval('x') retourne
                # la valeur que x avait au tour précédent.
                x = None

                try:
                    # essayer d'évaluer l'argument permet de faire des calculs
                    # du type Ra/g
                    x = eval(brut)
                    # traitement particulier des Constantes de type list (ex
                    # FSSP300_std_mid_diam)
                    if isinstance(x, list):
                        args_brut.append(x)
                    else:
                        args_brut.append(float(x))
                except ZeroDivisionError as e:
                    print(f"ATTENTION : {brut} : division par 0 => positionné à Nan")
                    args_brut.append(np.nan)
                except Exception as e:
                    args_brut.append(brut)
            else:
                args_brut.append(brut)

        # arguments optionnels
        for i, keyword in enumerate(tree.body[0].value.keywords):
            name = keyword.arg
            x = keyword.value.col_offset
            y = keyword.value.end_col_offset
            # arguments optionnels traités par ADC
            if name.startswith('HDR'):
                if not args_HDR:
                    args_HDR = dict()
                # faire un eval pour récupérer une liste (et non pas une string)
                ### TODO : si protected_specials contient des accents, alors y
                ###        est trop grand de 1 au moins :
                ###        CorFlux_spectral ( trb_cosp_mvt_Moncrieff97_%1800, $Arg1.array_dim, $Arg1.bornes, ctl_FT_Moncrieff_gill_gill_%1800, flx_cov_wu_2D_Eti_%1800 , flx_cov_wu_2D_csp_%1800, ctl_cor_Moncrieff_wu_%1800, DUMMY_FOR_TEST=12, HDR_name=['nom de param1', 'nom de param2'], HDR_english_name=['name of param1', 'name of param2'], HDR_unit=[None, 'Pa'], HDR_SAFIRE_comment=['le capteur a été réparé', 'le capteur a été réparé'])
                args_HDR[name] = eval(protected_specials[0][x:y])
            else:
                if not args_opt:
                    args_opt = dict()
                # faire un eval pour récupérer l'argument dans son type (et non
                # pas sous forme de string)
                args_opt[name] = eval(protected_specials[0][x:y])


    return oper_name, args_brut, args_opt, args_HDR


if __name__ == '__main__':

    # définition d'un logger basic
    #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')
    logger = logging.getLogger(__name__)

    # tests manuels
    line = "number_to_mass_concentration (mic_tabconc_spp300_sync_1, $Arg1.array_dim, FSSP300_std_mid_diam, 2.65, mic_massconc_spp300_sync_1)"
    print(f"\n=== mode = 'edifil', line = >{line}<")
    oper_name, args_brut, args_opt, args_HDR = parse_instruction(line, "edifil")
    print(f"  - oper_name = {oper_name}")
    print(f"  - args_brut = {args_brut}")
    print(f"  - args_opt  = {args_opt}")
    print(f"  - args_HDR  = {args_HDR}")
    input('...[ENTRÉE] pour continuer ')

    line = "number_to_mass_concentration (mic_tabconc_spp300_sync_1, $Arg1.array_dim, FSSP300_std_mid_diam, 2.65, mic_massconc_spp300_sync_1)"
    print(f"\n=== mode = None, line = >{line}<")
    oper_name, args_brut, args_opt, args_HDR = parse_instruction(line)
    print(f"  - oper_name = {oper_name}")
    print(f"  - args_brut = {args_brut}")
    print(f"  - args_opt  = {args_opt}")
    print(f"  - args_HDR  = {args_HDR}")
    input('...[ENTRÉE] pour continuer ')

    line = "pos_sol_mobile_loa(JDA, Time, Lon, Lat, Θ_0, Φ_0, AMU0)"
    print(f"\n=== mode = 'edifil', line = >{line}<")
    oper_name, args_brut, args_opt, args_HDR = parse_instruction(line, "edifil")
    print(f"  - oper_name = {oper_name}")
    print(f"  - args_brut = {args_brut}")
    print(f"  - args_opt  = {args_opt}")
    print(f"  - args_HDR  = {args_HDR}")
    input('...[ENTRÉE] pour continuer ')

    line = "CorFlux_spectral ($Chrono.COSPECTRE, $Arg1.array_dim, $Arg1.bornes, ctl_FT_Moncrieff_gill_gill_%1800,  flx_cov_wu_2D_Eti_%1800 , flx_cov_wu_2D_csp_%1800, ctl_cor_Moncrieff_wu_%1800 )"
    print(f"\n=== mode = 'edifil', line = >{line}<")
    oper_name, args_brut, args_opt, args_HDR = parse_instruction(line, "edifil")
    print(f"  - oper_name = {oper_name}")
    print(f"  - args_brut = {args_brut}")
    print(f"  - args_opt  = {args_opt}")
    print(f"  - args_HDR  = {args_HDR}")
    input('...[ENTRÉE] pour continuer ')

    line = "Test_and_demo ( tpr_sol20cm_c4_cal_%900, pre_TEST_SB2, OPT_val=[21, 22], OPT_dict={'cle1': 31, 'cle2': 32}, OPT_str=True)"
    print(f"\n=== mode = 'edifil', line = >{line}<")
    oper_name, args_brut, args_opt, args_HDR = parse_instruction(line, "edifil")
    print(f"  - oper_name = {oper_name}")
    print(f"  - args_brut = {args_brut}")
    print(f"  - args_opt  = {args_opt}")
    print(f"  - args_HDR  = {args_HDR}")
    input('...[ENTRÉE] pour continuer ')

    line = "Test_and_demo ( tpr_sol20cm_c4_cal_%900, pre_TEST_SB2, OPT_val=[21, 22], OPT_dict={'cle1': 31, 'cle2': 32}, OPT_str=True, OPT_str='ma chaine')"
    print(f"\n=== mode = 'edifil', line = >{line}<")
    try:
        oper_name, args_brut, args_opt, args_HDR = parse_instruction(line, "edifil")
        print(f"  - oper_name = {oper_name}")
        print(f"  - args_brut = {args_brut}")
        print(f"  - args_opt  = {args_opt}")
        print(f"  - args_HDR  = {args_HDR}")
    except Exception as e:
        print(f"ERREUR : {e}")
    input('...[ENTRÉE] pour continuer ')

    line = "Var_Ech(X, R_f, Decal, Toler_mnq, flag, V_x)"
    print(f"\n=== mode = 'edifil', line = >{line}<")
    oper_name, args_brut, args_opt, args_HDR = parse_instruction(line, "edifil")
    print(f"  - oper_name = {oper_name}")
    print(f"  - args_brut = {args_brut}")
    print(f"  - args_opt  = {args_opt}")
    print(f"  - args_HDR  = {args_HDR}")
    input('...[ENTRÉE] pour continuer ')

    in_file = '/tmp/x.fil'
    print(f"\n=== Input : {in_file}")

    # les .fil sont en utf-8 ou en lantin-1...
    try:
        with open(in_file, 'r') as handler:
            lines = handler.readlines()
    except FileNotFoundError:
        print(f"  --> copier un .fil dans : '{in_file}'")
        sys.exit(1)
    except UnicodeDecodeError:
        with open(in_file, 'r', encoding='iso-8859-1') as handler:
            lines = handler.readlines()

    print(f"=== appel de check_fil : {in_file}")
    oper_c_names  = ['Poly_1_flt', 'Correc_pics_mnq', 'Poly_1_dbl', 'Log_flt', 'Hyperb_poly_flt', 'number_to_mass_concentration' ]
    oper_py_names = ['PressAltiVect']#, 'Test_and_demo']
    print( " AVEC")
    print(f" - oper_c_names  = {oper_c_names}")
    print(f" - oper_py_names = {oper_py_names}")

    try:
        check_fil(in_file, lines, oper_c_names, oper_py_names, logger)
    except Exception as e:
        print(f"ERREUR CRITIQUE : {e}")
    else:
        print(f"--> check_fil on {in_file} : pass")
    input('...[ENTRÉE] pour continuer ')

    print(f"\n=== mode = '', appel de parse_instruction : {in_file}")
    for line in lines:
        print(f"\n  --- line = >{line.strip()}<")
        oper_name, args_brut, args_opt, args_HDR = parse_instruction(line)
        print(f"  - oper_name = {oper_name}")
        print(f"  - args_brut = {args_brut}")
        print(f"  - args_opt  = {args_opt}")
        print(f"  - args_HDR  = {args_HDR}")
        input('...[ENTRÉE] pour continuer ')

