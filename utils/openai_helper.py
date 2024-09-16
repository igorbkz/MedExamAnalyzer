import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_medical_exam(file_content: str) -> str:
    prompt = f"""Você é um médico experiente analisando os resultados de um exame médico. Forneça uma análise detalhada e profissional em português, como um médico faria, incluindo:

1. Um resumo geral do estado de saúde do paciente
2. Interpretação dos resultados dos exames, destacando valores normais e anormais
3. Possíveis implicações para a saúde do paciente
4. Recomendações para acompanhamento ou exames adicionais, se necessário
5. Sugestões de mudanças no estilo de vida ou tratamento, se aplicável

Analise cuidadosamente os seguintes resultados de exame médico e forneça sua análise profissional:

{file_content}"""
    
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000  # Increased token limit for more detailed analysis
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response.")
        return content
    except Exception as e:
        raise Exception(f"Error in OpenAI API request: {str(e)}")
