# tracker/urls.py
from django.urls import path
from .views import home
from .views import delete_transaction

urlpatterns = [
    path('', home, name='home'),
    path('delete_transaction/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
]
