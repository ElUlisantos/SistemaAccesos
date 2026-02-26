import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Acceso
from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Acceso


# Usamos @csrf_exempt porque el ESP32 no es un navegador web y no puede 
# enviar el token de seguridad CSRF que Django pide por defecto.
@csrf_exempt 
def verificar_acceso(request):
    # Verificamos que la petición sea de tipo POST
    if request.method == 'POST':
        try:
            # 1. Leemos el cuerpo de la petición y lo convertimos de JSON a un diccionario de Python
            data = json.loads(request.body)
            uid_recibido = data.get('id_Tarjeta')

            # 2. Buscamos en la base de datos si existe un Usuario con ese ID
            # .first() devuelve el objeto si lo encuentra, o None si no existe
            usuario_db = Usuario.objects.filter(id_Tarjeta=uid_recibido).first()

            # 3. Determinamos si se concede el acceso
            if usuario_db:
                estado = "Concedido"
                permiso = True
            else:
                estado = "Denegado"
                permiso = False

            # 4. Guardamos el registro en la bitácora (tabla Acceso)
            # Si el usuario no existe, usuario_db será None, lo cual está permitido en tu modelo
            Acceso.objects.create(
                usuario=usuario_db, 
                estado_Acceso=estado
            )

            # 5. Respondemos al ESP32 con un nuevo JSON
            return JsonResponse({
                'acceso': permiso, 
                'mensaje': estado
            })

        except Exception as e:
            # Si el ESP32 manda mal el formato, respondemos con un error
            return JsonResponse({'error': str(e)}, status=400)

    # Si alguien intenta acceder desde el navegador web (GET), lo rechazamos
    return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)

# Vista para registrar nuevos usuarios
def registrar_usuario(request):
    if request.method == 'POST':
        # Capturamos los datos del formulario HTML
        uid = request.POST.get('id_Tarjeta')
        nombre = request.POST.get('nombre_Usuario')
        rol = request.POST.get('rol_Usuario')
        
        # Guardamos en la base de datos
        if uid and nombre and rol:
            Usuario.objects.create(
                id_Tarjeta=uid, 
                nombre_Usuario=nombre, 
                rol_Usuario=rol
            )
            return redirect('historial_accesos') # Redirige a la tabla tras guardar
            
    # Si es GET, solo mostramos la página en blanco
    return render(request, 'control_rfid/registro.html')

# Vista para ver a qué hora se concedió el acceso
def historial_accesos(request):
    # Traemos todos los registros, ordenados del más reciente al más antiguo
    lista_accesos = Acceso.objects.all().order_by('-fecha', '-hora')
    
    # Se los pasamos a la plantilla HTML
    return render(request, 'control_rfid/historial.html', {'accesos': lista_accesos})

# Vista para el menú principal
def menu_principal(request):
    return render(request, 'control_rfid/menu.html')

# Vista para ver a todos los usuarios registrados
def lista_usuarios(request):
    usuarios_registrados = Usuario.objects.all()
    return render(request, 'control_rfid/lista_usuarios.html', {'usuarios': usuarios_registrados})

# Vista para eliminar un usuario específico
def eliminar_usuario(request, id_tarjeta):
    # Buscamos al usuario por su ID exacto
    usuario = get_object_or_404(Usuario, id_Tarjeta=id_tarjeta)
    
    # Lo eliminamos de la base de datos
    usuario.delete()
    
    # Redirigimos de vuelta a la lista de usuarios para ver los cambios
    return redirect('lista_usuarios')

@csrf_exempt
def api_registrar_tarjeta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uid_recibido = data.get('id_Tarjeta')

            # 1. Verificar si la tarjeta ya existe para no duplicarla
            if Usuario.objects.filter(id_Tarjeta=uid_recibido).exists():
                return JsonResponse({'exito': False, 'mensaje': 'La tarjeta ya está registrada.'})

            # 2. Guardar la nueva tarjeta con un nombre temporal
            Usuario.objects.create(
                id_Tarjeta=uid_recibido,
                nombre_Usuario='Usuario Pendiente (Editar)',
                rol_Usuario='Estudiante' # Rol por defecto
            )
            return JsonResponse({'exito': True, 'mensaje': 'Tarjeta registrada correctamente.'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)