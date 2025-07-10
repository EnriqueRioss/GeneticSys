# Roles de Usuario y Permisos

El sistema utiliza tres roles principales para controlar el acceso a la información.

## Administrador (ADM)
El rol de Administrador tiene **acceso total** al sistema.
- **Puede ver**: Todos los pacientes, todas las historias clínicas y todos los reportes sin restricciones.
- **Puede hacer**: Crear, editar y eliminar cualquier registro. También puede gestionar las cuentas de otros usuarios (crear, activar/desactivar, eliminar).
- **Acceso especial**: Tiene vistas de "Gestión de Usuarios" y "Gestión de Pacientes" para una administración global.

## Genetista (GEN)
El rol de Genetista está diseñado para los médicos que gestionan los casos.
- **Puede ver**: Únicamente los pacientes y las historias clínicas que han sido **asignados directamente a él**. No puede ver los casos de otros genetistas.
- **Puede hacer**: Crear nuevas historias clínicas (que se le asignan automáticamente) y registrar y editar toda la información de sus pacientes.
- **Vista principal**: Su dashboard y lista de pacientes están filtrados para mostrar solo "Mis Pacientes".

## Lector (LEC)
El rol de Lector es un perfil de **solo consulta**.
- **Asociación**: Cada Lector está asociado a un Genetista específico.
- **Puede ver**: Únicamente puede ver la información de los pacientes que pertenecen al Genetista al que está asociado.
- **No puede hacer**: No puede crear, editar ni eliminar ninguna información en el sistema. Su función es puramente de consulta.