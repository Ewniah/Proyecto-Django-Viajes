from decimal import Decimal
from django.conf import settings
from .models import PaqueteViaje

class Cart:
    def __init__(self, request):
        """
        Inicializa el carrito.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Guarda un carrito vacío en la sesión
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, paquete):
        """
        Añade un paquete al carrito.
        """
        paquete_id = str(paquete.id_paquete)
        if paquete_id not in self.cart:
            self.cart[paquete_id] = {'precio': str(paquete.precio), 'descripcion': paquete.descripcion}
            self.save()

    def save(self):
        # Marca la sesión como "modificada" para asegurarse de que se guarde
        self.session.modified = True

    def remove(self, paquete):
        """
        Elimina un paquete del carrito.
        """
        paquete_id = str(paquete.id_paquete)
        if paquete_id in self.cart:
            del self.cart[paquete_id]
            self.save()

    def __iter__(self):
        """
        Itera sobre los items en el carrito y obtiene los paquetes de la base de datos.
        """
        paquete_ids = self.cart.keys()
        paquetes = PaqueteViaje.objects.filter(id_paquete__in=paquete_ids)
        cart = self.cart.copy()
        for paquete in paquetes:
            cart[str(paquete.id_paquete)]['paquete'] = paquete
        
        for item in cart.values():
            item['precio'] = Decimal(item['precio'])
            yield item

    def __len__(self):
        """
        Cuenta todos los items en el carrito.
        """
        return len(self.cart)

    def get_total_price(self):
        return sum(Decimal(item['precio']) for item in self.cart.values())

    def clear(self):
        # Elimina el carrito de la sesión
        del self.session[settings.CART_SESSION_ID]
        self.save()