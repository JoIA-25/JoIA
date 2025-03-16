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
        /* ===== FONDO PRINCIPAL ===== */
        html, body, .stApp {
            background-color: #2E3F6A !important;
        }
        
        /* ===== LOGO ===== */
        [data-testid="stImage"] {
            position: fixed !important;
            top: 50px !important;
            left: 0px !important;
            width: 150px !important;
            height: auto !important;
            z-index: 1000 !important;
        }

        /* Asegurar que el logo no sea afectado por otros contenedores */
        [data-testid="stImageContainer"] {
            width: 150px !important;
            height: auto !important;
        }

        /* Ocultar bordes o sombras que Streamlit añade */
        [data-testid="stImage"] img {
            border: none !important;
            box-shadow: none !important;
        }
        /* ===== BOTONES CENTRADOS ===== */
        /* Contenedor principal de columnas */
        [data-testid="stHorizontalBlock"] {
            gap: 0.5rem !important;  /* Ajusta espacio entre columnas */
        }
        
        /* Cada columna individual */
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 0 5px !important;  /* Padding horizontal reducido */
        }
        
        /* Contenedor del botón (div.stButton) */
        [data-testid="stHorizontalBlock"] [data-testid="stButton"] {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
        }
        
        /* El botón en sí */
        [data-testid="stBaseButton-secondary"] {
            width: auto !important;
            min-width: 120px !important;
            margin: 0 auto !important;
            transition: all 0.3s ease !important;  /* Efecto hover suave */
        }
        
        /* Efecto hover para mejor UX */
        [data-testid="stBaseButton-secondary"]:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
                
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Cargar estilos
load_css()
# Insertar logo
st.image("logo.jpeg", use_container_width=False)
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

def send_number_to_speckle(
    numero: int, 
    client: SpeckleClient, 
    wrapper: StreamWrapper
) -> tuple[str, str]:
    """Envía número a Speckle y retorna object_id y commit_id"""
    transport = ServerTransport(client=client, stream_id=wrapper.stream_id)
    
    data = Base()
    data["numero"] = numero
    
    object_id = operations.send(
        base=data,
        transports=[transport],
        use_default_cache=False
    )
    
    commit_id = client.commit.create(
        stream_id=wrapper.stream_id,
        object_id=object_id,
        branch_name=wrapper.branch_name,
        message=f"Streamlit -> Número enviado: {numero}"
    )
    return object_id, commit_id

def send_text_to_speckle(
    text: str, 
    client: SpeckleClient, 
    wrapper: StreamWrapper
) -> tuple[str, str]:
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
    return """
    <div style="position: relative; width: 100%; height: 500px;">
        <iframe 
            id="speckleViewer"
            title="Speckle" 
            src="{model_url}#embed=%7B%22isEnabled%22%3Atrue%2C%22isTransparent%22%3Atrue%2C%22hideControls%22%3Atrue%2C%22hideSelectionInfo%22%3Atrue%2C%22noScroll%22%3Atrue%7D" 
            style="width: 100%; height: 100%; border: none;">
        </iframe>
    </div>

    <script>
    document.getElementById("speckleViewer").onload = function() {{
        try {{
            const iframeDoc = this.contentDocument || this.contentWindow.document;
            const canvas = iframeDoc.querySelector("canvas");
            if (canvas) {{
                canvas.style.backgroundColor = "#2E3F6A";
                canvas.parentElement.style.backgroundColor = "#2E3F6A";
            }}
        }} catch (error) {{
            console.log("Error de seguridad CORS (esperado):", error);
        }}
    }};
    </script>
    """.format(model_url=model_url)


# --------------------------
# Lógica principal
# --------------------------
def main():
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
                time.sleep(10)  # Esperar 10 segundos antes de actualizar
                st.rerun()  # Recargar la página para actualizar el visualizador
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Mostrar visualizador con la selección actual
    st.components.v1.html(generate_iframe(MODEL_URL_2), height=500)
if __name__ == "__main__":
    main()