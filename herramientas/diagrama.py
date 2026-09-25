# -*- coding: utf-8 -*-
"""Mapa de arquitectura · Cuidda — Entrega Final."""
import cairosvg

W, H = 2000, 1700

NAVY  = "#022454"
TEAL  = "#2FA5B8"
SOFT  = "#E8F5F7"
AMBER = "#B8760F"
AMB_S = "#FDF1DE"
RED   = "#B03A2E"
RED_S = "#FBE9E7"
GREEN = "#1F8A5B"
GRN_S = "#E4F4EC"
PURP  = "#5B2E9E"
PUR_S = "#F3ECFB"
GREY  = "#6B7785"
LINE  = "#C9D4DF"
WHITE = "#FFFFFF"
INK   = "#0B1B2B"

P = []

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def text(x, y, s, size=17, fill=INK, anchor="middle", weight="400", family="Comfortaa"):
    P.append(f'<text x="{x}" y="{y}" font-family="{family}, sans-serif" font-size="{size}" '
             f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def lines(x, y, rows, size=15, fill=INK, anchor="middle", lh=20, weight="400"):
    for i, r in enumerate(rows):
        text(x, y + i*lh, r, size, fill, anchor, weight)

def rect(x, y, w, h, fill=WHITE, stroke=LINE, rx=14, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    P.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

def oval(cx, cy, w, h, fill, stroke):
    P.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="2.5"/>')

def diamond(cx, cy, w, h, fill=AMB_S, stroke=AMBER):
    pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
    P.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')

def arrow(x1, y1, x2, y2, color=NAVY, dash=None, sw=2.4, marker="ah"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    P.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
             f'stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')

def path(d, color=NAVY, dash=None, sw=2.4, marker="ah"):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    P.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da} '
             f'marker-end="url(#{marker})"/>')

def tag(x, y, s, fill, stroke, tw=None, size=13):
    tw = tw or (len(s) * 8.2 + 26)
    rect(x - tw/2, y - 16, tw, 32, fill, stroke, rx=16, sw=1.8)
    text(x, y + 5, s, size, stroke, weight="700", family="Plus Jakarta Sans")

P.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

# ----------------------------------------------------------------- título
text(70, 68, "Mapa de arquitectura · Cuidda", 34, NAVY, "start", "700", "Plus Jakarta Sans")
text(70, 104, "Solicitud de cuidado entrante  →  calificacion con IA sobre la base de datos  "
              "→  validacion humana  →  salida multicanal", 18, GREY, "start")
P.append(f'<line x1="70" y1="130" x2="{W-70}" y2="130" stroke="{LINE}" stroke-width="2"/>')

# ============================================================ ESCENARIO 1
rect(60, 170, 1880, 640, "#FBFDFE", LINE, rx=20, sw=2, dash="10 7")
tag(290, 170, "ESCENARIO 1  ·  Ingesta y calificacion IA", SOFT, NAVY, tw=430, size=14)
text(1900, 205, "Make · us2 · Gmail cada 15 min", 14, GREY, "end")

# fila principal
oval(190, 300, 250, 92, SOFT, TEAL)
lines(190, 288, ["[1] Gmail", "Nueva solicitud entrante"], 15, NAVY, weight="700")
text(190, 370, "Trigger · Watch emails", 13, GREY)

rect(360, 250, 230, 100, WHITE, NAVY)
lines(475, 288, ["[2] Airtable", "Leer configuracion"], 15, NAVY, weight="700")
text(475, 324, "+ [3] Agregador de array", 12, GREY)

rect(630, 250, 230, 100, WHITE, NAVY)
lines(745, 276, ["[4] Airtable", "Distritos con cobertura", "filtro {Cubierto}=Si", "+ [5] Compactar"], 13, NAVY, weight="700")

rect(900, 250, 230, 100, WHITE, NAVY)
lines(1015, 282, ["[6] Airtable", "Leer catalogo turnos", "+ [7] Compactar"], 14, NAVY, weight="700")

rect(1170, 245, 250, 110, PUR_S, PURP, rx=16)
lines(1295, 282, ["[8] IA · Clasificar", "gpt-5-nano", "salida JSON estricta"], 14, PURP, weight="700")
text(1295, 375, "la cobertura ya viene filtrada por la base: la IA solo hace matching", 12, GREY)

rect(1460, 260, 170, 80, WHITE, NAVY)
text(1545, 305, "[9] Parse JSON", 15, NAVY, weight="700", family="Plus Jakarta Sans")

diamond(1790, 300, 200, 130)
lines(1790, 292, ["[10] Router", "Validacion"], 14, AMBER, weight="700")

for a, b in [(315, 360), (590, 630), (860, 900), (1130, 1170), (1420, 1460), (1630, 1690)]:
    arrow(a, 300, b, 300)

# espina del router
P.append(f'<path d="M 1890 300 H 1940" fill="none" stroke="{GREY}" stroke-width="2.4"/>')
P.append(f'<path d="M 1940 300 V 745" fill="none" stroke="{GREY}" stroke-width="2.4"/>')

# ---------- Ruta C · valida (y = 455)
path("M 1940 455 H 1885", GREEN, marker="ahg")
tag(1750, 392, "C · Solicitud valida", GRN_S, GREEN, tw=210)
rect(1625, 415, 260, 100, GRN_S, GREEN)
lines(1755, 447, ["[15] Airtable", "Leer base de conocimiento", "+ [16] Compactar RAG"], 13, GREEN, weight="700")

path("M 1625 465 H 1575", GREEN, marker="ahg")
rect(1305, 415, 260, 100, PUR_S, PURP, rx=16)
lines(1435, 447, ["[17] IA · Redactar propuesta", "claude-haiku-4.5", "max_tokens desde config"], 13, PURP, weight="700")

path("M 1305 465 H 1255", GREEN, marker="ahg")
rect(985, 415, 260, 100, GRN_S, GREEN)
lines(1115, 447, ["[18] Airtable", "Crear solicitud vinculada", "Estado = Procesado por IA"], 13, GREEN, weight="700")

path("M 985 465 H 935", GREEN, marker="ahg")
rect(665, 415, 260, 100, GRN_S, GREEN)
lines(795, 447, ["[19] Slack", "Pedir aprobacion humana", "devuelve el thread ts"], 13, GREEN, weight="700")

path("M 665 465 H 615", GREEN, marker="ahg")
rect(345, 415, 260, 100, GRN_S, GREEN)
lines(475, 447, ["[20] Airtable", "Guardar hilo de Slack", "Slack ts en la solicitud"], 13, GREEN, weight="700")

# ---------- Ruta B · fuera de cobertura (y = 600)
path("M 1940 600 H 1885", AMBER, marker="aha")
tag(1755, 539, "B · Fuera de cobertura", AMB_S, AMBER, tw=230)
rect(1625, 562, 260, 88, AMB_S, AMBER)
lines(1755, 597, ["[13] Airtable", "Solicitud = Rechazado"], 14, AMBER, weight="700")

path("M 1625 606 H 1575", AMBER, marker="aha")
rect(1305, 562, 260, 88, AMB_S, AMBER)
lines(1435, 597, ["[14] Gmail", "Respuesta amable al cliente"], 13, AMBER, weight="700")
text(1180, 606, "fin · sin propuesta", 12, GREY, "end")

# ---------- Ruta A · dato faltante (y = 730)
path("M 1940 730 H 1885", RED, marker="ahr")
tag(1755, 669, "A · Dato faltante", RED_S, RED, tw=190)
rect(1625, 692, 260, 88, RED_S, RED)
lines(1755, 727, ["[11] Airtable", "Registrar en Log de errores"], 13, RED, weight="700")

path("M 1625 736 H 1575", RED, marker="ahr")
rect(1305, 692, 260, 88, RED_S, RED)
lines(1435, 727, ["[12] Slack", "Alertar al equipo"], 14, RED, weight="700")
text(1180, 736, "fin · nada sale al cliente", 12, GREY, "end")

# ============================================================ HITL
rect(60, 845, 1880, 120, "#FFF8EC", AMBER, rx=20, sw=3)
text(1000, 886, "PAUSA  ·  HUMAN IN THE LOOP", 22, AMBER, "middle", "700", "Plus Jakarta Sans")
text(1000, 921, "El Escenario 1 termina aca. Una persona lee la propuesta y marca la casilla «Aprobado por Humano» en Airtable.", 16, INK)
text(1000, 947, "Si nadie la marca, nada sale al cliente: no hay reintento, no hay caducidad automatica, no hay camino alternativo.", 14, GREY)

path("M 795 515 V 845", AMBER, dash="9 6", marker="aha")

# ============================================================ ESCENARIO 2
rect(60, 1000, 1880, 400, "#FBFDFE", LINE, rx=20, sw=2, dash="10 7")
tag(305, 1000, "ESCENARIO 2  ·  Envio tras aprobacion humana", SOFT, NAVY, tw=460, size=14)
text(1900, 1035, "Make · us2 · trigger inteligente « From now on »", 14, GREY, "end")

oval(200, 1105, 280, 96, SOFT, TEAL)
lines(200, 1093, ["[1] Airtable", "Solicitud aprobada"], 15, NAVY, weight="700")
text(200, 1232, "Watch Records · campo « Modificado »", 12, GREY)

rect(370, 1055, 240, 100, WHITE, NAVY)
lines(490, 1087, ["[2] Airtable", "Leer configuracion", "+ [3] Compactar"], 14, NAVY, weight="700")

diamond(770, 1105, 220, 150)
lines(770, 1089, ["[4] Router", "Check de seguridad", "antes de enviar"], 13, AMBER, weight="700")

# ---------- ruta B · listo para enviar
tag(1035, 1030, "B · Listo para enviar", GRN_S, GREEN, tw=210)
rect(910, 1055, 250, 100, GRN_S, GREEN)
lines(1035, 1087, ["[7] Gmail", "Enviar propuesta", "In-Reply-To + References"], 13, GREEN, weight="700")

rect(1210, 1055, 250, 100, GRN_S, GREEN)
lines(1335, 1087, ["[8] Airtable", "Estado = Enviado", "+ Fecha envio"], 13, GREEN, weight="700")

rect(1510, 1055, 250, 100, GRN_S, GREEN)
lines(1635, 1087, ["[9] Slack", "Confirmar en el hilo", "thread_ts mapeado"], 13, GREEN, weight="700")

arrow(340, 1105, 370, 1105)
arrow(610, 1105, 655, 1105)
arrow(885, 1105, 910, 1105, GREEN, marker="ahg")
arrow(1160, 1105, 1210, 1105, GREEN, marker="ahg")
arrow(1460, 1105, 1510, 1105, GREEN, marker="ahg")

# ---------- ruta A · propuesta vacia
path("M 770 1180 V 1290 H 900", RED, marker="ahr")
tag(1035, 1222, "A · Propuesta vacia", RED_S, RED, tw=200)
rect(910, 1246, 250, 88, RED_S, RED)
lines(1035, 1281, ["[5] Airtable", "Registrar propuesta vacia"], 13, RED, weight="700")

arrow(1160, 1290, 1210, 1290, RED, marker="ahr")
rect(1210, 1246, 250, 88, RED_S, RED)
lines(1335, 1281, ["[6] Slack", "Alertar en el hilo"], 14, RED, weight="700")
text(1490, 1290, "fin · no sale ningun correo", 13, RED, "start")

# ---------- corte del loop
path("M 1335 1155 V 1200 H 200 V 1155", TEAL, dash="8 6", marker="aht")
text(770, 1192, "Estado = Enviado  →  el registro deja de cumplir la formula del trigger: el ciclo se cierra solo",
     13, TEAL, "middle")

# ============================================================ MEMORIA
rect(60, 1450, 1880, 195, SOFT, TEAL, rx=20, sw=2.5)
text(105, 1490, "MEMORIA Y REGISTRO DEL SISTEMA  ·  Airtable « Cuidda · Operaciones »",
     18, NAVY, "start", "700", "Plus Jakarta Sans")
text(1895, 1490, "lectura y escritura desde los dos escenarios", 13, GREY, "end")

tablas = [
    ("Solicitudes", "estado de cada caso"),
    ("Catalogo de turnos", "horario y tarifa"),
    ("Cobertura", "distritos de Trujillo"),
    ("Base de conocimiento", "hechos atomicos"),
    ("Log de errores", "toda falla queda escrita"),
    ("Configuracion", "cero datos hardcodeados"),
]
x0, wbox = 100, 293
for i, (n, d) in enumerate(tablas):
    x = x0 + i * (wbox + 8)
    rect(x, 1515, wbox, 80, WHITE, TEAL, rx=12, sw=2)
    text(x + wbox/2, 1548, n, 15, NAVY, weight="700", family="Plus Jakarta Sans")
    text(x + wbox/2, 1574, d, 13, GREY)

P.append(f'<path d="M 246 1595 V 1617 H 1125 V 1595" fill="none" stroke="{TEAL}" '
         f'stroke-width="2" stroke-dasharray="5 4"/>')
text(686, 1636, "Solicitudes → Catalogo de turnos  y  Solicitudes → Cobertura   "
                "(campos vinculados + campos de busqueda)", 13, TEAL)

P.append(f'<path d="M 1000 1400 V 1450" fill="none" stroke="{TEAL}" stroke-width="2.4" '
         f'stroke-dasharray="7 5" marker-end="url(#aht)"/>')
P.append(f'<path d="M 1000 810 V 845" fill="none" stroke="none"/>')

defs = f'''<defs>
<marker id="ah" markerWidth="11" markerHeight="11" refX="9" refY="4" orient="auto">
  <path d="M0,0 L9,4 L0,8 z" fill="{NAVY}"/></marker>
<marker id="aht" markerWidth="11" markerHeight="11" refX="9" refY="4" orient="auto">
  <path d="M0,0 L9,4 L0,8 z" fill="{TEAL}"/></marker>
<marker id="ahr" markerWidth="11" markerHeight="11" refX="9" refY="4" orient="auto">
  <path d="M0,0 L9,4 L0,8 z" fill="{RED}"/></marker>
<marker id="aha" markerWidth="11" markerHeight="11" refX="9" refY="4" orient="auto">
  <path d="M0,0 L9,4 L0,8 z" fill="{AMBER}"/></marker>
<marker id="ahg" markerWidth="11" markerHeight="11" refX="9" refY="4" orient="auto">
  <path d="M0,0 L9,4 L0,8 z" fill="{GREEN}"/></marker>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}">' + defs + "".join(P) + "</svg>")

open("arquitectura-cuidda.svg", "w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(), write_to="arquitectura-cuidda.png",
                 output_width=W, output_height=H)
print("ok")
