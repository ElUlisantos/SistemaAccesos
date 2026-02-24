from django.db import models

class Usuario(models.Model):
    # Entidad Usuario 
    id_Tarjeta = models.CharField(max_length=50, primary_key=True, verbose_name="ID Tarjeta") # [cite: 49]
    nombre_Usuario = models.CharField(max_length=100, verbose_name="Nombre del Usuario") # [cite: 47]
    rol_Usuario = models.CharField(max_length=50, verbose_name="Rol") # [cite: 46]

    def __str__(self):
        return f"{self.nombre_Usuario} - {self.id_Tarjeta}"

class Acceso(models.Model):
    # Entidad Accesos 
    id_Acceso = models.AutoField(primary_key=True) # [cite: 45]
    
    # Relación Gestiona 
    # Usamos ForeignKey. null=True permite registrar intentos de tarjetas desconocidas.
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True) 
    estado_Acceso = models.CharField(max_length=20, verbose_name="Estado de Acceso") # [cite: 48]
    
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha") # [cite: 50]
    hora = models.TimeField(auto_now_add=True, verbose_name="Hora") # [cite: 54]

    def __str__(self):
        return f"Acceso {self.id_Acceso} - {self.estado_Acceso}"