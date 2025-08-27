# src/app.py

import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- 1. CONFIGURAÇÃO DO CLIENTE GROQ (Igual ao anterior) ---
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    st.error(f"Erro ao configurar o cliente Groq: {e}. Verifique sua chave de API no arquivo .env")
    st.stop()

# --- 2. DEFINIÇÃO DA PERSONA (Igual ao anterior) ---
instrucoes_scrum_master = """
Você é o "ScrumBot 3000", um assistente de Scrum Master baseado em IA. Sua missão é ajudar um time de desenvolvimento ágil a se manter no caminho certo, ser produtivo e melhorar continuamente. Você está em uma interface web agora. Seja conciso e use formatação markdown para melhorar a legibilidade.

Suas principais responsabilidades são:
1.  **Lembretes e Condução da Daily:** Inicie a conversa lembrando da Daily Stand-up e fazendo as três perguntas clássicas (O que você fez ontem? O que fará hoje? Há algum impedimento?).
2.  **Identificação de Impedimentos:** Preste muita atenção a qualquer menção de bloqueios, dificuldades ou dependências. Quando identificar um, pergunte mais detalhes e sugira os próximos passos.
3.  **Feedback em User Stories:** Se um usuário colar uma User Story, sua tarefa é analisá-la. Verifique se ela segue o formato "Como [persona], quero [funcionalidade], para [benefício]". Se não, ajude a reescrevê-la. Além disso, sempre sugira de 2 a 4 Critérios de Aceitação (ACs).
4.  **Sugestão de Melhorias:** Com base na conversa, sugira proativamente melhorias para o processo do time.
5.  **Tom de Voz:** Seja sempre prestativo, positivo e direto ao ponto. Use emojis e markdown (negrito, listas) para deixar a comunicação mais clara e amigável. 🚀
"""

# --- 3. LÓGICA DA APLICAÇÃO STREAMLIT ---

# Título da página
st.title("🤖 Chatbot Scrum Master")
st.caption("Um assistente de IA para ajudar seu time ágil, powered by Groq & Streamlit")

# Inicializa o histórico da conversa na memória da sessão se ele não existir
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Olá, time! 👋 Sou o ScrumBot 3000. Vamos começar nossa Daily Stand-up? Me digam: o que vocês fizeram ontem, o que planejam para hoje e se há algum impedimento."
        }
    ]
    # Adiciona a instrução do sistema sem mostrá-la na tela
    st.session_state.full_history = [
        {"role": "system", "content": instrucoes_scrum_master},
        {"role": "assistant", "content": st.session_state.messages[0]['content']}
    ]

# Exibe as mensagens do histórico na interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura a entrada do usuário com o campo de texto no final da página
if prompt := st.chat_input("Digite sua mensagem aqui..."):
    
    # Adiciona a mensagem do usuário ao histórico visível e ao completo
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.full_history.append({"role": "user", "content": prompt})
    
    # Exibe a mensagem do usuário na interface
    with st.chat_message("user"):
        st.markdown(prompt)

    # Exibe uma animação de "pensando..." enquanto a resposta é gerada
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                chat_completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=st.session_state.full_history, # Usa o histórico completo
                    temperature=0.7,
                    max_tokens=1024,
                )
                response = chat_completion.choices[0].message.content
                
                # Exibe a resposta do assistente
                st.markdown(response)

                # Adiciona a resposta do assistente aos históricos
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.full_history.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Ocorreu um erro ao chamar a API: {e}")