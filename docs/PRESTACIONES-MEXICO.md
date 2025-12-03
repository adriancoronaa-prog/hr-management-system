# Prestaciones Laborales México - Referencia LFT

## Marco Legal

Este documento sirve como referencia para las prestaciones mínimas establecidas en la **Ley Federal del Trabajo (LFT)** de México, vigentes a partir de la reforma de enero 2023.

---

## 1. Vacaciones (Art. 76 LFT)

### Tabla de Días por Antigüedad (Reforma 2023)

| Años trabajados | Días de vacaciones (mínimo LFT) |
|-----------------|----------------------------------|
| 1 año | 12 días |
| 2 años | 14 días |
| 3 años | 16 días |
| 4 años | 18 días |
| 5 años | 20 días |
| 6 - 10 años | 22 días |
| 11 - 15 años | 24 días |
| 16 - 20 años | 26 días |
| 21 - 25 años | 28 días |
| 26 - 30 años | 30 días |
| 31 - 35 años | 32 días |

**Notas importantes:**
- Los días son **laborables**, no naturales
- El incremento es de **2 días por año** hasta llegar a 20 días
- A partir del 6° año, aumentan **2 días por cada 5 años** de servicio
- Las vacaciones deben disfrutarse dentro de los **6 meses siguientes** al cumplimiento del año de servicios (Art. 81 LFT)
- Mínimo **12 días continuos** obligatorios (Art. 78 LFT)

### Configuración JSON para el Sistema

```json
{
  "vacaciones_ley": {
    "1": 12,
    "2": 14,
    "3": 16,
    "4": 18,
    "5": 20,
    "6": 22,
    "11": 24,
    "16": 26,
    "21": 28,
    "26": 30,
    "31": 32
  }
}
```

### Ejemplo de Plan Superior a Ley (Ley + 3 días)

```json
{
  "vacaciones_empresa": {
    "1": 15,
    "2": 17,
    "3": 19,
    "4": 21,
    "5": 23,
    "6": 25,
    "11": 27,
    "16": 29,
    "21": 31,
    "26": 33,
    "31": 35
  }
}
```

---

## 2. Prima Vacacional (Art. 80 LFT)

### Mínimo Legal
- **25%** sobre los salarios correspondientes al periodo de vacaciones

### Cálculo

```
Prima Vacacional = Salario Diario × Días de Vacaciones × 0.25
```

**Ejemplo:**
- Salario diario: $500 MXN
- Días de vacaciones (año 1): 12 días
- Prima vacacional: $500 × 12 × 0.25 = **$1,500 MXN**

### Empresas con Prestaciones Superiores

| Nivel | Porcentaje |
|-------|------------|
| Ley | 25% |
| Bueno | 35-40% |
| Muy bueno | 50% |
| Excelente | 75-100% |

---

## 3. Aguinaldo (Art. 87 LFT)

### Mínimo Legal
- **15 días de salario** como mínimo
- Debe pagarse **antes del 20 de diciembre**
- Si no se cumplió el año completo, se paga la parte **proporcional**

### Cálculo

```
Aguinaldo Completo = Salario Diario × 15 días

Aguinaldo Proporcional = (Salario Diario × 15) × (Días trabajados / 365)
```

**Ejemplo proporcional:**
- Salario diario: $500 MXN
- Ingreso: 15 de marzo 2024
- Cálculo al 20 diciembre: 280 días trabajados
- Aguinaldo: ($500 × 15) × (280/365) = **$5,753.42 MXN**

### Empresas con Prestaciones Superiores

| Nivel | Días de aguinaldo |
|-------|-------------------|
| Ley | 15 días |
| Bueno | 20-25 días |
| Muy bueno | 30 días |
| Excelente | 40+ días |

**Nota:** Los trabajadores del gobierno federal reciben mínimo **40 días** de aguinaldo.

---

## 4. Prima Dominical (Art. 71 LFT)

### Mínimo Legal
- **25%** adicional sobre el salario diario ordinario
- Aplica cuando el trabajador labora en **domingo** y su día de descanso es otro día de la semana

### Cálculo

```
Prima Dominical = Salario Diario × 0.25
```

---

## 5. Días de Descanso Obligatorio (Art. 74 LFT)

### Días Festivos Oficiales

| Fecha | Motivo |
|-------|--------|
| 1 de enero | Año Nuevo |
| Primer lunes de febrero | Día de la Constitución |
| Tercer lunes de marzo | Natalicio de Benito Juárez |
| 1 de mayo | Día del Trabajo |
| 16 de septiembre | Día de la Independencia |
| Tercer lunes de noviembre | Día de la Revolución |
| 1 de diciembre (cada 6 años) | Transmisión del Poder Ejecutivo Federal |
| 25 de diciembre | Navidad |

**Pago por trabajar en día festivo:**
- Salario doble adicional al salario ordinario (Art. 75 LFT)
- Total = **3x el salario diario**

### Configuración JSON para el Sistema

```json
{
  "festivos_oficiales": [
    {"fecha": "01-01", "nombre": "Año Nuevo", "fijo": true},
    {"fecha": "primer_lunes_febrero", "nombre": "Día de la Constitución", "fijo": false},
    {"fecha": "tercer_lunes_marzo", "nombre": "Natalicio de Benito Juárez", "fijo": false},
    {"fecha": "01-05", "nombre": "Día del Trabajo", "fijo": true},
    {"fecha": "16-09", "nombre": "Día de la Independencia", "fijo": true},
    {"fecha": "tercer_lunes_noviembre", "nombre": "Día de la Revolución", "fijo": false},
    {"fecha": "25-12", "nombre": "Navidad", "fijo": true}
  ]
}
```

---

## 6. Otras Prestaciones de Ley

### Seguro Social (IMSS)

**Obligación del patrón:**
- Inscribir a los trabajadores en el IMSS
- Pagar cuotas obrero-patronales

**Cobertura:**
- Riesgos de trabajo
- Enfermedades y maternidad
- Invalidez y vida
- Retiro, cesantía y vejez
- Guarderías

### INFONAVIT

**Obligación del patrón:**
- Aportar 5% del salario del trabajador
- Permite acceso a créditos de vivienda

### Reparto de Utilidades (PTU) - Art. 117-131 LFT

- **10%** de las utilidades de la empresa
- Se reparte entre todos los trabajadores
- Pago máximo: **3 meses de salario** o promedio de PTU de últimos 3 años
- Fecha límite de pago: **30 de mayo**

---

## 7. Prestaciones Adicionales Comunes (No de Ley)

Estas prestaciones son beneficios que las empresas ofrecen de forma voluntaria:

### Económicas

| Prestación | Descripción típica |
|------------|-------------------|
| **Vales de despensa** | $1,000 - $3,000 MXN/mes |
| **Fondo de ahorro** | 5-13% del salario (empresa aporta igual) |
| **Bono de puntualidad** | $300 - $1,000 MXN/mes |
| **Bono de asistencia** | $300 - $1,000 MXN/mes |
| **Ayuda de transporte** | $500 - $2,000 MXN/mes |
| **Ayuda de comedor** | $50 - $100 MXN/día |
| **Bono de productividad** | Variable |

### Salud y Bienestar

| Prestación | Descripción típica |
|------------|-------------------|
| **Seguro de gastos médicos mayores** | Cobertura individual/familiar |
| **Seguro de vida** | 12-24 meses de salario |
| **Seguro dental** | Cobertura básica/amplia |
| **Seguro de visión** | Cobertura lentes/consultas |
| **Chequeo médico anual** | Check-up ejecutivo |

### Desarrollo

| Prestación | Descripción típica |
|------------|-------------------|
| **Capacitación** | Cursos, certificaciones |
| **Becas educativas** | % de colegiatura |
| **Días de estudio** | Permisos para exámenes |

### Tiempo

| Prestación | Descripción típica |
|------------|-------------------|
| **Días adicionales de vacaciones** | +3 a +10 días sobre ley |
| **Día de cumpleaños** | 1 día libre |
| **Viernes corto** | Salida 2-3pm |
| **Home office** | 1-5 días/semana |
| **Horario flexible** | Entrada/salida flexible |

---

## 8. Cálculo del Finiquito

Cuando termina la relación laboral, el trabajador tiene derecho a:

### Componentes del Finiquito

| Concepto | Cálculo |
|----------|---------|
| **Salario pendiente** | Días trabajados no pagados |
| **Aguinaldo proporcional** | (Salario diario × 15) × (días trabajados / 365) |
| **Vacaciones no disfrutadas** | Salario diario × días pendientes |
| **Prima vacacional** | 25% sobre vacaciones no disfrutadas |
| **Prima de antigüedad** | 12 días de salario por año (tope 2 salarios mínimos) |

### Prima de Antigüedad (Art. 162 LFT)

- **12 días de salario por cada año de servicio**
- El salario base está **topado a 2 salarios mínimos**
- Se paga en caso de:
  - Retiro voluntario con 15+ años de servicio
  - Despido (cualquier antigüedad)
  - Muerte del trabajador

**Ejemplo:**
- Antigüedad: 5 años
- Salario diario: $800 MXN (pero tope es $500 = 2 salarios mínimos aprox)
- Prima: 12 × 5 × $500 = **$30,000 MXN**

---

## 9. Jornadas de Trabajo (Art. 58-68 LFT)

| Jornada | Duración máxima |
|---------|-----------------|
| **Diurna** | 8 horas (6:00 - 20:00) |
| **Nocturna** | 7 horas (20:00 - 6:00) |
| **Mixta** | 7.5 horas |

### Tiempo Extra

| Tipo | Pago |
|------|------|
| Primeras 9 horas/semana | 200% (doble) |
| Excedente de 9 horas/semana | 300% (triple) |

---

## 10. Incapacidades

### Por Enfermedad General (IMSS)

| Periodo | Pago |
|---------|------|
| Días 1-3 | Sin pago (empresa puede cubrir) |
| Día 4 en adelante | 60% del salario (IMSS) |

**Duración máxima:** 52 semanas, prorrogables a 78

### Por Riesgo de Trabajo (IMSS)

- **100% del salario** desde el primer día
- Pagado por IMSS

### Por Maternidad (Art. 170 LFT)

- **12 semanas** con goce de sueldo (100%)
- 6 semanas antes + 6 semanas después del parto
- Transferibles hasta 4 semanas antes al después

### Por Paternidad (Art. 132 LFT)

- **5 días laborables** con goce de sueldo
- Por nacimiento o adopción

---

## Referencia Rápida - Valores para el Sistema

```python
# constantes_lft.py

VACACIONES_POR_ANTIGUEDAD = {
    1: 12, 2: 14, 3: 16, 4: 18, 5: 20,
    6: 22, 11: 24, 16: 26, 21: 28, 26: 30, 31: 32
}

PRIMA_VACACIONAL_MINIMA = 0.25  # 25%
AGUINALDO_MINIMO_DIAS = 15
PRIMA_DOMINICAL_MINIMA = 0.25  # 25%
PRIMA_ANTIGUEDAD_DIAS_POR_ANO = 12

FESTIVOS_FIJOS = [
    (1, 1),   # Año Nuevo
    (5, 1),   # Día del Trabajo
    (9, 16),  # Independencia
    (12, 25), # Navidad
]

JORNADA_MAXIMA_HORAS = {
    'diurna': 8,
    'nocturna': 7,
    'mixta': 7.5
}

HORAS_EXTRA_DOBLE_MAX_SEMANA = 9
```

---

## Actualizaciones

| Fecha | Cambio |
|-------|--------|
| Enero 2023 | Reforma vacaciones: mínimo 12 días (antes 6) |
| 2024 | Salario mínimo: $248.93 MXN diario (zona general) |

---

*Este documento es solo referencia. Consultar siempre la LFT vigente y/o un profesional legal para casos específicos.*
