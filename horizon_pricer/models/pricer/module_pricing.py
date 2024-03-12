import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta

from horizon.horizon_pricer.models.pricer.module_interpolation import *

from horizon.horizon_pricer.models.data.db.db_queries import query_mcl_titre_categorie, query_courbe, query_mcl_dataframe

from horizon.horizon_pricer.models.data.db.helpers.p_factory import add_years

from horizon.horizon_pricer.models.data.db.db_loading import dbsession


dbs = dbsession()



#######    get titres tools     #########

def titres_traitement():
    titres = query_mcl_dataframe(dbs)

    # titres['date_emission'] = titres['date_emission'].apply(lambda x: to_date(x))
    # titres['date_jouissance'] = titres['date_jouissance'].apply(lambda x: to_date(x))
    # titres['date_echeance'] = titres['date_echeance'].apply(lambda x: to_date(x))
    titres['taux_facial'] = titres['taux_facial'].astype(float)
    titres['nominal'] = titres['nominal'].astype(int)

    return titres

def titres_isin(isi):

    titres = titres_traitement()
    #    titres['date_emission'] = titres['date_emission'].values
    #    titres['date_jouissance'] = titres['date_jouissance'].values
    #    titres['date_echeance'] = titres['date_echeance'].values
    #    titres['taux_facial'] = titres['taux_facial'].values
    #    titres['nominal'] = titres['nominal'].astype(int)

    l = []
    for el in titres['code_isin']:
        l.append(el)

    lres = []

    for el in l:
        x = el[:-1].split('MA000')
        lres.append(x[1])

    titres.insert(1,'isin', lres)

    res = titres[titres['isin'] == isi]

    if len(res.index) == 0:
        print(f'####### {isi} do not exist #######')

    return res
    

def titres_isin_cat_all(date_valeur, categorie):
    df = query_mcl_titre_categorie(date_valeur, categorie, dbs)
    l_isin = [x[-7:-1] for x in df['code_isin']]
    df['isin'] = l_isin
    rv = df
    return rv

def get_type_titre(isin, date_valeur):
    dtitre = titres_isin(isin)
    if dtitre.empty == False:
        de = dtitre['date_emission'].values[0]
        dj = dtitre['date_jouissance'].values[0]
        dm = dtitre['date_echeance'].values[0]

        mi = dm - de
        mr = dm-date_valeur
        mi = mi.days
        mr = mr.days

        d1c = coupon_premier(date_valeur, dj, dm)
       
        if (de.day != dj.day or de.month != dj.month) or (de.day != dj.day and de.month == dj.month):
            rv = 'Atypiquenormale a n flux'
        elif de == dj and (de.day == dm.day and de.month == dm.month):
            rv = 'Obl ordinaire'
        elif d1c == dm:
            rv = 'Atypique a un flux'
        else:
            rv = 'Obl ordinaire'
    else:
        rv = f'titre {isin} nexiste pas'
    return rv


########    get coupon tools     #########

def coupon_premier(date_valeur, date_jouissance, date_echeance):
    cprem = date_jouissance

    while (cprem <= date_valeur) or (cprem <= date_jouissance):
        cprem = add_years(cprem, 1)
        coupon_premier = cprem
        coupon_premier = cprem
    if cprem > date_jouissance:
            cprem = date_jouissance
            coupon_premier = add_years(cprem, 1)
    return coupon_premier

def coupon_suivant(date_valeur, date_jouissance, date_echeance):
    cs = date_jouissance

    while (cs <= date_valeur) or (cs <= date_jouissance):
        cs = add_years(cs, 1)
        coupon_suivant = cs
    if cs > date_echeance:
        cs = date_echeance
    coupon_suivant = cs

    return coupon_suivant

def coupon_precedent(date_valeur,date_emission, date_jouissance, date_echeance):
    cp = date_jouissance

    while (cp <= date_valeur):
        cp = add_years(cp, 1)
        coupon_precedent = add_years(cp, -1)

    if date_valeur == date_echeance:
        coupon_precedent = date_echeance

    if date_emission != date_jouissance:
        if date_valeur < add_years(date_jouissance,1):
            cp = date_emission
            coupon_precedent = cp

    return coupon_precedent

def coupon_couru(date_valeur, date_emission, date_jouissance, date_echeance, taux_facial, Nominal):
    cp = coupon_precedent(date_valeur, date_emission, date_jouissance, date_echeance)
    A = add_years(cp,1)-cp
    if date_valeur < date_echeance:
        cc = taux_facial * Nominal * (date_valeur - cp)/(A)
    else:
        cc = taux_facial * Nominal * (date_valeur - cp)/365
    return cc

########    pricing tools     #########

def price_oblig_fixe(date_valeur,type_titre,isin,taux_courbe,taux_facial, Nominal,date_emission,date_jouissance,date_echeance,mat_init,mat_res, date_premier_coupon, cp, cs):
    dico = {}
    ktx, kp = 'taux', 'price'

    A = (add_years(cp,1)-cp).days
    taux_courbe = np.round(taux_courbe, 5)

    # Evalutaion des titres de Maturité initiale inférieure a 1 an
    if mat_init < 366 :
        price = Nominal * (1 + taux_facial * mat_init / 360) / (1 + taux_courbe * mat_res / 360)
        dico[ktx] = taux_courbe
        dico[kp] = price

    # Evalutaion des titres de Maturité initiale Supérieure a 1 an
    if mat_init > 365 :
        #    ' Maturité résiduelle inférieure a 1 an
        #    ' Cas de ligne postérieure a un flux
        if mat_res < 366 :
            if (type_titre == "Atypiquenormale a n flux" and date_valeur <= date_premier_coupon) or type_titre == "Atypique a un flux" :
                price = Nominal * (1 + taux_facial * mat_init / A) / (1 + taux_courbe * mat_res / 360)
                dico[ktx] = taux_courbe
                dico[kp] = price
            else:
                price = Nominal * (1 + taux_facial) / (1 + taux_courbe * mat_res / 360)
                dico[ktx] = taux_courbe
                dico[kp] = price

        #  Maturité résiduelle supérieure a 1 an
        if mat_res >= 365 :
            if date_valeur == cp :
                b = 366.1
            else:
                b = 365.25

            #  Calcul du nombre de coupons a venir
            Nombre_coupon = int(mat_res / b) + 1
            # Nombre de jours restant a courir jusqu'au prochain coupon
            Nombre_jour = (cs - date_valeur).days

            if (type_titre == "Obl ordinaire") or (type_titre == "Atypiquenormale a n flux" and date_valeur >= date_premier_coupon) :
                s = 0
                for j in range(1, Nombre_coupon + 1):
                    s = s + taux_facial / (1 + taux_courbe)**(j - 1)

                price = Nominal / ((1 + taux_courbe) ** (Nombre_jour / A)) * (s + 1 / (1 + taux_courbe) ** (Nombre_coupon - 1))

                dico[ktx] = taux_courbe
                dico[kp] = price

                        #           ' Cas d'une ligne postérieure a plusieurs flux
            if type_titre == "Atypiquenormale a n flux" and date_valeur < date_premier_coupon:
                if date_valeur <= date_jouissance :
                    Nombre_coupon = Nombre_coupon - 1
                s = 0
                for j in range(2, Nombre_coupon + 1):
                    s = s + taux_facial / (1 + taux_courbe)**(j - 1)

                price = Nominal / ((1 + taux_courbe)**(Nombre_jour / A)) * (taux_facial * (date_premier_coupon-date_emission).days / A + s + 1 / (1 + taux_courbe)**(Nombre_coupon - 1))
                dico[ktx] = taux_courbe
                dico[kp] = price

            if type_titre == "Atypiquefinale":
                suiv = date_jouissance
                while suiv < date_echeance:
                    avant_dernier = suiv
                    coupon_suivant(suiv, suiv, date_echeance, suiv)
                dernier_coupon = (date_echeance-avant_dernier).days
                coupon_precedent(avant_dernier, date_echeance, prec)
                annee_fin = (date_echeance-prec).days
                if dernier_coupon < 366 :
                    dernier_coupon = dernier_coupon + annee_fin
                s = 0
                for j in range(Nombre_coupon - 1):
                    s = s + taux_facial / (1 + taux_courbe) ** (j - 1)
                price = Nominal / ((1 + taux_courbe) ** (Nombre_jour / A)) * (s + (taux_facial * dernier_coupon / annee_fin + 1) / (1 + taux_courbe) ** (Nombre_coupon - 2 + dernier_coupon / annee_fin))
                dico[ktx] = taux_courbe
                dico[kp] = price

            #           ' Cas de ligne postérieure a un seul flux
            if type_titre == "Atypique a un flux" :
                price = Nominal * (1 + taux_facial * mat_init / A) / (1 + taux_courbe)**(Nombre_jour / A)
                dico[ktx] = taux_courbe
                dico[kp] = price
    return dico

def price_all_isin(isin, date_courbe, date_valeur):

    dtitre = titres_isin(isin)
    if dtitre.empty == False:
        try:
            tytitre = get_type_titre(isin, date_valeur)
            de = dtitre['date_emission'].values[0]
            dj = dtitre['date_jouissance'].values[0]
            dm = dtitre['date_echeance'].values[0]
            tf = dtitre['taux_facial'].values[0]
            tf =float(tf)/100
            nominal = dtitre['nominal'].values[0]
            nominal = int(nominal)

            mi = dm - de
            mr = dm-date_valeur
            mi = mi.days
            mr = mr.days

            d1c = coupon_premier(date_valeur, dj, dm)
            dcs = coupon_suivant(date_valeur, dj, dm)
            dcp = coupon_precedent(date_valeur, de, dj, dm)
            cc = coupon_couru(date_valeur, de, dj, dm, tf,nominal)
            if query_courbe(date_courbe, dbs).empty == False:
                tr = interpolation_courbe_bam(date_courbe, mr)
                p = price_oblig_fixe(date_valeur,
                    tytitre,
                    'isin',
                    tr['taux'], tf,
                    nominal,
                    de, dj, dm,
                    mi, mr,
                    d1c, dcp, dcs)

                dico = {
                    'isin': isin,
                    'nominal': nominal,
                    'date_emission': de,
                    'date_jouissance': dj,
                    'date_echeance': dm,
                    'date_valeur': date_valeur,
                    'date_premier_coupon': d1c,
                    'date_coupon_precedant': dcp,
                    'date_coupon_suivant': dcs,
                    'taux_facial': tf,
                    'coupon_couru': cc,
                    'type_ligne':get_type_titre(isin,date_valeur),
                    'mat_init':mi,
                    'mat_res': mr,
                    'taux_courbe': np.round(tr['taux'],5),
                    'prix': np.round(p['price'],2)
                }
            else:
                print(f'courbe {date_courbe} inexistante')
        except:
            dico = f'titre {isin} inexistant'
    return dico

def price_all_isin_tr_change(isin, date_valeur, xtaux_courbe):

    dtitre = titres_isin(isin)
    if dtitre.empty == False:
        try:
            tytitre = get_type_titre(isin, date_valeur)
            de = dtitre['date_emission'].values[0]
            dj = dtitre['date_jouissance'].values[0]
            dm = dtitre['date_echeance'].values[0]
            tf = dtitre['taux_facial'].values[0]
            tf =float(tf)/100
            nominal = dtitre['nominal'].values[0]
            nominal = int(nominal)

            mi = dm - de
            mr = dm-date_valeur
            mi = mi.days
            mr = mr.days

            d1c = coupon_premier(date_valeur, dj, dm)
            dcs = coupon_suivant(date_valeur, dj, dm)
            dcp = coupon_precedent(date_valeur, de, dj, dm)
            cc = coupon_couru(date_valeur, de, dj, dm, tf,nominal)

            p = price_oblig_fixe(date_valeur,
                tytitre,
                'isin',
                float(xtaux_courbe), tf,
                nominal,
                de, dj, dm,
                mi, mr,
                d1c, dcp, dcs)

            dico = {
                'isin': isin,
                'nominal': nominal,
                'date_emission': de,
                'date_jouissance': dj,
                'date_echeance': dm,
                'date_valeur': date_valeur,
                'date_premier_coupon': d1c,
                'date_coupon_precedant': dcp,
                'date_coupon_suivant': dcs,
                'taux_facial': tf,
                'coupon_couru': cc,
                'type_ligne':get_type_titre(isin,date_valeur),
                'mat_init':mi,
                'mat_res': mr,
                'taux_courbe': np.round(xtaux_courbe,5),
                'prix': np.round(p['price'],2)
            }
        except:
            dico = f'titre {isin} inexistant'
    return dico



def greeks(isin, date_valeur, xtaux_courbe):

    Pactuariel = price_all_isin_tr_change(isin, date_valeur, xtaux_courbe)['prix']
    Pbaisse = price_all_isin_tr_change(isin, date_valeur, xtaux_courbe-0.001)['prix']
    Phausse = price_all_isin_tr_change(isin, date_valeur, xtaux_courbe+0.001)['prix']

    s = 500 / Pactuariel * (Pbaisse - Phausse)

    d = s * (1 + xtaux_courbe)

    c = (Pbaisse + Phausse - 2 * Pactuariel) / 250*(Pactuariel * 0.0001 ** 2)

    dico_greeks = {'sensibilite':s, 'duration':d,'convexite':c}
    return dico_greeks


