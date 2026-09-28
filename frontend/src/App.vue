<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { Chart, ArcElement, DoughnutController, Legend, Tooltip } from 'chart.js'

Chart.register(ArcElement, DoughnutController, Legend, Tooltip)

type StatusPonto = 'DISPONIVEL' | 'EM USO' | 'SEM DADOS'

interface Ponto {
  ponto: string
  status: StatusPonto
  horario: string | null
}

interface HistoricoItem {
  ponto: string
  status: StatusPonto
  horario: string | null
}

const pontos = ref<Ponto[]>([
  { ponto: '01', status: 'SEM DADOS', horario: null },
  { ponto: '02', status: 'SEM DADOS', horario: null },
  { ponto: '03', status: 'SEM DADOS', horario: null }
])
const historico = ref<HistoricoItem[]>([])
const erro = ref('')
const graficoCanvas = ref<HTMLCanvasElement | null>(null)
let grafico: Chart<'doughnut'> | null = null
let intervalo: number | undefined

const disponiveis = computed(() => pontos.value.filter((p) => p.status === 'DISPONIVEL').length)
const emUso = computed(() => pontos.value.filter((p) => p.status === 'EM USO').length)
const semDados = computed(() => pontos.value.filter((p) => p.status === 'SEM DADOS').length)

function formatarHorario(dataISO: string | null): string {
  if (!dataISO) return '--:--:--'
  return new Date(dataISO).toLocaleTimeString('pt-BR', {
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

function classeStatus(status: StatusPonto): string {
  if (status === 'DISPONIVEL') return 'disponivel'
  if (status === 'EM USO') return 'ocupado'
  return 'carregando'
}

function textoStatus(status: StatusPonto): string {
  return status === 'DISPONIVEL' ? 'DISPONÍVEL' : status
}

function descricaoStatus(status: StatusPonto): string {
  if (status === 'DISPONIVEL') return 'Ponto livre para carregamento.'
  if (status === 'EM USO') return 'Veículo detectado no ponto de recarga.'
  return 'Nenhuma informação disponível.'
}

function atualizarGrafico(): void {
  if (!graficoCanvas.value) return
  const data = [disponiveis.value, emUso.value, semDados.value]

  if (grafico) {
    grafico.data.datasets[0].data = data
    grafico.update()
    return
  }

  grafico = new Chart(graficoCanvas.value, {
    type: 'doughnut',
    data: {
      labels: ['Disponíveis', 'Em uso', 'Sem dados'],
      datasets: [{
        data,
        backgroundColor: ['#37e6a1', '#ff6376', '#55aaff'],
        borderColor: '#101f31',
        borderWidth: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#c5d1de', padding: 18, usePointStyle: true }
        }
      }
    }
  })
}

async function atualizarDashboard(): Promise<void> {
  try {
    const [resStatus, resHistorico] = await Promise.all([
      fetch('/api/status'),
      fetch('/api/historico')
    ])

    if (!resStatus.ok || !resHistorico.ok) throw new Error('Falha ao consultar a API')

    const novosPontos = await resStatus.json() as Ponto[]
    const novoHistorico = await resHistorico.json() as HistoricoItem[]

    if (!Array.isArray(novosPontos) || !Array.isArray(novoHistorico)) {
      throw new Error('Formato inesperado da API')
    }

    pontos.value = novosPontos
    historico.value = novoHistorico
    erro.value = ''
    await nextTick()
    atualizarGrafico()
  } catch (e) {
    console.error(e)
    erro.value = 'Não foi possível atualizar os dados. Verifique o backend.'
  }
}

onMounted(async () => {
  await atualizarDashboard()
  intervalo = window.setInterval(atualizarDashboard, 3000)
})

onBeforeUnmount(() => {
  if (intervalo) window.clearInterval(intervalo)
  grafico?.destroy()
})
</script>

<template>
  <header class="topo">
    <div class="marca">
      <div class="logo">⚡</div>
      <div>
        <h1>SMART CHARGE</h1>
        <p>Monitoramento inteligente de estações de recarga</p>
      </div>
    </div>
    <div class="sistema-online"><span class="ponto-online"></span>Sistema online</div>
  </header>

  <main class="container">
    <section class="titulo-pagina">
      <p class="subtitulo">MONITORAMENTO EM TEMPO REAL</p>
      <h2>Estações de carregamento</h2>
      <p>Acompanhe a disponibilidade dos pontos de recarga.</p>
    </section>

    <p v-if="erro" class="aviso-erro">{{ erro }}</p>

    <section class="estacoes">
      <article v-for="ponto in pontos" :key="ponto.ponto" class="card-estacao">
        <div class="card-topo">
          <div><span class="identificador">PONTO DE RECARGA</span><h3>Estação {{ ponto.ponto }}</h3></div>
          <span class="numero-estacao">{{ ponto.ponto }}</span>
        </div>
        <div class="area-status" :class="classeStatus(ponto.status)">
          <div class="icone-status">⚡</div>
          <span class="status-label">STATUS ATUAL</span>
          <strong>{{ textoStatus(ponto.status) }}</strong>
          <p>{{ descricaoStatus(ponto.status) }}</p>
        </div>
        <div class="ultima-atualizacao">
          <span>Última atualização</span>
          <strong>{{ formatarHorario(ponto.horario) }}</strong>
        </div>
      </article>
    </section>

    <section class="painel-inferior">
      <article class="card-historico historico-geral">
        <div class="historico-topo">
          <div><span class="identificador">ATIVIDADE</span><h3>Histórico recente</h3></div>
          <span class="icone-historico">↻</span>
        </div>
        <div class="lista-historico">
          <p v-if="historico.length === 0" class="carregando-historico">Nenhum registro encontrado.</p>
          <div v-for="(item, index) in historico" :key="`${item.ponto}-${item.horario}-${index}`" class="item-historico">
            <div class="evento">
              <span class="indicador" :class="item.status === 'EM USO' ? 'vermelho' : 'verde'"></span>
              <div><strong>{{ item.status === 'EM USO' ? 'Em uso' : 'Disponível' }}</strong><p>Ponto {{ item.ponto }}</p></div>
            </div>
            <span class="hora-evento">{{ formatarHorario(item.horario) }}</span>
          </div>
        </div>
      </article>

      <article class="card-grafico">
        <div class="historico-topo">
          <div><span class="identificador">VISUALIZAÇÃO</span><h3>Ocupação atual</h3></div>
          <span class="icone-historico">◉</span>
        </div>
        <div class="grafico-area"><canvas ref="graficoCanvas"></canvas></div>
        <div class="resumo-grafico">
          <span><b>{{ disponiveis }}</b> disponíveis</span>
          <span><b>{{ emUso }}</b> em uso</span>
        </div>
      </article>
    </section>
  </main>

  <footer><span>⚡ Smart Charge</span><p>Sistema inteligente de monitoramento de pontos de recarga</p></footer>
</template>
