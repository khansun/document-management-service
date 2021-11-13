from django.urls import path, re_path
from django.conf.urls import include, url

from rest_framework import routers
from rest_framework.authtoken import views as authtoken_views

from papermerge.core import views


router = routers.DefaultRouter()

router.register(r"automates", views.AutomatesViewSet, basename="automate")
router.register(r"tags", views.TagsViewSet, basename="tag")
router.register("nodes", views.NodesViewSet, basename="node")
router.register(r"roles", views.RolesViewSet)
router.register(r"groups", views.GroupsViewSet)
router.register(r"users", views.UsersViewSet)
router.register(r"documents", views.DocumentVersionsViewSet, basename="document")
router.register(r"pages", views.PagesViewSet, basename="page")

urlpatterns = [
    re_path(
        r'documents/(?P<document_id>\d+)?/upload/(?P<file_name>[^/]+)$',
        views.DocumentUploadView.as_view()
    ),
    path('users/<int:pk>/change-password/', views.UserChangePassword.as_view()),
    path('users/me/', views.CurrentUserView.as_view()),
    path('content-types/<int:pk>/', views.ContentTypeRetrieve.as_view()),
    path('permissions/', views.PermissionsList.as_view()),
    path('auth-token/', authtoken_views.obtain_auth_token),
    url(r"^", include(router.urls)),
]
