"""
Formulario del Donante — Banco de Sangre Hospital Amazónico
Desplegado en Streamlit Community Cloud
25 preguntas — idéntico al sistema principal
"""
import streamlit as st
import datetime
import json
from supabase import create_client

st.set_page_config(
    page_title="Formulario Donante — Hospital Amazónico",
    page_icon="🩸",
    layout="centered"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase     = create_client(SUPABASE_URL, SUPABASE_KEY)

DEPARTAMENTOS = [
    "", "Amazonas", "Áncash", "Apurímac", "Arequipa", "Ayacucho", "Cajamarca",
    "Callao", "Cusco", "Huancavelica", "Huánuco", "Ica", "Junín", "La Libertad",
    "Lambayeque", "Lima", "Loreto", "Madre de Dios", "Moquegua", "Pasco",
    "Piura", "Puno", "San Martín", "Tacna", "Tumbes", "Ucayali"
]

UC_KEYS = [
    "c_nombres","c_apellidos","c_domicilio","c_ocup_otros","c_ct_otros",
    "c_rec_nom","c_rec_ape",
    "c_q1d","c_q3d","c_q8d","c_q9d","c_q10d","c_q11d","c_q12d","c_q13d",
    "c_q14d","c_q15d","c_q16d","c_q17d","c_q22d","c_q23d","c_q24d","c_q25d",
]

st.markdown("""
<style>
.hospital-header{background:linear-gradient(135deg,#b71c1c,#7f0000);
  padding:20px;border-radius:12px;text-align:center;margin-bottom:24px}
.hospital-header h2{color:#fff;margin:0;font-size:1.4rem}
.hospital-header p{color:#ffcdd2;margin:6px 0 0;font-size:.9rem}
.seccion{border-left:4px solid #b71c1c;padding:6px 12px;background:#fff8f8;
  border-radius:0 8px 8px 0;margin:20px 0 10px;font-weight:700;color:#7f0000}
</style>
""", unsafe_allow_html=True)

# ── Leer parámetro de campaña (?campania=ID) ──────────────────
_params      = st.query_params
_campania_id = _params.get("campania", None)
_campania_info = None
if _campania_id:
    try:
        _res = supabase.table("campanias_donacion").select(
            "id,nombre_campania,institucion,fecha_campania"
        ).eq("id", int(_campania_id)).execute()
        if _res.data:
            _campania_info = _res.data[0]
    except Exception:
        pass

if _campania_info:
    st.markdown(f"""
    <div class="hospital-header" style="background:linear-gradient(135deg,#e65100,#bf360c)">
      <h2>📣 CAMPAÑA — {_campania_info.get('nombre_campania','').upper()}</h2>
      <p>🏢 {_campania_info.get('institucion','')} &nbsp;|&nbsp;
         📅 {_campania_info.get('fecha_campania','')} &nbsp;|&nbsp;
         🩸 Banco de Sangre — Hospital Amazónico</p>
    </div>""", unsafe_allow_html=True)
    st.info("📣 Este formulario está vinculado a una campaña de donación voluntaria.")
else:
    st.markdown("""
    <div class="hospital-header">
      <h2>🩸 Banco de Sangre — Hospital Amazónico</h2>
      <p>Formulario previo de donación · Yarinacocha, Ucayali</p>
    </div>""", unsafe_allow_html=True)

def ya_envio_hoy(dni):
    hoy = datetime.date.today().isoformat()
    res = supabase.table("donantes_cloud").select("id") \
        .eq("dni", dni) \
        .gte("fecha_registro", hoy + "T00:00:00") \
        .lte("fecha_registro", hoy + "T23:59:59") \
        .execute()
    return len(res.data) > 0

if st.session_state.get("enviado"):
    if _campania_info:
        st.success(f"✅ ¡Registro recibido! Campaña: **{_campania_info.get('nombre_campania','')}**")
        st.info(f"🏢 {_campania_info.get('institucion','')} — {_campania_info.get('fecha_campania','')}\n\n¡Gracias por su donación voluntaria!")
    else:
        st.success("✅ Su registro fue recibido correctamente.")
        st.info("El personal del banco de sangre lo atenderá en breve. ¡Gracias por su donación!")
    st.balloons()
    st.stop()

# ── DATOS PERSONALES ─────────────────────────────────────────
st.markdown('<div class="seccion">Datos Personales</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    nombres          = st.text_input("Nombres completos *",  key="c_nombres")
    apellidos        = st.text_input("Apellidos *",           key="c_apellidos")
    dni              = st.text_input("DNI (8 dígitos) *", max_chars=8, key="c_dni")
    edad             = st.number_input("Edad *", min_value=18, max_value=65, value=None, step=1)
    sexo             = st.selectbox("Sexo *", ["", "Masculino", "Femenino"])
    estado_civil     = st.selectbox("Estado civil", ["", "Soltero(a)", "Casado(a)", "Conviviente", "Divorciado(a)", "Viudo(a)"])
    lugar_nacimiento = st.selectbox("Lugar de nacimiento", DEPARTAMENTOS)
    fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None,
                                      min_value=datetime.date(1950,1,1),
                                      max_value=datetime.date(2007,12,31),
                                      format="DD/MM/YYYY")
with c2:
    grado_instruccion    = st.selectbox("Grado de instrucción", ["","Primaria","Secundaria","Superior","Master","Doctorado"])
    domicilio            = st.text_input("Domicilio actual", key="c_domicilio")
    celular              = st.text_input("Celular (9 dígitos)", max_chars=9, key="c_celular")
    ocupacion_op         = st.selectbox("Ocupación", ["","Estudiante","Empleado","Independiente","Ama de casa","Otros"])
    ocupacion_otros      = st.text_input("Especifique su ocupación", key="c_ocup_otros") if ocupacion_op=="Otros" else ""
    centro_trabajo_op    = st.selectbox("Centro de trabajo", ["","Independiente","Sector Público","Sector Privado","Otros"])
    centro_trabajo_otros = st.text_input("Especifique su centro de trabajo", key="c_ct_otros") if centro_trabajo_op=="Otros" else ""

ocupacion      = ocupacion_otros      if ocupacion_op      == "Otros" else ocupacion_op
centro_trabajo = centro_trabajo_otros if centro_trabajo_op == "Otros" else centro_trabajo_op

# ── TIPO DE DONACIÓN ─────────────────────────────────────────
st.markdown('<div class="seccion">Tipo de Donación</div>', unsafe_allow_html=True)
tipo_donacion = st.radio("Usted dona como:", ["Voluntario","Reposición","Autólogo"], horizontal=True)

receptor_nombres = receptor_apellidos = receptor_dni = ""
if tipo_donacion == "Reposición":
    st.warning("Ingrese los datos del paciente receptor:")
    r1, r2, r3 = st.columns(3)
    with r1: receptor_nombres   = st.text_input("Nombres del paciente",  key="c_rec_nom")
    with r2: receptor_apellidos = st.text_input("Apellidos del paciente", key="c_rec_ape")
    with r3: receptor_dni       = st.text_input("DNI del paciente", max_chars=8, key="c_rec_dni")

# ── CUESTIONARIO (25 preguntas — igual al sistema principal) ──
st.markdown('<div class="seccion">Cuestionario de Selección</div>', unsafe_allow_html=True)
st.info("Responda con sinceridad. Sus respuestas son confidenciales y protegen su salud.")

resp = {}

resp["q1"] = st.radio("1. ¿Ha donado sangre anteriormente?", ["No","Sí"], horizontal=True, key="cq1")
if resp["q1"] == "Sí":
    resp["q1_detalle"] = st.text_input("¿Hace cuánto tiempo fue su última donación?", key="c_q1d")

resp["q2"] = st.radio("2. ¿Donó sangre en los últimos tres meses?", ["No","Sí"], horizontal=True, key="cq2")

resp["q3"] = st.radio("3. ¿Está tomando o tomó algún medicamento en los últimos días?", ["No","Sí"], horizontal=True, key="cq3")
if resp["q3"] == "Sí":
    resp["q3_detalle"] = st.text_input("¿Cuáles medicamentos?", key="c_q3d")

if sexo == "Femenino":
    q_fem = st.date_input("4. Fecha de última menstruación:", value=None, format="DD/MM/YYYY", key="cq4_fem")
    resp["q4"] = str(q_fem) if q_fem else "No indicada"
    resp["q7"] = st.radio("7. ¿Está gestando o dando de lactar?", ["No","Sí"], horizontal=True, key="cq7")
else:
    resp["q4"] = "N/A"
    resp["q7"] = "N/A"

resp["q5"] = st.radio("5. ¿Se encuentra actualmente bien de salud?", ["Sí","No"], horizontal=True, key="cq5")
resp["q6"] = st.radio("6. ¿Ha tenido fiebre, dolor de cabeza o enfermedad en las últimas dos semanas?", ["No","Sí"], horizontal=True, key="cq6")

resp["q8"] = st.radio("8. ¿Ha sido operado en los últimos seis meses?", ["No","Sí"], horizontal=True, key="cq8")
if resp["q8"] == "Sí":
    resp["q8_detalle"] = st.text_input("¿De qué fue operado?", key="c_q8d")

resp["q9"] = st.radio("9. ¿Ha recibido sangre, trasplante de órgano o tejidos?", ["No","Sí"], horizontal=True, key="cq9")
if resp["q9"] == "Sí":
    resp["q9_detalle"] = st.text_input("¿Qué recibió y hace cuánto tiempo?", key="c_q9d")

resp["q10"] = st.radio("10. ¿En los últimos 12 meses se realizó tatuajes o punción de piel (acupuntura, aretes)?", ["No","Sí"], horizontal=True, key="cq10")
if resp["q10"] == "Sí":
    resp["q10_detalle"] = st.text_input("Especifique (tatuaje, arete, acupuntura, etc.):", key="c_q10d")

resp["q11"] = st.radio("11. ¿Recibió alguna vacuna en el último mes?", ["No","Sí"], horizontal=True, key="cq11")
if resp["q11"] == "Sí":
    resp["q11_detalle"] = st.text_input("¿Cuál vacuna?", key="c_q11d")

resp["q12"] = st.radio("12. ¿Tuvo contacto con persona portadora de alguna enfermedad contagiosa?", ["No","Sí"], horizontal=True, key="cq12")
if resp["q12"] == "Sí":
    resp["q12_detalle"] = st.text_input("¿Qué enfermedad tenía la persona?", key="c_q12d")

resp["q13"] = st.radio("13. ¿Ha viajado recientemente a comunidades nativas, selva profunda o zonas con brotes de paludismo, fiebre amarilla o leishmaniasis?", ["No","Sí"], horizontal=True, key="cq13")
if resp["q13"] == "Sí":
    resp["q13_detalle"] = st.text_input("¿A qué zona específica viajó?", key="c_q13d")

resp["q14"] = st.radio("14. ¿Padece de alguna molestia que requiere control médico continuo?", ["No","Sí"], horizontal=True, key="cq14")
if resp["q14"] == "Sí":
    resp["q14_detalle"] = st.text_input("¿Cuál molestia?", key="c_q14d")

resp["q15"] = st.radio("15. ¿Consume usted algún tipo de droga?", ["No","Sí"], horizontal=True, key="cq15")
if resp["q15"] == "Sí":
    resp["q15_detalle"] = st.text_input("¿Cuál droga?", key="c_q15d")

resp["q16"] = st.radio("16. ¿Ha tenido tratamiento o procedimiento odontológico reciente?", ["No","Sí"], horizontal=True, key="cq16")
if resp["q16"] == "Sí":
    resp["q16_detalle"] = st.text_input("¿Qué tratamiento odontológico recibió?", key="c_q16d")

resp["q17"] = st.radio("17. ¿Tiene actualmente alguna herida en el cuerpo?", ["No","Sí"], horizontal=True, key="cq17")
if resp["q17"] == "Sí":
    resp["q17_detalle"] = st.text_input("¿En qué parte del cuerpo?", key="c_q17d")

resp["q18"] = st.radio("18. ¿Ha tenido más de dos parejas sexuales en el último año?", ["No","Sí"], horizontal=True, key="cq18")
resp["q19"] = st.radio("19. ¿Tiene alguna duda de ser portador de VIH, Hepatitis B o C?", ["No","Sí"], horizontal=True, key="cq19")
resp["q20"] = st.radio("20. En el último año, ¿ha tenido relaciones sexuales ocasionales sin protección?", ["No","Sí"], horizontal=True, key="cq20")
resp["q21"] = st.radio("21. ¿Ha tenido alguna prueba para VIH que dio positiva?", ["No","Sí"], horizontal=True, key="cq21")

resp["q22"] = st.radio("22. ¿Ha padecido de alguna enfermedad de transmisión sexual?", ["No","Sí"], horizontal=True, key="cq22")
if resp["q22"] == "Sí":
    resp["q22_detalle"] = st.text_input("¿Cuál enfermedad de transmisión sexual?", key="c_q22d")

resp["q23"] = st.radio("23. ¿Ha sido excluido como donante anteriormente?", ["No","Sí"], horizontal=True, key="cq23")
if resp["q23"] == "Sí":
    resp["q23_detalle"] = st.text_input("¿Por qué motivo fue excluido?", key="c_q23d")

resp["q24"] = st.radio("24. ¿Viajó fuera del país en el último año?", ["No","Sí"], horizontal=True, key="cq24")
if resp["q24"] == "Sí":
    resp["q24_detalle"] = st.text_input("¿A qué país/países?", key="c_q24d")

resp["q25"] = st.radio("25. ¿Padece o ha padecido de alguna enfermedad grave, crónica o infecciosa?", ["No","Sí"], horizontal=True, key="cq25")
if resp["q25"] == "Sí":
    resp["q25_detalle"] = st.text_input("Especifique qué enfermedad:", key="c_q25d")

# ── Conversión a mayúsculas ───────────────────────────────────
_hay_minus = False
for _k in UC_KEYS:
    _v = st.session_state.get(_k, "")
    if isinstance(_v, str) and _v != _v.upper():
        st.session_state[_k] = _v.upper()
        _hay_minus = True
if _hay_minus:
    st.rerun()

# ── ENVÍO ────────────────────────────────────────────────────
st.markdown("---")
if st.button("✅ Enviar Formulario", type="primary", use_container_width=True):
    errores = []
    if not nombres.strip():  errores.append("• Nombres completos es obligatorio")
    if not apellidos.strip(): errores.append("• Apellidos es obligatorio")
    if not dni.strip() or len(dni.strip()) != 8 or not dni.strip().isdigit():
        errores.append("• DNI debe tener exactamente 8 dígitos numéricos")
    if edad is None: errores.append("• Edad es obligatoria")
    if not sexo:     errores.append("• Sexo es obligatorio")

    if errores:
        st.error("Por favor corrija:\n" + "\n".join(errores))
        st.stop()

    if ya_envio_hoy(dni.strip()):
        st.warning(f"⚠️ El DNI **{dni}** ya tiene un registro hoy. Si es un error, consulte al personal.")
        st.stop()

    registro = {
        "nombres":                 nombres.strip().upper(),
        "apellidos":               apellidos.strip().upper(),
        "dni":                     dni.strip(),
        "edad":                    int(edad),
        "sexo":                    sexo,
        "estado_civil":            estado_civil,
        "grado_instruccion":       grado_instruccion,
        "lugar_nacimiento":        lugar_nacimiento,
        "fecha_nacimiento":        str(fecha_nacimiento) if fecha_nacimiento else "",
        "domicilio":               domicilio.strip().upper(),
        "celular":                 celular.strip(),
        "ocupacion":               ocupacion.strip().upper(),
        "centro_trabajo":          centro_trabajo.strip().upper(),
        "tipo_donacion":           tipo_donacion,
        "receptor_nombres":        receptor_nombres.strip().upper(),
        "receptor_apellidos":      receptor_apellidos.strip().upper(),
        "receptor_dni":            receptor_dni.strip(),
        "respuestas_cuestionario": json.dumps(resp, ensure_ascii=False),
        "sincronizado":            False,
        "campania_id":             int(_campania_id) if _campania_id else None,
    }

    try:
        supabase.table("donantes_cloud").insert(registro).execute()
        st.session_state["enviado"] = True
        st.rerun()
    except Exception as e:
        st.error(f"Error al guardar. Intente de nuevo.\nDetalle: {e}")
