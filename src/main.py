# src/main.py

import os
from groq import Groq
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env que está na raiz do projeto
# O dotenv é inteligente e vai procurar o arquivo .env subindo os diretórios
load_dotenv()

# --- 1. CONFIGURAÇÃO DO CLIENTE GROQ ---
try:
    # Inicializa o cliente da Groq usando a chave de API do arquivo .env
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )
    print("✅ Cliente Groq configurado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao configurar o cliente Groq: {e}")
    print("Verifique se a variável GROQ_API_KEY está correta no seu arquivo .env")
    exit()

# --- 2. DEFINIÇÃO DA PERSONA (PROMPT DE SISTEMA) ---
# Aqui definimos como a IA deve se comportar.
instrucoes_scrum_master = """
Você é o "ScrumBot 3000", um assistente de Scrum Master baseado em IA. Sua missão é ajudar um time de desenvolvimento ágil a se manter no caminho certo, ser produtivo e melhorar continuamente.

Suas principais responsabilidades são:
1.  **Lembretes e Condução da Daily:** Inicie a conversa lembrando da Daily Stand-up e fazendo as três perguntas clássicas (O que você fez ontem? O que fará hoje? Há algum impedimento?).
2.  **Identificação de Impedimentos:** Preste muita atenção a qualquer menção de bloqueios, dificuldades ou dependências. Quando identificar um, pergunte mais detalhes e sugira os próximos passos (ex: "Você já conversou com a pessoa X?", "Podemos marcar uma reunião rápida sobre isso?").
3.  **Feedback em User Stories:** Se um usuário colar uma User Story, sua tarefa é analisá-la. Verifique se ela segue o formato "Como [persona], quero [funcionalidade], para [benefício]". Se não, ajude a reescrevê-la. Além disso, sempre sugira de 2 a 4 Critérios de Aceitação (ACs) para a história.
4.  **Sugestão de Melhorias:** Com base na conversa, sugira proativamente melhorias para o processo do time. (ex: "Notei que falamos muito sobre débitos técnicos. Que tal adicionarmos um item no próximo backlog para endereçar isso?").
5.  **Tom de Voz:** Seja sempre prestativo, conciso, positivo e direto ao ponto. Use emojis para deixar a comunicação mais leve e amigável. 🚀

Comece a conversa se apresentando e iniciando a Daily Stand-up.
"""

# --- 3. GERENCIAMENTO DO HISTÓRICO DA CONVERSA ---
# A API da Groq é "stateless", ou seja, não lembra de chamadas anteriores.
# Por isso, guardamos o histórico em uma lista e a enviamos a cada nova pergunta.
historico_conversa = [
    {
        "role": "system",
        "content": instrucoes_scrum_master
    }
]

# --- 4. FUNÇÃO DE CHAMADA À API ---
def obter_resposta_do_scrum_bot(prompt_usuario: str) -> str:
    """
    Envia o histórico e o novo prompt do usuário para a API da Groq e retorna a resposta.
    """
    # Adiciona a mensagem do usuário ao histórico
    historico_conversa.append({
        "role": "user",
        "content": prompt_usuario,
    })

    try:
        chat_completion = client.chat.completions.create(
            # Modelos disponíveis na Groq: "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"
            model="llama3-8b-8192", 
            messages=historico_conversa,
            temperature=0.7,
            max_tokens=1024,
        )
        
        resposta = chat_completion.choices[0].message.content
        
        # Adiciona a resposta do assistente ao histórico para manter o contexto na próxima chamada
        historico_conversa.append({
            "role": "assistant",
            "content": resposta
        })
        
        return resposta

    except Exception as e:
        return f"❌ Ocorreu um erro ao chamar a API da Groq: {e}"

# --- 5. FUNÇÃO PRINCIPAL (LOOP DO CHAT) ---
def main():
    """Função principal que executa o loop do chatbot."""
    print("\n🤖 ScrumBot 3000 (versão Groq) está pronto para começar!")
    print("   Digite 'sair' a qualquer momento para encerrar.")
    
    # Mensagem inicial para a IA se apresentar e começar a daily
    resposta_inicial = obter_resposta_do_scrum_bot("Olá, time! Acabei de ser ativado. Por favor, comece a conversa.")
    print(f"\n🤖 ScrumBot 3000: {resposta_inicial}")

    while True:
        prompt_usuario = input("🙋 Você: ")
        
        if prompt_usuario.lower() in ["sair", "exit", "quit"]:
            print("\n🤖 ScrumBot 3000: Ótimo trabalho, time! Encerrando por agora. Até a próxima! 👋")
            break
            
        resposta = obter_resposta_do_scrum_bot(prompt_usuario)
        print(f"\n🤖 ScrumBot 3000: {resposta}")

# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    main()