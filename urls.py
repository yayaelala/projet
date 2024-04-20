from django.urls import path
from .views import notfound, view_home, view_imports, view_login, view_register, view_taux, view_tenors_range

urlpatterns = [
    path('', view_home.my_view, name='view_home'),
    path('import/', view_imports.my_view, name='view_imports'),
    path('login/', view_login.my_view, name='view_login'),
    #path('notfound/', notfound_view, name='notfound'),
    path('register/', view_register.my_view, name='view_register'),
    path('taux/', view_taux.my_view, name='view_taux'),
    path('tenors/', view_tenors_range.my_view, name='view_tenors_range'),

]