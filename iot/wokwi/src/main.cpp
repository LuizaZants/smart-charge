#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==========================
// SMART CHARGE
// Monitoramento de Estações de Recarga
// ==========================

// PONTO 01
#define TRIG_PIN_01 5
#define ECHO_PIN_01 18

// PONTO 02
#define TRIG_PIN_02 19
#define ECHO_PIN_02 21

// PONTO 03
#define TRIG_PIN_03 22
#define ECHO_PIN_03 23

const float LIMITE_OCUPADO = 80.0;

// Wi-Fi
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// MQTT
const char* MQTT_SERVER = "host.wokwi.internal";
const int MQTT_PORT = 1883;

const char* MQTT_TOPIC_01 = "smartcharge/ponto01/status";
const char* MQTT_TOPIC_02 = "smartcharge/ponto02/status";
const char* MQTT_TOPIC_03 = "smartcharge/ponto03/status";

WiFiClient espClient;
PubSubClient mqttClient(espClient);


// ==========================
// FUNÇÕES
// ==========================

float medirDistancia(int trigPin, int echoPin) {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duracao = pulseIn(echoPin, HIGH, 30000);

  if (duracao == 0) {
    return -1;
  }

  return duracao * 0.034 / 2.0;
}


void conectarWiFi() {

  Serial.print("Conectando ao Wi-Fi");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi conectado!");
}


void conectarMQTT() {

  while (!mqttClient.connected()) {

    Serial.print("Conectando ao Mosquitto... ");

    String clientId = "smartcharge-esp32-";
    clientId += String(random(0xffff), HEX);

    if (mqttClient.connect(clientId.c_str())) {

      Serial.println("CONECTADO!");

    } else {

      Serial.print("falhou. Codigo: ");
      Serial.println(mqttClient.state());

      delay(2000);
    }
  }
}


void publicarLeitura(
  const char* ponto,
  const char* topico,
  float distancia,
  bool ocupado
) {

  JsonDocument json;

  json["ponto"] = ponto;
  json["distancia"] = distancia;
  json["ocupado"] = ocupado;

  char mensagem[200];

  serializeJson(json, mensagem);

  if (mqttClient.publish(topico, mensagem)) {

    Serial.print("MQTT enviado: ");
    Serial.println(mensagem);

  } else {

    Serial.println("Falha ao publicar MQTT.");
  }
}


void processarPonto(
  const char* ponto,
  int trigPin,
  int echoPin,
  const char* topico
) {

  float distancia = medirDistancia(trigPin, echoPin);

  if (distancia < 0) {

    Serial.print("Ponto ");
    Serial.print(ponto);
    Serial.println(" | Leitura invalida.");

    return;
  }

  bool ocupado = distancia <= LIMITE_OCUPADO;

  Serial.print("Ponto ");
  Serial.print(ponto);

  Serial.print(" | Distancia: ");
  Serial.print(distancia);

  Serial.print(" cm | Status: ");

  Serial.println(
    ocupado
      ? "EM USO"
      : "DISPONIVEL"
  );

  publicarLeitura(
    ponto,
    topico,
    distancia,
    ocupado
  );
}


// ==========================
// SETUP
// ==========================

void setup() {

  Serial.begin(115200);

  // Ponto 01
  pinMode(TRIG_PIN_01, OUTPUT);
  pinMode(ECHO_PIN_01, INPUT);

  // Ponto 02
  pinMode(TRIG_PIN_02, OUTPUT);
  pinMode(ECHO_PIN_02, INPUT);

  // Ponto 03
  pinMode(TRIG_PIN_03, OUTPUT);
  pinMode(ECHO_PIN_03, INPUT);

  Serial.println();
  Serial.println("=============================");
  Serial.println("        SMART CHARGE");
  Serial.println("=============================");

  conectarWiFi();

  mqttClient.setServer(
    MQTT_SERVER,
    MQTT_PORT
  );

  conectarMQTT();
}


// ==========================
// LOOP
// ==========================

void loop() {

  if (!mqttClient.connected()) {
    conectarMQTT();
  }

  mqttClient.loop();


  // PONTO 01
  processarPonto(
    "01",
    TRIG_PIN_01,
    ECHO_PIN_01,
    MQTT_TOPIC_01
  );


  // PONTO 02
  processarPonto(
    "02",
    TRIG_PIN_02,
    ECHO_PIN_02,
    MQTT_TOPIC_02
  );


  // PONTO 03
  processarPonto(
    "03",
    TRIG_PIN_03,
    ECHO_PIN_03,
    MQTT_TOPIC_03
  );


  Serial.println("-----------------------------");

  delay(2000);
}