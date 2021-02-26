from django.urls import path
from accounts.views import IncreaseCounter,LoginAccount,GetAccounts,LoginTigraAdmin

urlpatterns = [
    path("visits/<phone>/", IncreaseCounter.as_view(), name="Increase"),
    path("login/",LoginAccount.as_view(),name="Login"),
    path("get_accounts/",GetAccounts.as_view(),name="GetAccounts"),
    path("admin-login/",LoginTigraAdmin.as_view(),name="LoginTigraAdmin")
]