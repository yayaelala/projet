import pandas as pd
from .db_loading import dbsession
from .db_tables import *
#from horizon.horizon_pricer.models.data.db.helpers.p_factory import format 

dbs = dbsession()



# ----------------------------------------------------------------
#   Functions marché secondaire
#
#  1 Function titre
# ------------------------
def query_titre_all(session):
    quer = dbs.query(Mcl.code_isin,
        Mcl.famille_instrument,
        Mcl.categorie_instrument,
        Mcl.libelle_court,
        Mcl.description,
        Mcl.isin_emetteur,
        Mcl.capital_emis,
        Mcl.qt_emise,
        Mcl.nominal,
        Mcl.taux_facial,
        Mcl.type_coupon,
        Mcl.date_emission,
        Mcl.date_jouissance,
        Mcl.date_echeance,
        Mcl.garantie,
        Mcl.nominal_actuel,
        Mcl.periodicite,
        Mcl.type_remboursement,
        Mcl.periodicite_amortissement,
        Mcl.forme_detention,
        Mcl.cote,
        Mcl.mnemonique,
        Mcl.isin_centralisateur,
        Mcl.nom_emetteur,
        Mcl.code_enregistrement,
        Mcl.dates_coupons,
        Mcl.statut_instrument
        )

    dquer = pd.read_sql(quer.statement, quer.session.bind)
    return dquer

def query_mcl(session):
    quer = dbs.query(
        Mcl.code_isin,
        Mcl.nom_emetteur,
        Mcl.famille_instrument,
        Mcl.capital_emis,
        Mcl.qt_emise,
        Mcl.taux_facial,
        Mcl.date_emission,
        Mcl.date_jouissance,
        Mcl.date_echeance,
        Mcl.nominal,
        Mcl.nominal_actuel,
        Mcl.garantie,
        Mcl.dates_coupons,
        Mcl.type_coupon,
        Mcl.periodicite,
        Mcl.type_remboursement,
        Mcl.periodicite_amortissement,
        Mcl.cote)
    # dquer = quer.all()
    dquer = pd.read_sql(quer.statement, quer.session.bind)
    return quer

def query_mcl_dataframe(session):
    """
    Récupère des données spécifiques de la table Maroclear liées aux titres.
    """
    quer = dbs.query(
        Mcl.code_isin,
        Mcl.nom_emetteur,
        Mcl.famille_instrument,
        Mcl.capital_emis,
        Mcl.qt_emise,
        Mcl.taux_facial,
        Mcl.date_emission,
        Mcl.date_jouissance,
        Mcl.date_echeance,
        Mcl.nominal,
        Mcl.nominal_actuel,
        Mcl.garantie,
        Mcl.dates_coupons,
        Mcl.type_coupon,
        Mcl.periodicite,
        Mcl.type_remboursement,
        Mcl.periodicite_amortissement,
        Mcl.cote)
    dquer = pd.read_sql(quer.statement, quer.session.bind)
    return dquer


def query_mcl_titre(datem, session):
    """
    comment:
    """
    quer = dbs.query(
        Mcl.code_isin,
        Mcl.nom_emetteur,
        Mcl.famille_instrument,
        Mcl.capital_emis,
        Mcl.qt_emise,
        Mcl.taux_facial,
        Mcl.date_emission,
        Mcl.date_jouissance,
        Mcl.date_echeance,
        Mcl.nominal,
        Mcl.nominal_actuel,
        Mcl.garantie,
        Mcl.dates_coupons,
        Mcl.type_coupon,
        Mcl.periodicite,
        Mcl.type_remboursement,
        Mcl.periodicite_amortissement
        ).filter(Mcl.date_echeance >= datem)
    # dquer = quer.all()
    dquer = pd.read_sql(quer.statement, quer.session.bind)
    return quer

def query_mcl_titre_categorie(datem, categorie, session):
    """
    comment:
    """
    quer = dbs.query(
        Mcl.code_isin,
        Mcl.nom_emetteur,
        Mcl.categorie_instrument,
        Mcl.famille_instrument,
        Mcl.capital_emis,
        Mcl.qt_emise,
        Mcl.taux_facial,
        Mcl.date_emission,
        Mcl.date_jouissance,
        Mcl.date_echeance,
        Mcl.nominal,
        Mcl.nominal_actuel,
        Mcl.garantie,
        Mcl.dates_coupons,
        Mcl.type_coupon,
        Mcl.periodicite,
        Mcl.type_remboursement,
        Mcl.periodicite_amortissement
        ).filter(Mcl.date_echeance >= datem,
        Mcl.categorie_instrument == categorie)
    # dquer = quer.all()
    dquer = pd.read_sql(quer.statement, quer.session.bind)
    return quer
#
#
#  2 Function courbe
# ------------------------

def query_tenors(datem, session):
    datem = pd.to_datetime(datem)
    quer = session.query(
        BkamCourbeTenors.date_marche,
        BkamCourbeTenors.tenors_y,
        BkamCourbeTenors.tenors_d,
        BkamCourbeTenors.taux
    ).filter(
        BkamCourbeTenors.date_marche == datem
    ).order_by(
        asc(BkamCourbeTenors.date_marche),
        asc(BkamCourbeTenors.tenors_d)
    ).all()
    return quer

import pandas as pd

def query_tenorrs(datem, session):
    datem = pd.to_datetime(datem)
    quer = session.query(
        BkamCourbeTenors.date_marche,
        BkamCourbeTenors.tenors_y,
        BkamCourbeTenors.tenors_d,
        (BkamCourbeTenors.taux * 100).label('taux')  # Multiplication par 100
    ).filter(
        BkamCourbeTenors.date_marche == datem
    ).order_by(
        asc(BkamCourbeTenors.date_marche),
        asc(BkamCourbeTenors.tenors_d)
    ).all()
    
    # Conversion du résultat de la requête en liste de dictionnaires
    quer_dicts = [{column: getattr(row, column) for column in row._fields} for row in quer]
    
    return quer_dicts


import pandas as pd
from sqlalchemy import asc

def query_tenors_range(date_start, date_end, session):
    date_start = pd.to_datetime(date_start)
    date_end = pd.to_datetime(date_end)
    quer = session.query(
        BkamCourbeTenors.date_marche,
        BkamCourbeTenors.tenors_y,
        BkamCourbeTenors.tenors_d,
        (BkamCourbeTenors.taux * 100).label('taux')  # Adjusted line
    ).filter(
        BkamCourbeTenors.date_marche >= date_start,
        BkamCourbeTenors.date_marche <= date_end
    ).order_by(
        asc(BkamCourbeTenors.date_marche),
        asc(BkamCourbeTenors.tenors_d)
    ).all()
    #dquer = pd.read_sql(quer.statement, quer.session.bind)
    return quer

def query_courbe(datem, session):
    #datem = pd.to_datetime(datem)
    quer = dbs.query(
        BkamCourbe.date_marche,
        BkamCourbe.date_echeance,
        BkamCourbe.transactions,
        BkamCourbe.taux,
        BkamCourbe.date_valeur,
        BkamCourbe.date_transaction
        ).filter(BkamCourbe.date_marche == datem).order_by(asc(BkamCourbe.date_echeance))
    # dquer = quer.all()
    dquer = pd.read_sql(quer.statement, quer.session.bind)
    return dquer

def query_courbe_range(date_initiale, date_finale, session):
    """ 
    pour importation de la BkamCourbe entre deux dates
    """
    quer = dbs.query(
        BkamCourbe.date_marche,
        BkamCourbe.date_echeance,
        BkamCourbe.transactions,
        BkamCourbe.taux,
        BkamCourbe.date_valeur,
        BkamCourbe.date_transaction
        ).filter(BkamCourbe.date_marche >= date_initiale,
        BkamCourbe.date_marche <= date_finale
        ).order_by(asc(BkamCourbe.date_marche))
    dquer = pd.read_sql(quer.statement, quer.session.bind)
    return dquer


def query_portefeuille(session):
    quer = session.query(
        Portefeuille.id,
        Portefeuille.nom,
        Portefeuille.description,
    )
    dquer = quer.all()
    return dquer

def query_titres(session, portefeuille_id):
    query = session.query(
        Titre.code_isin,
        Titre.nom_emetteur,
        Titre.famille_instrument,
        Titre.qt_emise,
        Titre.qt_ajoute,
    ).filter_by(portefeuille_id=portefeuille_id)
    dquer = query.all()
    return dquer



