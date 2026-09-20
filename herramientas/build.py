#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera los blueprints de los dos escenarios de Make del ecosistema Cuidda.
Todas las formas de modulo (module/version/parameters/mapper) fueron extraidas
empiricamente de Make con "Copy to clipboard", no inventadas.
"""
import json, os

# ---------------------------------------------------------------- conexiones
CONN_AIRTABLE = 10636792
CONN_GMAIL    = 10637014
CONN_AI       = 10636489
CONN_SLACK    = 11203706          # rubenvg.slack.com

# ---------------------------------------------------------------- Airtable
BASE   = "appxzAU6Buul0hoGw"
T_SOL  = "tbloHJ3bW32Tk892I"   # Solicitudes
T_CAT  = "tblj7zkYXiS7pC3ay"   # Catalogo de turnos
T_COB  = "tblU7qF4h7IVgwGjQ"   # Cobertura
T_KB   = "tblUNJi1OKLof4xeC"   # Base de conocimiento
T_ERR  = "tblY66MlpoRAAdtfc"   # Log de errores
T_CFG  = "tblcfTQrNzGIs110O"   # Configuracion

S = dict(
    codigo="fldswL3l4BgSrPlPr", fecha="fldCp9Y1gwRhSCl0L", familia="fld8OQzLKX51uSjDw",
    email="fld3Ib1fiEU0kn2qy", telefono="fldpLreceh6uHaCkX", mensaje="fld9hvQViF3qiMSJ6",
    distrito="fldtI5sKssoSkCH7G", turno="fldsv8LA5ssOnWSS6", prioridad="fldteTrPCuGze1xNH",
    resumen="fldrCsA2FhCd8UqgW", propuesta="fldGySVUs3LBUIhKN", monto="fld0ycmZJDZNUimVa",
    modelo="fldDl9tqsFnzCRq2C", estado="fldBo9QKnm6IgDr5e", aprobado="fldzxJRYLkmpV4rX9",
    motivo="fld41DhB7GzPaeEtU", envio="fldZWRSRiUlC6PR20",
    hilo="fldas42PaE0GpjyaO", msgid="fldJ9LamByno7XK7M", slackts="fld97SpvMvr2VXbII",
)

E = dict(codigo="fldQnblJ1AkLgDgOS", fecha="fldpJhwJ9RQn2d9TK", escenario="fldCBS5b75LuRSu2m",
         modulo="fldZbtjTPbFBJV5jR", tipo="fld7zqJB8MRrTFl1E", detalle="fldTHuHIKHsXUaGPU",
         resuelto="fldx4zH5G04eTF4U5")


def cfg(clave, mod=3):
    """Lee un valor de la tabla Configuracion. Cero datos hardcodeados."""
    return '{{ get(map(%d.array; "Valor"; "Clave"; "%s"); 1) }}' % (mod, clave)


def dsg(x, y, name):
    return {"designer": {"x": x, "y": y, "name": name}}


def airtable_search(mid, x, y, name, table, formula="", maxr="20"):
    return {"id": mid, "module": "airtable:ActionSearchRecords", "version": 3,
            "parameters": {"__IMTCONN__": CONN_AIRTABLE},
            "mapper": {"base": BASE, "useColumnId": False, "table": table,
                       "formula": formula, "maxRecords": maxr},
            "metadata": dsg(x, y, name)}


def airtable_create(mid, x, y, name, table, record):
    return {"id": mid, "module": "airtable:ActionCreateRecord", "version": 3,
            "parameters": {"__IMTCONN__": CONN_AIRTABLE},
            "mapper": {"base": BASE, "typecast": True, "useColumnId": False,
                       "table": table, "record": record},
            "metadata": dsg(x, y, name)}


def airtable_update(mid, x, y, name, table, rec_id, record):
    return {"id": mid, "module": "airtable:ActionUpdateRecords", "version": 3,
            "parameters": {"__IMTCONN__": CONN_AIRTABLE},
            "mapper": {"base": BASE, "typecast": True, "useColumnId": False,
                       "table": table, "id": rec_id, "record": record},
            "metadata": dsg(x, y, name)}


def slack_msg(mid, x, y, name, text, cfg_mod=3, thread_ts=None):
    m = {"channelWType": "manualy",
         "channel": cfg("slack_canal_operaciones", cfg_mod),
         "text": text, "parse": False, "mrkdwn": True}
    if thread_ts:
        m["thread_ts"] = thread_ts
    return {"id": mid, "module": "slack:CreateMessage", "version": 4,
            "parameters": {"__IMTCONN__": CONN_SLACK},
            "mapper": m, "metadata": dsg(x, y, name)}


def log_error(mid, x, y, name, escenario, modulo, tipo, detalle):
    return airtable_create(mid, x, y, name, T_ERR, {
        E["codigo"]: 'ERR-{{formatDate(now; "YYYYMMDD-HHmmss")}}',
        E["fecha"]: "{{now}}",
        E["escenario"]: escenario,
        E["modulo"]: modulo,
        E["tipo"]: tipo,
        E["detalle"]: detalle,
        E["resuelto"]: "No",
    })


def brk(mid, x, y, name, count=3, interval=15):
    return {"id": mid, "module": "builtin:Break", "version": 1,
            "mapper": {"retry": True, "interval": interval, "count": count},
            "metadata": dsg(x, y, name)}


def resume(mid, x, y, name, answer):
    return {"id": mid, "module": "builtin:Resume", "version": 1,
            "mapper": {"answer": answer, "AIUsage": {"inputTokens": "", "outputTokens": ""}},
            "metadata": dsg(x, y, name)}


def text_agg(mid, x, y, name, feeder, value):
    return {"id": mid, "module": "util:TextAggregator", "version": 1,
            "parameters": {"rowSeparator": "\n", "feeder": feeder},
            "mapper": {"value": value}, "metadata": dsg(x, y, name)}


def ai_ask(mid, x, y, name, model, prompt, onerror=None):
    # El identificador del modelo NO esta hardcodeado: se lee de la tabla Configuracion
    # en runtime. El campo Model del modulo acepta expresion cuando se activa "Map".
    m = {"id": mid, "module": "ai-tools:Ask", "version": 2,
         "parameters": {"makeConnectionId": CONN_AI, "model": cfg(model)},
         "mapper": {"input": prompt}, "metadata": dsg(x, y, name)}
    if onerror:
        m["onerror"] = onerror
    return m


def eq(a, b):
    return [{"a": a, "b": b, "o": "text:equal"}]


META = {
    "instant": False, "version": 1,
    "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True,
                 "autoCommitTriggerLast": True, "sequential": False, "slots": None,
                 "confidential": False, "dataloss": False, "dlq": True,
                 "freshVariables": False},
    "designer": {"orphans": []}, "zone": "us2.make.com", "notes": [],
}

# =================================================================== ESCENARIO 1
PROMPT_CLASIFICA = """Sos el sistema de admision de Cuidda, una plataforma que conecta familias con personal de salud verificado a domicilio en {ciudad}, Peru.
Tu tarea es leer un correo entrante de una familia y devolver SOLO un objeto JSON valido, sin texto adicional y sin bloques de codigo.

CLAVES EXACTAS QUE DEBES DEVOLVER:
familia: nombre de la persona que escribe, string vacio si no aparece.
email: correo de contacto. Si el cuerpo no trae uno, usa el del remitente.
telefono: SOLO digitos, sin prefijo de pais, sin espacios ni guiones. String vacio si no aparece.
distrito: el distrito escrito tal cual aparece en la lista de COBERTURA. String vacio si no se menciona.
turno: uno de los nombres exactos de la lista de CATALOGO DE TURNOS. String vacio si no se puede deducir.
prioridad: Alta, Media o Baja. Alta solo si hay riesgo declarado para el paciente, una alta hospitalaria en las proximas 48 horas o el cuidado empieza en menos de 24 horas.
resumen: maximo 30 palabras, en espanol, sin inventar nada.
monto_estimado: numero entero en soles. Tarifa del turno elegido mas el recargo de movilidad del distrito. 0 si falta el turno o el distrito.
datos_completos: si o no. Es 'si' unicamente cuando email, distrito y turno tienen valor.
distrito_cubierto: si o no. Es 'si' unicamente cuando el distrito aparece en COBERTURA con Cubierto=Si.
faltantes: lista en texto de que datos faltaron, string vacio si no falto ninguno.

REGLAS DURAS: no inventes telefonos, distritos, turnos ni montos. Si un dato no esta en el correo, devolvelo vacio y marca datos_completos en no. Si el distrito no esta en COBERTURA, distrito_cubierto es no.

COBERTURA VIGENTE (fuente: tabla Cobertura):
{{5.text}}

CATALOGO DE TURNOS (fuente: tabla Catalogo de turnos):
{{7.text}}

CORREO A PROCESAR
Asunto: {{1.subject}}
Remitente: {{1.fromName}} <{{1.fromEmail}}>
Cuerpo:
{{1.fullTextBody}}""".replace("{ciudad}", cfg("ciudad_operacion"))

PROMPT_REDACTA = """Sos quien le responde a las familias en Cuidda, plataforma de cuidado de salud a domicilio en {ciudad}, Peru. Escribi el correo de propuesta que la familia va a leer.

REGLAS DURAS:
1) Usa unicamente los datos de la SOLICITUD y los hechos de la BASE DE CONOCIMIENTO. Si un dato no esta ahi, no lo escribas. Nunca inventes precios, porcentajes, cantidad de profesionales ni tiempos de respuesta.
2) Nunca prometas diagnostico medico, atencion de emergencias ni disponibilidad inmediata garantizada.
3) Tono cercano y directo, sin lenguaje corporativo vacio. Del otro lado hay alguien preocupado por un familiar.
4) Estructura: saludo con el nombre, una linea que confirma que entendiste el pedido, el turno propuesto con su horario, el monto estimado en {moneda}, una linea sobre como se verifica al personal, una linea sobre el pago, y el cierre.
5) Deci que la propuesta tiene una vigencia de {vigencia} horas.
6) Tope duro de salida: {maxtok} tokens, que son unas 200 palabras. Si te estas pasando, corta, no resumas a la mitad. Sin emojis. Firma: {firma}
7) Devolve SOLO el cuerpo del correo, sin asunto y sin comillas.

Pensa paso a paso: primero mira que entradas de la base responden a lo que pregunta esta familia, despues escribi el correo apoyandote solo en esas.

SOLICITUD
Familia: {{9.familia}}
Distrito: {{9.distrito}}
Turno: {{9.turno}}
Monto estimado: {{9.monto_estimado}}
Resumen: {{9.resumen}}

BASE DE CONOCIMIENTO (entradas atomicas verificadas de Cuidda):
{{16.text}}""".replace("{ciudad}", cfg("ciudad_operacion")) \
               .replace("{moneda}", cfg("moneda")) \
               .replace("{vigencia}", cfg("horas_vigencia_propuesta")) \
               .replace("{maxtok}", cfg("max_tokens_propuesta")) \
               .replace("{firma}", cfg("firma_correo"))

TEL_E164 = cfg("prefijo_telefono_pais") + "{{9.telefono}}"


def escenario_1():
    m1 = {"id": 1, "module": "google-email:triggerWatchNewEmails", "version": 4,
          "parameters": {"__IMTCONN__": CONN_GMAIL, "filterType": "gmailSearch",
                         "format": "full", "q": "is:unread subject:(solicitud de cuidado)",
                         "markSeen": True, "limit": 1},
          "mapper": {}, "metadata": dsg(0, 0, "[1] Gmail · Nueva solicitud entrante")}

    m2 = airtable_search(2, 300, 0, "[2] Airtable · Leer configuracion del sistema", T_CFG)
    m3 = {"id": 3, "module": "builtin:BasicAggregator", "version": 1,
          "parameters": {"feeder": 2},
          "mapper": {"Clave": "{{2.Clave}}", "Valor": "{{2.Valor}}"},
          "metadata": dsg(600, 0, "[3] Tools · Compactar configuracion")}

    m4 = airtable_search(4, 900, 0, "[4] Airtable · Leer cobertura vigente", T_COB)
    m5 = text_agg(5, 1200, 0, "[5] Tools · Compactar cobertura", 4,
                  "- {{4.Distrito}} | Cubierto={{4.Cubierto}} | Recargo movilidad={{4.`Recargo movilidad soles`}}")

    m6 = airtable_search(6, 1500, 0, "[6] Airtable · Leer catalogo de turnos", T_CAT)
    m7 = text_agg(7, 1800, 0, "[7] Tools · Compactar catalogo de turnos", 6,
                  "- {{6.Turno}} | Horario={{6.Horario}} | Tarifa={{6.`Tarifa soles`}} | {{6.`Notas operativas`}}")

    err8 = [
        log_error(101, 2100, 300, "[8E] Airtable · Registrar fallo de la IA",
                  "Escenario 1 Ingesta", "[8] IA Extraer y clasificar", "Fallo de API de IA",
                  "{{8.error.message}} | Asunto: {{1.subject}} | Remitente: {{1.fromEmail}}"),
        slack_msg(102, 2400, 300, "[8E] Slack · Alertar fallo de la IA",
                  ":warning: *Cuidda · fallo de la API de IA*\n"
                  "El clasificador no respondio y la solicitud quedo sin procesar.\n"
                  "*De:* {{1.fromEmail}}\n*Asunto:* {{1.subject}}\n*Error:* {{8.error.message}}\n"
                  "_Queda registrada en la tabla Log de errores._"),
        brk(103, 2700, 300, "[8E] Break · Detener con reintento"),
    ]
    m8 = ai_ask(8, 2100, 0, "[8] IA · Extraer y clasificar solicitud",
                "modelo_id_clasificacion", PROMPT_CLASIFICA, onerror=err8)

    m9 = {"id": 9, "module": "json:ParseJSON", "version": 1, "parameters": {"type": ""},
          "mapper": {"json": "{{8.answer}}"},
          "metadata": dsg(2400, 0, "[9] Parsear clasificacion")}

    # -------- ruta A: dato faltante
    r_a_1 = log_error(11, 3000, -300, "[11] Airtable · Registrar error de validacion",
                      "Escenario 1 Ingesta", "[10] Router ruta A", "Dato faltante",
                      "Faltan: {{9.faltantes}} | De: {{1.fromEmail}} | Asunto: {{1.subject}}")
    r_a_1["filter"] = {"name": "A · Dato faltante",
                       "conditions": [eq("{{9.datos_completos}}", "no")]}
    r_a_2 = slack_msg(12, 3300, -300, "[12] Slack · Alertar dato faltante",
                      ":mag: *Cuidda · solicitud incompleta*\n"
                      "*De:* {{1.fromName}} <{{1.fromEmail}}>\n*Asunto:* {{1.subject}}\n"
                      "*Faltan:* {{9.faltantes}}\n"
                      "_No se genero propuesta. Registrada en Log de errores._")

    # -------- ruta B: fuera de cobertura
    r_b_1 = airtable_create(13, 3000, 0, "[13] Airtable · Registrar solicitud fuera de cobertura",
                            T_SOL, {
                                S["codigo"]: 'SOL-{{formatDate(now; "YYYYMMDD-HHmmss")}}',
                                S["fecha"]: "{{now}}",
                                S["familia"]: "{{9.familia}}",
                                S["email"]: "{{9.email}}",
                                S["telefono"]: TEL_E164,
                                S["mensaje"]: "{{1.fullTextBody}}",
                                S["prioridad"]: "{{9.prioridad}}",
                                S["resumen"]: "{{9.resumen}}",
                                S["estado"]: "Rechazado",
                                S["motivo"]: "Fuera de cobertura: {{9.distrito}}",
                                S["modelo"]: cfg("modelo_clasificacion"),
                                S["aprobado"]: False,
                                S["hilo"]: "{{1.threadId}}",
                                S["msgid"]: "{{1.headers.`message-id`}}",
                            })
    r_b_1["filter"] = {"name": "B · Fuera de cobertura",
                       "conditions": [eq("{{9.datos_completos}}", "si"),
                                      eq("{{9.distrito_cubierto}}", "no")]}
    r_b_2 = {"id": 14, "module": "google-email:sendAnEmail", "version": 4,
             "parameters": {"__IMTCONN__": CONN_GMAIL},
             "mapper": {"to": ["{{9.email}}"],
                        "subject": "Cuidda · todavia no llegamos a {{9.distrito}}",
                        "bodyType": "text",
                        "emailHeaders": [
                            {"key": "In-Reply-To", "value": "{{1.headers.`message-id`}}"},
                            {"key": "References", "value": "{{1.headers.`message-id`}}"}],
                        "content": "Hola {{9.familia}},\n\nGracias por escribirnos. Hoy Cuidda opera en "
                                   + cfg("ciudad_operacion") +
                                   " pero todavia no tenemos personal verificado disponible en {{9.distrito}}, "
                                   "y preferimos decirtelo antes que hacerte esperar por algo que no podemos cumplir.\n\n"
                                   "Apenas abramos tu zona te avisamos.\n\n" + cfg("firma_correo")},
             "metadata": dsg(3300, 0, "[14] Gmail · Responder fuera de cobertura")}

    # -------- ruta C: solicitud valida
    r_c_1 = airtable_search(15, 3000, 300, "[15] Airtable · Leer base de conocimiento",
                            T_KB, formula='{Activo} = "Si"')
    r_c_1["filter"] = {"name": "C · Solicitud valida",
                       "conditions": [eq("{{9.datos_completos}}", "si"),
                                      eq("{{9.distrito_cubierto}}", "si")]}
    r_c_2 = text_agg(16, 3300, 300, "[16] Tools · Compactar contexto RAG", 15,
                     "- {{15.Tema}} ({{15.Categoria}}): {{15.Contenido}}")
    err17 = [
        log_error(104, 3600, 600, "[17E] Airtable · Registrar fallo de redaccion",
                  "Escenario 1 Ingesta", "[17] IA Redactar propuesta", "Fallo de API de IA",
                  "{{17.error.message}} | Familia: {{9.familia}} | Distrito: {{9.distrito}}"),
        resume(105, 3900, 600, "[17E] Resume · Continuar con aviso",
               "PROPUESTA NO GENERADA - la API de IA fallo. Revisar a mano antes de aprobar."),
    ]
    r_c_3 = ai_ask(17, 3600, 300, "[17] IA · Redactar propuesta",
                   "modelo_id_redaccion", PROMPT_REDACTA, onerror=err17)
    r_c_4 = airtable_create(18, 3900, 300, "[18] Airtable · Crear solicitud vinculada", T_SOL, {
        S["codigo"]: 'SOL-{{formatDate(now; "YYYYMMDD-HHmmss")}}',
        S["fecha"]: "{{now}}",
        S["familia"]: "{{9.familia}}",
        S["email"]: "{{9.email}}",
        S["telefono"]: TEL_E164,
        S["mensaje"]: "{{1.fullTextBody}}",
        S["distrito"]: ["{{9.distrito}}"],
        S["turno"]: ["{{9.turno}}"],
        S["prioridad"]: "{{9.prioridad}}",
        S["resumen"]: "{{9.resumen}}",
        S["propuesta"]: "{{17.answer}}",
        S["monto"]: "{{9.monto_estimado}}",
        S["modelo"]: cfg("modelo_redaccion"),
        S["estado"]: "Procesado por IA",
        S["aprobado"]: False,
        S["hilo"]: "{{1.threadId}}",
        S["msgid"]: "{{1.headers.`message-id`}}",
    })
    r_c_5 = slack_msg(19, 4200, 300, "[19] Slack · Pedir aprobacion humana",
                      ":inbox_tray: *Cuidda · propuesta lista para revisar*\n"
                      "*Familia:* {{9.familia}}  ·  *Prioridad:* {{9.prioridad}}\n"
                      "*Distrito:* {{9.distrito}}  ·  *Turno:* {{9.turno}}\n"
                      "*Monto estimado:* {{9.monto_estimado}} " + cfg("moneda") + "\n"
                      "*Codigo:* {{18.`Codigo`}}\n\n```{{17.answer}}```\n\n"
                      "_Nada sale al cliente hasta que alguien marque *Aprobado por Humano* "
                      "y ponga el Estado en *Aprobado* en Airtable._")
    r_c_6 = airtable_update(20, 4500, 300, "[20] Airtable · Guardar hilo de Slack",
                            T_SOL, "{{18.id}}", {S["slackts"]: "{{19.ts}}"})

    m10 = {"id": 10, "module": "builtin:BasicRouter", "version": 1, "mapper": None,
           "metadata": dsg(2700, 0, "[10] Router · Rutas de validacion"),
           "routes": [{"flow": [r_a_1, r_a_2]},
                      {"flow": [r_b_1, r_b_2]},
                      {"flow": [r_c_1, r_c_2, r_c_3, r_c_4, r_c_5, r_c_6]}]}

    return {"name": "Cuidda · 1 · Ingesta y calificacion IA",
            "flow": [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10],
            "metadata": META}


# =================================================================== ESCENARIO 2
PROPUESTA_ESTADO = '{{if(length(trim(1.`Propuesta generada`)) = 0; "vacia"; "lista")}}'


def escenario_2():
    m1 = {"id": 1, "module": "airtable:TriggerWatchRecords", "version": 3,
          "parameters": {"__IMTCONN__": CONN_AIRTABLE, "base": BASE, "useColumnId": False,
                         "table": T_SOL,
                         "config": {"triggerField": "Modificado", "labelField": "Codigo"},
                         "maxRecords": 10, "view": "",
                         "formula": 'AND({Aprobado por Humano} = 1, {Estado} = "Aprobado")'},
          "mapper": {},
          "metadata": dsg(0, 0, "[1] Airtable · Solicitud aprobada por un humano")}

    m2 = airtable_search(2, 300, 0, "[2] Airtable · Leer configuracion del sistema", T_CFG)
    m3 = {"id": 3, "module": "builtin:BasicAggregator", "version": 1,
          "parameters": {"feeder": 2},
          "mapper": {"Clave": "{{2.Clave}}", "Valor": "{{2.Valor}}"},
          "metadata": dsg(600, 0, "[3] Tools · Compactar configuracion")}

    # -------- ruta A: la propuesta llego vacia (camino infeliz)
    a1 = log_error(5, 1200, -300, "[5] Airtable · Registrar propuesta vacia",
                   "Escenario 2 Envio", "[4] Router ruta A", "Propuesta vacia",
                   "La solicitud {{1.Codigo}} fue aprobada pero no tiene propuesta generada. No se envio nada.")
    a1["filter"] = {"name": "A · Propuesta vacia",
                    "conditions": [eq(PROPUESTA_ESTADO, "vacia")]}
    a2 = slack_msg(6, 1500, -300, "[6] Slack · Alertar propuesta vacia",
                   ":no_entry: *Cuidda · aprobacion bloqueada*\n"
                   "*Codigo:* {{1.Codigo}}  ·  *Familia:* {{1.Familia}}\n"
                   "La solicitud esta aprobada pero el campo *Propuesta generada* esta vacio, "
                   "asi que el correo NO salio.\n"
                   "_Revisar a mano y volver a marcar el Estado en Aprobado._",
                   thread_ts="{{1.`Slack ts`}}")

    # -------- ruta B: envio real a la familia
    err7 = [
        log_error(101, 1200, 600, "[7E] Airtable · Registrar fallo de envio",
                  "Escenario 2 Envio", "[7] Gmail Enviar propuesta", "Fallo de API de Gmail",
                  "{{7.error.message}} | Codigo: {{1.Codigo}} | Para: {{1.Email}}"),
        slack_msg(102, 1500, 600, "[7E] Slack · Alertar fallo de envio",
                  ":warning: *Cuidda · no se pudo enviar la propuesta*\n"
                  "*Codigo:* {{1.Codigo}}\n*Error:* {{7.error.message}}\n"
                  "_El estado queda en Aprobado y el flujo reintenta._"),
        brk(103, 1800, 600, "[7E] Break · Detener con reintento"),
    ]
    b1 = {"id": 7, "module": "google-email:sendAnEmail", "version": 4,
          "parameters": {"__IMTCONN__": CONN_GMAIL},
          "mapper": {"to": ["{{1.Email}}"],
                     "subject": "Cuidda · tu propuesta de cuidado ({{1.Codigo}})",
                     "bodyType": "text",
                     "emailHeaders": [
                         {"key": "In-Reply-To", "value": "{{1.`Message ID Gmail`}}"},
                         {"key": "References", "value": "{{1.`Message ID Gmail`}}"}],
                     "content": "{{1.`Propuesta generada`}}"},
          "metadata": dsg(1200, 300, "[7] Gmail · Enviar propuesta a la familia"),
          "onerror": err7}
    b1["filter"] = {"name": "B · Listo para enviar",
                    "conditions": [eq(PROPUESTA_ESTADO, "lista")]}

    b2 = airtable_update(8, 1500, 300, "[8] Airtable · Cerrar el ciclo (Enviado)",
                         T_SOL, "{{1.id}}",
                         {S["estado"]: "Enviado", S["envio"]: "{{now}}"})

    err9 = [resume(104, 1800, 600, "[9E] Resume · Seguir sin confirmacion en Slack",
                   "Slack no respondio. El correo ya salio y la solicitud quedo en Enviado.")]
    b3 = slack_msg(9, 1800, 300, "[9] Slack · Confirmar envio en el hilo",
                   ":white_check_mark: *Cuidda · propuesta enviada*\n"
                   "*Codigo:* {{1.Codigo}}  ·  *Familia:* {{1.Familia}}\n"
                   "*Para:* {{1.Email}}\n"
                   "_Estado actualizado a Enviado. Este registro ya no vuelve a entrar al flujo._",
                   thread_ts="{{1.`Slack ts`}}")
    b3["onerror"] = err9

    m4 = {"id": 4, "module": "builtin:BasicRouter", "version": 1, "mapper": None,
          "metadata": dsg(900, 0, "[4] Router · Check de seguridad antes de enviar"),
          "routes": [{"flow": [a1, a2]}, {"flow": [b1, b2, b3]}]}

    return {"name": "Cuidda · 2 · Envio tras aprobacion humana",
            "flow": [m1, m2, m3, m4],
            "metadata": META}


def contar(flow):
    n = 0
    for m in flow:
        n += 1
        if m.get("onerror"):
            n += contar(m["onerror"])
        if m.get("routes"):
            for r in m["routes"]:
                n += contar(r["flow"])
    return n


if __name__ == "__main__":
    out = "/mnt/user-data/outputs"
    here = os.path.dirname(os.path.abspath(__file__))
    for nombre, bp in (("cuidda-escenario-1", escenario_1()),
                       ("cuidda-escenario-2", escenario_2())):
        pretty = json.dumps(bp, ensure_ascii=False, indent=2)
        minified = json.dumps(bp, ensure_ascii=False, separators=(",", ":"))
        for d in (out, here):
            with open(os.path.join(d, nombre + ".blueprint.json"), "w", encoding="utf-8") as f:
                f.write(pretty)
        with open(os.path.join(here, nombre + ".min.json"), "w", encoding="utf-8") as f:
            f.write(minified)
        print(f"{nombre}: {contar(bp['flow'])} modulos, {len(minified)} chars")
