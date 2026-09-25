# Criterio 3 · Optimización de costos

No se trata de "limitar tokens". Se trata de decidir, tarea por tarea, qué modelo hace falta y qué trabajo directamente no hay que pagar.

## 3.1 Las dos tareas de IA del ecosistema no son la misma tarea

| | **[8] Extraer y clasificar** | **[17] Redactar la propuesta** |
|---|---|---|
| Qué hace | Lee un correo y devuelve un JSON con 11 claves | Escribe el correo que una familia preocupada va a leer |
| Quién consume la salida | Un router (una máquina) | Una persona |
| Tolerancia al error de estilo | Total: el JSON es correcto o no lo es | Cero: el tono es el producto |
| Se ejecuta | En el **100 %** de las solicitudes | Solo en las **válidas y dentro de cobertura** |
| Modelo elegido | **gpt-5-nano** (`small`) | **Claude Haiku 4.5** |

La primera es una tarea de extracción estructurada con un contrato rígido y ejemplos en el prompt. Un modelo nano la resuelve. La segunda es la cara de Cuidda frente a una familia que está buscando quién cuide a su mamá: ahí el estilo sí es el entregable.

## 3.2 Medición real de tokens

Los prompts están en el blueprint y se pueden medir. La parte fija se contó sobre el texto del propio `.json`; la parte dinámica, sobre los datos reales de las tablas.

| Módulo | Prompt fijo | Datos inyectados | **Input total** | **Output** |
|---|---|---|---|---|
| [8] Clasificar | 492 tok | Cobertura (9 distritos) 138 + Catálogo (5 turnos) 90 + correo ~250 | **≈ 970 tok** | ≈ 150 tok (JSON de 11 claves) |
| [17] Redactar | 379 tok | Base de conocimiento (10 entradas atómicas) 774 + solicitud 40 | **≈ 1 190 tok** | ≈ 300 tok (tope de 600) |

## 3.3 Matriz de decisión

Precios públicos por millón de tokens, septiembre 2026:

| Modelo | Input | Output |
|---|---|---|
| gpt-5-nano | $0.05 | $0.40 |
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Claude Sonnet 5 | $2.00 | $10.00 |
| Claude Opus 5 | $5.00 | $25.00 |

Costo por llamada, con los tokens medidos arriba:

| | Clasificar (970 in / 150 out) | Redactar (1 190 in / 300 out) |
|---|---|---|
| gpt-5-nano | **$0.000109** | $0.000180 |
| Claude Haiku 4.5 | $0.001720 | **$0.002690** |
| Claude Sonnet 5 | $0.003440 | $0.005380 |
| Claude Opus 5 | $0.008600 | $0.013450 |

Proyección sobre **1 000 solicitudes entrantes**, con la distribución real que arrojó el test de estrés (60 % válidas, 20 % fuera de cobertura, 20 % con datos faltantes). Solo las válidas llegan al redactor:

| Escenario | Clasificar | Redactar | **Total / 1 000** | vs. elegido |
|---|---|---|---|---|
| **Arquitectura elegida** (nano + Haiku, con ruteo) | 1 000 × $0.000109 = $0.11 | 600 × $0.002690 = $1.61 | **$1.72** | — |
| Todo nano, con ruteo | $0.11 | 600 × $0.000180 = $0.11 | $0.22 | −87 % **pero inaceptable** |
| Todo Haiku, con ruteo | 1 000 × $0.001720 = $1.72 | $1.61 | $3.33 | +94 % |
| Todo Haiku, sin ruteo | $1.72 | 1 000 × $0.002690 = $2.69 | $4.41 | +156 % |
| Todo Sonnet 5, sin ruteo | $3.44 | $5.38 | $8.82 | +413 % |
| Todo Opus 5, sin ruteo | $8.60 | $13.45 | $22.05 | +1 182 % |

### De dónde sale el ahorro

Contra la alternativa más razonable que alguien elegiría sin pensarlo mucho — **un solo modelo bueno y barato para todo, sin ruteo: $4.41** — el ahorro es de **$2.69 por cada 1 000 solicitudes, un 61 %**, y se descompone en dos decisiones independientes:

| Decisión | Ahorro / 1 000 | Peso |
|---|---|---|
| Bajar el **clasificador** a nano (la salida es JSON, no prosa) | $1.61 | 60 % del ahorro |
| **No redactar** lo que no se va a enviar (rutas A y B cortan antes de [17]) | $1.08 | 40 % del ahorro |

Contra "todo Sonnet 5 sin ruteo" el ahorro es del **80.5 %**; contra "todo Opus 5", del **92.2 %**.

### Por qué no "todo nano"

Es la fila más barata de la tabla y está descartada a propósito. El redactor escribe el correo que recibe una familia, y con nano aparecen tres fallas que en este negocio cuestan más que los $1.50 ahorrados: inventa montos cuando la tarifa no está explícita, promete disponibilidad que Cuidda no puede garantizar, y cae en el tono corporativo vacío que el prompt prohíbe. El costo de un correo mal escrito no es de API: es una familia que no vuelve.

## 3.4 Límite de tokens de salida

El módulo `ai-tools:Ask` de Make AI Toolkit **no expone un parámetro de max tokens** (sus únicos parámetros son la conexión y el modelo). Decirlo así es más útil que fingir un campo que no existe. El tope se aplica donde sí se puede:

1. **En el prompt, con un valor leído de la base.** La regla 6 del redactor dice literalmente: *"Tope duro de salida: `{{ get(map(3.array; "Valor"; "Clave"; "max_tokens_propuesta"); 1) }}` tokens, que son unas 200 palabras. Si te estás pasando, corta, no resumas a la mitad."* El valor vive en `Configuracion.max_tokens_propuesta = 600`: subirlo o bajarlo es editar una fila de Airtable.
2. **En el clasificador, acotando la salida por diseño.** Devuelve 11 claves y `resumen` tiene tope de 30 palabras. La salida no puede crecer.
3. **En el contexto de entrada.** Los tres `Search Records` que alimentan los prompts tienen `maxRecords: 20`. La cobertura, el catálogo y la base de conocimiento no pueden inflar el prompt sin límite aunque las tablas crezcan.

## 3.5 El identificador del modelo: lo que quisimos hacer y lo que se puede

La intención era leer el identificador del modelo de `Configuracion` igual que todo lo demás:

```
{{ get(map(3.array; "Valor"; "Clave"; "modelo_id_clasificacion"); 1) }}
```

**No funciona, y vale la pena contarlo.** El campo `Model` de `ai-tools:Ask` no es un campo mapeable del bundle: es un parámetro de configuración del módulo. Make no evalúa IML ahí en tiempo de ejecución, así que el escenario intentaba invocar un modelo llamado literalmente `{{ get(map(3.array; ...` y el módulo fallaba. Lo detectamos en la tabla `Log de errores`, en el campo `Detalle`, que trae el mensaje textual del proveedor — exactamente para lo que se diseñó esa tabla.

Así que el identificador va literal en los dos módulos, y lo que sí es dinámico es el **nombre legible** del modelo, que se lee de `Configuracion` y se escribe en `Solicitudes.Modelo usado` en cada solicitud. El costo real sigue siendo auditable solicitud por solicitud desde el dashboard; cambiar de modelo son dos ediciones en Make en vez de una celda en Airtable.

Preferimos dejar esto escrito antes que mostrar una captura del blueprint con la expresión adentro y no decir que no se evalúa.

## 3.6 El costo de no hardcodear nada

Hay que decirlo: leer `Configuracion`, `Cobertura` y `Catalogo de turnos` en cada corrida cuesta **6 de las operaciones** del Escenario 1. Es el precio de que ningún valor esté escrito dentro del flujo, y se paga a conciencia.

El siguiente paso natural, cuando el volumen lo justifique, es cachear esas tres tablas en un **Make Data Store** refrescado una vez al día: mismas garantías de no-hardcoding, seis operaciones menos por solicitud. No está implementado hoy porque a este volumen la diferencia es de centavos y la lectura directa es más fácil de auditar para el profesor y para el equipo.

---

**Fuentes de precios:** [Pricing | OpenAI API](https://developers.openai.com/api/docs/pricing) · [OpenAI API Pricing — pricepertoken](https://pricepertoken.com/pricing-page/provider/openai) · [Claude Haiku 4.5 — Anthropic](https://www.anthropic.com/claude/haiku) · [Claude API Pricing — BenchLM](https://benchlm.ai/anthropic/api-pricing)
