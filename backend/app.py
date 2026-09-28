import os

from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient


# =========================
# CONFIGURAÇÕES
# =========================

load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

PONTOS = ["01", "02", "03"]


# =========================
# FLASK
# =========================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# =========================
# INFLUXDB
# =========================

influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

query_api = influx_client.query_api()


# =========================
# PÁGINA PRINCIPAL
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# STATUS DOS 3 PONTOS
# =========================

@app.route("/api/status")
def obter_status():
    """
    Retorna o último status registrado
    para cada ponto de recarga.
    """

    resultados = []

    try:

        for ponto in PONTOS:

            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
                |> range(start: -30d)
                |> filter(fn: (r) => r["_measurement"] == "status_vaga")
                |> filter(fn: (r) => r["_field"] == "status")
                |> filter(fn: (r) => r["ponto"] == "{ponto}")
                |> last()
            '''

            tables = query_api.query(
                query,
                org=INFLUXDB_ORG
            )

            encontrado = False

            for table in tables:
                for record in table.records:

                    resultados.append({
                        "ponto": ponto,
                        "status": record.get_value(),
                        "horario": record.get_time().isoformat()
                    })

                    encontrado = True

            # Caso ainda não exista registro
            # para determinado ponto
            if not encontrado:

                resultados.append({
                    "ponto": ponto,
                    "status": "SEM DADOS",
                    "horario": None
                })

        return jsonify(resultados)

    except Exception as erro:

        print(
            f"Erro ao consultar InfluxDB: {erro}"
        )

        return jsonify({
            "erro": "Não foi possível consultar o InfluxDB."
        }), 500


# =========================
# HISTÓRICO
# =========================

@app.route("/api/historico")
def obter_historico():
    """
    Retorna as últimas mudanças de status
    dos três pontos de recarga.
    """

    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -30d)
        |> filter(fn: (r) => r["_measurement"] == "status_vaga")
        |> filter(fn: (r) => r["_field"] == "status")
        |> sort(columns: ["_time"], desc: false)
    '''

    try:

        tables = query_api.query(
            query,
            org=INFLUXDB_ORG
        )

        registros = []

        for table in tables:
            for record in table.records:

                ponto = record.values.get("ponto")

                if ponto not in PONTOS:
                    continue

                registros.append({
                    "ponto": ponto,
                    "status": record.get_value(),
                    "horario": record.get_time().isoformat()
                })

        # Garante ordem cronológica
        registros.sort(
            key=lambda registro: registro["horario"]
        )

        # Último status individual de cada ponto
        ultimo_status = {
            "01": None,
            "02": None,
            "03": None
        }

        mudancas = []

        for registro in registros:

            ponto = registro["ponto"]
            status = registro["status"]

            if status != ultimo_status[ponto]:

                mudancas.append(registro)

                ultimo_status[ponto] = status

        # Mais recentes primeiro
        mudancas.reverse()

        # 10 últimas mudanças
        return jsonify(mudancas[:10])

    except Exception as erro:

        print(
            f"Erro ao consultar histórico: {erro}"
        )

        return jsonify([]), 500


# =========================
# INICIALIZAÇÃO
# =========================

if __name__ == "__main__":

    print()
    print("==============================")
    print("   SMART CHARGE - Dashboard")
    print("==============================")
    print("Acesse: http://localhost:5000")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )