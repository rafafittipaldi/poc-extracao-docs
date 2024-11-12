import base64
import json
from openai import OpenAI
from langchain_community.callbacks.manager import get_openai_callback

class OpenAIAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = self.initialize_openai_client(api_key)

    @staticmethod
    def initialize_openai_client(api_key):
        return OpenAI(api_key=api_key)

    @staticmethod
    def encode_image(image_file):
        return base64.b64encode(image_file.getvalue()).decode("utf-8")

    '''@staticmethod
    def create_prompt_text(additional_details=None):
        base_prompt = """
        Você é um agente que trabalha para uma instituição financeira
        Você é especialista em perícia criminal e sua função é analisar documentos falsos e analisar o documento a seguir e prover uma resposta
        A sua resposta deve ser uma única palavra sendo o tipo do documento dentre as seguintes opções: CPF, RG ou CNH
        Você somente aceitará arquivos nas extensões jpg, bmp, pdf, png, gif e jpeg
        Caso sua análise não seja algum dos documentos brasileiros que citei como instrução (CPF, RG ou CNH) você deverá responder que é um documento não aceito para análise
        Caso perceba que o documento não está legível ou distorcido para coletar os dados, você deverá responder que é um documento não aceito para análise
        Se você entendeu as instruções até agora, não é necessário responder mais nada e somente a resposta da análise da imagem no formato json com todas as informações encontradas na imagem, como números, textos e datas
        Na última vez que conversamos, gostei muito do modelo de resposta abaixo que você me forneceu e você vai utilizar ele como template
        {
            "documentos": [
                {
                    "tipo": "RG",
                    "numero_registro": "0123456789",
                    "nome": "DANIEL COELHO DA COSTA",
                    "nome_pai": "EDIVALDO DA COSTA",
                    "nome_mae": "ROSA COELHO DA COSTA",
                    "naturalidade": "SÃO PAULO - SP",
                    "data_nascimento": "19/DEZ/1980",
                    "data_expedicao": "21/DEZ/2012",
                    "cpf": "342.002.171-42",
                    "estado": "ESTADO DO RIO DE JANEIRO",
                },
                {
                    "tipo": "CPF",
                    "numero": "000.000.000-00",
                    "nome": "NOME DA PESSOA",
                    "data_nascimento": "01/01/1990",
                    "data_inscricao": "01/2000",
                }
            ]
        }
        Poderia adicionar no seu json de resposta parâmetros que correspondem as coordenadas limites de cada documento dentro da imagem
        Como um bom especialista e perito em análise em documentos, adicione no seu json com um breve texto a veracidade do documento, incluindo análise de marcas d'agua, bordas, fontes, selos e hologramas compatíveis com governo de cada estado de emissão
        Analise com profundidade a foto do documento, incluindo as cores do espelho, sobreposição de fotos, assinaturas e impressão digital sem sinais de modificação, se as fontes utilizadas são uniformes e se o alinhamento dos textos estão nos padrões
        A foto deve estar bem colada e integrada ao documento, sem sinais de alteração ou substituição
        Compare a formatação, as cores e os elementos gráficos com um RG que você saiba que é legítimo
        Verifique se a data de emissão e os dados pessoais (como data de nascimento) fazem sentido
        Verifique se a foto no documento possui filtros não permitidos
        Após sua análise de veracidade citado acima, inclua em seu json um percentual de 0% a 100% de veracidade, nas seguintes tags [{veracidade:[{observação,veracidade}]}]
        """
        if additional_details:
            base_prompt += f"\n\nContexto adicional para a análise do documento:\n{additional_details}"
        return base_prompt'''
    
    @staticmethod
    def create_prompt_text(additional_details=None):
            base_prompt = """
            Você é um especialista em perícia criminal trabalhando para uma instituição financeira. Sua tarefa é analisar documentos de identificação brasileiros e fornecer uma resposta estruturada em JSON.

            ### Instruções:
            1. **Tipos de Documentos Aceitos**: CPF, RG, CNH.
            2. **Formatos de Arquivo Aceitos**: jpg, bmp, pdf, png, gif, jpeg.
            3. **Respostas Possíveis**:
            - Se o documento for um CPF, RG ou CNH, forneça as informações extraídas no formato JSON.
            - Se o documento não for um dos tipos aceitos ou estiver ilegível, responda com: `"documento não aceito para análise"`.
            
            ### Exemplo de Resposta JSON:
            ```json
            {
                "documentos": [
                    {
                        "tipo": "RG",
                        "numero_registro": "0123456789",
                        "nome": "DANIEL COELHO DA COSTA",
                        "nome_pai": "EDIVALDO DA COSTA",
                        "nome_mae": "ROSA COELHO DA COSTA",
                        "naturalidade": "SÃO PAULO - SP",
                        "data_nascimento": "19/DEZ/1980",
                        "data_expedicao": "21/DEZ/2012",
                        "cpf": "342.002.171-42",
                        "estado": "ESTADO DO RIO DE JANEIRO"
                    },
                    {
                        "tipo": "CPF",
                        "numero": "000.000.000-00",
                        "nome": "NOME DA PESSOA",
                        "data_nascimento": "01/01/1990",
                        "data_inscricao": "01/2000"
                    }
                ]
            }
            ```

            ### Análise de Veracidade:
            - Verifique a presença de marcas d'água, bordas, fontes, selos e hologramas compatíveis com o governo do estado de emissão.
            - Analise a foto do documento, verificando sobreposição, assinaturas e impressão digital.
            - Compare a formatação, cores e elementos gráficos com um documento legítimo.
            - Verifique se a data de emissão e os dados pessoais fazem sentido.
            - Se a foto tiver filtros ou modificações, inclua essa observação.

            ### Veracidade no JSON:
            - Adicione um campo de veracidade com uma porcentagem de 0% a 100%, indicando a autenticidade do documento.
            - Exemplo:
            ```json
            { "veracidade": [{veracidade:[{observação,veracidade}]}] }
            ```

            Se você entendeu as instruções, forneça apenas a resposta no formato JSON.

            """
            
            if additional_details:
                base_prompt += f"\n\n### Contexto Adicional:\n{additional_details}"
            
            return base_prompt

    @staticmethod
    def create_payload(prompt_text, base64_image):
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
                ],
            }
        ]

    def analyze_document(self, messages):
        try:
            with get_openai_callback() as cb:
                response = self.client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0,  # Definir temperatura para 0 para garantir consistência
                    top_p=1,        # Considerar todas as palavras possíveis
                    stream=False
                )
                response_json = response.choices[0].message.content.replace("```json", "").replace("```", "")
                return json.loads(response_json), response.choices[0].message.content
        except Exception as e:
            return None, f"An error occurred: {e}"