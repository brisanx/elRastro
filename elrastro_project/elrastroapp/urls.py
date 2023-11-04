from django.urls import path
from elrastroapp import views

urlpatterns = [
    path('api/usuarios/', views.usuarios_list_view, name='usuarios_list'),
    path('api/usuarios/<str:usuario_id>/', views.view_usuario, name='view_usuario'),
    path('api/usuarios/create/', views.create_usuario, name='create_usuario'),
]
