import streamlit as st
import paho.mqtt.client as mqtt
import threading
import time

# Variáveis globais para armazenar dados recebidos
nivel_agua = 0.0
temperatura = 0.0
umidade = 0.0

# Callback MQTT para quando uma mensagem é recebida
def on_message(client, userdata, msg):
    global nivel_agua, temperatura, umidade
    payload = msg.payload.decode()
    # Exemplo de mensagem: "Nivel: 23.45 cm | T: 28.5 | U: 40.2"
    try:
        parts = payload.split("|")
        nivel_agua = float(parts[0].split(":")[1].replace("cm", "").strip())
        temperatura = float(parts[1].split(":")[1].strip())
        umidade = float(parts[2].split(":")[1].strip())
    except Exception as e:
        print("Erro ao processar mensagem:", e)

# Função para rodar o cliente MQTT em outra thread
def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.subscribe("enchente/nivel")
    client.loop_forever()

# Inicia thread MQTT
threading.Thread(target=mqtt_thread, daemon=True).start()

# Interface Streamlit
st.title("Dashboard Monitoramento de Enchente")

while True:
    st.metric(label="Nível da Água (cm)", value=f"{nivel_agua:.2f}")
    st.metric(label="Temperatura (°C)", value=f"{temperatura:.2f}")
    st.metric(label="Umidade (%)", value=f"{umidade:.2f}")

    if nivel_agua < 80.0:
        st.warning("⚠️ ALERTA DE ENCHENTE! Nível de água elevado!")
    else:
        st.success("Nível de água normal")

    time.sleep(5)
