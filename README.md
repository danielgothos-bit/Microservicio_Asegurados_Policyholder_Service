# Microservicio de Asegurados — Policyholder Service

Microservicio de InsureFlow definido en la sección 4.2 del documento de arquitectura.

## Responsabilidad

Administrar los perfiles de los asegurados, sus datos de contacto y la verificación de identidad (KYC).

## Tecnología

Python · Django REST Framework · PostgreSQL (`policyholder_db`) · Celery + Redis · Docker

## Modelo de datos (3FN, IDs UUID)

`asegurado` (national_id y email únicos, kyc_status) y `doc_kyc` (documentos de verificación).

## Endpoints

```
POST /api/v1/asegurados — registrar asegurado
GET  /api/v1/asegurados — listar (filtro ?national_id=)
GET  /api/v1/asegurados/{id} — consultar asegurado
PUT  /api/v1/asegurados/{id} — actualizar datos de contacto
GET  /api/v1/asegurados/{id}/kyc — estado de verificación
PUT  /api/v1/asegurados/{id}/kyc — aprobar/rechazar KYC
POST /api/v1/asegurados/{id}/kyc/documentos — cargar documento KYC
GET  /health — estado del servicio y de su base de datos
POST /api/v1/eventos — endpoint interno donde otros microservicios entregan eventos
```

## Eventos

Publica:
- policyholder.created
- policyholder.kyc_updated

Consume:
- (ninguno)

Los eventos se encolan con Celery/Redis y se entregan por HTTP al endpoint `/api/v1/eventos` de cada
suscriptor, con reintentos y backoff exponencial (módulo `comun/eventos.py`). Cada evento se procesa una
sola vez (idempotencia por `event_id`).

## Variables de entorno

- `DATABASE_URL`, `REDIS_URL`: base de datos y Redis propios
- `INTERNAL_TOKEN`: token compartido por todos los microservicios para los eventos
- `RUN_WORKER_IN_WEB=1`: corre el worker de Celery dentro del mismo contenedor (Render gratis)
- `SYNC_TIMEOUT`: timeout de las llamadas REST síncronas (3 s por defecto)
- (ninguna)

Si una URL no está configurada, el servicio funciona en modo aislado (omite esa validación o ese evento).

## Ejecución local

```bash
docker compose up --build
```

El servicio queda en http://localhost:8002 y las migraciones se aplican solas al arrancar.

Pruebas:

```bash
docker compose exec policyholder_service python manage.py test asegurados
```

## Despliegue en Render

En Render: **New → Blueprint** → conectar este repositorio → **Deploy Blueprint**.
El `render.yaml` crea el servicio web, su PostgreSQL y su Redis (plan gratis).
