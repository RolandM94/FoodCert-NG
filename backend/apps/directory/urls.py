from django.urls import path

from apps.directory.views import (
    BranchDirectoryDetailView,
    BranchDirectoryView,
    EmployerDirectoryDetailView,
    EmployerDirectoryView,
    FoodHandlerDirectoryDetailView,
    FoodHandlerDirectoryView,
    GlobalSearchView,
)

urlpatterns = [
    path("directory/food-handlers/", FoodHandlerDirectoryView.as_view(), name="directory-food-handlers"),
    path("directory/food-handlers/<uuid:pk>/", FoodHandlerDirectoryDetailView.as_view(), name="directory-food-handler-detail"),
    path("directory/employers/", EmployerDirectoryView.as_view(), name="directory-employers"),
    path("directory/employers/<uuid:pk>/", EmployerDirectoryDetailView.as_view(), name="directory-employer-detail"),
    path("directory/branches/", BranchDirectoryView.as_view(), name="directory-branches"),
    path("directory/branches/<uuid:pk>/", BranchDirectoryDetailView.as_view(), name="directory-branch-detail"),
    path("directory/global-search/", GlobalSearchView.as_view(), name="directory-global-search"),
]
