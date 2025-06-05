# Projeto de Monitoramento de Enchentes com IoT e MQTT

## Descrição Geral

Este projeto tem como objetivo demonstrar uma solução de monitoramento preventivo contra enchentes, utilizando sensores conectados a um microcontrolador ESP32, que envia dados para um broker MQTT (Mosquitto). Um dashboard em Python (Streamlit) exibe os dados em tempo real e emite alertas.

## Arquitetura da Solução

A arquitetura é dividida em três camadas principais:

### 1. **Camada IoT (dispositivos e sensores)**

* **ESP32**: microcontrolador Wi-Fi responsável por ler os sensores e enviar os dados via MQTT.
* **Sensor Ultrassônico (HC-SR04)**: mede o nível da água.
* **Sensor DHT22**: mede temperatura e umidade do ar.
* **LEDs**: indicam o status do nível da água (normal ou alerta).
* **OLED Display**: mostra os dados locais no dispositivo.
* **Buzzer**: alerta sonoro em caso de risco.

### 2. **Camada de Back-End (comunicação e integração)**

* **Broker MQTT (Mosquitto)**: recebe os dados publicados pelo ESP32.

  * Tópico usado: `enchente/nivel`
* **Python (paho-mqtt + Streamlit)**: subscreve ao tópico MQTT e exibe os dados em um dashboard.

### 3. **Camada de Aplicação (Dashboard)**

* **Dashboard em Streamlit**: apresenta as informações de forma amigável ao usuário com alertas visuais.
* Exibe:

  * Nível da água (cm)
  * Temperatura (Celsius)
  * Umidade (%)
  * Status: Normal ou Alerta de Enchente

---

## Funcionamento do Projeto

1. O ESP32 mede periodicamente a distância da água com o sensor ultrassônico.
2. Mede temperatura e umidade com o sensor DHT22.
3. Envia esses dados para o broker MQTT usando Wi-Fi.
4. O dashboard Python recebe esses dados e os exibe em tempo real.
5. Quando o nível da água está abaixo de 80 cm, os LEDs e buzzer são ativados e um alerta é mostrado no dashboard.

---

## Instruções para Executar o Projeto

### 1. Simulação no Wokwi

* Acesse: [Simulação Wokwi](https://wokwi.com/projects/432871241623937025)
* Clique em "Start Simulation"
* Observe a saída no monitor serial e no display OLED

### 2. Instalação do Dashboard Python

#### Requisitos:

* Python 3.8+
* Dependências:

```bash
pip install paho-mqtt streamlit
```

### 3. Executar o Dashboard:

```bash
streamlit run dashboard.py
```

### 4. Arquivo `dashboard.py` (código completo):

```python
import streamlit as st
import paho.mqtt.client as mqtt

st.set_page_config(page_title="Monitoramento de Enchentes", layout="centered")
st.title("Monitoramento de Enchentes")

status = st.empty()
nivel = st.metric("Nível da água", "...")
temp = st.metric("Temperatura", "...")
umid = st.metric("Umidade", "...")

broker = "broker.hivemq.com"
topic = "enchente/nivel"

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    parts = payload.split("|")
    try:
        nivel_val = parts[0].split(":")[1].replace("cm", "").strip()
        temp_val = parts[1].split(":")[1].strip()
        umid_val = parts[2].split(":")[1].strip()

        nivel.metric("Nível da água", f"{nivel_val} cm")
        temp.metric("Temperatura", f"{temp_val} °C")
        umid.metric("Umidade", f"{umid_val} %")

        if float(nivel_val) < 80:
            status.warning("🚨 Risco de enchente!")
        else:
            status.success("✅ Status: Normal")

    except:
        status.error("Erro ao processar dados")

client = mqtt.Client()
client.on_message = on_message
client.connect(broker, 1883)
client.subscribe(topic)
client.loop_start()
```

---

## Conclusão

Este projeto demonstra uma solução de IoT completa para monitoramento de enchentes com captura de dados, publicação MQTT, atuação local e visualização em tempo real via dashboard. Pode ser expandido com armazenamento em nuvem, histórico de dados e integração com sistemas de defesa civil.

---

## Créditos

Nomes: Marco Antonio (559256), Leonardo Fernandes Mesquita (559623), Guilherme Augusto (559765)
Projeto GS FIAP 2025 – Sistema de Alerta de Enchentes
