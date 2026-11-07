from django.contrib.auth import views as auth
from django.urls import path
from . import views as v

urlpatterns = [
    path("", v.home, name="home"),
    path("p/<slug:slug>/", v.place_detail, name="place_detail"),
    path("p/<slug:slug>/qr.svg", v.place_qr, name="place_qr"),
    path("signup/", v.signup, name="signup"),
    path("login/", auth.LoginView.as_view(), name="login"),
    path("logout/", auth.LogoutView.as_view(), name="logout"),
    path("dashboard/", v.dashboard, name="dashboard"),
    path("dashboard/new/", v.place_create, name="place_create"),
    path("dashboard/<slug:slug>/", v.manage_place, name="manage_place"),
    path("dashboard/<slug:slug>/item/new/", v.item_edit, name="item_new"),
    path("dashboard/<slug:slug>/item/<int:pk>/", v.item_edit, name="item_edit"),
    path("dashboard/<slug:slug>/item/<int:pk>/toggle/", v.item_toggle, name="item_toggle"),
    path("dashboard/<slug:slug>/item/<int:pk>/delete/", v.item_delete, name="item_delete"),
]
