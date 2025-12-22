# Guía de Deploy - Railway

Sistema RRHH desplegado como monorepo con 2 servicios en Railway.

## Arquitectura

```
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│     Backend     │
│   (Next.js)     │     │    (Django)     │
│  Port: 3000     │     │   Port: 8000    │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   PostgreSQL    │
                        │   (Railway)     │
                        └─────────────────┘
```

## Pre-requisitos

1. Cuenta en [Railway](https://railway.app)
2. Repositorio en GitHub conectado a Railway
3. PostgreSQL provisionado en Railway

---

## Paso 1: Crear Proyecto en Railway

1. Ve a Railway Dashboard → **New Project**
2. Selecciona **Deploy from GitHub repo**
3. Conecta tu repositorio

---

## Paso 2: Configurar PostgreSQL

1. En el proyecto, click **+ New** → **Database** → **PostgreSQL**
2. Railway creará la variable `DATABASE_URL` automáticamente

---

## Paso 3: Configurar Backend (Django)

### 3.1 Crear servicio

1. Click **+ New** → **GitHub Repo**
2. Selecciona el mismo repo
3. En **Settings**:
   - **Root Directory**: `backend`
   - **Build Command**: (dejar vacío, usa Nixpacks)
   - **Start Command**: (usa el de railway.json)

### 3.2 Variables de entorno

Configura estas variables en **Variables**:

| Variable | Valor | Requerida |
|----------|-------|-----------|
| `SECRET_KEY` | (generar con `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) | ✅ |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | ✅ |
| `ALLOWED_HOSTS` | `${{RAILWAY_PUBLIC_DOMAIN}}` | ✅ |
| `CORS_ALLOWED_ORIGINS` | `https://tu-frontend.railway.app` | ✅ |
| `CSRF_TRUSTED_ORIGINS` | `https://tu-frontend.railway.app` | ✅ |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | ✅ (referencia) |
| `ANTHROPIC_API_KEY` | tu-api-key | ✅ |
| `FRONTEND_URL` | `https://tu-frontend.railway.app` | ⚠️ |

### 3.3 Vincular PostgreSQL

1. En Variables del backend, click **+ Add Variable Reference**
2. Selecciona `DATABASE_URL` de PostgreSQL

---

## Paso 4: Configurar Frontend (Next.js)

### 4.1 Crear servicio

1. Click **+ New** → **GitHub Repo**
2. Selecciona el mismo repo
3. En **Settings**:
   - **Root Directory**: `frontend`
   - **Build Command**: (dejar vacío, usa Nixpacks)
   - **Start Command**: `node server.js`

### 4.2 Variables de entorno

| Variable | Valor | Requerida |
|----------|-------|-----------|
| `NEXT_PUBLIC_API_URL` | `https://tu-backend.railway.app` | ✅ |

---

## Paso 5: Deploy Inicial

1. Haz push a la rama `main`
2. Railway detectará cambios y desplegará automáticamente
3. Verifica los logs de cada servicio

### Verificar Backend

```bash
curl https://tu-backend.railway.app/api/health/
# Debe retornar: {"status": "healthy", "service": "rrhh-backend", "database": "connected"}
```

### Verificar Frontend

Navega a `https://tu-frontend.railway.app` - debe cargar la página de login.

---

## Paso 6: Migraciones y Datos Iniciales

El backend ejecuta migraciones automáticamente en cada deploy (ver `railway.json`).

Para cargar datos de prueba (solo primera vez):

1. Ve a Railway → Backend → **Shell**
2. Ejecuta:
   ```bash
   python manage.py seed_data
   ```

---

## Dominios Personalizados

1. En cada servicio → **Settings** → **Domains**
2. Click **+ Custom Domain**
3. Configura CNAME en tu DNS:
   ```
   api.tudominio.com  → CNAME → tu-backend.railway.app
   app.tudominio.com  → CNAME → tu-frontend.railway.app
   ```
4. Actualiza las variables de entorno con los nuevos dominios

---

## Monitoreo

### Health Check

- Backend: `GET /api/health/` → `{"status": "healthy"}`
- Frontend: Railway usa `/` por defecto

### Logs

- Railway Dashboard → Servicio → **Logs**
- O usa CLI: `railway logs`

---

## Troubleshooting

### Error: "SECRET_KEY must be set"

La variable `SECRET_KEY` no está configurada. Genera una:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Error: "CORS blocked"

Verifica que `CORS_ALLOWED_ORIGINS` incluya el dominio exacto del frontend (con https://).

### Error: "Database connection failed"

1. Verifica que `DATABASE_URL` esté referenciando correctamente a PostgreSQL
2. Revisa que PostgreSQL esté corriendo en Railway

### Build fallido en Frontend

Si el build de Next.js falla:

1. Verifica que `output: "standalone"` esté en `next.config.ts`
2. Revisa los logs de build para errores de TypeScript

---

## Costos Estimados (Railway)

| Servicio | RAM | Costo Aprox. |
|----------|-----|--------------|
| Backend | 512MB | ~$5/mes |
| Frontend | 512MB | ~$5/mes |
| PostgreSQL | 1GB | ~$5/mes |
| **Total** | | **~$15/mes** |

Railway ofrece $5 de crédito gratis al mes.

---

## Actualizar en Producción

```bash
# Desde tu máquina local
git add .
git commit -m "feat: nueva funcionalidad"
git push origin main

# Railway despliega automáticamente
```
