# Smart Charge - Frontend

Frontend obrigatório do projeto desenvolvido com Vue.js 3, TypeScript e Vite. A visualização utiliza Chart.js.

## Executar

Com o backend Flask já rodando em `http://127.0.0.1:5000`:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`.

O Vite encaminha automaticamente `/api/status` e `/api/historico` para o backend Flask na porta 5000.

## Build

```powershell
npm run build
```
