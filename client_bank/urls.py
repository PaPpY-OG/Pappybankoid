
from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.loginView, name='client_login'),
    path('signup/',views.signUp, name='client_signUP'),
    # path("",views.cardPurchaseEndpoint),
    # path("profiles/", views.getAllProfile,),
    # path("profile/", views.profilePage, name='client_profile_page'),
    path("logout/",views.Logout_Page, name='Logout'),
    path("transfer/", views.TransferPage, name="client_transfer"),
    path("profile/", views.ProfilePage, name="client_profile"),
    path("pin/", views.PinPage, name="client_pin"),
    path("dash/", views.DashboardPage, name="client_dashboard"),
    path("transactions/", views.TransactionPage, name="client_transactions")
]


# <int:profile_id>/