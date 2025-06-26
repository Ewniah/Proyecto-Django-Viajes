from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView, 
    LogoutView, 
    PasswordChangeView, 
    PasswordChangeDoneView
)
from . import views
from .forms import CustomPasswordChangeForm

app_name = 'agencia'

urlpatterns = [
    # ---- URLs Públicas y de Paquetes ----
    path('', views.inicio_view, name='inicio'),
    path('paquetes/', views.listar_paquetes, name='listar_paquetes'),
    path('paquete/<int:id_paquete>/', views.detalle_paquete, name='detalle_paquete'),

    # ---- URLs de Autenticación ----
    path('registro/', views.registro_view, name='registro'),
    path('login/', LoginView.as_view(template_name='agencia/iniciar_sesion.html'), name='iniciar_sesion'),
    path('logout/', LogoutView.as_view(next_page='agencia:inicio'), name='cerrar_sesion'),

    # ---- URLs de Reservas y Pagos (Protegidas) ----
    path('paquete/<int:id_paquete>/reservar/', views.crear_reserva_view, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    path('reserva/<int:id_reserva>/', views.detalle_reserva_view, name='detalle_reserva'),
    path('reserva/<int:id_reserva>/pagar/', views.procesar_pago_view, name='procesar_pago'),
    path('reserva/<int:id_reserva>/cancelar/', views.cancelar_reserva_view, name='cancelar_reserva'),

    # ---- URLs de Perfil de Usuario (Protegidas) ----
    path('perfil/', views.perfil_usuario_view, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    
    path('perfil/cambiar-contraseña/', 
        PasswordChangeView.as_view(
            template_name='agencia/cambiar_contraseña.html',
            success_url=reverse_lazy('agencia:password_change_done'),
            form_class=CustomPasswordChangeForm
        ), 
        name='password_change'),
    
    path('perfil/cambiar-contraseña/listo/', 
        PasswordChangeDoneView.as_view(
            template_name='agencia/cambiar_contraseña_listo.html'
        ), 
        name='password_change_done'),

    # ---- URLs de Administración (Frontend, Protegidas) ----
    path('admin-paquetes/', views.gestionar_paquetes_view, name='gestionar_paquetes'),
    path('admin-paquetes/crear/', views.crear_paquete_view, name='crear_paquete'),

    path('admin-paquetes/crear/', views.crear_paquete_view, name='crear_paquete'),
    path('admin-paquetes/editar/<int:id_paquete>/', views.editar_paquete_view, name='editar_paquete'),
    path('admin-paquetes/eliminar/<int:id_paquete>/', views.eliminar_paquete_view, name='eliminar_paquete'),

    path('admin-paquetes/crear/', views.crear_paquete_view, name='crear_paquete'),
    path('reportes/', views.reportes_view, name='reportes'),

    path('admin-paquetes/crear/', views.crear_paquete_view, name='crear_paquete'),
    path('admin-roles/', views.gestionar_roles_view, name='gestionar_roles'),
    path('admin-roles/cambiar/<int:user_id>/', views.cambiar_rol_usuario_view, name='cambiar_rol'),

    path('reportes/', views.reportes_view, name='reportes'),
    path('reportes/descargar-csv/', views.descargar_reporte_reservas_csv, name='descargar_reporte_csv'),

    path('carrito/', views.cart_detail_view, name='cart_detail'),
    path('carrito/añadir/<int:id_paquete>/', views.cart_add_view, name='cart_add'),
    path('carrito/eliminar/<int:id_paquete>/', views.cart_remove_view, name='cart_remove'),

    path('carrito/eliminar/<int:id_paquete>/', views.cart_remove_view, name='cart_remove'),
    path('checkout/', views.checkout_view, name='checkout'),

    
]