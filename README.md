# Agencia de Viajes - Proyecto Django

Este es un proyecto web full-stack desarrollado con Django que simula el sistema de gestión de una agencia de viajes. La aplicación permite a los clientes registrarse, ver paquetes de viaje, realizar y gestionar reservas, mientras que los administradores pueden gestionar los paquetes y ver reportes del negocio.

---

## 🚀 Características Principales

### Para Clientes:
- **Autenticación de Usuarios:** Sistema de registro, inicio y cierre de sesión usando correo electrónico.
- **Gestión de Perfil:** Los usuarios pueden ver y editar sus datos personales y cambiar su contraseña.
- **Catálogo de Paquetes:** Visualización de paquetes de viaje con galerías de imágenes en carrusel y búsqueda por destino.
- **Ciclo de Reserva:** Creación de reservas, simulación de pago, cancelación y visualización de historial de reservas.

### Para Administradores:
- **Panel de Gestión Frontend:** CRUD completo (Crear, Leer, Actualizar, Eliminar) para paquetes de viaje directamente desde el sitio.
- **Gestión de Roles:** Un superusuario puede promover a otros usuarios al rol de administrador.
- **Dashboard de Reportes:** Visualización de métricas clave como ingresos totales y paquetes más populares.

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python, Django
* **Base de Datos:** Oracle Database XE
* **Frontend:** HTML5, CSS3, JavaScript
* **Framework de Diseño:** Bootstrap 5
* **Librerías Principales de Python:**
    * `oracledb`: para la conexión con la base de datos.
    * `Pillow`: para el procesamiento de imágenes.
    * `django-phonenumber-field`: para la validación de teléfonos internacionales.
    * `pyrut` (o función personalizada): para la validación de RUT chileno.

---

## ⚙️ Instalación y Puesta en Marcha

Para ejecutar este proyecto en un entorno de desarrollo local, sigue estos pasos:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/Ewniah/Proyecto-Django-Viajes](https://github.com/Ewniah/Proyecto-Django-Viajes)
    cd Proyecto-Django-Viajes
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Base de Datos:**
    * Asegúrate de tener una instancia de Oracle Database XE corriendo.
    * Verifica las credenciales de conexión en `viajes_project/settings.py`.

5.  **Aplicar las migraciones:**
    ```bash
    python manage.py migrate
    ```

6.  **Crear un superusuario** para acceder al panel de administración:
    ```bash
    python manage.py createsuperuser
    ```

7.  **Ejecutar el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```
    El sitio estará disponible en `http://127.0.0.1:8000/`.

---

## 👤 Autor

* **Ewniah** - https://github.com/Ewniah
