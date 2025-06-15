import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Cliente, PaqueteViaje, ImagenPaquete
from phonenumber_field.formfields import PhoneNumberField
from itertools import cycle
from django.forms import inlineformset_factory

# ---- FUNCIÓN DE VALIDACIÓN DE RUT (VERSIÓN CORREGIDA Y ROBUSTA) ----
def validar_rut_chileno(rut):
    """
    Función para validar un RUT chileno usando el algoritmo Módulo 11.
    """
    try:
        rut_limpio = rut.upper().replace(".", "").replace("-", "")
        cuerpo = rut_limpio[:-1]
        dv = rut_limpio[-1]

        if not cuerpo.isdigit():
            return False

        reversed_cuerpo = map(int, reversed(cuerpo))
        factors = cycle(range(2, 8))
        
        suma = sum(d * f for d, f in zip(reversed_cuerpo, factors))
        
        resto = suma % 11
        dv_calculado = 11 - resto
        
        if dv_calculado == 11:
            dv_esperado = '0'
        elif dv_calculado == 10:
            dv_esperado = 'K'
        else:
            dv_esperado = str(dv_calculado)
            
        return dv_esperado == dv
    except (ValueError, IndexError):
        return False


# ---- FORMULARIOS DE LA APLICACIÓN ----

class RegistroForm(forms.Form):
    nombre = forms.CharField(required=True, label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido = forms.CharField(required=True, label="Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@correo.com'}))
    password = forms.CharField(required=True, label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirmation = forms.CharField(required=True, label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    rut = forms.CharField(
        required=True,
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'})
    )
    
    telefono = PhoneNumberField(
        required=True,
        label="Teléfono",
        region="CL",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'}),
        error_messages={
            'invalid': "Por favor, introduce un número válido. Puede ser local (ej: 912345678) o internacional (+569...)."
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
    
    def clean_rut(self):
        rut_ingresado = self.cleaned_data.get('rut', '').strip()
        
        if not validar_rut_chileno(rut_ingresado):
            raise forms.ValidationError("El RUT ingresado no es válido (dígito verificador incorrecto).")
        
        rut_limpio = rut_ingresado.upper().replace(".", "")
        rut_normalizado = f"{rut_limpio[:-1]}-{rut_limpio[-1]}"

        if Cliente.objects.filter(rut=rut_normalizado).exists():
            raise forms.ValidationError("Este RUT ya está registrado.")
        
        return rut_normalizado

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and Cliente.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Este número de teléfono ya está registrado.")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', "Las contraseñas no coinciden.")
        
        return cleaned_data


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña antigua",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )
    new_password1 = forms.CharField(
        label="Contraseña nueva",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text="Tu contraseña debe contener al menos 8 caracteres y no puede ser demasiado común."
    )
    new_password2 = forms.CharField(
        label="Confirmación de contraseña nueva",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    error_messages = {
        'password_mismatch': "Las dos contraseñas no coinciden.",
        'password_incorrect': "Tu contraseña antigua es incorrecta. Por favor, inténtalo de nuevo."
    }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ClienteUpdateForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['rut', 'telefono']
        labels = {
            'rut': 'RUT',
            'telefono': 'Teléfono'
        }
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PaqueteViajeForm(forms.ModelForm):
    class Meta:
        model = PaqueteViaje
        fields = '__all__'
        labels = {
            'imagen': 'Imagen Principal del Paquete',
            'descripcion': 'Descripción del Paquete',
            'precio': 'Precio (CLP)',
            'destino': 'Destino Principal',
            'vuelo': 'Detalles del Vuelo',
            'alojamiento': 'Detalles del Alojamiento',
            'tour': 'Detalles del Tour',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_termino': 'Fecha de Término',
        }
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'vuelo': forms.TextInput(attrs={'class': 'form-control'}),
            'alojamiento': forms.TextInput(attrs={'class': 'form-control'}),
            'tour': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

ImagenPaqueteFormSet = inlineformset_factory(
    PaqueteViaje,  # Modelo Padre
    ImagenPaquete, # Modelo Hijo
    fields=('imagen',), # Campos a mostrar para cada imagen
    extra=1, # Cuántos formularios vacíos mostrar para añadir nuevas imágenes
    can_delete=True # Permitir eliminar imágenes existentes
)