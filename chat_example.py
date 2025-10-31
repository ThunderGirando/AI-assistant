import google.generativeai as genai

# Configurar API key
genai.configure(api_key='YOUR_API_KEY_HERE')

# Criar modelo
model = genai.GenerativeModel('gemini-2.0-flash')

# Iniciar chat session
chat = model.start_chat(history=[])

print("=== Exemplo de Chat Multi-Turn com Gemini ===")
print("Digite suas mensagens. Digite 'sair' para encerrar.\n")

while True:
    user_input = input("Você: ")
    if user_input.lower() == 'sair':
        break

    # Enviar mensagem e manter contexto
    response = chat.send_message(user_input)
    print(f"Gemini: {response.text}")
    print()

print("Chat encerrado!")
