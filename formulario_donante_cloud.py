"""
Formulario del Donante — Banco de Sangre Hospital Amazónico
Desplegado en Streamlit Community Cloud
"""
import streamlit as st
import streamlit.components.v1 as components
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

def tiu(label, key, **kwargs):
    """Fuerza mayúsculas modificando session_state ANTES de renderizar el widget."""
    if key in st.session_state and isinstance(st.session_state[key], str):
        st.session_state[key] = st.session_state[key].upper()
    return st.text_input(label, key=key, **kwargs)

DEPARTAMENTOS = [
    "", "Amazonas", "Áncash", "Apurímac", "Arequipa", "Ayacucho", "Cajamarca",
    "Callao", "Cusco", "Huancavelica", "Huánuco", "Ica", "Junín", "La Libertad",
    "Lambayeque", "Lima", "Loreto", "Madre de Dios", "Moquegua", "Pasco",
    "Piura", "Puno", "San Martín", "Tacna", "Tumbes", "Ucayali"
]

st.markdown("""
<style>
.hospital-header {
    background: linear-gradient(135deg, #b71c1c 0%, #7f0000 100%);
    padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 24px;
}
.hospital-header h2 { color: #fff; margin: 0; font-size: 1.4rem; }
.hospital-header p  { color: #ffcdd2; margin: 6px 0 0; font-size: .9rem; }
.seccion { border-left: 4px solid #b71c1c; padding: 6px 12px;
           background: #fff8f8; border-radius: 0 8px 8px 0;
           margin: 20px 0 10px; font-weight: 700; color: #7f0000; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hospital-header">
  <h2>🩸 Banco de Sangre — Hospital Amazónico</h2>
  <p>Formulario previo de donación · Yarinacocha, Ucayali</p>
</div>
""", unsafe_allow_html=True)

# ── Forzar MAYÚSCULAS en el teclado del celular ──────────────
# components.html SÍ ejecuta JS y puede acceder al DOM padre
components.html("""
<script>
(function(){
  function fijar(){
    try {
      var doc = window.parent.document;
      doc.querySelectorAll('input[type="text"]').forEach(function(el){
        el.setAttribute('autocapitalize','characters');
        el.style.textTransform='uppercase';
      });
    } catch(e){}
  }
  fijar();
  setInterval(fijar, 400);
})();
</script>
""", height=0, scrolling=False)

def ya_envio_hoy(dni):
    hoy = datetime.date.today().isoformat()
    res = supabase.table("donantes_cloud").select("id") \
        .eq("dni", dni) \
        .gte("fecha_registro", hoy + "T00:00:00") \
        .lte("fecha_registro", hoy + "T23:59:59") \
        .execute()
    return len(res.data) > 0

# Si ya envió, mostrar confirmación
if st.session_state.get("enviado"):
    st.success("✅ Su registro fue recibido correctamente.")
    st.info("El personal del banco de sangre lo atenderá en breve. ¡Gracias por su donación!")
    st.balloons()
    st.stop()

# ── DATOS PERSONALES ─────────────────────────────────────────
st.markdown('<div class="seccion">Datos Personales</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    nombres          = tiu("Nombres completos *",  "c_nombres")
    apellidos        = tiu("Apellidos *",           "c_apellidos")
    dni              = st.text_input("DNI (8 dígitos) *", max_chars=8, key="c_dni")
    edad             = st.number_input("Edad *", min_value=18, max_value=65, value=None, step=1)
    sexo             = st.selectbox("Sexo *", ["", "Masculino", "Femenino"])
    estado_civil     = st.selectbox("Estado civil", ["", "Soltero(a)", "Casado(a)", "Conviviente", "Divorciado(a)", "Viudo(a)"])
    lugar_nacimiento = st.selectbox("Lugar de nacimiento", DEPARTAMENTOS)
    fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None,
                                      min_value=datetime.date(1950, 1, 1),
                                      max_value=datetime.date(2007, 12, 31),
                                      format="DD/MM/YYYY")
with c2:
    grado_instruccion    = st.selectbox("Grado de instrucción", ["", "Primaria", "Secundaria", "Superior", "Master", "Doctorado"])
    domicilio            = tiu("Domicilio actual",               "c_domicilio")
    celular              = st.text_input("Celular (9 dígitos)",  max_chars=9, key="c_celular")
    ocupacion_op         = st.selectbox("Ocupación", ["", "Estudiante", "Empleado", "Independiente", "Ama de casa", "Otros"])
    ocupacion_otros      = tiu("Especifique su ocupación",        "c_ocup_otros") if ocupacion_op == "Otros" else ""
    centro_trabajo_op    = st.selectbox("Centro de trabajo", ["", "Independiente", "Sector Público", "Sector Privado", "Otros"])
    centro_trabajo_otros = tiu("Especifique su centro de trabajo","c_ct_otros")   if centro_trabajo_op == "Otros" else ""

ocupacion      = ocupacion_otros      if ocupacion_op      == "Otros" else ocupacion_op
centro_trabajo = centro_trabajo_otros if centro_trabajo_op == "Otros" else centro_trabajo_op

# ── TIPO DE DONACIÓN ─────────────────────────────────────────
st.markdown('<div class="seccion">Tipo de Donación</div>', unsafe_allow_html=True)
tipo_donacion = st.radio("Usted dona como:", ["Voluntario", "Reposición", "Autólogo"], horizontal=True)

receptor_nombres = receptor_apellidos = receptor_dni = ""
if tipo_donacion == "Reposición":
    st.warning("Ingrese los datos del paciente receptor:")
    r1, r2, r3 = st.columns(3)
    with r1: receptor_nombres   = tiu("Nombres del paciente",  "c_rec_nom")
    with r2: receptor_apellidos = tiu("Apellidos del paciente","c_rec_ape")
    with r3: receptor_dni       = st.text_input("DNI del paciente", max_chars=8, key="c_rec_dni")

# ── CUESTIONARIO ─────────────────────────────────────────────
st.markdown('<div class="seccion">Cuestionario de Selección</div>', unsafe_allow_html=True)
st.info("Responda con sinceridad. Sus respuestas son confidenciales y protegen su salud.")

resp = {}

resp["q1"] = st.radio("1. ¿Ha donado sangre anteriormente?", ["No", "Sí"], horizontal=True)
if resp["q1"] == "Sí":
    resp["q1_detalle"] = tiu("¿Hace cuánto tiempo fue su última donación?", "c_q1d")

resp["q2"] = st.radio("2. ¿Donó sangre en los últimos tres meses?", ["No", "Sí"], horizontal=True)

resp["q3"] = st.radio("3. ¿Está tomando o tomó algún medicamento en los últimos días?", ["No", "Sí"], horizontal=True)
if resp["q3"] == "Sí":
    resp["q3_detalle"] = tiu("¿Cuáles medicamentos?", "c_q3d")

if sexo == "Femenino":
    q_fem = st.date_input("4. Fecha de última menstruación:", value=None, format="DD/MM/YYYY")
    resp["q4"] = str(q_fem) if q_fem else "No indicada"
    resp["q7"] = st.radio("7. ¿Está gestando o dando de lactar?", ["No", "Sí"], horizontal=True)
else:
    resp["q4"] = "N/A"
    resp["q7"] = "N/A"

resp["q5"] = st.radio("5. ¿Se encuentra actualmente bien de salud?", ["Sí", "No"], horizontal=True)
resp["q6"] = st.radio("6. ¿Ha tenido fiebre, dolor de cabeza o enfermedad en las últimas dos semanas?", ["No", "Sí"], horizontal=True)

resp["q8"] = st.radio("8. ¿Ha sido operado en los últimos seis meses?", ["No", "Sí"], horizontal=True)
if resp["q8"] == "Sí":
    resp["q8_detalle"] = tiu("¿De qué fue operado?", "c_q8d")

resp["q9"] = st.radio("9. ¿Ha recibido sangre, trasplante de órgano o tejidos?", ["No", "Sí"], horizontal=True)
if resp["q9"] == "Sí":
    resp["q9_detalle"] = tiu("¿Qué recibió y hace cuánto tiempo?", "c_q9d")

resp["q10"] = st.radio("10. ¿En los últimos 12 meses se realizó tatuajes o punción de piel?", ["No", "Sí"], horizontal=True)
if resp["q10"] == "Sí":
    resp["q10_detalle"] = tiu("Especifique (tatuaje, arete, acupuntura, etc.):", "c_q10d")

resp["q11"] = st.radio("11. ¿Recibió alguna vacuna en el último mes?", ["No", "Sí"], horizontal=True)
if resp["q11"] == "Sí":
    resp["q11_detalle"] = tiu("¿Cuál vacuna?", "c_q11d")

resp["q12"] = st.radio("12. ¿Tuvo contacto con persona portadora de alguna enfermedad contagiosa?", ["No", "Sí"], horizontal=True)
if resp["q12"] == "Sí":
    resp["q12_detalle"] = tiu("¿Qué enfermedad tenía la persona?", "c_q12d")

resp["q13"] = st.radio("13. ¿Ha viajado a zonas con paludismo, fiebre amarilla o leishmaniasis?", ["No", "Sí"], horizontal=True)
if resp["q13"] == "Sí":
    resp["q13_detalle"] = tiu("¿A qué zona específica viajó?", "c_q13d")

resp["q14"] = st.radio("14. ¿Padece alguna molestia que requiere control médico continuo?", ["No", "Sí"], horizontal=True)
if resp["q14"] == "Sí":
    resp["q14_detalle"] = tiu("¿Cuál molestia?", "c_q14d")

resp["q15"] = st.radio("15. ¿Consume usted algún tipo de droga?", ["No", "Sí"], horizontal=True)

resp["q16"] = st.radio("16. ¿Ha tenido alguna enfermedad de transmisión sexual?", ["No", "Sí"], horizontal=True)
if resp["q16"] == "Sí":
    resp["q16_detalle"] = tiu("¿Cuál enfermedad?", "c_q16d")

resp["q17"] = st.radio("17. ¿Ha tenido múltiples parejas sexuales en los últimos 12 meses?", ["No", "Sí"], horizontal=True)
resp["q18"] = st.radio("18. ¿Se ha realizado prueba de VIH/SIDA u otras enfermedades de transmisión sexual?", ["No", "Sí"], horizontal=True)
resp["q19"] = st.radio("19. ¿Ha estado en prisión en el último año?", ["No", "Sí"], horizontal=True)
resp["q20"] = st.radio("20. ¿Ha consumido bebidas alcohólicas en las últimas 24 horas?", ["No", "Sí"], horizontal=True)

# ── ENVÍO ────────────────────────────────────────────────────
st.markdown("---")
if st.button("✅ Enviar Formulario", type="primary", use_container_width=True):
    # Validaciones
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
        st.warning(f"⚠️ El DNI **{dni}** ya tiene un registro hoy. "
                   "Si es un error, consulte al personal del banco de sangre.")
        st.stop()

    # Normalizar todos los campos de texto a MAYÚSCULAS antes de guardar
    for k in list(resp.keys()):
        if k.endswith("_detalle") and isinstance(resp[k], str):
            resp[k] = resp[k].strip().upper()

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
    }

    try:
        supabase.table("donantes_cloud").insert(registro).execute()
        st.session_state["enviado"] = True
        st.rerun()
    except Exception as e:
        st.error(f"Error al guardar. Intente de nuevo.\nDetalle: {e}")
