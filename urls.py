from django.urls import path
from .views import view_home,view_pentes, view_tenors_range,view_imports, view_operation,view_login,view_portefeuille, view_register, view_Mcl,view_pricer, view_taux, view_tenors

urlpatterns = [
    path('home/', view_home.my_view, name='view_home'),
    path('import/', view_imports.my_view, name='view_imports'),
    path('', view_login.login, name='view_login'),
    path('register/', view_register.my_view, name='view_register'),
    path('taux/', view_taux.my_view, name='view_taux'),  
    path('tenors/', view_tenors.my_view, name='view_tenors'),
    path('tenors_range/', view_tenors_range.my_view, name='view_tenors_range'),
    path('pentes/', view_pentes.my_view, name='view_pentes'),
    path('mcl/', view_Mcl.my_view, name='view_Mcl'),
    path('pricer/', view_pricer.my_view, name='view_pricer'),
    path('portefeuille/creer/', view_portefeuille.creer_portefeuille, name='creer_portefeuille'),
    path('portefeuille/liste/', view_portefeuille.liste_portefeuilles, name='liste_portefeuilles'),
    path('portefeuille/details/<int:portefeuille_id>/', view_portefeuille.details_portefeuille, name='details_portefeuille'),
    path('portefeuille/ajouter_titre/<int:portefeuille_id>/', view_portefeuille.ajouter_titre, name='ajouter_titre2'),
    path('operation/', view_operation.my_view, name='view_operation'),  
    
]