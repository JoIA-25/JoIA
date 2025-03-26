import time
import streamlit as st
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.objects.base import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.wrapper import StreamWrapper

# Configurar página y CSS
st.set_page_config(page_title='JoIA | Belén Reyes', page_icon='💎')

def load_css():
    css = """
    <style>
        /* Cargar la fuente BilkoOpti */
        @font-face {
            font-family: 'BilkoOpti';
            src: url('https://joia-25.github.io/JoIA/partials/BilkoOpti-Regular.otf') format('opentype');
        }

        /* Cargar la fuente Punkto-Regular */
        @font-face {
            font-family: 'Punkto-Regular';
            src: url('https://joia-25.github.io/JoIA/partials/Punkto-Regular.otf') format('opentype');
        }

        /* ===== FONDO PRINCIPAL ===== */
        html, body, .stApp {
            background-color: #2E3F6A !important;
        }

        /* ===== CONTENEDOR DEL LOGO ===== */
        .svg-container {
            margin-top: 0 !important;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            animation: moveLogo 3s forwards;
            animation-delay: 3s;
        }

        /* Animación de desplazamiento */
        @keyframes moveLogo {
            0% { transform: translateX(0); }
            100% { transform: translateX(calc(-50vw + 130px)); }
        }

        .svg-container img {
            position: relative;
            display: flex;
            width: 100%;
            max-width: 150px !important;
            height: 100%;
            max-width: 200px; /* Duplicación de max-width */
        }

        /* ===== TEXTO PRINCIPAL (JoIA | Belén Reyes) ===== */
        .custom-text {
            position: absolute;
            bottom: 20%; /* Ajustar desde el inferior del contenedor de la imagen */
            font-family: 'BilkoOpti', sans-serif !important;
            font-size: clamp(1rem, 1vw, 2.5rem) !important;
            color: white !important;
            text-align: center !important;
            line-height: 1.1 !important;
            z-index: 10;
        }

        /* ===== TEXTO SECUNDARIO (JEWELLERY) ===== */
        .custom-text-small {
            position: absolute;
            bottom: 5%; /* Ajustar desde el inferior del contenedor de la imagen */
            font-family: 'Punkto-Regular', sans-serif !important;
            font-size: clamp(0.8rem, 0.8vw, 1.8rem) !important;
            color: white !important;
            text-align: center !important;
            letter-spacing: 2px;
            z-index: 10;
        }

    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

image_url = "https://joia-25.github.io/JoIA/partials/belen_animated_output.svg"

# Función para manejar la carga de la imagen y esperar a su carga
def load_image():
    time.sleep(1.5)
    return True  # Retornar True una vez la imagen esté cargada (en un caso real, usar `onload`)

# Función para mostrar el logo y el texto
def show_logo_and_text():
    # Mostrar el logo y el texto principal cuando la imagen esté cargada
    st.markdown(
        f"""
        <div class="svg-container">
            <img src="{image_url}" alt="Logo JoIA" id="logo">
            <p class="custom-text">JoIA | Belén Reyes</p>
            <p class="custom-text-small">J E W E L L E R Y</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------
# Funciones Speckle
# --------------------------

# Configuración constante
TOKEN = "a1af46876375c70f446bb77e6d0092f11447f4dd5e"
MODEL_URL = "https://app.speckle.systems/projects/4fe6b2ee63/models/b9eba9b3d4"
HOST = "speckle.xyz"
MODEL_URL_2 = "https://app.speckle.systems/projects/4fe6b2ee63/models/6151567ec8"
wrapper2 = StreamWrapper(MODEL_URL_2)

def initialize_speckle_client() -> SpeckleClient:
    """Inicializa y autentica el cliente de Speckle"""
    account = get_account_from_token(TOKEN, HOST)
    client = SpeckleClient(host=HOST)
    client.authenticate_with_account(account)
    return client

def send_text_to_speckle(text: str, client: SpeckleClient, wrapper: StreamWrapper) -> tuple[str, str]:
    """Envía texto a Speckle y retorna object_id y commit_id"""
    transport = ServerTransport(client=client, stream_id=wrapper.stream_id)
    
    data = Base()
    data["seleccion"] = text
    
    object_id = operations.send(
        base=data,
        transports=[transport],
        use_default_cache=False
    )
    
    commit_id = client.commit.create(
        stream_id=wrapper.stream_id,
        object_id=object_id,
        branch_name=wrapper.branch_name,
        message=f"Streamlit -> Selección enviada: {text}"
    )
    return object_id, commit_id

def generate_iframe(model_url: str) -> str:
    """Genera el código HTML del iframe con los parámetros de Speckle Viewer."""
    return f"""
    <div style="position: relative; width: 100%; height: 500px;">
        <iframe 
            id="speckleViewer"
            title="Speckle" 
            src="{model_url}#embed=%7B%22isEnabled%22%3Atrue%2C%22isTransparent%22%3Atrue%2C%22hideControls%22%3Atrue%2C%22hideSelectionInfo%22%3Atrue%2C%22noScroll%22%3Atrue%7D" 
            style="width: 100%; height: 100%; border: none;">
        </iframe>
    </div>
    """

# --------------------------
# Lógica principal
# --------------------------
def main():
    if load_image():  # Asegurarse de que la imagen se ha cargado
        show_logo_and_text()  # Mostrar logo y texto solo después de la carga de la imagen

    wrapper = StreamWrapper(MODEL_URL)
    client = initialize_speckle_client()
    
    # Estado inicial con selección por defecto
    if "seleccion" not in st.session_state:
        st.session_state.seleccion = "Anillo"
   
    # Mostrar selección de joyería
    st.write("Selecciona un tipo de joyería:")
    col1, col2, col3 = st.columns(3)

    if col1.button("Anillo"):
        st.session_state.seleccion = "Anillo"
    if col2.button("Dije"):
        st.session_state.seleccion = "Dije"
    if col3.button("Collar"):
        st.session_state.seleccion = "Collar"

    # Si hubo un cambio de selección, enviar datos y esperar
    if "seleccion_actualizada" not in st.session_state or st.session_state.seleccion_actualizada != st.session_state.seleccion:
        st.session_state.seleccion_actualizada = st.session_state.seleccion
        with st.spinner(f"Enviando '{st.session_state.seleccion}' al modelo... Esperando actualización..."):
            try:
                send_text_to_speckle(st.session_state.seleccion, client, wrapper)
                time.sleep(10)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    # Mostrar visualizador con la selección actual
    st.components.v1.html(generate_iframe(MODEL_URL_2), height=500)
if __name__ == "__main__":
    main()
