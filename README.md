# RRHH Multi-empresa

Sistema integral de Recursos Humanos para empresas mexicanas con:
- 🤖 **Chat con IA** como interfaz principal (Claude API)
- 💰 **Cálculo de nómina** según LFT, ISR e IMSS
- 🏖️ **Gestión de vacaciones** con cálculo automático
- 📄 **Procesamiento de documentos** (INE, CURP, CSF)
- 🔐 **3 niveles de acceso**: Admin, RRHH, Empleado

## Roles y Permisos

| Funcionalidad | Admin | RRHH | Empleado |
|---------------|:-----:|:----:|:--------:|
| Gestionar empresas | ✅ | ❌ | ❌ |
| Ver empresas | ✅ | ✅* | ❌ |
| Crear/editar empleados | ✅ | ✅* | ❌ |
| Ver empleados | ✅ | ✅* | Solo él |
| Procesar nómina | ✅ | ✅* | ❌ |
| Ver recibos | ✅ | ✅* | Solo suyos |
| Solicitar vacaciones | ✅ | ✅ | ✅ |
| Aprobar vacaciones | ✅ | ✅* | ❌ |
| Chat con IA | ✅ | ✅ | ✅ (limitado) |

*Solo empresas asignadas

## Instalación Local

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Editar con tus valores
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173

## Variables de Entorno (.env)

```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
USE_SQLITE=True
ANTHROPIC_API_KEY=sk-ant-api...  # Para chat IA
```

## Despliegue

### Railway (Recomendado)
1. Conectar repositorio
2. Agregar PostgreSQL
3. Configurar variables de entorno
4. Deploy automático

### Variables Producción
```env
DJANGO_SECRET_KEY=clave-segura
DEBUG=False
DATABASE_URL=postgres://...
ANTHROPIC_API_KEY=sk-ant-api...
```

## Comandos del Chat IA

- "Crea empresa Tacos El Güero con RFC TAC201015AB1"
- "Alta empleado Juan Pérez, sueldo $600 diarios"
- "¿Cuántas vacaciones le tocan a María?"
- "Calcula aguinaldo de Pedro"
- "Procesa nómina quincenal"

## API Docs

Swagger: http://localhost:8000/api/docs/

---
Desarrollado para gestión de RRHH en México 🇲🇽
