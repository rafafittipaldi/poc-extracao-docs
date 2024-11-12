import boto3
import botocore.exceptions
import os
from PIL import Image, UnidentifiedImageError
from trp import Document

class AWSIdentityDocumentAnalyzer:
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region):
        try:
            # Inicializa o cliente Textract da AWS
            self.textract_client = boto3.client(
                'textract',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )
        except botocore.exceptions.BotoCoreError as e:
            # Captura qualquer erro relacionado ao boto3
            self.textract_client = None
            print(f"Erro ao conectar com o Textract: {e}")

    def analyze_document(self, image_path):
        """ Pré-processa a imagem para escala de cinza e envia para o Textract. """
        try:
            # Pré-processa a imagem para escala de cinza
            processed_image_path = self.preprocess_image_to_grayscale(image_path)
            
            # Abre a imagem e a envia para o Textract
            with open(processed_image_path, 'rb') as document:
                response = self.textract_client.analyze_document(
                    Document={'Bytes': document.read()},
                    FeatureTypes=['FORMS']  # Usar FORMS para maior precisão
                )
            
            # Processa a resposta do Textract
            return self.process_textract_response(response)
        except Exception as e:
            print(f"Erro ao analisar o documento: {e}")
            return None

    @staticmethod
    def preprocess_image_to_grayscale(image_path):
        """ Pré-processa a imagem para convertê-la em escala de cinza. """
        try:
            # Verifica se a extensão do arquivo é suportada
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
            file_extension = os.path.splitext(image_path)[1].lower()
            if file_extension not in valid_extensions:
                raise ValueError(f"Extensão de arquivo desconhecida: {file_extension}")

            # Tenta abrir a imagem
            image = Image.open(image_path)
            
            # Converte a imagem para escala de cinza
            grayscale_image = image.convert('L')  # 'L' mode is for grayscale
            
            # Salva a imagem pré-processada
            processed_image_path = f"grayscale_{image_path}"
            grayscale_image.save(processed_image_path)
            
            return processed_image_path
        except UnidentifiedImageError:
            print(f"Erro: Não foi possível identificar a imagem no caminho: {image_path}")
            return image_path  # Retorna a imagem original se houver erro
        except Exception as e:
            print(f"Erro ao pré-processar a imagem: {e}")
            return image_path  # Retorna a imagem original se houver erro

    @staticmethod
    def process_textract_response(response):
        """ Processa a resposta do Textract e retorna um vetor de dicionários key-value. """
        extracted_data = []
        
        # Usa a biblioteca trp para processar a resposta
        doc = Document(response)
        
        for page in doc.pages:
            for field in page.form.fields:
                key = field.key.text if field.key else None
                value = field.value.text if field.value else None
                if key and value:
                    extracted_data.append({'key': key, 'value': value})
        
        return extracted_data
    
    def detect_text(self, image_path):
        """ Usa o método detect_document_text para realizar OCR em documentos não estruturados. """
        try:
            with open(image_path, 'rb') as document:
                response = self.textract_client.detect_document_text(
                    Document={'Bytes': document.read()}
                )
            return self.process_detect_text_response(response)
        except botocore.exceptions.BotoCoreError as e:
            print(f"Erro ao detectar texto no documento: {e}")
            return None

    @staticmethod
    def process_detect_text_response(response):
        """ Processa a resposta do Textract para o método detect_document_text. """
        extracted_text = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                extracted_text.append(block['Text'])
        return "\n".join(extracted_text)