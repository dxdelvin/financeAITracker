# tracker/urls.py
from django.urls import path
from .views import home, reports
from .views import delete_transaction

urlpatterns = [
    path('', home, name='home'),
    path('reports/', reports, name='reports'),
    path('delete_transaction/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
]
