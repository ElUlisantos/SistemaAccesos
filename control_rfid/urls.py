from django.urls import path
from . import views

urlpatterns = [
    # Esta es la ruta exacta a la que apuntará tu ESP32

    path('', views.menu_principal, name='menu_principal'),
    path('api/verificar/', views.verificar_acceso, name='verificar_acceso'),
    path('registro/', views.registrar_usuario, name='registrar_usuario'),
    path('historial/', views.historial_accesos, name='historial_accesos'),
    # Rutas para la gestión de usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    # El <str:id_tarjeta> captura el UID (ej. "A1 B2 C3 D4") y se lo pasa a la vista
    path('usuarios/eliminar/<str:id_tarjeta>/', views.eliminar_usuario, name='eliminar_usuario'),
]