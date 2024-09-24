## E0

### Consideraciones generales

El suscriptor al broker está corriendo constantemente en su contenedor, este recibe la información del broker y la envía a la API para que esta maneje la acción correspondiente (que puede ser un post o un put, este en último en caso de que ya exista el fixture y haya que actualizarlo). Esto se hizo así siguiendo la arquitectura sugerida para esta entrega (ver imagen e0-diagram.png en la carpeta docs).

Luego la API almacena o actualiza los fixtures en la base de datos (implementada con PostgreSQL directamente en la instancia EC2), y luego mediante requests con los parámetros indicados en el enunciado se realizan las consultas correspondientes. Importante destacar que los endpoints para las consultas son iguales a los que se usan como ejemplo para cada requisito funcional en el enunciado. De todas formas, si hay alguna duda/confusión se puede ver el archivo api.py para ver como están estructurados los endpoints.

La API y el suscriptor al broker estarán ejecutándose en un contenedores separados constantemente (al momento de la revisión esta estará corriendo), el servicio de PostgreSQL estará activo en todo momento ya que se implementó directamente en la instancia EC2. Además, esta funcionará a través del puerto 8000 que está configurado con NGINX, por lo para hacer consultas la sintaxis es: arqui-2024-gspate.me/*endpoint*.

**PD**: En caso de que no les lleguen a funcionar las credenciales IAM para revisar la instancia, por favor envíenme un correo a gustavo.gonzalez@uc.cl y les entrego mis credenciales del root email (me enrredé mucho con lo de las credenciales IAM pero estoy casi seguro de que lo hice bien, y en caso de que me haya mandado alguna embarrada no quiero que perjudique tanto mi nota siendo que le dediqué bastantes horas a esta entrega). Gracias :)

### Cómo hacer funcionar desde 0 la app

*(Esto en caso de que no esté ejecutandose previamente)*

En la terminal de ubuntu correspondiente a mi instancia EC2:

- 1° Ubicarse en la carpeta "proyecto_arqui" con el comando: cd proyecto_arqui
- 2° Ejecutar los contenedores: docker-compose start

### Cómo detener la ejecución de la app

- 1° Ubicarse en la carpeta "proyecto_arqui" con el comando: cd proyecto_arqui
- 2° Detener los contenedores con el comando: docker-compose stop

### Nombre del dominio

 arqui-2024-gspate.me

### Método de acceso al servidor con archivo .pem y ssh

Primero abro la terminal (estoy trabajando en MacOS) y ejecuto el siguiente comando:

ssh -i "&lt;ruta_archivo.pem&gt;" ubuntu@&lt;nombre del dominio&gt;

### Puntos logrados y no logrados

Se lograron todos los requisitos esenciales.

Se lograron todos los requisitos funcionales.

Se lograron todos los requisitos no funcionales.

Se lograron todos los requisitos funcionales de Docker-Compose, menos el RNF2 (que la base de datos esté dentro de un contenedor).

Se lograron todos los requisitos variables de HTTPS.

No se logró ningún requisito del balanceador de carga.



