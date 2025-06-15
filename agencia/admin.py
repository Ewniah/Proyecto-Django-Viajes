from django.contrib import admin
from .models import Cliente, PaqueteViaje, Reserva, Pago, ImagenPaquete

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('rut', 'get_username', 'get_email', 'telefono')
    search_fields = ('rut', 'user__username', 'user__email')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Usuario (Username)'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Correo Electrónico'


class ImagenPaqueteInline(admin.TabularInline):
    model = ImagenPaquete
    extra = 1 # Muestra un campo vacío para subir una imagen por defecto


class PaqueteViajeAdmin(admin.ModelAdmin):
    list_display = ('id_paquete', 'descripcion', 'destino', 'precio', 'fecha_inicio', 'fecha_termino')
    search_fields = ('descripcion', 'destino')
    list_filter = ('destino', 'fecha_inicio')
    inlines = [ImagenPaqueteInline]


class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'rut_cliente', 'id_paquete', 'fecha_reserva', 'estado')
    search_fields = ('id_reserva', 'rut_cliente__rut', 'id_paquete__descripcion')
    list_filter = ('estado', 'fecha_reserva', 'rut_cliente')


class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'id_reserva', 'metodo_pago')
    search_fields = ('id_pago', 'id_reserva__id_reserva')
    list_filter = ('metodo_pago',)


admin.site.register(Cliente, ClienteAdmin)
admin.site.register(PaqueteViaje, PaqueteViajeAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Pago, PagoAdmin)
admin.site.register(ImagenPaquete)