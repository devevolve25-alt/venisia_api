import google.generativeai as genai

# Garanta que sua chave esteja aqui
GOOGLE_API_KEY = "AIzaSyCN4nls8tIiWDE8e6DL_xN-k4Ct_B6bwhM"

genai.configure(api_key=GOOGLE_API_KEY)

# Mudamos de 'gemini-1.5-flash' para 'gemini-pro' ou apenas 'gemini-1.5-flash' sem o v1beta
# Vamos tentar o 'gemini-1.5-flash-latest' ou 'gemini-1.5-flash'
model = genai.GenerativeModel('gemini-1.5-flash') 

def perguntar_ao_panteao(pergunta: str, dados_usuarios: list):
    contexto = (
        f"Você é o Oráculo da VENDISIA, uma IA mística e sábia. "
        f"Os membros do Panteão são: {', '.join(dados_usuarios)}. "
        "Responda de forma mística, porém clara."
    )
    
    try:
        # Tente usar o método de geração
        response = model.generate_content(f"{contexto}\nPergunta: {pergunta}")
        return response.text
    except Exception as e:
        # Se falhar de novo, vamos tentar o nome alternativo do modelo
        try:
            model_alt = genai.GenerativeModel('gemini-pro')
            response = model_alt.generate_content(f"{contexto}\nPergunta: {pergunta}")
            return response.text
        except:
            return f"O Oráculo ainda está em transe. Erro técnico: {str(e)}"
