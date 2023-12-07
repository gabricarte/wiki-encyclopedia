from django.urls import path

from . import views

app_name = "encyclopedia" 

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("search/", views.search, name="search_results"),
    path("add/", views.add, name="add"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random/", views.random_entry, name="random") 
]

