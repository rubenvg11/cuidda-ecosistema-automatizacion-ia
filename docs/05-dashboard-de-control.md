# Criterio 5 · Dashboard de control

**Panel público:** https://rubenvg11.github.io/cuidda-ecosistema-automatizacion-ia/

La consigna aclaraba que esto es más que el link a la base: tiene que ser un panel de control. El panel es una página propia, con la identidad de Cuidda, que explica qué significa cada número y **embebe las vistas de Airtable en vivo**. No hay copias ni cachés: lo que se ve es la misma fila que el flujo acaba de escribir.

## Los tres paneles

| Panel | Vista compartida | Qué muestra |
|---|---|---|
| **1 · Pipeline de solicitudes** | [`shrpJFMWZ6SJe51ZU`](https://airtable.com/appxzAU6Buul0hoGw/shrpJFMWZ6SJe51ZU) | Todas las solicitudes agrupadas por `Estado`, con distrito, turno, prioridad, monto y modelo usado. El encabezado de cada grupo es el contador de ese estado. |
| **2 · Cola de aprobación humana** | [`shrMEr61iDjfBKKat`](https://airtable.com/appxzAU6Buul0hoGw/shrMEr61iDjfBKKat) | Filtrada por `Estado = "Procesado por IA"`: lo que espera una decisión de una persona. |
| **3 · Errores por tipo** | [`shrQMSuA6fTTzrltH`](https://airtable.com/appxzAU6Buul0hoGw/shrQMSuA6fTTzrltH) | `Log de errores` agrupado por `Tipo de error`, con el nodo exacto que falló. |

## Los cuatro indicadores

| Indicador | Cómo se calcula | Dónde se lee |
|---|---|---|
| Solicitudes por estado | `count(Solicitudes)` agrupado por `Estado` | Panel 1 · encabezado de cada grupo |
| Cola de aprobación humana | `count(Solicitudes)` donde `Estado = "Procesado por IA"` | Panel 2 · contador inferior |
| Monto en juego | `sum(Monto estimado)` | Panel 1 · barra de resumen |
| **Tasa de errores** | `count(Log de errores) ÷ (count(Solicitudes) + count(Log · "Dato faltante")) × 100` | Panel 3 ÷ Panel 1 |

### Por qué el denominador de la tasa de errores es raro

Una solicitud con datos faltantes **nunca llega a crear una fila** en `Solicitudes`: muere en la ruta A y solo deja rastro en `Log de errores`. Si se dividiera por las solicitudes creadas, esos casos desaparecerían del denominador y la tasa quedaría artificialmente baja — justo en el escenario donde más importa que no lo esté. Sumarlos es lo que hace que el número signifique lo que uno cree que significa: *de cada 100 correos que entraron, cuántos terminaron mal*.

## Minimización de datos en el panel

El panel es público, así que las vistas compartidas ocultan **9 campos** de `Solicitudes`: `Familia`, `Email`, `Telefono`, `Mensaje original`, `Resumen IA`, `Propuesta generada`, `Hilo Gmail`, `Message ID Gmail` y `Slack ts`. En `Log de errores` se oculta `Detalle`, porque ahí sí puede aparecer el correo de un remitente.

Queda visible exactamente lo que un panel de control necesita: el código, la fecha, el distrito, el turno, la prioridad, el monto, el modelo y el estado. **Ni un dato personal.**

## Cómo está hecho

La página es un único `index.html` sin dependencias más que las tipografías de Cuidda (Comfortaa y Plus Jakarta Sans). Las vistas se incrustan con el endpoint de embed de Airtable:

```html
<iframe src="https://airtable.com/embed/appxzAU6Buul0hoGw/shrpJFMWZ6SJe51ZU"></iframe>
```

Se publica con **GitHub Pages** desde la raíz de este mismo repositorio, así que el panel y el código que lo genera viven juntos y no pueden desincronizarse.
