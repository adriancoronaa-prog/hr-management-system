# Arquitectura Técnica - RRHH Multi-empresa

## Stack Tecnológico

### Frontend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 18.x | Framework UI |
| TypeScript | 5.x | Tipado estático |
| Vite | 5.x | Build tool |
| Tailwind CSS | 3.x | Estilos |
| shadcn/ui | latest | Componentes UI |
| React Router | 6.x | Navegación |
| TanStack Query | 5.x | Estado servidor / caché |
| Zustand | 4.x | Estado global |
| React Hook Form | 7.x | Formularios |
| Zod | 3.x | Validación |
| date-fns | 3.x | Manejo de fechas |
| Recharts | 2.x | Gráficas |
| Lucide React | latest | Iconos |

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.12 | Lenguaje |
| Django | 5.x | Framework web |
| Django REST Framework | 3.15 | API REST |
| PostgreSQL | 16 | Base de datos |
| Redis | 7.x | Caché / Sesiones |
| Celery | 5.x | Tareas asíncronas |
| boto3 | latest | AWS S3 |
| django-cors-headers | latest | CORS |
| djangorestframework-simplejwt | latest | Autenticación JWT |
| django-filter | latest | Filtrado API |
| drf-spectacular | latest | Documentación OpenAPI |
| Pillow | latest | Procesamiento imágenes |
| python-docx | latest | Generación documentos |
| openpyxl | latest | Excel export/import |
| WeasyPrint | latest | Generación PDF |

### Infraestructura
| Servicio | Uso |
|----------|-----|
| Docker | Contenedores |
| Docker Compose | Orquestación local |
| Railway / Render | Hosting (producción) |
| AWS S3 | Almacenamiento documentos |
| AWS CloudFront | CDN (opcional) |
| Sentry | Monitoreo errores |
| GitHub Actions | CI/CD |

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTE                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │   Browser   │  │  Mobile PWA │  │   Tablet    │                      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                      │
└─────────┼────────────────┼────────────────┼─────────────────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    React SPA (Vite + TypeScript)                   │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │  Auth   │ │Dashboard│ │Empleados│ │Vacacion.│ │ Docs    │     │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │              TanStack Query (Cache & Sync)                  │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                           │ REST API (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND                                        │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    Django + DRF                                    │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │  │
│  │  │Empresas │ │Empleados│ │Contratos│ │Vacacion.│ │  Docs   │     │  │
│  │  │   App   │ │   App   │ │   App   │ │   App   │ │   App   │     │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                    Services Layer                           │ │  │
│  │  │  • CalculadorVacaciones  • GeneradorReportes                │ │  │
│  │  │  • GestorDocumentos      • NotificacionesService            │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                           │                                              │
│            ┌──────────────┼──────────────┐                              │
│            ▼              ▼              ▼                              │
│     ┌───────────┐  ┌───────────┐  ┌───────────┐                        │
│     │PostgreSQL │  │   Redis   │  │  Celery   │                        │
│     │    DB     │  │   Cache   │  │  Workers  │                        │
│     └───────────┘  └───────────┘  └───────────┘                        │
└─────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SERVICIOS EXTERNOS                                  │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐            │
│  │  AWS S3   │  │   SMTP    │  │  Sentry   │  │  Backup   │            │
│  │  Storage  │  │   Email   │  │  Monitor  │  │  Service  │            │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura del Proyecto

### Backend (Django)

```
backend/
├── config/                     # Configuración Django
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Configuración base
│   │   ├── development.py     # Config desarrollo
│   │   └── production.py      # Config producción
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                       # Aplicaciones Django
│   ├── __init__.py
│   │
│   ├── core/                   # Funcionalidad común
│   │   ├── models.py          # BaseModel, mixins
│   │   ├── permissions.py     # Permisos personalizados
│   │   ├── pagination.py
│   │   └── utils.py
│   │
│   ├── usuarios/               # Autenticación y usuarios
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   │
│   ├── empresas/               # Gestión de empresas
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── filters.py
│   │   └── services.py
│   │
│   ├── empleados/              # Gestión de empleados
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── filters.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── calculador_antiguedad.py
│   │       └── importador_excel.py
│   │
│   ├── contratos/              # Gestión de contratos
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   │
│   ├── vacaciones/             # Gestión de vacaciones
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── calculador_vacaciones.py
│   │       ├── generador_periodos.py
│   │       └── aprobador.py
│   │
│   ├── prestaciones/           # Planes y prestaciones
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── calculador_prestaciones.py
│   │
│   ├── documentos/             # Gestión documental
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── storage.py     # Abstracción S3
│   │       └── procesador.py
│   │
│   ├── reportes/               # Reportes y exportación
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── excel_generator.py
│   │       └── pdf_generator.py
│   │
│   └── notificaciones/         # Sistema de alertas
│       ├── models.py
│       ├── tasks.py           # Celery tasks
│       └── services.py
│
├── templates/                  # Templates (emails, PDFs)
│   └── emails/
│       ├── vacaciones_aprobada.html
│       └── contrato_por_vencer.html
│
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── Dockerfile
└── docker-compose.yml
```

### Frontend (React)

```
frontend/
├── public/
│   └── favicon.ico
│
├── src/
│   ├── main.tsx               # Entry point
│   ├── App.tsx                # App component
│   ├── vite-env.d.ts
│   │
│   ├── assets/                # Imágenes, fuentes
│   │   └── logo.svg
│   │
│   ├── components/            # Componentes reutilizables
│   │   ├── ui/               # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── EmpresaSelector.tsx
│   │   │   └── MainLayout.tsx
│   │   │
│   │   ├── forms/
│   │   │   ├── EmpleadoForm.tsx
│   │   │   ├── ContratoForm.tsx
│   │   │   └── VacacionesForm.tsx
│   │   │
│   │   └── shared/
│   │       ├── DataTable.tsx
│   │       ├── Calendar.tsx
│   │       ├── FileUploader.tsx
│   │       └── LoadingSpinner.tsx
│   │
│   ├── pages/                 # Páginas/vistas
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── ForgotPasswordPage.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   │
│   │   ├── empresas/
│   │   │   ├── EmpresasPage.tsx
│   │   │   └── EmpresaFormPage.tsx
│   │   │
│   │   ├── empleados/
│   │   │   ├── EmpleadosPage.tsx
│   │   │   ├── EmpleadoFormPage.tsx
│   │   │   └── EmpleadoDetailPage.tsx
│   │   │
│   │   ├── contratos/
│   │   │   └── ContratosPage.tsx
│   │   │
│   │   ├── vacaciones/
│   │   │   ├── VacacionesPage.tsx
│   │   │   ├── CalendarioPage.tsx
│   │   │   └── SolicitudesPage.tsx
│   │   │
│   │   ├── prestaciones/
│   │   │   ├── PlanesPage.tsx
│   │   │   └── PlanFormPage.tsx
│   │   │
│   │   ├── documentos/
│   │   │   └── DocumentosPage.tsx
│   │   │
│   │   └── reportes/
│   │       └── ReportesPage.tsx
│   │
│   ├── hooks/                 # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useEmpresa.ts
│   │   ├── useEmpleados.ts
│   │   └── useVacaciones.ts
│   │
│   ├── services/              # API calls
│   │   ├── api.ts            # Axios instance
│   │   ├── auth.service.ts
│   │   ├── empresas.service.ts
│   │   ├── empleados.service.ts
│   │   ├── contratos.service.ts
│   │   ├── vacaciones.service.ts
│   │   └── documentos.service.ts
│   │
│   ├── stores/                # Zustand stores
│   │   ├── authStore.ts
│   │   └── empresaStore.ts
│   │
│   ├── types/                 # TypeScript types
│   │   ├── index.ts
│   │   ├── empresa.types.ts
│   │   ├── empleado.types.ts
│   │   ├── vacaciones.types.ts
│   │   └── api.types.ts
│   │
│   ├── utils/                 # Utilidades
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   ├── routes/                # Configuración rutas
│   │   ├── index.tsx
│   │   └── ProtectedRoute.tsx
│   │
│   └── styles/
│       └── globals.css
│
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
├── Dockerfile
└── .env.example
```

---

## API REST - Endpoints Principales

### Autenticación
```
POST   /api/auth/login/           # Login
POST   /api/auth/logout/          # Logout
POST   /api/auth/refresh/         # Refresh token
GET    /api/auth/me/              # Usuario actual
```

### Empresas
```
GET    /api/empresas/             # Listar empresas (del usuario)
POST   /api/empresas/             # Crear empresa
GET    /api/empresas/{id}/        # Detalle empresa
PUT    /api/empresas/{id}/        # Actualizar empresa
DELETE /api/empresas/{id}/        # Desactivar empresa
```

### Empleados
```
GET    /api/empleados/                    # Listar empleados
POST   /api/empleados/                    # Crear empleado
GET    /api/empleados/{id}/               # Detalle empleado
PUT    /api/empleados/{id}/               # Actualizar empleado
DELETE /api/empleados/{id}/               # Dar de baja empleado

GET    /api/empleados/{id}/vacaciones/    # Saldo vacaciones
GET    /api/empleados/{id}/contratos/     # Contratos del empleado
GET    /api/empleados/{id}/documentos/    # Documentos del empleado
GET    /api/empleados/{id}/prestaciones/  # Prestaciones calculadas

POST   /api/empleados/importar/           # Importar desde Excel
```

### Contratos
```
GET    /api/contratos/                    # Listar contratos
POST   /api/contratos/                    # Crear contrato
GET    /api/contratos/{id}/               # Detalle contrato
PUT    /api/contratos/{id}/               # Actualizar contrato

GET    /api/contratos/por-vencer/         # Contratos próximos a vencer
```

### Vacaciones
```
GET    /api/vacaciones/solicitudes/       # Listar solicitudes
POST   /api/vacaciones/solicitudes/       # Crear solicitud
GET    /api/vacaciones/solicitudes/{id}/  # Detalle solicitud
PUT    /api/vacaciones/solicitudes/{id}/  # Actualizar solicitud

POST   /api/vacaciones/solicitudes/{id}/aprobar/   # Aprobar
POST   /api/vacaciones/solicitudes/{id}/rechazar/  # Rechazar

GET    /api/vacaciones/calendario/        # Vista calendario
GET    /api/vacaciones/periodos/          # Periodos vacacionales
POST   /api/vacaciones/registro-historico/  # Registro retroactivo
```

### Prestaciones
```
GET    /api/prestaciones/planes/          # Listar planes
POST   /api/prestaciones/planes/          # Crear plan
GET    /api/prestaciones/planes/{id}/     # Detalle plan
PUT    /api/prestaciones/planes/{id}/     # Actualizar plan

GET    /api/prestaciones/tipos/           # Catálogo tipos prestación
GET    /api/prestaciones/comparativa/     # Comparativa vs ley

POST   /api/prestaciones/ajustes/         # Crear ajuste individual
GET    /api/prestaciones/ajustes/         # Listar ajustes
```

### Documentos
```
GET    /api/documentos/                   # Listar documentos
POST   /api/documentos/                   # Subir documento
GET    /api/documentos/{id}/              # Detalle/descargar
DELETE /api/documentos/{id}/              # Eliminar documento

GET    /api/documentos/categorias/        # Listar categorías
POST   /api/documentos/categorias/        # Crear categoría

GET    /api/documentos/por-vencer/        # Documentos por vencer
POST   /api/documentos/descarga-masiva/   # Descargar ZIP
```

### Reportes
```
GET    /api/reportes/dashboard/           # Datos dashboard
GET    /api/reportes/plantilla/           # Reporte plantilla
GET    /api/reportes/vacaciones/          # Reporte vacaciones
GET    /api/reportes/contratos/           # Reporte contratos

POST   /api/reportes/exportar/excel/      # Exportar a Excel
POST   /api/reportes/exportar/pdf/        # Exportar a PDF
```

---

## Seguridad

### Autenticación
- JWT (JSON Web Tokens) con refresh tokens
- Access token: 15 minutos
- Refresh token: 7 días
- Blacklist de tokens al logout

### Autorización
- Permisos basados en roles (RBAC)
- Filtrado por empresa (multi-tenancy)
- Cada usuario solo ve empresas asignadas

### Protección de Datos
- Cifrado de datos sensibles en BD (salarios, CURP)
- HTTPS obligatorio
- Headers de seguridad (CORS, CSP, HSTS)
- Sanitización de inputs
- Rate limiting en endpoints sensibles

### Cumplimiento
- Ley Federal de Protección de Datos Personales (México)
- Logs de auditoría para acceso a datos sensibles
- Política de retención de datos

---

## Deployment

### Docker Compose (Desarrollo)

```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: rrhh_db
      POSTGRES_USER: rrhh_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=True
      - DATABASE_URL=postgres://rrhh_user:${DB_PASSWORD}@db:5432/rrhh_db
      - REDIS_URL=redis://redis:6379/0

  celery:
    build: ./backend
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000/api

volumes:
  postgres_data:
```

### Producción (Railway/Render)

```yaml
# railway.yaml
services:
  backend:
    build:
      context: ./backend
    env:
      - DATABASE_URL=${{Postgres.DATABASE_URL}}
      - REDIS_URL=${{Redis.REDIS_URL}}
      - SECRET_KEY=${{SECRET_KEY}}
      - AWS_ACCESS_KEY_ID=${{AWS_ACCESS_KEY_ID}}
      - AWS_SECRET_ACCESS_KEY=${{AWS_SECRET_ACCESS_KEY}}
      - AWS_S3_BUCKET=${{AWS_S3_BUCKET}}
    
  frontend:
    build:
      context: ./frontend
    env:
      - VITE_API_URL=https://api.rrhh-app.com
```

---

## Monitoreo y Logging

### Sentry (Errores)
```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False
)
```

### Logging
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/app.log',
        },
    },
    'loggers': {
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
```

---

## Testing

### Backend
```bash
# Unit tests
pytest apps/ --cov=apps --cov-report=html

# Integration tests
pytest tests/integration/
```

### Frontend
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```
