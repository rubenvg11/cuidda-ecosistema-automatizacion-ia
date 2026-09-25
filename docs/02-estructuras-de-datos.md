# Criterio 2 · Estructuras de datos documentadas

Dos cosas distintas: cómo está modelada la base, y qué forma tiene el dato mientras viaja entre nodos.

## 2.1 El modelo en Airtable · base `Cuidda · Operaciones`

`appxzAU6Buul0hoGw`

| Tabla | ID | Rol |
|---|---|---|
| **Solicitudes** | `tbloHJ3bW32Tk892I` | El caso. Una fila por familia que escribió. |
| **Cobertura** | `tblU7qF4h7IVgwGjQ` | Los 9 distritos de Trujillo, si hay personal y cuánto recarga la movilidad. |
| **Catalogo de turnos** | `tblj7zkYXiS7pC3ay` | Los 5 turnos con su horario, tarifa y notas operativas. |
| **Base de conocimiento** | `tblUNJi1OKLof4xeC` | 10 entradas atómicas verificadas. Es el RAG. |
| **Log de errores** | `tblY66MlpoRAAdtfc` | Toda falla, de API o de validación, queda escrita acá. |
| **Configuracion** | `tblcfTQrNzGIs110O` | Pares clave-valor leídos en runtime. Es lo que hace que no haya datos hardcodeados. |

### Las relaciones (y por qué existen)

```
                    ┌──────────────────────┐
                    │      Cobertura       │
                    │  Distrito · Cubierto │
                    │  Recargo movilidad   │
                    └──────────┬───────────┘
                               │ link
                    ┌──────────▼───────────┐          ┌────────────────────────┐
                    │     Solicitudes      │◄─ link ──│  Catalogo de turnos    │
                    │  Codigo · Estado     │          │  Turno · Horario       │
                    │  Prioridad · Monto   │          │  Tarifa soles          │
                    └──────────────────────┘          └────────────────────────┘

       lookups que bajan a Solicitudes:
         Cubierto (from Distrito) · Recargo movilidad soles (from Distrito)
         Horario (from Turno)     · Tarifa soles (from Turno)
```

El requisito de la consigna era **evitar datos aislados**, y acá se cumple de forma concreta: en `Solicitudes` no hay una columna de texto que diga "Huanchaco" y otra que diga "20". Hay un **campo vinculado** al record real de `Cobertura`, y el recargo llega por **lookup**. Si mañana Huanchaco pasa a recargo 25, las solicitudes existentes lo reflejan sin tocar nada; si Huanchaco deja de tener cobertura, el dato viaja solo.

Lo mismo con los turnos: la tarifa de "Noche" vive en un único lugar. El campo `Monto estimado` de una solicitud se puede auditar contra `Tarifa soles (from Turno)` + `Recargo movilidad soles (from Distrito)` sin salir de la fila.

### Ciclo de vida de una solicitud

`Estado` es una máquina de estados, no una etiqueta suelta:

```
   Pendiente ──► Procesado por IA ──► Aprobado ──► Enviado
                        │                  ▲
                        │                  └── una persona, a mano
                        ├──► Rechazado   (fuera de cobertura)
                        └──► Error       (falla registrada)
```

`Enviado` es un estado absorbente: es lo que corta el loop del Escenario 2.

## 2.2 Los esquemas JSON de transferencia

Cada salto entre nodos tiene un contrato explícito. Están en [`schemas/`](../schemas/) como JSON Schema 2020-12, válidos y ejecutables contra un validador.

| # | Archivo | Qué contrato describe |
|---|---|---|
| 01 | [`01-gmail-a-clasificador`](../schemas/01-gmail-a-clasificador.schema.json) | Correo entrante → módulo `[8]`. Incluye la lista de campos **descartados** por minimización de datos. |
| 02 | [`02-clasificacion-ia`](../schemas/02-clasificacion-ia.schema.json) | **El contrato central**: las 12 claves que el clasificador debe devolver, la tabla de ruteo y tres ejemplos (camino feliz, fuera de cobertura y camino infeliz). |
| 03 | [`03-solicitud-airtable`](../schemas/03-solicitud-airtable.schema.json) | El record escrito en `Solicitudes`, indexado por `fieldId` y no por nombre. |
| 04 | [`04-log-de-errores`](../schemas/04-log-de-errores.schema.json) | El record de error, con la directiva (`Break` / `Resume` / sin reintento) que corresponde a cada tipo. |
| 05 | [`05-airtable-a-escenario-2`](../schemas/05-airtable-a-escenario-2.schema.json) | El handoff entre escenarios. Airtable no es solo destino: es el bus de mensajes. |
| 06 | [`06-canales-de-salida`](../schemas/06-canales-de-salida.schema.json) | Payloads de Slack y Gmail, con el mapeo de Thread ID en cada uno. |

### El contrato que más importa

El módulo `[8]` devuelve texto. El módulo `[9]` lo parsea. El router `[10]` decide. Si ese texto no es JSON válido con esas 12 claves exactas, todo lo que sigue se cae. Por eso el prompt lo declara clave por clave y el esquema lo fija con `additionalProperties: false` y enums cerrados:

```json
{
  "familia": "Rosa Mendoza",
  "email": "rosa.mendoza@example.com",
  "telefono": "987654321",
  "distrito_mencionado": "Huanchaco",
  "distrito": "Huanchaco",
  "turno": "Noche",
  "prioridad": "Alta",
  "resumen": "Señora de 78 años con fractura de cadera, alta hospitalaria en 48 horas, necesita apoyo nocturno.",
  "monto_estimado": 190,
  "datos_completos": "si",
  "distrito_cubierto": "si",
  "faltantes": ""
}
```

Hay **dos claves de distrito y no una**, y la diferencia es el corazón del ruteo. `distrito_mencionado` es lo que escribió la familia, sea lo que sea: *"Laredo"*, *"el centro de Trujillo"*, *"acá por Moche"*. `distrito` solo tiene valor si ese lugar aparece en la lista de distritos con cobertura que la base inyectó en el prompt. De ahí sale `distrito_cubierto`, que no es un juicio de la IA sino la consecuencia de haber encontrado o no una coincidencia.

Esto también es lo que permite que un correo completo de un distrito sin cobertura caiga en la **ruta B** (se le responde) y no en la **ruta A** (dato faltante): `datos_completos` mira `distrito_mencionado`, no `distrito`.

`telefono` sale **sin prefijo y solo con dígitos** a propósito: el prefijo lo pone Make leyendo `Configuracion.prefijo_telefono_pais`, y el resultado se escribe como `+51987654321` en un campo de tipo *Número de teléfono*. Así el `+` no se pierde y el formato E.164 no depende de que la IA se acuerde de ponerlo.

## 2.3 Escritura por ID de campo

Make escribe usando el `fieldId` de Airtable (`fld…`), nunca el nombre visible:

```json
"record": {
  "fldswL3l4BgSrPlPr": "SOL-{{formatDate(now; \"YYYYMMDD-HHmmss\")}}",
  "fld8OQzLKX51uSjDw": "{{9.familia}}",
  "fldtI5sKssoSkCH7G": ["{{9.distrito}}"]
}
```

Renombrar "Familia" a "Nombre de la familia" en Airtable no rompe nada. Es la diferencia entre un flujo que sobrevive a que alguien ordene la base y uno que se cae el martes siguiente.
