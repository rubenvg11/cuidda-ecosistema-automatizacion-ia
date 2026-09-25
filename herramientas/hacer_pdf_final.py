# -*- coding: utf-8 -*-
"""Entrega Final · Cuidda — Ecosistema de Automatizacion IA Autonomo."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, Preformatted, Image,
                                KeepTogether, PageBreak)

NAVY = colors.HexColor("#022454")
TEAL = colors.HexColor("#2FA5B8")
INK = colors.HexColor("#000000")
SOFT = colors.HexColor("#E8F5F7")
GREY = colors.HexColor("#6B7785")
AMBER = colors.HexColor("#D98A1F")
GREEN = colors.HexColor("#1F8A5B")
RED = colors.HexColor("#B03A2E")
LINE = colors.HexColor("#DDE3EA")
CODEBG = colors.HexColor("#F4F7FA")

F = "fonts/"
pdfmetrics.registerFont(TTFont("Cf", F + "Comfortaa-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Cf-B", F + "Comfortaa-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Jk", F + "Jakarta-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Jk-B", F + "Jakarta-Bold.ttf"))

ANCHO = 164 * mm


def S(name, **kw):
    base = dict(name=name, fontName="Cf", fontSize=9.5, leading=14,
                textColor=INK, alignment=TA_LEFT, spaceAfter=5)
    base.update(kw)
    return ParagraphStyle(**base)


st_h1 = S("h1", fontName="Jk-B", fontSize=15, leading=19, textColor=NAVY,
          spaceBefore=13, spaceAfter=7)
st_h2 = S("h2", fontName="Jk-B", fontSize=11, leading=15, textColor=TEAL,
          spaceBefore=11, spaceAfter=5)
st_h3 = S("h3", fontName="Cf-B", fontSize=9.6, leading=13.5, textColor=NAVY,
          spaceBefore=8, spaceAfter=3)
st_body = S("body")
st_note = S("note", fontSize=8.5, leading=12.5, textColor=GREY)
st_cap = S("cap", fontSize=8, leading=11.5, textColor=GREY, spaceBefore=3)
st_lead = S("lead", fontSize=10, leading=15, textColor=NAVY)
st_cell = S("cell", fontSize=8.3, leading=11.8)
st_head = S("head", fontName="Jk-B", fontSize=8.2, leading=11.5, textColor=colors.white)
st_code = ParagraphStyle("code", fontName="Courier", fontSize=7.2, leading=9.4,
                         textColor=INK)


def P(t, s=st_body):
    return Paragraph(t, s)


def sp(h=4):
    return Spacer(1, h)


def callout(texto, color=TEAL, titulo=None):
    inner = []
    if titulo:
        inner.append(P("<b>%s</b>" % titulo, S("ct", fontName="Cf-B", fontSize=9,
                                               leading=13, textColor=color)))
    inner.append(P(texto, S("cb", fontSize=8.8, leading=13)))
    t = Table([[inner]], colWidths=[ANCHO])
    fondo = SOFT
    if color == AMBER:
        fondo = colors.HexColor("#FDF6EC")
    elif color == RED:
        fondo = colors.HexColor("#FBECEA")
    elif color == GREEN:
        fondo = colors.HexColor("#E7F5EE")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fondo),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    return t


def code(txt, ancho=ANCHO):
    t = Table([[Preformatted(txt, st_code)]], colWidths=[ancho])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODEBG),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
    ]))
    return t


def tabla(datos, anchos, cabecera=True):
    filas = []
    for i, fila in enumerate(datos):
        out = []
        for c in fila:
            if isinstance(c, str):
                estilo = st_head if (cabecera and i == 0) else st_cell
                out.append(Paragraph(c, estilo))
            else:
                out.append(c)
        filas.append(out)
    t = Table(filas, colWidths=anchos, repeatRows=1 if cabecera else 0)
    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.white),
    ]
    if cabecera:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
                   ("BACKGROUND", (0, 1), (-1, -1), SOFT)]
    else:
        estilo += [("BACKGROUND", (0, 0), (-1, -1), SOFT)]
    t.setStyle(TableStyle(estilo))
    return t


def figura(archivo, titulo, pie, ancho=ANCHO, alto_max=118 * mm):
    if not os.path.exists(archivo):
        return callout("Evidencia pendiente: <b>%s</b>." % archivo, AMBER, titulo)
    iw, ih = ImageReader(archivo).getSize()
    w = ancho
    h = w * ih / iw
    if h > alto_max:
        h = alto_max
        w = h * iw / ih
    img = Image(archivo, width=w, height=h)
    marco = Table([[img]], colWidths=[w])
    marco.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return KeepTogether([
        P(titulo, S("ct2", fontName="Jk-B", fontSize=9, leading=13,
                    textColor=NAVY, spaceBefore=8, spaceAfter=4)),
        marco,
        P(pie, st_cap),
        sp(6),
    ])


LOGO = ImageReader("logo-cuidda.png")
_lw, _lh = LOGO.getSize()
LOGO_H = 6.2 * mm
LOGO_W = LOGO_H * _lw / _lh


def marca(canvas, doc):
    canvas.saveState()
    canvas.drawImage(LOGO, 24 * mm, 279.6 * mm, width=LOGO_W, height=LOGO_H,
                     mask="auto", preserveAspectRatio=True, anchor="sw")
    canvas.setFillColor(GREY)
    canvas.setFont("Cf", 7.5)
    canvas.drawRightString(186 * mm, 282 * mm,
                           "Entrega Final · Ecosistema de Automatización IA Autónomo")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.7)
    canvas.line(24 * mm, 278 * mm, 186 * mm, 278 * mm)
    canvas.setFillColor(GREY)
    canvas.setFont("Cf", 7.5)
    canvas.drawString(24 * mm, 14 * mm, "Rubén Vásquez · Cuidda · octubre 2026")
    canvas.drawRightString(186 * mm, 14 * mm, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate("Cuidda-Entrega-Final.pdf", pagesize=A4,
                      leftMargin=23 * mm, rightMargin=23 * mm,
                      topMargin=32 * mm, bottomMargin=20 * mm,
                      title="Entrega Final · Cuidda",
                      author="Rubén Vásquez")
frame = Frame(23 * mm, 20 * mm, ANCHO, 244 * mm, id="main",
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="texto", frames=[frame], onPage=marca)])

REPO = "https://github.com/rubenvg11/cuidda-ecosistema-automatizacion-ia"
PAGES = "https://rubenvg11.github.io/cuidda-ecosistema-automatizacion-ia/"

E = []

# ============================================================ portada
E.append(P("Ecosistema de automatización IA autónomo", st_h1))
E.append(P("Solicitud de cuidado entrante » calificación con IA sobre la base de datos "
           "» validación humana » salida multicanal", st_lead))
E.append(sp(4))

E.append(tabla([
    ["Entregable", "Dónde"],
    ["Repositorio público", '<font color="#2FA5B8">%s</font>' % REPO],
    ["Panel de control en vivo", '<font color="#2FA5B8">%s</font>' % PAGES],
    ["Blueprints de Make", "<b>blueprints/</b> — los dos <b>.json</b> completos, sin fragmentar"],
    ["Esquemas de transferencia", "<b>schemas/</b> — 6 archivos JSON Schema 2020-12"],
    ["Evidencia del test", "<b>evidencias/</b> — mapa de arquitectura y capturas de las corridas"],
], [42 * mm, 122 * mm]))
E.append(sp(6))

E.append(P("Qué resuelve", st_h2))
E.append(P(
    "Cuidda conecta familias con personal de salud verificado a domicilio en Trujillo. "
    "Las solicitudes llegan por correo, en lenguaje natural: <i>«a mi mamá le dan de alta "
    "pasado mañana y no podemos dejarla sola de noche»</i>. Alguien tiene que leer eso, "
    "cruzarlo con qué distritos cubrimos y qué turnos existen, calcular un monto, y "
    "contestar algo que no prometa lo que no podemos cumplir.", st_body))
E.append(P(
    "El riesgo de automatizarlo con IA no es que escriba feo. Es que <b>invente</b>: una "
    "tarifa, un distrito que no cubrimos, una disponibilidad inmediata. Del otro lado hay "
    "una familia decidiendo quién entra a su casa a cuidar a su madre. Un correo mal "
    "escrito no es un problema de marketing: es una familia que no vuelve.", st_body))
E.append(P(
    "Por eso el ecosistema ataca el riesgo por tres lados: <b>le saca a la IA la posibilidad "
    "de inventar</b> —le inyecta la cobertura y el catálogo reales desde la base de datos y "
    "le prohíbe salirse de ahí—, <b>le saca la decisión de negocio</b> —la ruta que toma cada "
    "solicitud la deriva el flujo de los campos extraídos, no el modelo— y <b>le saca la "
    "posibilidad de enviar sola</b>: ninguna rama puede escribirle a una familia sin que "
    "antes una persona haya aprobado el texto.", st_body))
E.append(sp(3))

E.append(P("El stack", st_h2))
E.append(tabla([
    ["Capa", "Herramienta", "Rol"],
    ["Orquestador", "<b>Make</b> · zona us2", "2 escenarios, 41 módulos en total"],
    ["Base de datos y memoria", "<b>Airtable</b>", "6 tablas relacionadas: el estado, las reglas y el registro"],
    ["Procesamiento IA", "<b>Claude Haiku 4.5</b>", "clasificar y redactar, con ruteo que evita la llamada cara"],
    ["Canal de salida", "<b>Gmail</b> + <b>Slack</b>", "la familia recibe correo; el equipo aprueba en Slack"],
], [33 * mm, 47 * mm, 84 * mm]))
E.append(sp(4))
E.append(callout(
    "La consigna permitía Gmail, Slack o WhatsApp API. Se eligieron los dos primeros porque "
    "<b>la entrada del sistema ya es un correo</b>: responder por el mismo canal mantiene el "
    "hilo y no obliga a la familia a instalar nada. WhatsApp Business exigiría una plantilla "
    "aprobada por Meta, y el mensaje de propuesta de Cuidda es demasiado largo y variable "
    "para encajar en una plantilla. Queda documentado como el siguiente canal a sumar, "
    "no como un olvido.", TEAL, "Por qué Gmail y Slack, y no WhatsApp"))


# ============================================================ criterio 1
E.append(P("1 · Mapa de arquitectura", st_h1))
E.append(P("El diagrama completo: triggers, routers, APIs, nodos de IA y destino de los datos. "
           "No está dibujado a mano — lo genera <b>herramientas/diagrama.py</b>, así que "
           "cambiar el flujo y volver a correr el script mantiene el mapa sincronizado.", st_body))

E.append(figura("arquitectura-cuidda.png",
                "Mapa completo del ecosistema",
                "Escenario 1 arriba, la pausa humana en el medio, Escenario 2 abajo y la capa "
                "de memoria al pie. Cada caja lleva el mismo numeral que el módulo en Make."))

E.append(P("Escenario 1 · Ingesta y calificación IA — 28 módulos, 3 rutas", st_h2))
E.append(P(
    "<b>Trigger inteligente.</b> El módulo [1] observa Gmail con el filtro "
    "<b>is:unread subject:(solicitud de cuidado)</b> y arranca en <b>From now on</b>: Make "
    "guarda la marca de tiempo del arranque y nunca procesa correo viejo. Además marca como "
    "leído lo que procesa, así que un correo no puede entrar dos veces.", st_body))
E.append(P(
    "<b>Carga de contexto.</b> Antes de llamar a la IA, el flujo lee de Airtable la "
    "configuración [2], los distritos con cobertura [4] y el catálogo de turnos [6], y los "
    "compacta [3][5][7]. Si mañana Cuidda abre un distrito o cambia una tarifa, el prompt "
    "cambia solo.", st_body))
E.append(sp(2))
E.append(callout(
    "El módulo [4] no lee la tabla <b>Cobertura</b> entera: la lee con la fórmula "
    "<b>{Cubierto} = \"Si\"</b>. El prompt recibe una lista que <b>ya filtró la base de "
    "datos</b>, y la única pregunta que le queda a la IA es <i>«¿el lugar que escribió esta "
    "familia está en esta lista?»</i>. No es un detalle de implementación: en el test de "
    "estrés, pedirle a un modelo barato que leyera una columna <b>Si/No</b> por línea falló "
    "3 de 5 veces. La regla de quién tiene cobertura vive en Airtable, donde se audita y se "
    "cambia sin tocar un prompt.", GREEN, "La regla de negocio no la evalúa la IA"))
E.append(P(
    "<b>Motor de IA y ruteo.</b> El módulo [8] devuelve un JSON de 12 claves, [9] lo parsea "
    "y el router [10] decide con una expresión que se calcula sobre esos campos:", st_body))
E.append(code(
    '{{ if(length(trim(9.distrito_mencionado)) = 0; "A";\n'
    '   if(length(trim(9.turno))              = 0; "A";\n'
    '   if(length(trim(9.distrito))           = 0; "B"; "C"))) }}'))
E.append(sp(3))
E.append(tabla([
    ["Ruta", "Cuándo", "Qué hace"],
    ['<b><font color="#B03A2E">A · Dato faltante</font></b>',
     "no dice dónde vive<br/>o no dice qué turno",
     "[11] registra en Log de errores con la lista de lo que faltó · [12] avisa por Slack. "
     "No crea solicitud y <b>no gasta la llamada de redacción</b>."],
    ['<b><font color="#B8760F">B · Fuera de cobertura</font></b>',
     "el correo está completo<br/>pero el lugar no está<br/>en la lista de la base",
     "[13] crea la solicitud como Rechazado con el motivo · [14] responde a la familia por "
     "Gmail, en el mismo hilo, nombrando el lugar tal como ella lo escribió. Sin propuesta: "
     "no tiene sentido redactar algo que no se puede cumplir."],
    ['<b><font color="#1F8A5B">C · Solicitud válida</font></b>',
     "completo y dentro<br/>de cobertura",
     "[15] lee la base de conocimiento · [16] la compacta · [17] redacta la propuesta · "
     "[18] crea la solicitud vinculada · [19] pide aprobación en Slack · [20] guarda el ts "
     "de ese mensaje para responder después en el mismo hilo."],
], [33 * mm, 38 * mm, 93 * mm]))
E.append(sp(4))
E.append(callout(
    "El Escenario 1 termina en [19]/[20]. <b>No hay rama que envíe una propuesta.</b> "
    "La única salida hacia el cliente en todo el escenario es el correo de la ruta B, que es "
    "un «todavía no llegamos a tu zona» — no una propuesta comercial.",
    AMBER, "Dónde termina la máquina"))

E.append(P("Escenario 2 · Envío tras aprobación humana — 13 módulos, 2 rutas", st_h2))
E.append(P(
    "El trigger [1] observa la tabla Solicitudes por el campo <b>Modificado</b> con la "
    "fórmula <b>AND({Aprobado por Humano} = 1, {Estado} = \"Aprobado\")</b>, también en "
    "<b>From now on</b>. Un registro que nadie aprobó nunca entra al flujo: no es un filtro "
    "posterior, es la condición de entrada.", st_body))
E.append(sp(2))
E.append(tabla([
    ["Ruta", "Condición", "Qué hace"],
    ['<b><font color="#B03A2E">A · Propuesta vacía</font></b>',
     "length(trim(Propuesta generada)) = 0",
     "[5] registra el caso · [6] avisa en el hilo de Slack. <b>No sale ningún correo.</b>"],
    ['<b><font color="#1F8A5B">B · Listo para enviar</font></b>',
     "la propuesta tiene contenido",
     "[7] envía por Gmail con In-Reply-To y References para caer en el hilo original · "
     "[8] cierra el ciclo con Estado = Enviado y Fecha envío · [9] confirma en el hilo de Slack."],
], [37 * mm, 44 * mm, 83 * mm]))
E.append(sp(4))
E.append(P("Nombres de nodo", st_h3))
E.append(P(
    "Todos los módulos llevan en Make el mismo nombre y el mismo numeral que en este mapa. "
    "Un error registrado en la tabla Log de errores dice, por ejemplo, "
    "<b>[17] IA Redactar propuesta</b>: se ubica en el diagrama sin adivinar.", st_body))

E.append(PageBreak())

# ============================================================ criterio 2
E.append(P("2 · Estructuras de datos documentadas", st_h1))
E.append(P("Dos cosas distintas: cómo está modelada la base, y qué forma tiene el dato "
           "mientras viaja entre nodos.", st_lead))

E.append(P("El modelo en Airtable", st_h2))
E.append(tabla([
    ["Tabla", "Rol"],
    ["<b>Solicitudes</b>", "El caso. Una fila por familia que escribió."],
    ["<b>Cobertura</b>", "Los 9 distritos de Trujillo: si hay personal y cuánto recarga la movilidad."],
    ["<b>Catalogo de turnos</b>", "Los 5 turnos con su horario, tarifa y notas operativas."],
    ["<b>Base de conocimiento</b>", "10 entradas atómicas verificadas. Es el RAG."],
    ["<b>Log de errores</b>", "Toda falla, de API o de validación, queda escrita acá."],
    ["<b>Configuracion</b>", "12 pares clave-valor leídos en runtime. Es lo que hace que no haya datos hardcodeados."],
], [44 * mm, 120 * mm]))
E.append(sp(5))

E.append(P("Las relaciones, y por qué existen", st_h3))
E.append(code(
    "                  +----------------------+\n"
    "                  |      Cobertura       |\n"
    "                  |  Distrito · Cubierto |\n"
    "                  |  Recargo movilidad   |\n"
    "                  +----------+-----------+\n"
    "                             | link\n"
    "                  +----------v-----------+        +------------------------+\n"
    "                  |     Solicitudes      |<- link |  Catalogo de turnos    |\n"
    "                  |  Codigo · Estado     |        |  Turno · Horario       |\n"
    "                  |  Prioridad · Monto   |        |  Tarifa soles          |\n"
    "                  +----------------------+        +------------------------+\n"
    "\n"
    "   lookups que bajan a Solicitudes:\n"
    "     Cubierto (from Distrito)  ·  Recargo movilidad soles (from Distrito)\n"
    "     Horario  (from Turno)     ·  Tarifa soles            (from Turno)"))
E.append(sp(4))
E.append(P(
    "El requisito era <b>evitar datos aislados</b>, y acá se cumple de forma concreta: en "
    "Solicitudes no hay una columna de texto que diga «Huanchaco» y otra que diga «20». Hay "
    "un <b>campo vinculado</b> al registro real de Cobertura, y el recargo llega por "
    "<b>lookup</b>. Si mañana Huanchaco pasa a recargo 25, las solicitudes existentes lo "
    "reflejan sin tocar nada. Si Huanchaco deja de tener cobertura, el dato viaja solo — y "
    "el módulo [4] deja de inyectarlo en el prompt en la corrida siguiente.", st_body))
E.append(P(
    "Lo mismo con los turnos: la tarifa de «Noche» vive en un único lugar. El campo Monto "
    "estimado de una solicitud se audita contra <b>Tarifa soles (from Turno)</b> más "
    "<b>Recargo movilidad soles (from Distrito)</b> sin salir de la fila. En el test de "
    "estrés esa verificación se hizo fila por fila y cerró exacta.", st_body))
E.append(sp(3))

E.append(P("Ciclo de vida de una solicitud", st_h3))
E.append(code(
    "   Pendiente --> Procesado por IA --> Aprobado --> Enviado\n"
    "                       |                  ^\n"
    "                       |                  +--- una persona, a mano\n"
    "                       +--> Rechazado   (fuera de cobertura)\n"
    "                       +--> Error       (falla registrada)"))
E.append(P("<b>Enviado</b> es un estado absorbente: es lo que corta el loop del Escenario 2.", st_note))
E.append(sp(4))

E.append(P("Los esquemas JSON de transferencia", st_h2))
E.append(P("Cada salto entre nodos tiene un contrato explícito, publicado en <b>schemas/</b> "
           "como JSON Schema 2020-12 válido y ejecutable contra un validador.", st_body))
E.append(sp(2))
E.append(tabla([
    ["Archivo", "Qué contrato describe"],
    ["01 · gmail-a-clasificador", "Correo entrante » módulo [8]. Incluye la lista de campos <b>descartados</b> por minimización de datos."],
    ["02 · clasificacion-ia", "<b>El contrato central</b>: las 12 claves que debe devolver el clasificador, la tabla de ruteo y tres ejemplos."],
    ["03 · solicitud-airtable", "El registro escrito en Solicitudes, indexado por fieldId y no por nombre."],
    ["04 · log-de-errores", "El registro de error, con la directiva que corresponde a cada tipo."],
    ["05 · airtable-a-escenario-2", "El handoff entre escenarios. Airtable no es solo destino: es el bus de mensajes."],
    ["06 · canales-de-salida", "Payloads de Slack y Gmail, con el mapeo de Thread ID en cada uno."],
], [46 * mm, 118 * mm]))
E.append(sp(5))

E.append(P("El contrato que más importa", st_h3))
E.append(P(
    "El módulo [8] devuelve texto. El [9] lo parsea. El router [10] decide. Si ese texto no "
    "es JSON válido con estas 12 claves exactas, todo lo que sigue se cae. Por eso el prompt "
    "lo declara clave por clave y el esquema lo fija con <b>additionalProperties: false</b> "
    "y enums cerrados.", st_body))
E.append(code(
    '{\n'
    '  "familia": "Marco Antonio Delgado Chavez",\n'
    '  "email": "marco.delgado@example.com",\n'
    '  "telefono": "946307128",\n'
    '  "distrito_mencionado": "el centro de Trujillo",\n'
    '  "distrito": "Trujillo Centro",\n'
    '  "turno": "Manana",\n'
    '  "prioridad": "Media",\n'
    '  "resumen": "Senora mayor que vive sola y se marea al caminar,\n'
    '              necesita acompanamiento de lunes a viernes.",\n'
    '  "monto_estimado": 90,\n'
    '  "datos_completos": "si",\n'
    '  "distrito_cubierto": "si",\n'
    '  "faltantes": ""\n'
    '}'))
E.append(sp(4))
E.append(callout(
    "Hay <b>dos claves de distrito y no una</b>, y ahí está el corazón del ruteo. "
    "<b>distrito_mencionado</b> es lo que escribió la familia, sea lo que sea: «Laredo», «el "
    "centro de Trujillo», «acá por Moche». <b>distrito</b> solo tiene valor si ese lugar "
    "aparece en la lista de distritos con cobertura que la base inyectó en el prompt.<br/><br/>"
    "Eso es lo que permite que un correo completo de un distrito sin cobertura caiga en la "
    "<b>ruta B</b> (se le responde) y no en la <b>ruta A</b> (dato faltante): al router le "
    "falta un distrito válido, pero no le falta información de la familia.",
    TEAL, "Por qué dos claves de distrito"))
E.append(sp(4))
E.append(callout(
    "<b>telefono</b> sale sin prefijo y solo con dígitos <b>a propósito</b>. El prefijo lo "
    "pone Make leyendo <b>Configuracion.prefijo_telefono_pais</b>, y el resultado se escribe "
    "como <b>+51946307128</b> en un campo de tipo «Número de teléfono». Así el signo + no se "
    "pierde y el formato E.164 no depende de que la IA se acuerde de ponerlo.",
    GREEN, "Teléfono en E.164"))
E.append(sp(4))

E.append(P("Escritura por ID de campo", st_h3))
E.append(P("Make escribe usando el fieldId de Airtable, nunca el nombre visible:", st_body))
E.append(code(
    '"record": {\n'
    '  "fldswL3l4BgSrPlPr": "SOL-{{formatDate(now; \\"YYYYMMDD-HHmmss\\")}}",\n'
    '  "fld8OQzLKX51uSjDw": "{{9.familia}}",\n'
    '  "fldtI5sKssoSkCH7G": ["{{9.distrito}}"]\n'
    '}'))
E.append(P(
    "Renombrar «Familia» a «Nombre de la familia» en Airtable no rompe nada. Es la diferencia "
    "entre un flujo que sobrevive a que alguien ordene la base y uno que se cae el martes "
    "siguiente.", st_note))

# ============================================================ criterio 3
E.append(P("3 · Optimización de costos", st_h1))
E.append(P("No se trata de limitar tokens. Se trata de decidir, tarea por tarea, qué modelo "
           "hace falta y qué trabajo directamente no hay que pagar — y de medir esa decisión "
           "en vez de suponerla.", st_lead))

E.append(P("Las dos tareas de IA no son la misma tarea", st_h2))
E.append(tabla([
    ["", "[8] Extraer y clasificar", "[17] Redactar la propuesta"],
    ["Qué hace", "Lee un correo y devuelve un JSON de 12 claves", "Escribe el correo que una familia preocupada va a leer"],
    ["Quién lo consume", "Un router (una máquina)", "Una persona"],
    ["Tolerancia al error", "Cero de otro tipo: si erra el distrito, la familia entra a la ruta equivocada", "Cero: el tono es el producto"],
    ["Se ejecuta", "En el <b>100 %</b> de las solicitudes", "Solo en las válidas y dentro de cobertura"],
], [30 * mm, 66 * mm, 68 * mm]))
E.append(sp(5))

E.append(P("El experimento que cambió la arquitectura", st_h2))
E.append(P(
    "La hipótesis inicial era la del manual: <b>modelo barato para clasificar, modelo bueno "
    "para redactar</b>. El clasificador arrancó en el modelo <b>small</b> de Make AI Toolkit "
    "—la fila más barata de la matriz— y el test de estrés lo desarmó.", st_body))
E.append(sp(2))
E.append(tabla([
    ["Caso del test", "Qué hizo el modelo barato", "Consecuencia"],
    ["«el centro de Trujillo»", "Devolvió <b>Trujillo</b>, que no existe en Cobertura", "Airtable creó un distrito fantasma por typecast"],
    ["Huanchaco (Cubierto = Si)", "Lo marcó fuera de cobertura", "Se rechazó a una familia que sí se puede atender"],
    ["Moche + Día completo", "Monto estimado erróneo", "La propuesta habría salido con un precio mal calculado"],
], [36 * mm, 62 * mm, 66 * mm]))
E.append(sp(4))
E.append(P(
    "<b>3 de 5 corridas mal.</b> Con Claude Haiku 4.5 en el mismo prompt, las mismas cinco "
    "corridas dieron distrito exacto, cobertura correcta y montos que cierran contra la base "
    "(Trujillo Centro S/ 90, Moche S/ 175). Dos decisiones salieron de ahí:", st_body))
E.append(sp(2))
E.append(tabla([
    ["1", "<b>Subir el clasificador a Haiku 4.5.</b> Cuesta 16 veces más por llamada y sigue "
          "siendo un costo de centavos frente al de rechazar mal a una familia."],
    ["2", "<b>Sacarle la regla de negocio al modelo.</b> El módulo [4] filtra la cobertura en "
          "Airtable y el router deriva la ruta de los campos extraídos. Aunque el modelo se "
          "equivoque, no puede inventar una cobertura que la base no dice."],
], [8 * mm, 156 * mm], cabecera=False))
E.append(sp(4))
E.append(callout(
    "La fila más barata de la tabla está descartada <b>con datos, no por intuición</b>. Esa "
    "es la diferencia entre una matriz de decisión y una tabla de precios copiada: la matriz "
    "se completa corriendo el flujo.", TEAL, "Lo que vale de este criterio"))

E.append(P("Medición real de tokens", st_h2))
E.append(P("Los prompts están en el blueprint y se pueden medir. La parte fija se contó sobre "
           "el texto del propio .json; la dinámica, sobre los datos reales de las tablas.", st_body))
E.append(sp(2))
E.append(tabla([
    ["Módulo", "Prompt fijo", "Datos inyectados", "Input total", "Output"],
    ["[8] Clasificar", "612 tok", "Cobertura 96 + Catálogo 90 + correo ~250", "<b>≈ 1 050 tok</b>", "≈ 170 tok"],
    ["[17] Redactar", "379 tok", "Base de conocimiento 774 + solicitud 40", "<b>≈ 1 190 tok</b>", "≈ 300 tok"],
], [26 * mm, 22 * mm, 60 * mm, 30 * mm, 26 * mm]))
E.append(sp(5))

E.append(P("Matriz de decisión", st_h2))
E.append(P("Precios públicos por millón de tokens, septiembre 2026:", st_note))
E.append(tabla([
    ["Modelo", "Input", "Output", "Clasificar (1050/170)", "Redactar (1190/300)"],
    ["gpt-5-nano / small", "$0.05", "$0.40", "$0.000121", "$0.000180"],
    ["<b>Claude Haiku 4.5</b>", "$1.00", "$5.00", "<b>$0.001900</b>", "<b>$0.002690</b>"],
    ["Claude Sonnet 5", "$2.00", "$10.00", "$0.003800", "$0.005380"],
    ["Claude Opus 5", "$5.00", "$25.00", "$0.009500", "$0.013450"],
], [36 * mm, 20 * mm, 22 * mm, 42 * mm, 44 * mm]))
E.append(sp(5))

E.append(P("Proyección sobre 1 000 solicitudes entrantes", st_h3))
E.append(P("Con la distribución del test de estrés: 60 % válidas, 20 % fuera de cobertura, "
           "20 % con datos faltantes. <b>Solo las válidas llegan al redactor.</b>", st_note))
E.append(tabla([
    ["Escenario", "Clasificar", "Redactar", "Total / 1 000", "vs. elegido"],
    ["<b>Arquitectura elegida</b><br/>Haiku + ruteo", "$1.90", "$1.61", "<b>$3.51</b>", "—"],
    ["Haiku sin ruteo<br/>(redactar siempre)", "$1.90", "$2.69", "$4.59", "+31 %"],
    ["nano para clasificar", "$0.12", "$1.61", "$1.73", "−51 % <b>y 3 de 5 mal</b>"],
    ["Todo Sonnet 5, sin ruteo", "$3.80", "$5.38", "$9.18", "+162 %"],
    ["Todo Opus 5, sin ruteo", "$9.50", "$13.45", "$22.95", "+554 %"],
], [46 * mm, 24 * mm, 24 * mm, 30 * mm, 40 * mm]))
E.append(sp(5))

E.append(P("De dónde sale el ahorro", st_h3))
E.append(P(
    "Con el clasificador ya fijado en Haiku, el ahorro viene de <b>no redactar lo que no se "
    "va a enviar</b>: las rutas A y B cortan antes del módulo [17]. Son <b>$1.08 cada 1 000 "
    "solicitudes, un 24 %</b>, y crece con el porcentaje de correos incompletos o fuera de "
    "zona — justo los que más abundan cuando un negocio empieza a crecer. Contra la "
    "alternativa perezosa de un modelo grande sin ruteo, el ahorro es del <b>62 %</b> "
    "(Sonnet 5) y del <b>85 %</b> (Opus 5).", st_body))
E.append(sp(3))
E.append(callout(
    "Bajar el clasificador a nano ahorraría $1.78 más cada 1 000 solicitudes. En el test "
    "equivocó el distrito, la cobertura y el monto en 3 de 5 casos. <b>Una familia mal "
    "rechazada cuesta más que $1.78</b>, y un monto mal calculado en un correo firmado por "
    "Cuidda cuesta bastante más que eso.", RED, "Por qué no se toma el ahorro más grande"))

E.append(P("Límite de tokens de salida", st_h2))
E.append(P(
    "El módulo <b>ai-tools:Ask</b> de Make AI Toolkit <b>no expone un parámetro de max "
    "tokens</b> — sus únicos parámetros son la conexión y el modelo. Decirlo así es más útil "
    "que fingir un campo que no existe. El tope se aplica donde sí se puede:", st_body))
E.append(sp(2))
E.append(tabla([
    ["Dónde", "Cómo"],
    ["<b>En el prompt</b>, con un valor leído de la base",
     "La regla 6 del redactor dice: «Tope duro de salida: <b>{{ get(map(3.array; \"Valor\"; "
     "\"Clave\"; \"max_tokens_propuesta\"); 1) }}</b> tokens, que son unas 200 palabras. Si te "
     "estás pasando, corta, no resumas a la mitad.» El valor vive en Configuracion = 600."],
    ["<b>En el clasificador</b>, por diseño",
     "Devuelve 12 claves y el campo resumen tiene tope de 30 palabras. La salida no puede crecer."],
    ["<b>En el contexto de entrada</b>",
     "Los tres Search Records tienen maxRecords: 20. Las tablas no pueden inflar el prompt "
     "sin límite aunque crezcan."],
], [52 * mm, 112 * mm]))
E.append(sp(5))

E.append(P("El identificador del modelo: lo que quisimos hacer y lo que se puede", st_h2))
E.append(P("La intención era leerlo de <b>Configuracion</b> igual que todo lo demás:", st_body))
E.append(code('{{ get(map(3.array; "Valor"; "Clave"; "modelo_id_clasificacion"); 1) }}'))
E.append(P(
    "<b>No funciona, y vale la pena contarlo.</b> El campo <b>Model</b> de <b>ai-tools:Ask</b> "
    "no es un campo mapeable del bundle: es un parámetro de configuración del módulo. Make no "
    "evalúa IML ahí en tiempo de ejecución, así que el escenario intentaba invocar un modelo "
    "llamado literalmente <b>{{ get(map(3.array; ...</b> y el módulo fallaba. Lo detectamos en "
    "la tabla Log de errores, en el campo <b>Detalle</b>, que guarda el mensaje textual del "
    "proveedor — exactamente para lo que se diseñó esa tabla.", st_body))
E.append(P(
    "Así que el identificador va literal en los dos módulos, y lo que sí es dinámico es el "
    "<b>nombre legible</b>, que se lee de Configuracion y se escribe en "
    "<b>Solicitudes.Modelo usado</b> en cada solicitud: el costo real sigue siendo auditable "
    "fila por fila desde el dashboard. Preferimos dejarlo escrito antes que mostrar una "
    "captura del blueprint con la expresión adentro y no aclarar que no se evalúa.", st_body))
E.append(sp(3))

E.append(P("El costo de no hardcodear nada", st_h3))
E.append(P(
    "Hay que decirlo: leer Configuracion, Cobertura y Catalogo de turnos en cada corrida "
    "cuesta <b>6 de las operaciones</b> del Escenario 1. Es el precio de que ningún valor "
    "esté escrito dentro del flujo, y se paga a conciencia. El siguiente paso natural, cuando "
    "el volumen lo justifique, es cachear esas tres tablas en un <b>Data Store de Make</b> "
    "refrescado una vez al día: mismas garantías, seis operaciones menos por solicitud. No "
    "está implementado hoy porque a este volumen la diferencia es de centavos y la lectura "
    "directa es más fácil de auditar.", st_body))

E.append(PageBreak())

# ============================================================ criterio 4
E.append(P("4 · Seguridad y resiliencia", st_h1))
E.append(P("Tres preguntas: qué datos toca el sistema, qué pasa cuando algo se rompe, y quién "
           "autoriza lo que sale hacia afuera.", st_lead))

E.append(P("Minimización de datos", st_h2))
E.append(P("Cuidda maneja datos de salud de personas mayores. El principio: <b>cada capa "
           "recibe lo mínimo que necesita para hacer su trabajo, y nada más.</b>", st_body))
E.append(sp(2))
E.append(tabla([
    ["Capa", "Qué recibe", "Qué se descarta"],
    ["Gmail » clasificador", "subject, fromName, fromEmail, fullTextBody, threadId, message-id",
     "htmlBody, cc, bcc, to, labelIds, snippet, adjuntos, sizeEstimate, historyId"],
    ["Clasificador » Airtable", "Las 12 claves del contrato JSON", "El correo nunca se reenvía crudo a la IA de redacción"],
    ["Redactor (RAG)", "Distrito, turno, monto, resumen y la base de conocimiento",
     "<b>No recibe el correo original, ni el email, ni el teléfono</b>"],
    ["Slack", "Nombre, prioridad, distrito, turno, monto y la propuesta",
     "<b>No recibe el email ni el teléfono de la familia</b>"],
    ["Dashboard público", "Código, fecha, distrito, turno, prioridad, monto, modelo, estado",
     "<b>9 campos ocultos</b>, todos los que contienen datos personales"],
], [33 * mm, 66 * mm, 65 * mm]))
E.append(sp(4))
E.append(callout(
    "<b>El redactor no ve datos de contacto.</b> Le llega distrito, turno, monto y resumen. "
    "No necesita el correo ni el teléfono para escribir la propuesta, así que no los recibe. "
    "Si mañana el proveedor de IA cambia, lo que nunca salió de Airtable sigue sin salir.<br/><br/>"
    "<b>El panel público no tiene ni un dato personal.</b> La vista compartida de Log de "
    "errores oculta el campo Detalle justamente porque ahí sí puede aparecer un correo de "
    "remitente.", TEAL, "Dos decisiones que vale subrayar"))
E.append(sp(3))
E.append(P(
    "Ninguna API key vive dentro del flujo. Las cuatro conexiones son credenciales OAuth "
    "gestionadas por Make y referenciadas por id numérico. El blueprint publicado en el repo "
    "contiene <b>ids de conexión, no secretos</b>.", st_body))

E.append(P("Rutas de error", st_h2))
E.append(P("Hay <b>seis handlers</b> repartidos en los dos escenarios, y ninguno hace lo "
           "mismo que el otro, porque los fallos no son iguales.", st_body))
E.append(sp(3))

E.append(P("[8] IA · Extraer y clasificar » <b>Break</b> con reintento", st_h3))
E.append(code(
    "onerror -> [8E] Airtable · Registrar fallo de la IA    (Tipo = \"Fallo de API de IA\")\n"
    "        -> [8E] Slack   · Alertar fallo de la IA       (con el error textual)\n"
    "        -> [8E] Break   · Detener con reintento        (3 intentos, cada 15 s)"))
E.append(P(
    "Si el clasificador no responde no hay nada que hacer aguas abajo: sin JSON no hay ruta. "
    "<b>Break</b> congela la ejecución en <i>Incomplete executions</i> y Make la reintenta "
    "sola. No se escribe ninguna solicitud a medias.", st_body))
E.append(sp(3))

E.append(P("[9] Parsear clasificación » <b>Break</b> con reintento", st_h3))
E.append(P(
    "Este handler <b>no estaba en el diseño original: lo pidió el test</b>. Claude devuelve "
    "el JSON envuelto en un bloque de código aunque el prompt lo prohíba, y el parser "
    "respondía <i>«Source is not valid JSON. Code: DataError»</i>. Se arregló por los dos "
    "lados: el flujo normaliza la respuesta antes de parsear —misma idea que el "
    "<b>trim()</b> del Escenario 2: normalizar y después comparar— y, si aun así falla, hay "
    "una ruta de error que lo registra con la <b>respuesta cruda</b> del modelo, avisa por "
    "Slack y deja la ejecución para reintentar.", st_body))
E.append(code('{{ trim(replace(replace(8.answer; "```json"; ""); "```"; "")) }}'))
E.append(sp(3))

E.append(P("[17] IA · Redactar propuesta » <b>Resume</b>", st_h3))
E.append(code(
    "onerror -> [17E] Airtable · Registrar fallo de redaccion\n"
    "        -> [17E] Resume   · Continuar con aviso\n"
    "             answer = \"PROPUESTA NO GENERADA - la API de IA fallo.\n"
    "                        Revisar a mano antes de aprobar.\""))
E.append(P(
    "Acá la decisión es la contraria, y es deliberada. La solicitud ya fue validada: perderla "
    "porque el redactor se cayó sería el peor resultado posible. <b>Resume</b> inyecta un "
    "texto de aviso y el flujo sigue: la solicitud se crea igual y el mensaje de Slack dice "
    "en el cuerpo que la propuesta no se generó. <b>Preferimos una propuesta vacía y visible "
    "antes que una solicitud perdida en silencio.</b>", st_body))
E.append(sp(3))
E.append(tabla([
    ["Handler", "Directiva", "Por qué esa y no otra"],
    ["[8] fallo de IA", "<b>Break</b> 3×15 s", "Sin JSON no hay ruta posible. Reintentar sí arregla el problema."],
    ["[9] JSON inválido", "<b>Break</b> 3×15 s", "El modelo puede acertar en el segundo intento. Se guarda la respuesta cruda para poder depurarlo."],
    ["[11] dato faltante", "sin reintento", "No es un fallo de sistema, es un correo incompleto. Reintentar no lo arregla."],
    ["[17] fallo de redacción", "<b>Resume</b>", "La solicitud ya vale. Perderla es peor que entregarla sin texto."],
    ["[7] fallo de Gmail", "<b>Break</b> 3×15 s", "El estado no avanza, así que el registro vuelve a entrar solo."],
    ["[9] fallo de Slack", "<b>Resume</b>", "El correo ya salió. Que Slack no conteste es molesto, no grave."],
], [34 * mm, 28 * mm, 102 * mm]))
E.append(sp(4))
E.append(P("Los dos escenarios tienen <b>Store incomplete executions = Yes</b>, que es el "
           "requisito técnico para que la directiva Break con reintento funcione.", st_note))
E.append(sp(3))
E.append(P(
    "Lo importante del handler de Gmail es lo que <b>no</b> pasa: como Break detiene el flujo, "
    "el módulo [8] del Escenario 2 nunca corre, así que el Estado se queda en <b>Aprobado</b>. "
    "El registro sigue cumpliendo la fórmula del trigger y vuelve a entrar cuando Gmail se "
    "recupere. <b>Nunca se marca como «Enviado» un correo que no salió.</b>", st_body))

E.append(P("Punto de validación humana", st_h2))
E.append(P("El sistema <b>no puede</b> escribirle una propuesta a una familia por su cuenta. "
           "La frontera es física, no una convención:", st_body))
E.append(sp(2))
E.append(tabla([
    ["1", "El Escenario 1 escribe la solicitud con Estado = «Procesado por IA» y <b>Aprobado "
          "por Humano = false</b>. Siempre. No hay rama que lo ponga en true."],
    ["2", "Publica en Slack la propuesta completa con el código de la solicitud y la frase "
          "<i>«Nada sale al cliente hasta que alguien marque Aprobado por Humano y ponga el "
          "Estado en Aprobado en Airtable»</i>."],
    ["3", "El Escenario 2 <b>solo existe</b> para registros que cumplen la fórmula. Los no "
          "aprobados ni siquiera entran al flujo."],
], [10 * mm, 154 * mm], cabecera=False))
E.append(sp(4))
E.append(callout(
    "Hacen falta <b>dos acciones humanas distintas</b> —marcar la casilla y cambiar el "
    "estado— para que un correo salga. Un clic accidental en la casilla no dispara nada.",
    GREEN, "Doble llave"))

E.append(P("Check de seguridad", st_h2))
E.append(P("Filtro para evitar loops infinitos", st_h3))
E.append(P(
    "El Escenario 2 termina poniendo <b>Estado = Enviado</b>. Eso toca el campo Modificado, "
    "que es el trigger field, así que el registro vuelve a pasar por el trigger — pero ya no "
    "cumple la fórmula, porque Estado dejó de ser «Aprobado». El ciclo se corta solo. No "
    "depende de un contador, ni de un delay, ni de una lista de procesados: <b>la condición "
    "de entrada deja de ser verdadera por efecto de la propia acción</b>.", st_body))
E.append(sp(3))

E.append(P("Comparación de tipos correcta en los filtros", st_h3))
E.append(P(
    "Las tres rutas del Escenario 1 comparan <b>texto contra texto</b> con <b>text:equal</b> "
    "sobre un enum cerrado de tres valores, nunca con <b>notequal</b> sobre un campo libre. "
    "<i>Esto corrige directamente la observación sobre el filtro de la ruta «Baja», donde un "
    "notequal se solapaba con la ruta «Alta».</i> Y el valor comparado no lo escribe el "
    "modelo: lo deriva el flujo.", st_body))
E.append(sp(2))
E.append(tabla([
    ["Ruta", "Condición"],
    ["A · Dato faltante", 'ruta = "A"'],
    ["B · Fuera de cobertura", 'ruta = "B"'],
    ["C · Solicitud válida", 'ruta = "C"'],
], [44 * mm, 120 * mm]))
E.append(sp(3))
E.append(P(
    "En el router del Escenario 2 el problema era distinto: había que preguntar si un campo "
    "de texto largo está vacío. En vez de comparar el campo contra una cadena vacía —que es "
    "donde se cuelan los espacios y los saltos de línea— se normaliza primero y se compara "
    "contra un enum:", st_body))
E.append(code('{{if(length(trim(1.`Propuesta generada`)) = 0; "vacia"; "lista")}}'))
E.append(P("Ruta A pregunta <b>= \"vacia\"</b>, ruta B pregunta <b>= \"lista\"</b>. Texto "
           "contra texto, dos valores posibles, sin ambigüedad.", st_note))
E.append(sp(4))

E.append(P("El AND del blueprint se escribe de una sola forma, y no es la intuitiva", st_h3))
E.append(P(
    "Esto costó una tarde de test y merece quedar escrito. En el JSON de un blueprint de "
    "Make, el campo <b>conditions</b> es un array de arrays: el <b>array externo es un "
    "OR</b> y el <b>interno es un AND</b>.", st_body))
E.append(code(
    '"conditions": [[c1], [c2]]     // c1 O c2   <- parece un AND y no lo es\n'
    '"conditions": [[c1, c2]]       // c1 Y c2   <- el AND de verdad'))
E.append(P(
    "Escrito de la primera forma, la ruta B pasaba a ser <i>«datos_completos = si <b>o</b> "
    "distrito_cubierto = no»</i>, que es verdadera casi siempre: <b>todas</b> las solicitudes "
    "se registraban además como rechazadas y el test creaba dos filas por corrida. El síntoma "
    "en History era claro una vez que se sabía qué mirar —17 operaciones donde la ruta C sola "
    "son 15— pero el blueprint se veía perfectamente razonable.", st_body))
E.append(P(
    "La forma de verificarlo no es leer el JSON: es <b>abrir el filtro en la UI de Make "
    "después de importar</b>. Si entre las dos condiciones dice <b>or</b> en vez de "
    "<b>and</b>, el blueprint está mal aunque el escenario corra sin errores. Es la clase de "
    "bug que no rompe nada: solo hace lo incorrecto, en silencio.", st_body))
E.append(sp(3))

E.append(P("Prompt dinámico con variables del sistema", st_h3))
E.append(P(
    "Ningún prompt tiene datos fijos. La ciudad, la moneda, la firma, las horas de vigencia y "
    "el tope de tokens salen de Configuracion; la cobertura, el catálogo de turnos y la base "
    "de conocimiento salen de sus tablas y se inyectan agregados. Si mañana Cuidda abre en "
    "Chiclayo, se agrega la fila y el prompt cambia solo.", st_body))

E.append(P("Lo que todavía no está resuelto", st_h2))
E.append(P("Un informe que solo dice lo que funciona no sirve para operar. Cuatro cosas quedan "
           "abiertas:", st_body))
E.append(sp(2))
E.append(tabla([
    ["El plan Free de Make puede sustituir el modelo",
     "El propio módulo avisa: <i>«Some models are available only on Make paid plans. If "
     "you're on the free plan or a trial, your scenario will run using a free model.»</i> La "
     "elección de Claude Haiku 4.5 se respeta recién en plan pago. El campo Modelo usado "
     "registra lo que el escenario pidió, no necesariamente lo que Make ejecutó."],
    ["El monto lo sigue calculando la IA",
     "Tarifa y recargo ya están en Airtable como lookups. Lo correcto es que Monto estimado "
     "sea un campo fórmula y que la IA no haga aritmética. Es el próximo cambio; se dejó "
     "fuera de esta entrega para no tocar el esquema en medio del test."],
    ["No hay política de retención",
     "Los correos originales quedan en Mensaje original indefinidamente. Para un sistema que "
     "maneja datos de salud, lo correcto es vaciar ese campo a los 90 días de Fecha envío."],
    ["El motivo de rechazo lo escribe la máquina",
     "Cuando una persona decide no aprobar una propuesta, hoy no hay campo donde deje por "
     "qué. Es el primer agujero que taparía antes de poner esto en producción."],
], [50 * mm, 114 * mm], cabecera=False))

# ============================================================ criterio 5
E.append(P("5 · Dashboard de control", st_h1))
E.append(P("Es más que el link a la base. El panel es una página propia, con la identidad de "
           "Cuidda, que explica qué significa cada número y <b>embebe las vistas de Airtable "
           "en vivo</b>. No hay copias ni cachés: lo que se ve es la misma fila que el flujo "
           "acaba de escribir.", st_lead))
E.append(sp(3))
E.append(callout('<font color="#2FA5B8">%s</font>' % PAGES, TEAL, "Panel público"))

E.append(figura("evidencias/dashboard-recorte.png",
                "El panel de control",
                "Publicado con GitHub Pages desde el mismo repositorio, así que el panel y el "
                "código que lo genera no pueden desincronizarse."))

E.append(P("Los tres paneles", st_h2))
E.append(tabla([
    ["Panel", "Qué muestra"],
    ["<b>1 · Pipeline de solicitudes</b>", "Todas las solicitudes agrupadas por Estado, con distrito, turno, prioridad, monto y modelo usado. El encabezado de cada grupo es el contador de ese estado."],
    ["<b>2 · Cola de aprobación humana</b>", "Filtrada por Estado = «Procesado por IA»: lo que espera una decisión de una persona."],
    ["<b>3 · Errores por tipo</b>", "Log de errores agrupado por Tipo de error, con el nodo exacto que falló."],
], [48 * mm, 116 * mm]))
E.append(sp(5))

E.append(P("Los cuatro indicadores", st_h2))
E.append(tabla([
    ["Indicador", "Cómo se calcula", "Dónde se lee"],
    ["Solicitudes por estado", "count(Solicitudes) agrupado por Estado", "Panel 1 · encabezado de grupo"],
    ["Cola de aprobación humana", 'count(Solicitudes) donde Estado = "Procesado por IA"', "Panel 2 · contador inferior"],
    ["Monto en juego", "sum(Monto estimado)", "Panel 1 · barra de resumen"],
    ["<b>Tasa de errores</b>", "count(Log de errores) ÷ (count(Solicitudes) + count(Log · \"Dato faltante\")) × 100", "Panel 3 ÷ Panel 1"],
], [40 * mm, 78 * mm, 46 * mm]))
E.append(sp(4))
E.append(callout(
    "Una solicitud con datos faltantes <b>nunca llega a crear una fila</b> en Solicitudes: "
    "muere en la ruta A y solo deja rastro en Log de errores. Si se dividiera por las "
    "solicitudes creadas, esos casos desaparecerían del denominador y la tasa quedaría "
    "artificialmente baja, justo en el escenario donde más importa que no lo esté. Sumarlos "
    "es lo que hace que el número signifique lo que uno cree que significa: <i>de cada 100 "
    "correos que entraron, cuántos terminaron mal</i>.",
    AMBER, "Por qué el denominador de la tasa de errores es raro"))
E.append(sp(4))

E.append(P("Minimización de datos en el panel", st_h2))
E.append(P(
    "El panel es público, así que las vistas compartidas ocultan <b>9 campos</b> de "
    "Solicitudes: Familia, Email, Telefono, Mensaje original, Resumen IA, Propuesta generada, "
    "Hilo Gmail, Message ID Gmail y Slack ts. En Log de errores se oculta Detalle. Queda "
    "visible exactamente lo que un panel de control necesita: el código, la fecha, el "
    "distrito, el turno, la prioridad, el monto, el modelo y el estado. <b>Ni un dato "
    "personal.</b>", st_body))

E.append(PageBreak())

# ============================================================ test de estres
E.append(P("Test de estrés", st_h1))
E.append(P("Cinco ejecuciones que recorren las tres rutas del Escenario 1, incluido el camino "
           "infeliz con datos incompletos. Todas se corrieron sobre la base limpia, una por "
           "correo, con Run once, y cada una dejó su rastro en History.", st_lead))
E.append(sp(3))
E.append(tabla([
    ["#", "Caso", "Lugar que escribe", "Turno", "Ruta", "Monto"],
    ["1", "Alta hospitalaria, urgente", "Huanchaco", "Noche", '<font color="#1F8A5B"><b>C · válida</b></font>', "<b>190</b>"],
    ["2", "Acompañamiento de mañana", "«el centro de Trujillo»", "Manana", '<font color="#1F8A5B"><b>C · válida</b></font>', "<b>90</b>"],
    ["3", "Día completo post-operatorio", "Moche", "Dia completo", '<font color="#1F8A5B"><b>C · válida</b></font>', "<b>175</b>"],
    ["4", "Distrito sin personal", "Laredo", "Tarde", '<font color="#B8760F"><b>B · fuera de cobertura</b></font>', "—"],
    ["5", "<b>Camino infeliz</b><br/>sin lugar ni turno", "—", "—", '<font color="#B03A2E"><b>A · dato faltante</b></font>', "—"],
], [7 * mm, 40 * mm, 34 * mm, 22 * mm, 44 * mm, 17 * mm]))
E.append(sp(4))
E.append(P("El monto se verifica contra la base: tarifa del turno más recargo de movilidad del "
           "distrito. Caso 1: 170 + 20. Caso 2: 90 + 0. Caso 3: 160 + 15. El caso 2 es a "
           "propósito una <b>variante</b> del nombre del distrito: el correo dice «el centro de "
           "Trujillo» y en Cobertura la fila se llama «Trujillo Centro».", st_note))

E.append(figura("evidencias/test-1-ruta-c.png",
                "Ruta C · solicitud válida",
                "El recorrido completo: configuración, cobertura filtrada, catálogo, "
                "clasificación, RAG, redacción, creación de la solicitud vinculada y pedido de "
                "aprobación en Slack. Las rutas A y B quedan sin burbuja."))
E.append(figura("evidencias/test-4-fuera-cobertura.png",
                "Ruta B · fuera de cobertura",
                "Laredo está en la tabla Cobertura con Cubierto = No, así que el módulo [4] no "
                "lo inyecta en el prompt y la clave distrito queda vacía. El router manda el "
                "bundle por la ruta B: no se llama al redactor, se registra Rechazado y se le "
                "responde a la familia."))
E.append(figura("evidencias/test-5-camino-infeliz.png",
                "Ruta A · camino infeliz",
                "Correo sin lugar ni turno. El router corta en la ruta A: el caso queda en Log "
                "de errores con la lista de lo que faltó y se avisa por Slack. No se crea "
                "solicitud y no se gasta la llamada de redacción."))
E.append(figura("evidencias/slack-hitl.png",
                "El punto de validación humana en Slack",
                "El mensaje con la propuesta completa y la advertencia de que nada sale hasta "
                "que una persona marque la casilla."))
E.append(figura("evidencias/escenario-2-envio.png",
                "Escenario 2 · envío tras la aprobación",
                "Una vez marcada la casilla y cambiado el estado, el Escenario 2 envía el "
                "correo en el hilo original y cierra el ciclo con Estado = Enviado."))
E.append(figura("evidencias/dashboard-con-datos.png",
                "El panel con datos reales",
                "El pipeline después del test, con las solicitudes repartidas entre los "
                "estados y la tasa de errores calculable."))

E.append(PageBreak())

# ============================================================ cierre
E.append(P("Cómo reproducirlo", st_h1))
E.append(P("Los blueprints y el diagrama no están hechos a mano: se generan.", st_body))
E.append(code(
    "# los dos blueprints de Make\n"
    "python herramientas/build.py\n"
    "\n"
    "# el mapa de arquitectura (svg + png)\n"
    "pip install cairosvg\n"
    "python herramientas/diagrama.py\n"
    "\n"
    "# este PDF\n"
    "python herramientas/hacer_pdf_final.py"))
E.append(P(
    "Para levantarlo en otra cuenta de Make: crear un escenario nuevo, menú <b>(...)</b>, "
    "<b>Import blueprint</b>, subir el .json. Hay que volver a apuntar las cuatro conexiones "
    "—Airtable, Gmail, Slack y Make AI— a las propias, porque los ids de conexión del "
    "blueprint pertenecen a esta cuenta.", st_body))

E.append(P("Qué aprendí construyéndolo", st_h1))
E.append(P(
    "<b>La base de datos no es el final del flujo, es el medio.</b> Airtable no guarda el "
    "resultado: guarda las reglas con las que se toma la decisión. La cobertura y el catálogo "
    "de turnos entran al prompt en cada corrida, así que el comportamiento del sistema cambia "
    "editando una fila, no un escenario. Eso es lo que separa una automatización de un script "
    "con pasos.", st_body))
E.append(P(
    "<b>A la IA hay que darle la tarea más chica posible.</b> La primera versión le pedía que "
    "extrajera datos <i>y</i> evaluara la regla de cobertura <i>y</i> decidiera la ruta. "
    "Fallaba. La versión que funciona le pide solo extraer: la base filtra los distritos "
    "cubiertos antes de armar el prompt y el router deriva la ruta de los campos extraídos. "
    "El modelo pasó de tomar decisiones de negocio a leer un correo, que es lo único que sabe "
    "hacer bien.", st_body))
E.append(P(
    "<b>La pausa humana no es un freno, es el producto.</b> Al principio la pensé como un "
    "requisito de la consigna. Terminó siendo la parte que más defiendo: en un negocio donde "
    "una familia entrega la llave de su casa, que una persona lea el correo antes de que "
    "salga no es fricción, es la razón por la que confían.", st_body))
E.append(P(
    "<b>Medir cambia la respuesta.</b> Iba a entregar esto con el clasificador en el modelo "
    "más barato y una tabla de precios que lo justificaba. El test de estrés lo tiró abajo en "
    "tres de cinco corridas. La tabla de costos que quedó vale más que la anterior, no porque "
    "el número sea mejor, sino porque el número salió de correr el flujo.", st_body))
E.append(sp(4))
E.append(callout(
    "Los handlers de error no son todos iguales, y esa es la parte interesante. <b>Break</b> "
    "cuando reintentar arregla el problema; <b>Resume</b> cuando perder el dato es peor que "
    "entregarlo incompleto; <b>ningún reintento</b> cuando el problema está en la entrada y "
    "no en el sistema. Decidir cuál va en cada nodo obliga a preguntarse qué es lo peor que "
    "puede pasar en ese punto exacto.", TEAL, "Lo que más me hizo pensar"))

doc.build(E)
print("PDF generado:", os.path.abspath("Cuidda-Entrega-Final.pdf"))
