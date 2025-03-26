import time
import streamlit as st
from streamlit.components.v1 import html
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.objects.base import Base
from specklepy.transports.server import ServerTransport
from specklepy.api.wrapper import StreamWrapper

# Configurar página
st.set_page_config(page_title='JoIA | Belén Reyes', page_icon='💎')

# URL de la imagen SVG
image_url = "https://joia-25.github.io/JoIA/partials/belen_animated_output.svg"

# HTML con retraso en la carga de imagen y texto
html(f'''
    <div class="svg-container" style="text-align: center;">
        <img src="{image_url}" alt="Logo JoIA" id="logo" style="display: none; width: 150px;">
        <p class="custom-text" id="title-text" style="display: none; font-family: sans-serif; color: white; font-size: 24px; margin: 10px 0 0;">JoIA | Belén Reyes</p>
        <p class="custom-text-small" id="subtitle-text" style="display: none; font-family: sans-serif; color: white; font-size: 16px; letter-spacing: 2px; margin: 5px 0 0;">J E W E L L E R Y</p>
    </div>

    <script>
        setTimeout(function() {{
            document.getElementById("logo").style.display = "block";
        }}, 2000);

        setTimeout(function() {{
            document.getElementById("title-text").style.display = "block";
            document.getElementById("subtitle-text").style.display = "block";
        }}, 3000);
    </script>
''', height=300)

# --------------------------
# Funciones Speckle
# --------------------------

# Configuración Speckle
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
    wrapper = StreamWrapper(MODEL_URL)
    client = initialize_speckle_client()
    
    # Estado inicial con selección por defecto
    if "seleccion" not in st.session_state:
        st.session_state.seleccion = "Anillo"
    
    time.sleep(4.5)

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
