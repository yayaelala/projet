import datetime as dt

from horizon.horizon_pricer.models.data.db.db_loading import dbsession

from horizon.horizon_pricer.models.data.db.db_tables import Mcl, MasiComposition, MasiIndices

from horizon.horizon_pricer.models.data.db.db_queries import query_mcl, query_titre_all, query_masi_composition, query_masi_volume, query_cours_valeurs_cm, query_masi_indice, query_masi_indice_name

from horizon.horizon_pricer.models.pricer.module_interpolation import *

from horizon.horizon_pricer.models.pricer.module_pricing import *


dbs = dbsession()


def titres_traitement_all():
    df = pd.DataFrame(query_titre_all(dbs), columns=query_titre_all(dbs)[0].keys())
    titres = df

    titres['date_emission'] = titres['date_emission'].apply(lambda x: to_date(str(x)))
    titres['date_jouissance'] = titres['date_jouissance'].apply(lambda x: to_date(str(x)))
    titres['date_echeance'] = titres['date_echeance'].apply(lambda x: to_date(str(x)))
    titres['taux_facial'] = titres['taux_facial'].astype(float)
    titres['nominal'] = titres['nominal'].astype(int)

    return titres


def titres_all_new_isin(isi):

    titres = titres_traitement_all()

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


def titres_all_isin():
    titres = titres_traitement_all()

    l = []
    for el in titres['code_isin']:
        l.append(el)

    lres = []

    for el in l:
        x = el[:-1].split('MA000')
        lres.append(x[1])

    titres.insert(1,'isin', lres)

    res = titres

    if len(res.index) == 0:
        print(f'####### {isi} do not exist #######')

    return res