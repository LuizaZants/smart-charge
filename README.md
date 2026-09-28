# Smart Charge

Aplicação Web + IoT para monitoramento da disponibilidade de pontos de recarga de veículos elétricos.

## Arquitetura

ESP32/Wokwi + sensores HC-SR04 → MQTT → Mosquitto → Python → InfluxDB → API Flask → Vue.js 3 + TypeScript + Vite + Chart.js.

O projeto possui três pontos de recarga independentes. O ESP32 publica as leituras via MQTT; o cliente Python processa mudanças de estado e persiste no InfluxDB; a API Flask consulta status e histórico; o frontend Vue atualiza automaticamente os indicadores e o gráfico.

## Estrutura

- `iot/wokwi/`: ESP32 simulado, sensores e configuração PlatformIO/Wokwi.
- `backend/mqtt_client.py`: recebe mensagens MQTT e grava mudanças no InfluxDB.
- `backend/app.py`: API Flask (`/api/status` e `/api/historico`).
- `frontend/`: interface oficial em Vue 3 + TypeScript + Vite + Chart.js.
- `backend/templates/` e `backend/static/`: dashboard legado preservado como backup da versão funcional anterior.

## 1. Backend Python

Na raiz do projeto:

```powershell
.\.venv\Scripts\Activate.ps1
py backend/mqtt_client.py
```

Em outro terminal:

```powershell
.\.venv\Scripts\Activate.ps1
py backend/app.py
```

Se for preparar o ambiente do zero:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha as configurações do InfluxDB.

## 2. Frontend obrigatório

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173`.

O Vite encaminha `/api/*` para o Flask em `http://127.0.0.1:5000`, portanto o backend deve estar rodando.

## 3. Wokwi

O projeto do dispositivo está em `iot/wokwi`. Se o firmware precisar ser recompilado:

```powershell
cd iot/wokwi
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
```

Depois inicie a simulação Wokwi.

## Fluxo de execução para apresentação

1. InfluxDB (porta 8086)
2. Mosquitto (porta 1883)
3. `py backend/mqtt_client.py`
4. `py backend/app.py`
5. `cd frontend` + `npm run dev`
6. Wokwi
7. Abrir `http://localhost:5173`

## Tecnologias obrigatórias atendidas

- Vue.js 3
- TypeScript
- Vite
- Chart.js
- Python
- MQTT + Mosquitto
- ESP32/Wokwi
- InfluxDB
- Git + GitHub
