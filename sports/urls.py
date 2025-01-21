from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("home/", views.home, name='home'),
    path("home/logout", LogoutView.as_view(), name='logout'),
    path("", views.landing_page, name='landing_page'),
    path("about/", views.about, name='about'),
    path("contact/", views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('projects/<int:pk>/upload/', views.upload_file, name='upload_file'),
    path('projects/<int:pk>/leave/', views.leave_project, name='leave_project'),
    path('projects/<int:pk>/request_join/', views.request_join_project, name='request_join_project'),
    path('projects/<int:pk>/manage_requests/', views.manage_requests, name='manage_requests'),
    path('projects/<int:pk>/post_message/', views.post_message, name='post_message'),
    path('projects/<int:pk>/delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('projects/file_metadata/<int:file_id>/', views.file_metadata, name='file_metadata'),
    path('projects/file_contents/<int:file_id>/', views.file_contents, name='file_contents'),
]