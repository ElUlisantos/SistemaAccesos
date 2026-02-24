from django.contrib import admin
from .models import Usuario, Acceso

# Registramos los modelos para que aparezcan en el panel
admin.site.register(Usuario)
admin.site.register(Acceso)