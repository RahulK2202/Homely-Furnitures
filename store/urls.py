from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# app_name="store"
urlpatterns = [
    path('category/', views.category, name='category'),
    path('category/<int:pid>/', views.category, name='category_with_id'),

    path('search/',views.search,name="search"),

]
