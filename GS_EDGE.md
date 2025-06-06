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

Funcionamento do Projeto:
Este sistema monitora o nível da água em tempo real utilizando sensores conectados ao ESP32 e exibe os dados em um painel gráfico desenvolvido com Python (Streamlit).

Coleta de Dados (ESP32):
O ESP32 mede a distância da água usando o sensor ultrassônico HC-SR04.
A distância é convertida no nível da água (em cm) com base na altura total do reservatório (por exemplo, 400 cm).
Mede também a temperatura e a umidade do ar com o sensor DHT22.
Os dados são enviados via Wi-Fi para um broker MQTT público (HiveMQ).

Estrutura da Mensagem:
Os dados são enviados no seguinte formato para o tópico enchente/nivel:
Nivel: 120cm | Temp: 26.3C | Umidade: 71%
📊 Monitoramento com Streamlit
O dashboard desenvolvido em Python com Streamlit recebe os dados MQTT em tempo real.

Os dados são exibidos com:

Métricas de leitura atual

Gráficos de barra e linha

Atualização automática a cada 5 segundos

Alerta visual com base no nível da água

🚨 Lógica de Alerta por Nível da Água
O sistema possui três níveis de alerta, conforme a altura da água:

0 a 150 cm: Nível Normal

LED azul aceso

Mensagem de operação normal no OLED e painel

151 a 249 cm: Alerta

Mensagem de alerta no painel e display

250 cm ou mais: Risco de Enchente

LED vermelho aceso

Alerta crítico no OLED e painel gráfico
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

```powershell
pip install paho-mqtt streamlit
```ou caso não for:
python -m streamlit run dashboard.py

### 3. Executar o Dashboard:

```powershell
streamlit run dashboard.py
```

### 4. Arquivo `dashboard.py` :

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
