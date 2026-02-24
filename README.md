1.- Crear el entorno virtual
Para no mezclar las librerías del proyecto con las de la computadora, se debe crear un entorno aislado:
python -m venv env

2. Activar el entorno virtual
El comando depende del sistema operativo que esté usando la persona:

En Windows (CMD/PowerShell): 
env\Scripts\activate

En Mac/Linux o Git Bash: 
source env/bin/activate

3. Instalar Django (Dependencia principal)
pip install django

4. Construir la base de datos
python manage.py makemigrations
python manage.py migrate

6. Crear un administrador
python manage.py createsuperuser
(El sistema pedirá inventar un nombre de usuario, correo y contraseña).

7. Levantar el servidor
python manage.py runserver 
