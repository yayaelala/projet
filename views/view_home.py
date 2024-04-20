from django.shortcuts import render
from django.http import HttpResponseServerError
from sqlalchemy.exc import SQLAlchemyError
from horizon_pricer.models.data.db.db_tables import *
from horizon_pricer.models.data.db.db_queries import *
from horizon_pricer.models.data.db.db_loading import *

def my_view(request):

    dbs = dbsession()

    try:
        # Utilisez la session dbs pour interagir avec la base de données
        # par exemple :
        # tenors = dbs.query(BkamCourbeTenors).all()

        # Pour cet exemple, je vais simplement créer un dictionnaire
        # comme dans votre code original
        one = {'title': 'Hello Master', 'SudoUser': 'Yahya'}

    except SQLAlchemyError:
        db_err_msg = """
        Django has encountered an issue with your SQL database. The problem
        might be caused by one of the following things:

        1. You may need to initialize your database tables with `alembic`.
           Check your README.txt for descriptions and try to run it.

        2. Your database server may not be running. Check that the
           database server referred to by the "sqlalchemy.url" setting in
           your configuration is running.

        After you fix the problem, please restart your Django application to
        try it again.
        """
        return HttpResponseServerError(db_err_msg, content_type='text/plain')

    return render(request, 'template_home.jinja2', {'one': one})
