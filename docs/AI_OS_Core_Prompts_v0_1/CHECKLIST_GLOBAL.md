# Checklist global de verificación

Antes de considerar completa cualquier fase:

- [ ] No se ha duplicado ownership.
- [ ] La app modificada sigue funcionando standalone.
- [ ] No se accede directamente a SQLite de otra app.
- [ ] Todo contrato lleva versión.
- [ ] Todo write remoto es idempotente.
- [ ] Los eventos tienen source autorizado.
- [ ] Los fallos no se convierten en estados falsamente exitosos.
- [ ] Las acciones irreversibles requieren confirmación.
- [ ] Los secretos no aparecen en DB/eventos/logs.
- [ ] Se distinguen hechos verificados de campos declarados.
- [ ] Existen tests normales, límite y negativos.
- [ ] Se han ejecutado las pruebas reales que el entorno permite.
- [ ] Lo no verificado se documenta explícitamente.
