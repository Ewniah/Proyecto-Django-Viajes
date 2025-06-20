from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import PaqueteViaje, Cliente, Reserva, Pago
from django.contrib.auth.models import User
from .forms import RegistroForm, UserUpdateForm, ClienteUpdateForm, PaqueteViajeForm, ImagenPaqueteFormSet
from django.db.models import Sum, Count
from django.core.mail import send_mail

# --- Vistas Públicas de Paquetes ---

def listar_paquetes(request):
    query = request.GET.get('q')
    paquetes = PaqueteViaje.objects.all().order_by('id_paquete')
    
    if query:
        paquetes = paquetes.filter(destino__icontains=query)
    
    context = {
        'paquetes': paquetes,
        'titulo_pagina': 'Paquetes de Viaje Disponibles',
        'query': query
    }
    return render(request, 'agencia/listar_paquetes.html', context)

def detalle_paquete(request, id_paquete):
    paquete = get_object_or_404(PaqueteViaje, id_paquete=id_paquete)
    context = {'paquete': paquete, 'titulo_pagina': paquete.descripcion}
    return render(request, 'agencia/detalle_paquete.html', context)


# --- Vistas de Autenticación y Perfil ---

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            rut = form.cleaned_data['rut']
            telefono = form.cleaned_data['telefono']

            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = nombre
            user.last_name = apellido
            user.save()

            Cliente.objects.create(user=user, rut=rut, telefono=telefono)

            try:
                send_mail(
                    '¡Bienvenido a Viajes Bonitos!',
                    f'Hola {nombre},\n\nGracias por registrarte en nuestra agencia de viajes. ¡Estamos muy contentos de tenerte con nosotros!\n\nExplora nuestros destinos y encuentra tu próxima aventura.\n\nSaludos,\nEl equipo de Viajes Bonitos', # Cuerpo del mensaje
                    'noreply@viajesbonitos.com',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, '¡Registro exitoso! Te hemos enviado un correo de bienvenida.')
            except Exception as e:
                messages.warning(request, f'Registro exitoso, pero no se pudo enviar el correo de bienvenida. Error: {e}')

            return redirect('agencia:iniciar_sesion')
    else:
        form = RegistroForm()
    return render(request, 'agencia/registrarse.html', {'form': form})

@login_required
def perfil_usuario_view(request):
    return render(request, 'agencia/perfil.html')

@login_required
def editar_perfil_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        cliente_form = ClienteUpdateForm(request.POST, instance=request.user.cliente)
        if user_form.is_valid() and cliente_form.is_valid():
            user_form.save()
            cliente_form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
            return redirect('agencia:perfil_usuario')
    else:
        user_form = UserUpdateForm(instance=request.user)
        cliente_form = ClienteUpdateForm(instance=request.user.cliente)
    context = {'user_form': user_form, 'cliente_form': cliente_form}
    return render(request, 'agencia/editar_perfil.html', context)


# --- Vistas de Reservas y Pagos (Protegidas) ---

@login_required
def crear_reserva_view(request, id_paquete):
    paquete = get_object_or_404(PaqueteViaje, id_paquete=id_paquete)
    cliente = request.user.cliente
    
    reserva_existente = Reserva.objects.filter(rut_cliente=cliente, id_paquete=paquete).exclude(estado='Cancelada').exists()
    if reserva_existente:
        messages.error(request, f'Ya tienes una reserva activa para el paquete "{paquete.descripcion}".')
        return redirect('agencia:mis_reservas')

    nueva_reserva = Reserva.objects.create(
        rut_cliente=cliente,
        id_paquete=paquete,
        fecha_reserva=timezone.now().date(),
        estado='Reservado'
    )
    
    messages.info(request, f'¡Reserva para el paquete "{paquete.descripcion}" creada! Procede con el pago.')
    return redirect('agencia:procesar_pago', id_reserva=nueva_reserva.id_reserva)

@login_required
def procesar_pago_view(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    if reserva.rut_cliente != request.user.cliente:
        messages.error(request, "No tienes permiso para acceder a esta reserva.")
        return redirect('agencia:mis_reservas')

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        Pago.objects.create(id_reserva=reserva, metodo_pago=metodo_pago)
        reserva.estado = 'Pagado'
        reserva.save()
        messages.success(request, f'¡Pago con {metodo_pago} realizado con éxito! Tu reserva ha sido confirmada.')
        return redirect('agencia:mis_reservas')

    context = {'reserva': reserva}
    return render(request, 'agencia/procesar_pago.html', context)

@login_required
def mis_reservas_view(request):
    try:
        cliente = request.user.cliente
        lista_reservas = Reserva.objects.filter(rut_cliente=cliente).exclude(estado='Cancelada').order_by('-fecha_reserva')
    except Cliente.DoesNotExist:
        lista_reservas = []
    context = {'reservas': lista_reservas}
    return render(request, 'agencia/mis_reservas.html', context)

@login_required
def cancelar_reserva_view(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    if reserva.rut_cliente != request.user.cliente:
        messages.error(request, "Acción no permitida.")
        return redirect('agencia:mis_reservas')
    
    if reserva.estado == 'Pagado':
        messages.error(request, "No puedes cancelar una reserva que ya ha sido pagada. Por favor, contacta a soporte.")
    elif reserva.estado == 'Reservado':
        reserva.estado = 'Cancelada'
        reserva.save()
        messages.info(request, f'La reserva N°{reserva.id_reserva} ha sido cancelada.')
    else:
        messages.warning(request, "Esta reserva no se puede cancelar.")
    
    return redirect('agencia:mis_reservas')

@login_required
def detalle_reserva_view(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
    if reserva.rut_cliente != request.user.cliente:
        messages.error(request, "No tienes permiso para ver esta reserva.")
        return redirect('agencia:mis_reservas')
    context = {'reserva': reserva}
    return render(request, 'agencia/detalle_reserva.html', context)


# --- Vistas de Administración (Frontend) ---

def es_admin(user):
    return user.is_staff

@login_required
@user_passes_test(es_admin)
def crear_paquete_view(request):
    if request.method == 'POST':
        form = PaqueteViajeForm(request.POST, request.FILES)
        formset = ImagenPaqueteFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            paquete_creado = form.save()
            
            formset.instance = paquete_creado
            formset.save()
            
            messages.success(request, '¡El nuevo paquete de viaje y sus imágenes han sido creados con éxito!')
            return redirect('agencia:gestionar_paquetes')
    else:
        form = PaqueteViajeForm()
        formset = ImagenPaqueteFormSet()

    context = {
        'form': form,
        'formset': formset,
        'titulo_pagina': 'Crear Nuevo Paquete'
    }
    return render(request, 'agencia/crear_paquete.html', context)

@login_required
@user_passes_test(es_admin)
def gestionar_paquetes_view(request):
    paquetes = PaqueteViaje.objects.all().order_by('id_paquete')
    context = {
        'paquetes': paquetes
    }
    return render(request, 'agencia/gestionar_paquetes.html', context)

def inicio_view(request):
    return render(request, 'agencia/inicio.html')

@login_required
@user_passes_test(es_admin)
def editar_paquete_view(request, id_paquete):
    paquete = get_object_or_404(PaqueteViaje, id_paquete=id_paquete)

    if request.method == 'POST':
        form = PaqueteViajeForm(request.POST, request.FILES, instance=paquete)
        formset = ImagenPaqueteFormSet(request.POST, request.FILES, instance=paquete)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'El paquete "{paquete.descripcion}" ha sido actualizado con éxito.')
            return redirect('agencia:gestionar_paquetes')
    else:
        form = PaqueteViajeForm(instance=paquete)
        formset = ImagenPaqueteFormSet(instance=paquete)

    context = {
        'form': form,
        'formset': formset,
        'titulo_pagina': f'Editando: {paquete.descripcion}'
    }
    return render(request, 'agencia/editar_paquete.html', context)

@login_required
@user_passes_test(es_admin)
def eliminar_paquete_view(request, id_paquete):
    paquete = get_object_or_404(PaqueteViaje, id_paquete=id_paquete)

    if request.method == 'POST':
        paquete.delete()
        messages.warning(request, f'El paquete "{paquete.descripcion}" ha sido eliminado.')
        return redirect('agencia:gestionar_paquetes')

    context = {
        'paquete': paquete
    }
    return render(request, 'agencia/eliminar_paquete_confirm.html', context)

@login_required
@user_passes_test(es_admin)
def reportes_view(request):
    ingresos_totales = Pago.objects.aggregate(total=Sum('id_reserva__id_paquete__precio'))['total'] or 0

    total_reservas = Reserva.objects.count()

    paquetes_populares = PaqueteViaje.objects.annotate(
        num_reservas=Count('reserva')
    ).order_by('-num_reservas')[:5]

    context = {
        'ingresos_totales': ingresos_totales,
        'total_reservas': total_reservas,
        'paquetes_populares': paquetes_populares,
    }
    return render(request, 'agencia/reportes.html', context)

def es_superusuario(user):
    return user.is_superuser

@login_required
@user_passes_test(es_superusuario)
def gestionar_roles_view(request):
    usuarios = User.objects.filter(is_superuser=False).order_by('username')
    context = {
        'usuarios': usuarios
    }
    return render(request, 'agencia/gestionar_roles.html', context)

@login_required
@user_passes_test(es_superusuario)
def cambiar_rol_usuario_view(request, user_id):
    if request.method == 'POST':
        usuario_a_modificar = get_object_or_404(User, id=user_id)

        usuario_a_modificar.is_staff = not usuario_a_modificar.is_staff
        usuario_a_modificar.save()

        messages.success(request, f"Se ha cambiado el rol de {usuario_a_modificar.username} correctamente.")

    return redirect('agencia:gestionar_roles')