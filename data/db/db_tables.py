from sqlalchemy import ( 
    create_engine, Sequence, ForeignKey, MetaData, Column, desc, asc, Date, Integer, String, VARCHAR, Float, Numeric, Text, DateTime, func
)
from sqlalchemy.ext.declarative import declarative_base
from .db_loading import dbsession



Base = declarative_base()

TABLE_ID = Sequence('table_id_seq', start = 1)
TABLE_ID_bkamcourbetenors = Sequence('table_id_bkamcourbetenors_seq', start=1)
TABLE_ID_mcl_VF = Sequence ('table_id_mcl_VF_seq', start = 1)
TABLE_ID_portefeuille = Sequence ('table_id_ptf', start = 1)
TABLE_ID_titre = Sequence ('table_id_titre', start = 1)


class BkamCourbe(Base):

    __tablename__ = 'bkam_courbe'

    id = Column(Integer, TABLE_ID, primary_key=True, server_default=TABLE_ID.next_value())
    date_marche = Column(Date)
    date_echeance = Column(Date)
    transactions = Column(VARCHAR)
    taux = Column(Float)
    date_valeur = Column(Date)
    date_transaction = Column(Date)

    def __init__(self, date_marche, date_echeance, transactions, taux, date_valeur,date_transaction):
        self.date_marche=date_marche
        self.date_echeance=date_echeance
        self.transactions=transactions
        self.taux=taux
        self.date_valeur=date_valeur
        self.date_transaction=date_transaction

    def __repr__(self):
        return '[id:%d][date_marche:%s]' % self.id, self.date_marche



class BkamCourbeTenors(Base):

    __tablename__ = 'bkam_courbe_tenors'

    id = Column(Integer, TABLE_ID_bkamcourbetenors, primary_key=True, server_default=TABLE_ID_bkamcourbetenors.next_value())
    date_marche = Column(Date)
    tenors_y = Column(VARCHAR)
    tenors_d = Column(Integer)
    taux = Column(Float)

    def __init__(self, date_marche, tenors_y, tenors_d, taux):
        self.date_marche=date_marche
        self.tenors_y=tenors_y
        self.tenors_d=tenors_d
        self.taux=taux

    def __repr__(self):
        return '[id:%d][date_marche:%s]' % self.id, self.date_marche
    



class Mcl(Base):

    __tablename__ = 'mcl'

    id = Column(Integer, TABLE_ID_mcl_VF, primary_key=True, server_default=TABLE_ID_mcl_VF.next_value())
    code_isin = Column(VARCHAR)
    famille_instrument = Column(VARCHAR)
    categorie_instrument = Column(VARCHAR)
    libelle_court = Column(VARCHAR)
    description = Column(VARCHAR)
    isin_emetteur = Column(VARCHAR)
    capital_emis = Column(VARCHAR)
    qt_emise = Column(VARCHAR)
    nominal = Column(Float)
    taux_facial = Column(VARCHAR)
    type_coupon = Column(VARCHAR)
    date_emission = Column(Date)
    date_jouissance = Column(Date)
    date_echeance = Column(Date)
    garantie = Column(VARCHAR)
    nominal_actuel = Column(Float)
    periodicite = Column(VARCHAR)
    type_remboursement = Column(VARCHAR)
    periodicite_amortissement = Column(VARCHAR)
    forme_detention = Column(VARCHAR)
    cote = Column(VARCHAR)
    mnemonique = Column(VARCHAR)
    isin_centralisateur = Column(VARCHAR)
    nom_emetteur = Column(VARCHAR)
    code_enregistrement = Column(VARCHAR)
    dates_coupons = Column(VARCHAR)
    statut_instrument = Column(VARCHAR)


class Portefeuille(Base):
    __tablename__ = 'portefeuille'

    id = Column(Integer, TABLE_ID_portefeuille, primary_key=True, server_default = TABLE_ID_portefeuille.next_value())
    nom = Column(String(100))
    description = Column(Text)

    def __repr__(self):
        return f"<Portefeuille(id={self.id}, nom='{self.nom}')>"
    

class Titre(Base):
    __tablename__ = 'titre'

    id = Column(Integer, TABLE_ID_titre, primary_key=True, server_default = TABLE_ID_titre.next_value())
    portefeuille_id = Column(Integer, ForeignKey('portefeuille.id'))
    code_isin = Column(String(100))
    nom_emetteur = Column(VARCHAR)
    famille_instrument = Column(VARCHAR)
    qt_emise = Column(VARCHAR)
    qt_ajoute = Column(VARCHAR)

    def __repr__(self):
        return f"<Titre(id={self.id}, isin='{self.isin}')>"
    
