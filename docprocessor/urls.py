from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_document, name='upload_document'),
    path('process/<int:document_id>/', views.process_document, name='process_document'),
    path('summarize/', views.summarize_view, name='summarize'),
    path('generate/', views.generate_view, name='generate'),
    path('analyze/', views.analyze_view, name='analyze'),
    path('accessibility/', views.accessibility_view, name='accessibility'),
    path('youtube_result/<int:result_id>/', views.youtube_result_view, name='youtube_result'),
    path('download/result/<int:result_id>/', views.download_result_pdf, name='download_result_pdf'),
    path('download/youtube/<int:result_id>/', views.download_youtube_result_pdf, name='download_youtube_result_pdf'),
    # Auth
    path('login/', LoginView.as_view(template_name='docprocessor/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register_view, name='register'),
]