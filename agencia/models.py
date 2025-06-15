from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    rut = models.CharField(max_length=12, unique=True, help_text="RUT del cliente, normalizado (ej: 12345678-9).")
    telefono = PhoneNumberField(null=False, blank=False, unique=True, help_text="Número de teléfono internacional.")

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'CLIENTE'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class PaqueteViaje(models.Model):
    id_paquete = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=255, help_text="Descripción detallada del paquete.")
    precio = models.IntegerField(help_text="Precio del paquete, sin decimales.")
    destino = models.CharField(max_length=100, help_text="Destino principal del paquete.")
    vuelo = models.CharField(max_length=100, null=True, blank=True, help_text="Información del vuelo.")
    alojamiento = models.CharField(max_length=100, null=True, blank=True, help_text="Información del alojamiento.")
    tour = models.CharField(max_length=100, null=True, blank=True, help_text="Información sobre tours incluidos.")
    fecha_inicio = models.DateField(help_text="Fecha de inicio del paquete (YYYY-MM-DD).")
    fecha_termino = models.DateField(help_text="Fecha de término del paquete (YYYY-MM-DD).")

    def __str__(self):
        return f"{self.descripcion} ({self.destino})"

    class Meta:
        db_table = 'AGENCIADEVIAJES'
        verbose_name = "Paquete de Viaje"
        verbose_name_plural = "Paquetes de Viaje"

class ImagenPaquete(models.Model):
    paquete = models.ForeignKey(PaqueteViaje, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='paquetes_galeria/')

    def __str__(self):
        return f"Imagen para {self.paquete.descripcion}"


class Reserva(models.Model):
    id_reserva = models.BigAutoField(primary_key=True)
    rut_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='rut', to_field='rut', help_text="RUT del cliente que hizo la reserva.")
    id_paquete = models.ForeignKey(PaqueteViaje, on_delete=models.CASCADE, db_column='id_paquete', to_field='id_paquete', help_text="ID del paquete reservado.")
    fecha_reserva = models.DateField(help_text="Fecha en que se realizó la reserva.")
    estado = models.CharField(max_length=20, help_text="Estado actual de la reserva (Ej: Reservado, Pagado, Cancelada).")

    def __str__(self):
        return f"Reserva {self.id_reserva} - Paquete {self.id_paquete.id_paquete if self.id_paquete else 'N/A'} por {self.rut_cliente.rut if self.rut_cliente else 'N/A'}"
    
    class Meta:
        db_table = 'RESERVA'
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"


class Pago(models.Model):
    id_pago = models.BigAutoField(primary_key=True)
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, db_column='id_reserva', to_field='id_reserva', help_text="ID de la reserva asociada a este pago.")
    metodo_pago = models.CharField(max_length=50, help_text="Método utilizado para el pago (Ej: Débito, Crédito).")

    def __str__(self):
        return f"Pago {self.id_pago} para Reserva {self.id_reserva.id_reserva if self.id_reserva else 'N/A'} ({self.metodo_pago})"
    
    class Meta:
        db_table = 'PAGO'
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"