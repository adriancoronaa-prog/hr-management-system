import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    # Local apps
    'apps.core',
    'apps.usuarios',
    'apps.empresas',
    'apps.empleados',
    'apps.contratos',
    'apps.vacaciones',
    'apps.prestaciones',
    'apps.documentos',
    'apps.nomina',
    'apps.chat',
    'apps.integraciones',
    'apps.reportes',
    'apps.desempeno',
    'apps.notificaciones',
    'apps.solicitudes',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'rrhh_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Use SQLite for development if no PostgreSQL
if os.getenv('USE_SQLITE', 'False') == 'True':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

AUTH_USER_MODEL = 'usuarios.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ========================================
# API DOCUMENTATION (Swagger/OpenAPI)
# ========================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sistema RRHH API',
    'DESCRIPTION': '''
## API del Sistema de Recursos Humanos

Sistema integral para gestión de RRHH de empresas mexicanas.

### Módulos disponibles:

- **Usuarios**: Autenticación, perfiles, roles
- **Empresas**: Gestión multi-empresa
- **Empleados**: Expedientes digitales, documentos
- **Contratos**: Laborales con renovaciones y adendas
- **Vacaciones**: Cálculo según Ley Federal del Trabajo
- **Prestaciones**: Planes y beneficios adicionales
- **Nómina**: Cálculo ISR, IMSS, percepciones/deducciones
- **Desempeño**: KPIs, evaluaciones 360°, matriz 9-box
- **Chat IA**: 93+ acciones disponibles via lenguaje natural
- **Integraciones**: Google Calendar, bancos
- **Reportes**: Excel, PDF

### Autenticación

Usar JWT Bearer token en el header:
```
Authorization: Bearer <access_token>
```

Obtener token en `/api/token/` con email y password.
Refrescar token en `/api/token/refresh/`.

### Validaciones Fiscales

El sistema valida documentos fiscales mexicanos:
- **RFC**: Persona física (13 chars) y moral (12 chars)
- **CURP**: 18 caracteres con entidad federativa
- **NSS**: 11 dígitos con dígito verificador IMSS
- **CLABE**: 18 dígitos bancarios
''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'TAGS': [
        {'name': 'auth', 'description': 'Autenticación JWT'},
        {'name': 'usuarios', 'description': 'Gestión de usuarios y perfiles'},
        {'name': 'empresas', 'description': 'Administración de empresas'},
        {'name': 'empleados', 'description': 'Expedientes de empleados'},
        {'name': 'contratos', 'description': 'Contratos laborales y adendas'},
        {'name': 'vacaciones', 'description': 'Gestión de vacaciones'},
        {'name': 'prestaciones', 'description': 'Planes de prestaciones'},
        {'name': 'nomina', 'description': 'Cálculo y gestión de nómina'},
        {'name': 'desempeno', 'description': 'Evaluaciones y KPIs'},
        {'name': 'chat', 'description': 'Chat IA con acciones'},
        {'name': 'integraciones', 'description': 'Google Calendar y otros'},
        {'name': 'reportes', 'description': 'Generación de reportes'},
        {'name': 'solicitudes', 'description': 'Solicitudes y aprobaciones'},
        {'name': 'notificaciones', 'description': 'Sistema de notificaciones'},
        {'name': 'documentos', 'description': 'Gestión documental'},
    ],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'filter': True,
    },
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# ========================================
# EMAIL CONFIGURATION
# ========================================
# En desarrollo: usa console backend (muestra emails en terminal)
# En producción: usa SMTP real
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)

# Configuración SMTP (para producción)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Remitente por defecto
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'RRHH Sistema <noreply@rrhh.local>')

# URL del frontend (para links en emails)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# ========================================
# GOOGLE CALENDAR CONFIGURATION
# ========================================
import json

# Cargar credenciales desde archivo JSON de Google
GOOGLE_CREDENTIALS_FILE = BASE_DIR / 'backend' / 'client_secret_470031425940-dfhf98q2qdn4ud5v0q8td7vo7d9poabt.apps.googleusercontent.com.json'

if GOOGLE_CREDENTIALS_FILE.exists():
    with open(GOOGLE_CREDENTIALS_FILE) as f:
        _google_creds = json.load(f)
        _web_creds = _google_creds.get('web', _google_creds.get('installed', {}))
        GOOGLE_CLIENT_ID = _web_creds.get('client_id', '')
        GOOGLE_CLIENT_SECRET = _web_creds.get('client_secret', '')
else:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')

GOOGLE_REDIRECT_URI = os.getenv(
    'GOOGLE_REDIRECT_URI',
    'http://localhost:8000/api/integraciones/google/callback/'
)
