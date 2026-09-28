# Smart Charge — IoT / Wokwi

Projeto local preparado para **PlatformIO + Wokwi for VS Code**.

## Estrutura

- `platformio.ini`: configura ESP32 + Arduino e instala PubSubClient/ArduinoJson.
- `src/main.cpp`: firmware do Smart Charge.
- `diagram.json`: ESP32 + HC-SR04.
- `wokwi.toml`: aponta o Wokwi para o firmware gerado pelo PlatformIO.

## Antes de simular

O Mosquitto local deve estar rodando na porta 1883 com uma configuração que permita a conexão:

```conf
listener 1883
allow_anonymous true
```

Exemplo:

```cmd
mosquitto -c "C:\Program Files\Mosquitto\smartcharge.conf" -v
```

Em outro CMD, para observar as mensagens:

```cmd
mosquitto_sub -h localhost -p 1883 -t smartcharge/ponto01/status -v
```

## VS Code

1. Abra **esta pasta `iot/wokwi`** como pasta do projeto no VS Code.
2. Aguarde o PlatformIO carregar.
3. Compile pelo comando `PlatformIO: Build` (ou pelo botão de Build).
4. Depois execute `Wokwi: Start Simulator`.
5. O código usa `host.wokwi.internal` para acessar o Mosquitto da máquina pelo gateway local do Wokwi.

## Teste

No HC-SR04, altere a distância:

- acima de 80 cm → `DISPONIVEL`
- até 80 cm → `EM USO`

Tópico MQTT:

`smartcharge/ponto01/status`

Exemplo de payload:

```json
{"ponto":"01","distancia":30.94,"ocupado":true}
```
