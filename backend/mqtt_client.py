import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision


# =========================
# CONFIGURAÇÕES MQTT
# =========================

BROKER = "localhost"
PORT = 1883

# Recebe ponto01, ponto02 e ponto03
TOPIC = "smartcharge/+/status"


# =========================
# CONFIGURAÇÕES INFLUXDB
# =========================

load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

write_api = influx_client.write_api()


# =========================
# ÚLTIMO STATUS DE CADA PONTO
# =========================

ultimo_status = {
    "01": None,
    "02": None,
    "03": None
}


# =========================
# SALVAR NO INFLUXDB
# =========================

def salvar_status(ponto, status):

    try:

        registro = (
            Point("status_vaga")
            .tag("ponto", ponto)
            .field("status", status)
        )

        write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=registro,
            write_precision=WritePrecision.NS
        )

        print(
            f"Status do Ponto {ponto} "
            f"salvo no InfluxDB!"
        )

        return True

    except Exception as erro:

        print(
            f"Erro ao salvar Ponto {ponto} "
            f"no InfluxDB: {erro}"
        )

        return False


# =========================
# MQTT - CONEXÃO
# =========================

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):

    if reason_code == 0:

        print("Conectado ao Mosquitto!")
        print(f"Escutando o tópico: {TOPIC}")
        print()

        client.subscribe(TOPIC)

    else:

        print(
            f"Falha na conexão MQTT. "
            f"Código: {reason_code}"
        )


# =========================
# MQTT - RECEBER MENSAGEM
# =========================

def on_message(client, userdata, msg):

    try:

        dados = json.loads(
            msg.payload.decode()
        )

        ponto = str(dados["ponto"]).zfill(2)
        distancia = float(dados["distancia"])
        ocupado = bool(dados["ocupado"])

        status = (
            "EM USO"
            if ocupado
            else "DISPONIVEL"
        )


        print("------------------------------")
        print(f"Tópico: {msg.topic}")
        print(f"Ponto: {ponto}")
        print(f"Distância: {distancia:.2f} cm")
        print(f"Status: {status}")


        # =========================
        # VALIDA O PONTO
        # =========================

        if ponto not in ultimo_status:

            print(
                f"Ponto desconhecido: {ponto}"
            )

            return


        # =========================
        # VERIFICA MUDANÇA
        # =========================

        status_anterior = ultimo_status[ponto]

        if status != status_anterior:

            print(
                f"Mudança detectada no Ponto {ponto}: "
                f"{status_anterior} -> {status}"
            )

            salvou = salvar_status(
                ponto,
                status
            )

            # Só atualiza a memória se
            # realmente conseguiu salvar
            if salvou:

                ultimo_status[ponto] = status

        else:

            print(
                f"Ponto {ponto}: status não mudou. "
                f"Registro não salvo."
            )


    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError
    ) as erro:

        print(
            f"Mensagem MQTT inválida: {erro}"
        )


# =========================
# INICIALIZAÇÃO
# =========================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message


print("==============================")
print("     SMART CHARGE - MQTT")
print("==============================")
print("Conectando ao Mosquitto...")
print()


client.connect(
    BROKER,
    PORT,
    60
)

client.loop_forever()