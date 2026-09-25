# Criterio 4 · Seguridad y resiliencia

Tres preguntas: qué datos toca el sistema, qué pasa cuando algo se rompe, y quién autoriza lo que sale hacia afuera.

## 4.1 Minimización de datos

Cuidda maneja datos de salud de personas mayores. El principio es simple: **cada capa recibe lo mínimo que necesita para hacer su trabajo, y nada más.**

| Capa | Qué recibe | Qué se descarta |
|---|---|---|
| Trigger Gmail → clasificador | `subject`, `fromName`, `fromEmail`, `fullTextBody`, `threadId`, `headers.message-id` | `htmlBody`, `cc`, `bcc`, `to`, `labelIds`, `snippet`, adjuntos, `sizeEstimate`, `historyId` |
| Clasificador → Airtable | Las 11 claves del contrato JSON | El correo nunca se reenvía crudo a la IA de redacción |
| Redactor (RAG) | Distrito, turno, monto, resumen y la base de conocimiento | **No recibe el correo original, ni el email, ni el teléfono de la familia** |
| Slack | Nombre, prioridad, distrito, turno, monto y la propuesta | **No recibe el email ni el teléfono de la familia** |
| Dashboard público | Código, fecha, distrito, turno, prioridad, monto, modelo, estado | **9 campos ocultos**: Familia, Email, Teléfono, Mensaje original, Resumen IA, Propuesta generada, Hilo Gmail, Message ID Gmail, Slack ts |

Dos decisiones vale la pena subrayar:

- **El redactor no ve datos de contacto.** Le llega distrito, turno, monto y resumen. No necesita el correo ni el teléfono para escribir la propuesta, así que no los recibe. Si mañana el proveedor de IA cambia, lo que nunca salió de Airtable sigue sin salir.
- **El panel público no tiene ni un dato personal.** La vista compartida de `Log de errores` oculta el campo `Detalle` justamente porque ahí sí puede aparecer un correo de remitente. El panel muestra el tipo de error, el módulo y el escenario, que es todo lo que un panel de control necesita.

Además: ninguna API key vive dentro del flujo. Las cuatro conexiones (Airtable, Gmail, Slack, Make AI) son credenciales OAuth gestionadas por Make y referenciadas por id numérico (`__IMTCONN__`). El blueprint que se publica en el repo contiene ids de conexión, **no secretos**. El video demo oculta las pantallas de credenciales.

## 4.2 Rutas de error

Hay **cinco** handlers de error repartidos en los dos escenarios, y ninguno hace lo mismo que el otro, porque los fallos no son iguales.

### Escenario 1

**[8] IA · Extraer y clasificar → `Break` con reintento**

```
onerror → [8E] Airtable · Registrar fallo de la IA   (Log de errores, Tipo = "Fallo de API de IA")
        → [8E] Slack · Alertar fallo de la IA        (#operaciones, con el error textual)
        → [8E] Break · Detener con reintento         (retry: 3 intentos, cada 15 s)
```

Si el clasificador no responde no hay nada que hacer aguas abajo: sin JSON no hay ruta. `Break` congela la ejecución en *Incomplete executions* y Make la reintenta sola. No se escribe ninguna solicitud a medias. Esto es exactamente lo que pedía la consigna: **el sistema registra un error si la API de IA falla**, y además lo avisa por el canal donde está el equipo.

**[17] IA · Redactar propuesta → `Resume`**

```
onerror → [17E] Airtable · Registrar fallo de redaccion
        → [17E] Resume · Continuar con aviso
                  answer = "PROPUESTA NO GENERADA - la API de IA fallo. Revisar a mano antes de aprobar."
```

Acá la decisión es la contraria y es deliberada. La solicitud de una familia ya fue validada: perderla porque el redactor se cayó sería el peor resultado posible. `Resume` inyecta un texto de aviso y el flujo sigue: la solicitud se crea igual en Airtable, y el mensaje que llega a Slack dice en el cuerpo que la propuesta no se generó. Una persona la escribe a mano y aprueba. **Preferimos una propuesta vacía y visible antes que una solicitud perdida en silencio.**

**[11] Router ruta A → registro sin reintento.** Un dato faltante no es un fallo de sistema, es un correo incompleto. Reintentar no lo arregla. Se registra en `Log de errores` con la lista exacta de lo que faltó y se avisa por Slack.

### Escenario 2

**[7] Gmail · Enviar propuesta → `Break` con reintento**

```
onerror → [7E] Airtable · Registrar fallo de envio
        → [7E] Slack · Alertar fallo de envio
        → [7E] Break · Detener con reintento (3 × 15 s)
```

Lo importante es lo que **no** pasa: como `Break` detiene el flujo, el módulo [8] nunca corre, así que el `Estado` se queda en `Aprobado`. El registro sigue cumpliendo la fórmula del trigger y vuelve a entrar cuando Gmail se recupere. **Nunca se marca como "Enviado" un correo que no salió.**

**[9] Slack · Confirmar envío → `Resume`.** El correo ya salió y el estado ya se cerró. Que Slack no conteste es molesto, no grave: `Resume` deja constancia y el flujo termina bien.

Los dos escenarios tienen **Store incomplete executions = Yes** (`"dlq": true` en el blueprint), que es el requisito técnico para que la directiva `Break` con reintento funcione.

## 4.3 Punto de validación humana (HITL)

El sistema **no puede** escribirle a una familia por su cuenta. La frontera es física, no una convención:

1. El Escenario 1 escribe la solicitud con `Estado = "Procesado por IA"` y `Aprobado por Humano = false`. Siempre. No hay rama que lo ponga en true.
2. Publica en Slack la propuesta completa con el código de la solicitud y la frase *"Nada sale al cliente hasta que alguien marque Aprobado por Humano y ponga el Estado en Aprobado en Airtable"*.
3. El Escenario 2 **solo existe** para registros que cumplen `AND({Aprobado por Humano} = 1, {Estado} = "Aprobado")`. Es la fórmula del trigger, no un filtro posterior: los registros no aprobados ni siquiera entran al flujo.

Hacen falta **dos acciones humanas distintas** (marcar la casilla y cambiar el estado) para que un correo salga. Un clic accidental en la casilla no dispara nada.

## 4.4 Check de seguridad

**Filtro para evitar loops infinitos.** El Escenario 2 termina poniendo `Estado = "Enviado"`. Eso toca el campo `Modificado`, que es el trigger field, así que el registro vuelve a pasar por el trigger — pero ya no cumple la fórmula, porque `Estado` dejó de ser `"Aprobado"`. El ciclo se corta solo. No depende de un contador, ni de un delay, ni de una lista de procesados: **la condición de entrada deja de ser verdadera por efecto de la propia acción**. Es la forma más difícil de romper por accidente.

**Comparación de tipos correcta en los filtros.** Las tres rutas del Escenario 1 comparan texto contra texto con `text:equal` sobre dos banderas que la IA devuelve como enum cerrado (`"si"` / `"no"`), nunca con `notequal` sobre un campo libre:

| Ruta | Condición |
|---|---|
| A · Dato faltante | `datos_completos = "no"` |
| B · Fuera de cobertura | `datos_completos = "si"` **y** `distrito_cubierto = "no"` |
| C · Solicitud válida | `datos_completos = "si"` **y** `distrito_cubierto = "si"` |

Son mutuamente excluyentes y cubren todo el espacio de valores: ningún bundle puede caer en dos rutas ni quedarse sin ninguna. *(Esto corrige directamente la observación del profesor sobre el filtro de la ruta "Baja", donde un `notequal` se solapaba con la ruta "Alta".)*

**El AND del blueprint se escribe de una sola forma, y no es la intuitiva.** Esto costó una tarde entera de test y merece quedar escrito. En el JSON de un blueprint de Make, el campo `conditions` es un array de arrays: el **array externo es un OR** y el **interno es un AND**.

```json
"conditions": [[c1], [c2]]     // c1 O c2      ← lo que parece un AND y no lo es
"conditions": [[c1, c2]]       // c1 Y c2      ← el AND de verdad
```

Escrito de la primera forma, la ruta B pasaba a ser *"datos_completos = si **o** distrito_cubierto = no"*, que es verdadera casi siempre: **todas** las solicitudes se registraban además como rechazadas y el test de estrés creaba dos filas por corrida. El síntoma en History era claro una vez que se sabía qué mirar — 17 operaciones donde la ruta C sola son 15 — pero el blueprint se veía perfectamente razonable.

La forma de verificarlo no es leer el JSON: es abrir el filtro en la UI de Make después de importar. Si entre las dos condiciones dice **or** en vez de **and**, el blueprint está mal aunque el escenario corra sin errores. Es la clase de bug que no rompe nada, solo hace lo incorrecto en silencio.

En el router del Escenario 2 el problema era distinto: había que preguntar si un campo de texto largo está vacío. En vez de comparar el campo contra `""` — que es donde se cuelan los espacios y los saltos de línea — se normaliza primero y se compara contra un enum:

```
{{if(length(trim(1.`Propuesta generada`)) = 0; "vacia"; "lista")}}
```

Ruta A pregunta `= "vacia"`, ruta B pregunta `= "lista"`. Texto contra texto, dos valores posibles, sin ambigüedad.

**Prompt dinámico con variables del sistema.** Ningún prompt tiene datos fijos. La ciudad, la moneda, la firma, las horas de vigencia y el tope de tokens salen de `Configuracion`; la cobertura, el catálogo de turnos y la base de conocimiento salen de sus tablas y se inyectan agregados. Si mañana Cuidda abre en Chiclayo, se agrega la fila y el prompt cambia solo.

## 4.5 Lo que todavía no está resuelto

Un informe que solo dice lo que funciona no sirve para operar. Tres cosas quedan abiertas:

- **El plan Free de Make puede sustituir el modelo.** El propio módulo avisa: *"Some models are available only on Make paid plans. If you're on the free plan or a trial, your scenario will run using a free model."* Es decir que la elección de Claude Haiku 4.5 se respeta recién en plan pago. En Free el costo de IA es cero pero la calidad de redacción no está garantizada, y el campo `Modelo usado` registra lo que el escenario pidió, no necesariamente lo que Make ejecutó.
- **No hay borrado ni retención automática.** Los correos originales quedan en `Mensaje original` indefinidamente. Para un sistema que maneja datos de salud, lo correcto es una política de retención (por ejemplo, vaciar `Mensaje original` a los 90 días de `Fecha envio`). Es una automatización más, no está construida.
- **El `Motivo de rechazo` lo escribe la máquina, no la persona.** Cuando un humano decide no aprobar una propuesta, hoy no hay campo donde deje por qué. Es el primer agujero que taparía antes de poner esto en producción.
