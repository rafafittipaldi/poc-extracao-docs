import streamlit as st
import tempfile
from openai_service import OpenAIAnalyzer
from aws_textract_service import AWSIdentityDocumentAnalyzer

# Set page configuration at the very beginning
st.set_page_config(page_title="POC - Extrator de textos de documentos (Rafael Fittipaldi)", layout="centered", initial_sidebar_state="collapsed")

class MainAuth:
    def __init__(self, openai_analyzer, aws_analyzer):
        self.openai_analyzer = openai_analyzer
        self.aws_analyzer = aws_analyzer

    @staticmethod
    def save_uploaded_file(uploaded_file):
        # Cria um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
        return temp_file.name

    def run(self):
        st.title("Extrator de textos de documentos (Rafael Fittipaldi)")

        # File uploader allows user to add their own image
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

        # Define the analyze_button variable before using it
        show_details = st.checkbox("Adicione detalhes sobre a imagem", value=False)
        additional_details = st.text_area("Adicione detalhes ou contexto sobre a imagem aqui:", disabled=not show_details) if show_details else None
        analyze_button = st.button("Analise os documentos", type="secondary")

        if uploaded_file:
            with st.expander("Image", expanded=True):
                st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

            if analyze_button:
                with st.spinner("Analisando o documento..."):
                    # Análise com GPT-4 Vision
                    response_json, raw_response = None, None
                    try:
                        base64_image = self.openai_analyzer.encode_image(uploaded_file)
                        prompt_text = self.openai_analyzer.create_prompt_text(additional_details)
                        messages = self.openai_analyzer.create_payload(prompt_text, base64_image)
                        response_json, raw_response = self.openai_analyzer.analyze_document(messages)
                    except Exception as e:
                        st.error(f"Falha ao analisar o documento com GPT-4 Vision: {e}")

                    # Análise com AWS Textract
                    response_aws_text_forms, response_aws_text_lines = None, None
                    try:
                        image_path = self.save_uploaded_file(uploaded_file)
                        response_aws_text_lines  = self.aws_analyzer.detect_text(image_path)
                        response_aws_text_forms  = self.aws_analyzer.analyze_document(image_path)
                    except Exception as e:
                        st.error(f"Falha ao analisar o documento com AWS Textract: {e}")

                    # Exibir os resultados, se disponíveis
                    if response_json:
                        st.caption("Resultado JSON (AI)")
                        st.json(response_json)
                        st.caption("Resultado MARKDOWN (AI)")
                        st.markdown(raw_response)

                    if response_aws_text_lines:
                        st.caption("Resultado Textract (AWS) Forms")
                        st.json(response_aws_text_forms)

                    if response_aws_text_lines:
                        st.caption("Resultado Textract (AWS) com Lines (Não possui estrutura Key/Value)")
                        st.code(response_aws_text_lines)

        if not uploaded_file and analyze_button:
            st.warning("Please upload an image.")

if __name__ == "__main__":
    # Retrieve the OpenAI API Key from secrets
    api_key = st.text_input("OpenAI API Key", type="password", value="???????????")
    openai_analyzer = OpenAIAnalyzer(api_key)

    # AWS Textract credentials
    aws_access_key_id = st.text_input("AWS Access Key ID", value="???????")
    aws_secret_access_key = st.text_input("AWS Secret Access Key", type="password", value="?????????")
    aws_region = st.text_input("AWS Region", value="us-east-1")
    aws_analyzer = AWSIdentityDocumentAnalyzer(aws_access_key_id, aws_secret_access_key, aws_region)

    # Instancia e executa a aplicação principal
    app = MainAuth(openai_analyzer, aws_analyzer)
    app.run()