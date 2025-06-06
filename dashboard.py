import streamlit as st
import paho.mqtt.client as mqtt
import threading
import time
import pandas as pd
import altair as alt
from datetime import datetime

# Variáveis globais para armazenar dados recebidos
nivel_agua = 0.0
temperatura = 0.0
umidade = 0.0

# Callback MQTT para quando uma mensagem é recebida
def on_message(client, userdata, msg):
    global nivel_agua, temperatura, umidade
    payload = msg.payload.decode()
    try:
        parts = payload.split("|")
        nivel_agua = float(parts[0].split(":")[1].replace("cm", "").strip())
        if nivel_agua < 0:
            nivel_agua = 0.0
        temperatura = float(parts[1].split(":")[1].replace("C", "").strip())
        umidade = float(parts[2].split(":")[1].replace("%", "").strip())
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

# Configuração da página e CSS dark
st.set_page_config(page_title="Dashboard Monitoramento de Enchente", layout="wide")
st.markdown(
    """
    <style>
    .reportview-container, .main, header, footer {
        background-color: #121212;
        color: #eee;
    }
    h1 {
        color: #00bcd4;
        font-weight: 700;
    }
    .stMetric-value {
        color: #80deea !important;
        font-size: 32px !important;
        font-weight: 600 !important;
        transition: color 0.5s ease;
    }
    .stMetric-label {
        color: #b2ebf2 !important;
        font-size: 20px !important;
        font-weight: 500 !important;
    }
    .stWarning, .stError {
        background-color: #b00020 !important;
        color: white !important;
        padding: 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .stSuccess {
        background-color: #388e3c !important;
        color: white !important;
        padding: 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .last-update {
        color: #bbb;
        font-size: 14px;
        margin-bottom: 15px;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌊 Dashboard Monitoramento de Enchente")

if 'history' not in st.session_state:
    st.session_state.history = []

# Loop da interface Streamlit (limite de 50 registros no histórico)
while True:
    st.session_state.history.append({
        "time": datetime.now(),
        "nivel_agua": nivel_agua,
        "temperatura": temperatura,
        "umidade": umidade
    })

    if len(st.session_state.history) > 50:
        st.session_state.history.pop(0)

    df = pd.DataFrame(st.session_state.history)

    st.markdown(f'<div class="last-update">Última atualização: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Nível da Água (cm)", value=f"{nivel_agua:.2f}")
    col2.metric(label="Temperatura (°C)", value=f"{temperatura:.2f}")
    col3.metric(label="Umidade (%)", value=f"{umidade:.2f}")

    # ALERTA COM NÍVEIS PERSONALIZADOS
    if nivel_agua >= 250:
        st.error("🔴 **RISCO DE ENCHENTE!**\n\nO nível da água ultrapassou 250 cm.")
        st.toast("🔴 Nível crítico: RISCO DE ENCHENTE!", icon="🚨")
    elif nivel_agua >= 150:
        st.warning("🟡 **ALERTA:**\n\nNível da água entre 150 e 249 cm.")
        st.toast("🟡 Alerta: Nível elevado", icon="⚠️")
    else:
        st.success("🟢 **Nível da água normal**\n\nTudo sob controle.")
        st.toast("🟢 Normal: Nível seguro", icon="✅")

    # Dados para gráficos refinados
    data_refinado = pd.DataFrame({
        'Medição': ['Nível da Água', 'Temperatura', 'Umidade'],
        'Valor': [nivel_agua, temperatura, umidade]
    })

    cores = ['#0288d1', '#4caf50', '#fbc02d']

    graf_col1, graf_col2, graf_col3 = st.columns(3)
    for col, medicao, cor in zip(
        [graf_col1, graf_col2, graf_col3],
        ['Nível da Água', 'Temperatura', 'Umidade'],
        cores
    ):
        df_temp = data_refinado[data_refinado['Medição'] == medicao]
        chart = alt.Chart(df_temp).mark_bar(
            size=50,
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5,
            opacity=0.7
        ).encode(
            x=alt.X('Medição:N', axis=alt.Axis(labelAngle=0, labelColor='white', ticks=False, domain=False)),
            y=alt.Y('Valor:Q', scale=alt.Scale(domain=[0, max(100, df_temp['Valor'].values[0]*1.2)]), axis=alt.Axis(grid=False, labelColor='white', titleColor='white')),
            color=alt.value(cor),
            tooltip=[alt.Tooltip('Valor:Q', title='Valor')]
        ).properties(width=150, height=250)
        col.altair_chart(chart, use_container_width=True)

    line_chart = alt.Chart(df).mark_line(point=True, color='#80deea').encode(
        x=alt.X('time:T', axis=alt.Axis(labelColor='white', titleColor='white', format='%Y-%m-%d %H:%M:%S'), title='Data e Hora'),
        y=alt.Y('nivel_agua:Q', axis=alt.Axis(labelColor='white', titleColor='white'), title='Nível da Água (cm)'),
        tooltip=[
            alt.Tooltip('time:T', title='Data e Hora', format='%Y-%m-%d %H:%M:%S'),
            alt.Tooltip('nivel_agua:Q', title='Nível da Água (cm)')
        ]
    ).properties(width=700, height=300)

    st.altair_chart(line_chart, use_container_width=True)

    time.sleep(5)
