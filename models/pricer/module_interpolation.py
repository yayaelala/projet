import pandas as pd
import numpy as np
from datetime import date, timedelta
import datetime as dt

from collections import namedtuple

from dateutil.relativedelta import relativedelta

from horizon.horizon_pricer.models.data.db.db_queries import query_mcl_titre_categorie, query_courbe, query_courbe_range, query_tenors, query_mcl

from horizon.horizon_pricer.models.data.db.helpers.p_factory import add_years, to_date

from horizon.horizon_pricer.models.data.db.db_loading import dbsession



dbs = dbsession()



pd.options.mode.chained_assignment = None  # default='warn'

####     Building Class courbe     #

def courbe_bam_delta(date_initial, date_finale):
    """#spread des tenors entre deux dates
    #objectif -> comparer les ténors de la courbe BAM
    # example format :
    # date_initial = '2016-12-31'
    # date_finale = '2017-12-31'
    """
    df = interpolation_tenors_bam(date_initial)
    dfg = interpolation_tenors_bam(date_finale)
    dg = (dfg['taux']-df['taux'])*100
    df.insert(4, 'taux_final', dfg['taux'])
    df.insert(5, 'spread', dg)

    df['taux'] = df['taux'].apply(lambda x: np.round(x,4))
    df['taux_final'] = df['taux_final'].apply(lambda x: np.round(x,4))
    df['spread'] = df['spread'].apply(lambda x: np.round(x,4))
    return df

def courbe_bam_traite(d):
    df = query_courbe(d, dbs)
    df['m'] = df['date_echeance']-df['date_valeur']
    df['m'] = np.round(df['m'].dt.days,0)
    df['r'] = df['taux'].apply(lambda x: float(x))
    df['m'][0] = 1
    # courbe BAM
    # dg = dict(zip(df['m'], df['r']))
    dg = pd.DataFrame([df['m'], df['r']]).T
    p = dg[dg.m<2]
    g = dg[dg.m>56]
    x = pd.concat([p,g])
    return x

d1 = dt.date(2021, 1, 1)
d2 = dt.date(2021, 6, 21)

date_valeur = dt.date(2019,6,21)

DICO_PERIODE = [
    '13:S',
    '26:S',
    '52:S',
    '1:A',
    '2:A',
    '3:A',
    '4:A',
    '5:A',
    '6:A',
    '7:A',
    '8:A',
    '9:A',
    '10:A',
    '11:A',
    '12:A',
    '13:A',
    '14:A',
    '15:A',
    '16:A',
    '17:A',
    '18:A',
    '19:A',
    '20:A',
    '21:A',
    '22:A',
    '23:A',
    '24:A',
    '25:A',
    '26:A',
    '27:A',
    '28:A',
    '29:A',
    '30:A'
]

######## tenors & volume courbe tools #########

def delta_periode(date, per: str) -> int:
    n, p = per.upper().split(':')
    inum = int(n)
    mapp = {
        'A': 'years',
        'M': 'months',
        'S': 'weeks',
        'D': 'days'
    }
    if p in mapp:
        args = {mapp[p]: inum}
        rv = ((date + relativedelta(**args)) - date).days
    else:
        rv = 0  # ou toute autre valeur par défaut que vous souhaitez
    return rv

def get_tenors(date_valeur):
    list_per = []
    for el in DICO_PERIODE:
        list_per.append(delta_periode(date_valeur,el))
    return list_per

def dico_get_tenors(date_valeur):
    dico_tenors = dico_tenors = {
        '13s': get_tenors(date_valeur)[0],
        '26s': get_tenors(date_valeur)[1],
        '52s': get_tenors(date_valeur)[2],
        '1an': get_tenors(date_valeur)[3],
        '2ans': get_tenors(date_valeur)[4],
        '3ans': get_tenors(date_valeur)[5],
        '4ans': get_tenors(date_valeur)[6],
        '5ans': get_tenors(date_valeur)[7],
        '6ans': get_tenors(date_valeur)[8],
        '7ans': get_tenors(date_valeur)[9],
        '8ans': get_tenors(date_valeur)[10],
        '9ans': get_tenors(date_valeur)[11],
        '10ans': get_tenors(date_valeur)[12],
        '11ans': get_tenors(date_valeur)[13],
        '12ans': get_tenors(date_valeur)[14],
        '13ans': get_tenors(date_valeur)[15],
        '14ans': get_tenors(date_valeur)[16],
        '15ans': get_tenors(date_valeur)[17],
        '16ans': get_tenors(date_valeur)[18],
        '17ans': get_tenors(date_valeur)[19],
        '18ans': get_tenors(date_valeur)[20],
        '19ans': get_tenors(date_valeur)[21],
        '20ans': get_tenors(date_valeur)[22],
        '21ans': get_tenors(date_valeur)[23],
        '22ans': get_tenors(date_valeur)[24],
        '23ans': get_tenors(date_valeur)[25],
        '24ans': get_tenors(date_valeur)[26],
        '25ans': get_tenors(date_valeur)[27],
        '26ans': get_tenors(date_valeur)[28],
        '27ans': get_tenors(date_valeur)[29],
        '28ans': get_tenors(date_valeur)[30],
        '29ans': get_tenors(date_valeur)[31],
        '30ans': get_tenors(date_valeur)[32]
    }
    return dico_tenors

def get_volume_courbe(date_initial, date_finale):
    df = query_courbe_range(date_initial, date_finale, dbs)

    df['date_echeance'] = pd.to_datetime(df['date_echeance'])
    df['date_marche'] = pd.to_datetime(df['date_marche'])
    df['mr'] = (df['date_echeance'] - df['date_marche']).dt.days

    dg = df.drop_duplicates(['date_echeance', 'transactions', 'taux', 'date_valeur'])
    dg['transactions'] = dg['transactions'].str.replace(',', '.').str.replace(' ', '').astype(float)

    dg_volume_global = dg['transactions'].sum()
    dg_volume_par_titre = dg.groupby(['date_echeance'])['transactions'].sum()

    dg.reset_index(drop=True, inplace=True)

    dico_rv = {'volume_global': dg_volume_global,
               'volume_titre': dg_volume_par_titre,
               'traitement_courbe': dg}

    return dico_rv

def get_volume_courbe_strates(date_valeur_tenors, date_initial, date_finale):

    d_mr = dico_get_tenors(date_valeur_tenors)
    dg = get_volume_courbe(date_initial,date_finale)['traitement_courbe']

    rv_13s = dg[(dg['mr'] >= 0) & (dg['mr'] <= d_mr['13s'])].agg({'transactions': [sum]}).values[0][0]
    rv_26s = dg[(dg['mr'] > d_mr['13s']) & (dg['mr'] <= d_mr['26s'])].agg({'transactions': [sum]}).values[0][0]
    rv_52s = dg[(dg['mr'] > d_mr['26s']) & (dg['mr'] <= d_mr['52s'])].agg({'transactions': [sum]}).values[0][0]
    rv_1ans = dg[(dg['mr'] > d_mr['52s']) & (dg['mr'] <= d_mr['1an'])].agg({'transactions': [sum]}).values[0][0]
    rv_2ans = dg[(dg['mr'] > d_mr['1an']) & (dg['mr'] <= d_mr['2ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_3ans = dg[(dg['mr'] > d_mr['2ans']) & (dg['mr'] <= d_mr['3ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_4ans = dg[(dg['mr'] > d_mr['3ans']) & (dg['mr'] <= d_mr['4ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_5ans = dg[(dg['mr'] > d_mr['4ans']) & (dg['mr'] <= d_mr['5ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_6ans = dg[(dg['mr'] > d_mr['5ans']) & (dg['mr'] <= d_mr['6ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_7ans = dg[(dg['mr'] > d_mr['6ans']) & (dg['mr'] <= d_mr['7ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_8ans = dg[(dg['mr'] > d_mr['7ans']) & (dg['mr'] <= d_mr['8ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_9ans = dg[(dg['mr'] > d_mr['8ans']) & (dg['mr'] <= d_mr['9ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_10ans = dg[(dg['mr'] > d_mr['9ans']) & (dg['mr'] <= d_mr['10ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_11ans = dg[(dg['mr'] > d_mr['10ans']) & (dg['mr'] <= d_mr['11ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_12ans = dg[(dg['mr'] > d_mr['11ans']) & (dg['mr'] <= d_mr['12ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_13ans = dg[(dg['mr'] > d_mr['12ans']) & (dg['mr'] <= d_mr['13ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_14ans = dg[(dg['mr'] > d_mr['13ans']) & (dg['mr'] <= d_mr['14ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_15ans = dg[(dg['mr'] > d_mr['14ans']) & (dg['mr'] <= d_mr['15ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_16ans = dg[(dg['mr'] > d_mr['15ans']) & (dg['mr'] <= d_mr['16ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_17ans = dg[(dg['mr'] > d_mr['16ans']) & (dg['mr'] <= d_mr['17ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_18ans = dg[(dg['mr'] > d_mr['17ans']) & (dg['mr'] <= d_mr['18ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_19ans = dg[(dg['mr'] > d_mr['18ans']) & (dg['mr'] <= d_mr['19ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_20ans = dg[(dg['mr'] > d_mr['19ans']) & (dg['mr'] <= d_mr['20ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_21ans = dg[(dg['mr'] > d_mr['20ans']) & (dg['mr'] <= d_mr['21ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_22ans = dg[(dg['mr'] > d_mr['21ans']) & (dg['mr'] <= d_mr['22ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_23ans = dg[(dg['mr'] > d_mr['22ans']) & (dg['mr'] <= d_mr['23ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_24ans = dg[(dg['mr'] > d_mr['23ans']) & (dg['mr'] <= d_mr['24ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_25ans = dg[(dg['mr'] > d_mr['24ans']) & (dg['mr'] <= d_mr['25ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_26ans = dg[(dg['mr'] > d_mr['25ans']) & (dg['mr'] <= d_mr['26ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_27ans = dg[(dg['mr'] > d_mr['26ans']) & (dg['mr'] <= d_mr['27ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_28ans = dg[(dg['mr'] > d_mr['27ans']) & (dg['mr'] <= d_mr['28ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_29ans = dg[(dg['mr'] > d_mr['28ans']) & (dg['mr'] <= d_mr['29ans'])].agg({'transactions': [sum]}).values[0][0]
    rv_30ans = dg[(dg['mr'] > d_mr['29ans']) & (dg['mr'] <= d_mr['30ans'])].agg({'transactions': [sum]}).values[0][0]




    rv = {
      '0-13s': rv_13s,
      '13s-26s': rv_26s,
      '26s-52s': rv_52s,
      '52s-1an': rv_1ans,
      '1-2ans': rv_2ans,
      '2-3ans': rv_3ans,
      '3-4ans': rv_4ans,
      '4-5ans': rv_5ans,
      '5-6ans': rv_6ans,
      '6-7ans': rv_7ans,
      '7-8ans': rv_8ans,
      '8-9ans': rv_9ans,
      '9-10ans': rv_10ans,
      '10-11ans': rv_11ans,
      '11-12ans': rv_12ans,
      '12-13ans': rv_13ans,
      '13-14ans': rv_14ans,
      '14-15ans': rv_15ans,
      '15-16ans': rv_16ans,
      '16-17ans': rv_17ans,
      '17-18ans': rv_18ans,
      '18-19ans': rv_19ans,
      '19-20ans': rv_20ans,
      '20-21ans': rv_21ans,
      '21-22ans': rv_22ans,
      '22-23ans': rv_23ans,
      '23-24ans': rv_24ans,
      '24-25ans': rv_25ans,
      '25-26ans': rv_26ans,
      '26-27ans': rv_27ans,
      '27-28ans': rv_28ans,
      '28-29ans': rv_29ans,
      '29-30ans': rv_30ans
    }
    return rv


########    Interpolation tools     #########

# interpolation monetaire
def interpolation_monetaire(taux, maturite, base_a):
    """
   taux : taux actuariel à monetariser
   base_a : année en cours (366 ou 365)
   maturite : mr
   """
    rv = ((1 + taux)**(maturite / base_a) - 1) * (360 / maturite)
    return rv

# interpolation actuariel
def interpolation_actuariel(taux, maturite, base_a):
    """
   taux : taux monétaire à actiualiser
   base_a : base annuelle année en cours (366 ou 365)
   """
    rv = (1 + (taux * maturite/360))**(base_a / maturite)-1
    #rv = pow(1 + (taux * maturite / 360), base_a / maturite) - 1
    return rv

Point = namedtuple('Point', ['maturite', 'taux'])
# interpolation
def interpolation_courbe_bam(date_courbe, mat_res):
    """ Retun a rate for a given yiled curve and a maturity
    df : query courbe
    d : date courbe
    mat_res : maturités résiduelles
    """
    df = query_courbe(date_courbe, dbs)
    if df.empty == False:
        df['mr'] = df['date_echeance']-df['date_valeur']
        df['mr'] = df['mr'].apply(lambda x: x.days)

        #df['mr'] = df['mr'].dt.days

        m = df['mr']

        df['taux'] = df['taux'].astype(float)
        r = df['taux']
        c = len(m)-1
        m[0] =  1
        r[0] =  r[1]

        courbe = [Point(x[0],x[1]) for x in list(zip(m,r))]

        A = (add_years(date_courbe, 1) - date_courbe)
        A = A.days
        l_A_inf = []

        for x in df['date_valeur']:
            A_inf = (add_years(x, 1) - x)
            A_inf = A_inf.days
            l_A_inf.append(A_inf)

        dico = {}
        ktx, km = 'taux', 'mat_res'

        for i in range(len(m)-1):

            if mat_res < courbe[0].maturite:
                x = (courbe[0].taux * (courbe[1].maturite - mat_res)) - (courbe[1].taux * (courbe[0].maturite - mat_res)) / (courbe[1].maturite - courbe[0].maturite)
                dico[ktx] = x
                dico[km] = mat_res

            elif mat_res >= courbe[c].maturite:
                try:
                    x = ((courbe[c].taux * (mat_res - courbe[c-1].maturite)) - (courbe[c-1].taux*(mat_res - courbe[c].maturite))) / (courbe[c].maturite - courbe[c-1].maturite)
                    dico[ktx] = x
                    dico[km] = mat_res
                except:
                    dico[ktx] = 'x_erreur'
                    dico[km] = 'mat_res_erreur'

            elif (courbe[i].maturite < 365) and (courbe[i+1].maturite >= 365) and (courbe[i].maturite <= mat_res) and (mat_res <= courbe[i+1].maturite):
                if mat_res >= 365:
                    x = (interpolation_actuariel(courbe[i].taux, courbe[i].maturite, A) + ((courbe[i+1].taux - interpolation_actuariel(courbe[i].taux, courbe[i].maturite, A)) * (mat_res - courbe[i].maturite) / (courbe[i+1].maturite - courbe[i].maturite)))
                    dico[ktx] = x
                    dico[km] = mat_res
                else:
                    if mat_res < 365:
                        x = (courbe[i].taux + (interpolation_monetaire(courbe[i+1].taux, courbe[i+1].maturite, A) - courbe[i].taux) * ((mat_res - courbe[i].maturite) / (courbe[i+1].maturite - courbe[i].maturite)))
                        dico[ktx] = x
                        dico[km] = mat_res

            else:
                if (courbe[i].maturite <= mat_res) and (mat_res < courbe[i+1].maturite) and (courbe[i].maturite >= 365 or courbe[i+1].maturite < 365):
                    x = courbe[i].taux + ((courbe[i+1].taux - courbe[i].taux) * (mat_res - courbe[i].maturite)) / (courbe[i+1].maturite - courbe[i].maturite)
                    dico[ktx] = x
                    dico[km] = mat_res
            rv = dico
    else:
        print('courbe inexistante dans la db')
    return rv

# Deductions Tenors
def interpolation_tenors_bam(date_valeur):
    df = query_courbe(date_valeur, dbs)
    list_tenors = list(dico_get_tenors(date_valeur).values())
    lres = {}
    for mr in list_tenors:
        rr = interpolation_courbe_bam(date_valeur, mr)
        lres[mr] = rr['taux']

    y_tenors = list(dico_get_tenors(date_valeur).keys())
    dres = pd.DataFrame([lres])

    df_res = dres.T
    df_res.reset_index(drop=False, inplace=True)

    df_res['years'] = y_tenors
    df_res['date_marche'] = date_valeur

    df_res.columns=['tenors_d','taux','tenors_y', 'date_marche']
    df_res = df_res[['date_marche','tenors_y','tenors_d', 'taux']]
    return df_res

# interpolation zero coupon
def interpolation_courbe_bam_zc(df,d):
    dc = courbe_bam_traite(d)
    # annee en cours
    A = (add_years(d, 1) - d)
    A = A.days
    # courbe tenors
    d_tenors = [91, 182 ,364, 365, 730, 1095, 1460, 1825, 2190, 2555, 2920, 3285, 3650, 4015, 4380, 4745,5110, 5475, 5840, 6205, 6570, 6935, 7300, 7665, 8030, 8396, 8760, 9125, 9490, 9855, 10220, 10585, 10950]
    l = []
    for k in range(len(d_tenors)):
        x = interpolation_courbe_bam(df,d, d_tenors[k])
        #x['taux'] = round(x['taux'], 6)
        l.append(x)

    dc_interp = pd.DataFrame(l)
    dc_interp = dc_interp[['mat_res' , 'taux']]
    dc_interp.columns = ['m' , 'r']

    # Marche secondaire ST == dc_mon / dc_mon_actu
    c_inf_65 = dc[ dc['m'] < 365 ]
    c_eg_65 = dc_interp[ dc_interp['m'] == 365 ]
    dc_mon = c_inf_65.append(c_eg_65)
    dc_mon.reset_index(drop=True, inplace=True)

    # Marche secondaire LT
    c_sup_65 = dc_interp[ dc_interp['m'] > 365 ]
    # dc_actu = c_sup_65

    # interpol actuariel
    x_mon_actu = interpolation_actuariel(dc_mon['r'], dc_mon['m'], A)
    dc_mon_actu = pd.DataFrame({'m': dc_mon['m'], 'r': x_mon_actu})
    last_mon_sup = len(dc_mon_actu['m'])-1

    zc1 = dc_mon['r'][last_mon_sup]
    m_zc1 = dc_mon['m'][last_mon_sup]

    m_zc2 = d_tenors[4]
    r_tenors_zc2 = interpolation_courbe_bam(df, d, m_zc2)

    x1 = 1 + zc1
    x2 = 1 + r_tenors_zc2['taux']
    zc2 = (x1 * x2)**(1/2)-1
    l_zc =[zc1, zc2]
    l_mzc = [m_zc1, m_zc2]

    # extrapole == bootstrap
    f = interpolate.interp1d(l_mzc, l_zc, kind = 'linear', fill_value="extrapolate")

    l_res = []
    for k in range(4,len(d_tenors)):
        l_res.append(f(d_tenors[k]))

    rdf = pd.DataFrame({'m': d_tenors[4:], 'r': l_res})
    final = pd.concat([dc_mon_actu, rdf])
    final['r'] = final['r'].apply(lambda x: np.round(x,5))
    return final

# interpolation_titres_cat
def interpolation_titres_cat(date_valeur, date_courbe, categorie):
    df = query_courbe(date_courbe, dbs)
    titres = query_mcl_titre_categorie(date_valeur,categorie, dbs)

    l = []
    for el in titres['code_isin']:
        l.append(el)
    lres = []
    for el in l:
        x = el[:-1].split('MA000')
        lres.append(x[1])
    #titres['isin'] = lres
    titres.insert(1,'isin', lres)
    # interpolate titres
    titres['date_valeur'] = date_valeur
    titres['maturite_res'] = titres['date_echeance']-titres['date_valeur']
    titres['mat_init'] = titres['date_echeance']-titres['date_emission']
    titres['maturite_res'] = titres['maturite_res'].astype('timedelta64[D]')
    titres['maturite_res'] = titres['maturite_res'].astype(int)

    mat_titre = titres['maturite_res']
    lres_titre = []
    for mr in mat_titre:
        rr = interpolation_courbe_bam(date_courbe, mr)
        lres_titre.append(rr)

    dres_titre = pd.DataFrame(lres_titre)
    titres['taux_courbe'] = dres_titre['taux']

    df_final = pd.DataFrame()
    df_final['date_courbe'] = titres['date_valeur']
    df_final['code_isin'] = titres['isin']
    df_final['taux_facial'] = titres['taux_facial']
    df_final['date_emission'] = titres['date_emission']
    df_final['date_jouissance'] = titres['date_jouissance']
    df_final['date_echeance'] = titres['date_echeance']
    df_final['taux_courbe'] = titres['taux_courbe'].apply(lambda x: round(x,5))
    df_final['maturite_res'] = titres['maturite_res']

    return df_final


def get_list_tenors_sim(date_courbe):
    df = interpolation_tenors_bam(date_courbe)
    l_ty = df['tenors_y']
    l_td = df['tenors_d']
    l_r = df['taux'].apply(lambda x: np.round(x,5))

    res = [[x[0],x[1],x[2]] for x in list(zip(l_ty, l_td, l_r))]

    return res

def interpolation_courbe_tenors_sim(data ,mat_res):
    """ Retun a rate for a given yield curve and a maturity
    df : query courbe
    d : date courbe
    mat_res : maturités résiduelles
    """
    ddata = pd.DataFrame(data, columns=['ty','mr','taux'])

    df = ddata
    m = df['mr']

    df['taux'] = df['taux'].astype(float)
    r = df['taux']
    c = len(m)-1
    m[0] =  1
    r[0] =  r[1]

    date_jour = dt.date.today()

    courbe = [Point(x[0],x[1]) for x in list(zip(m,r))]

    A = (add_years(date_jour, 1) - date_jour)
    A = A.days
    l_A_inf = []

    df = ddata

    m = df['mr'].astype(float)

    df['taux'] = df['taux'].astype(float)
    r = df['taux']
    c = len(m)-1
    m[0] =  1
    r[0] =  r[1]
    date_jour = dt.date.today()
    courbe = [Point(x[0],x[1]) for x in list(zip(m,r))]

    A = (add_years(date_jour, 1) - date_jour)
    A = A.days
    l_A_inf = []

    dico = {}
    ktx, km = 'taux', 'mat_res'

    for i in range(len(m)-1):

        if mat_res < courbe[0].maturite:
            x = (courbe[0].taux * (courbe[1].maturite - mat_res)) - (courbe[1].taux * (courbe[0].maturite - mat_res)) / (courbe[1].maturite - courbe[0].maturite)
            dico[ktx] = x
            dico[km] = mat_res

        elif mat_res >= courbe[c].maturite:
            x = ((courbe[c].taux * (mat_res - courbe[c-1].maturite)) - (courbe[c-1].taux*(mat_res - courbe[c].maturite))) / (courbe[c].maturite - courbe[c-1].maturite)
            dico[ktx] = x
            dico[km] = mat_res

        elif (courbe[i].maturite < 365) and (courbe[i+1].maturite >= 365) and (courbe[i].maturite <= mat_res) and (mat_res <= courbe[i+1].maturite):
            if mat_res >= 365:
                x = (interpolation_actuariel(courbe[i].taux, courbe[i].maturite, A) + ((courbe[i+1].taux - interpolation_actuariel(courbe[i].taux, courbe[i].maturite, A)) * (mat_res - courbe[i].maturite) / (courbe[i+1].maturite - courbe[i].maturite)))
                dico[ktx] = x
                dico[km] = mat_res
            else:
                if mat_res < 365:
                    x = (courbe[i].taux + (interpolation_monetaire(courbe[i+1].taux, courbe[i+1].maturite, A) - courbe[i].taux) * ((mat_res - courbe[i].maturite) / (courbe[i+1].maturite - courbe[i].maturite)))
                    dico[ktx] = x
                    dico[km] = mat_res

        else:
            if (courbe[i].maturite <= mat_res) and (mat_res < courbe[i+1].maturite) and (courbe[i].maturite >= 365 or courbe[i+1].maturite < 365):
                x = courbe[i].taux + ((courbe[i+1].taux - courbe[i].taux) * (mat_res - courbe[i].maturite)) / (courbe[i+1].maturite - courbe[i].maturite)
                dico[ktx] = x
                dico[km] = mat_res
        rv = dico

    else:
        print('courbe inexistante dans la db')
    return rv




