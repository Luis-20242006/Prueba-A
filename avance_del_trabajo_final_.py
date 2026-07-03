# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Trivia Prehispánica", page_icon="🦙", layout="centered")

# COLOCAR EL TÍTULO DEL JUEGO
st.title("🦙🌄 Trivia sobre culturas prehispánicas")
st.write("¡Bienvenidos al juego de trivia! Desarrollado por Luis de la Cruz y Deyvid Blas.")
st.markdown("---")

# URL DIRECTA DEL EXCEL EN GITHUB (Se lee automáticamente)
# Al estar en la misma carpeta raíz en GitHub, Streamlit lo encuentra buscando el nombre directamente.
NOMBRE_ARCHIVO = "BASE DE DATOS - AVANCE.xlsx"

try:
    # LEER LA BASE DE DATOS AUTOMÁTICAMENTE DESDE GITHUB
    df = pd.read_excel(NOMBRE_ARCHIVO)

    # ESTABLECER LAS COLUMNAS REQUERIDAS
    columnas_requeridas = ["nivel", "periodo", "cultura", "pregunta", "A", "B", "C", "D", "respuesta"]
    
    falta_columna = False
    for columna in columnas_requeridas:
        if columna not in df.columns:
            st.error(f"❌ Falta la columna '{columna}' en el Excel de GitHub.")
            falta_columna = True
    
    if falta_columna:
        st.stop()

    # ORGANIZAR LA SELECCIÓN DE NIVELES
    orden_niveles = ["Fácil", "Intermedio", "Difícil"]
    niveles = [nivel for nivel in orden_niveles if nivel in df["nivel"].unique()]

    if not niveles:
        st.error("❌ No se encontraron niveles válidos ('Fácil', 'Intermedio', 'Difícil') en el archivo.")
        st.stop()

    # SELECCIÓN DE NIVEL EN LA INTERFAZ
    nivel_elegido = st.selectbox("📚 Elige un nivel para comenzar:", niveles)
    
    # FILTRAR LAS PREGUNTAS CORRESPONDIENTES AL NIVEL ELEGIDO
    preguntas_nivel = df[df["nivel"] == nivel_elegido]

    if len(preguntas_nivel) == 0:
        st.error("❌ No existen preguntas para ese nivel.")
        st.stop()

    st.success(f"✅ ¡Base de datos cargada con éxito desde GitHub! Nivel actual: {nivel_elegido}.")
    st.markdown("---")

    # INICIALIZAR VARIABLES DE SESIÓN (Para que Streamlit recuerde el estado del juego)
    if "juego_iniciado" not in st.session_state or st.session_state.get("nivel_previo") != nivel_elegido:
        cantidad_preguntas = min(10, len(preguntas_nivel))
        st.session_state.preguntas = preguntas_nivel.sample(n=cantidad_preguntas, random_state=None).reset_index(drop=True)
        st.session_state.cantidad_preguntas = cantidad_preguntas
        st.session_state.respuestas_usuario = {}
        st.session_state.juego_iniciado = True
        st.session_state.nivel_previo = nivel_elegido
        st.session_state.juego_terminado = False

    # MOSTRAR PREGUNTAS
    st.subheader("📝 Responde las siguientes preguntas:")
    
    for index, fila in st.session_state.preguntas.iterrows():
        numero = index + 1
        st.markdown(f"### 📖 Pregunta {numero} de {st.session_state.cantidad_preguntas}")
        st.caption(f"🕰️ Período: {fila['periodo']} | 🗿 Cultura: {fila['cultura']}")
        st.write(f"**{fila['pregunta']}**")
        
        # Opciones de respuesta en radio buttons
        opciones = {
            f"A) {fila['A']}": "A",
            f"B) {fila['B']}": "B",
            f"C) {fila['C']}": "C",
            f"D) {fila['D']}": "D"
        }
        
        # Guardar la respuesta seleccionada por el usuario
        seleccion = st.radio(
            "Selecciona tu respuesta:", 
            options=list(opciones.keys()), 
            key=f"p_{numero}",
            index=None, # Inicia sin ninguna marcada
            label_visibility="collapsed"
        )
        
        if seleccion:
            st.session_state.respuestas_usuario[index] = opciones[seleccion]
        st.markdown("---")

    # BOTÓN PARA CALCULAR RESULTADOS
    if len(st.session_state.respuestas_usuario) < st.session_state.cantidad_preguntas:
        st.warning("⚠️ Responde todas las preguntas para poder finalizar el juego.")
    else:
        if st.button("🏁 FINALIZAR JUEGO Y VER RESULTADOS", type="primary"):
            st.session_state.juego_terminado = True

    # MOSTRAR RESULTADOS
    if st.session_state.get("juego_terminado"):
        puntaje = 0
        st.subheader("📊 Resultados del Juego")
        
        for index, fila in st.session_state.preguntas.iterrows():
            numero = index + 1
            resp_usuario = st.session_state.respuestas_usuario.get(index)
            correcta = str(fila["respuesta"]).strip().upper()
            
            if resp_usuario == correcta:
                puntaje += 1
                st.success(f"Pregunta {numero}: ¡Correcto! (Tu respuesta: {resp_usuario})")
            else:
                st.error(f"Pregunta {numero}: Incorrecto. Tu respuesta: {resp_usuario} | Respuesta correcta: {correcta}")
        
        porcentaje = (puntaje / st.session_state.cantidad_preguntas) * 100
        st.markdown(f"## ➡️ Puntaje Final: {puntaje}/{st.session_state.cantidad_preguntas}")
        
        if porcentaje == 100:
            st.balloons()
            st.title("🏆 ¡Perfecto!")
        elif porcentaje >= 80:
            st.success("🌟 Excelente trabajo")
        elif porcentaje >= 60:
            st.info("👏 Muy bien")
        elif porcentaje >= 40:
            st.warning("👀 Puedes mejorar")
        else:
            st.error("📖 Sigue estudiando las culturas prehispánicas")
            
        st.write("👌 ¡Gracias por jugar!")

except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo '{NOMBRE_ARCHIVO}' en el repositorio de GitHub. Asegúrate de subirlo con el mismo nombre y extensión.")
except Exception as e:
    st.error(f"Hubo un error al procesar el archivo: {e}")
