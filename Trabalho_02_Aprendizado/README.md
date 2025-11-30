# Trabalho 02 - Sistema de Aprendizado Q-Learning Multi-Agentes

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Professor:** Gleifer Vaz Alves
**Tema:** Aprendizagem por reforço em sistema de cruzamento viário

---

## Descrição

Sistema multi-agentes com aprendizado por reforço (Q-Learning) para otimização de decisões em cruzamento viário. Implementado com MASPY usando arquitetura BDI + Reinforcement Learning.

**Extensão do Trabalho 01:** Mantém o domínio (cruzamento de veículos) mas substitui negociação direta por aprendizado de política ótima.

---

## Estrutura de Arquivos

```
Trabalho_02_Aprendizado/
├── cruzamento_maspy_learning.py    # Sistema principal Q-Learning
├── comparar_cenarios.py            # Comparador de múltiplos cenários
├── executar_testes.py              # Suite de 28 testes automatizados
├── testar_graficos.py              # Teste rápido de matplotlib
├── cruzamento_maspy_gui.py         # Tentativa de GUI (descontinuada)
├── RELATORIO_TESTES.md             # Relatório de validação (28/28 testes)
├── CONFORMIDADE_TRABALHO02.md      # Análise de conformidade com requisitos
└── resultados/                     # Resultados organizados por timestamp
    ├── YYYYMMDD_HHMMSS/
    │   ├── metricas_aprendizado.csv
    │   ├── info_execucao.txt
    │   └── graficos/
    │       ├── recompensa_por_episodio.png
    │       ├── recompensa_acumulada.png
    │       ├── media_movel.png
    │       ├── comparacao_desempenho.png
    │       └── analise_convergencia.png
    └── ultima_execucao -> YYYYMMDD_HHMMSS
```

---

## Agentes

### 1. CoordenadorLearningAgent
Agente que aprende a política ótima de escolha de veículos.

**Arquitetura BDI:**
- Beliefs: status, episodio_atual, recompensa_total
- Goals: Goal("aprender")
- Plans: iniciar_aprendizado() - Executa Q-Learning via EnvModel

**Parâmetros de Aprendizado:**
- num_episodes: Número de episódios (default: 100)
- reward_correto: Recompensa por escolha ótima (+100)
- penalidade_multiplicador: Fator de penalização (1.5)

### 2. VeiculoLearningAgent
Agente observador que registra estatísticas.

**Arquitetura BDI:**
- Beliefs: veiculo_id, prioridade, status, tentativas, sucessos, falhas
- Goals: Goal("observar_cruzamento")
- Plans: monitorar_ambiente() - Observa passivamente

**Métricas Coletadas:**
- Histórico de ações (escolhido/não escolhido)
- Recompensa acumulada individual
- Taxa de sucesso/falha

---

## Ambiente

### CruzamentoLearningEnvironment
Ambiente de aprendizado por reforço (SART).

**States (Estados):**
- v{N}_passou: Boolean para cada veículo (1-10)
- Estado inicial: todos em 0 (aguardando)
- Estado terminal: todos em 1 (atravessaram)

**Actions (Ações):**
- escolher_veiculo(id): Seleciona veículo para atravessar

**Rewards (Recompensas):**
- Escolha ótima (maior prioridade): +100
- Escolha subótima: penalidade proporcional

**Transitions (Transições):**
- Determinísticas: escolher → marca como atravessado

---

## Sistemas de Suporte

### MetricsCollector
Sistema centralizado para coleta de métricas.

**Funcionalidades:**
- Registra recompensas por episódio
- Calcula função de utilidade PEAS
- Detecta convergência automaticamente
- Gera relatórios estatísticos
- Exporta CSV e cria 5 tipos de gráficos

### ScenarioComparator
Sistema para comparação entre cenários.

**Funcionalidades:**
- Compara múltiplos cenários
- Identifica melhor configuração
- Gera relatórios e gráficos comparativos

---

## Experimentos (10 cenários)

| # | Nome | Descrição | Veículos |
|---|------|-----------|----------|
| 1 | padrao | 10 veículos diversos | 10 |
| 2 | base | Ambulância vs normais | 4 |
| 3 | emergencias | Múltiplas emergências | 4 |
| 4 | iguais | Prioridades iguais | 4 |
| 5 | pesados | Cargas pesadas | 4 |
| 6 | transporte_publico | Ônibus, táxi | 6 |
| 7 | prioridades_proximas | Diferenças pequenas | 5 |
| 8 | extremos | 1 vs 100 | 2 |
| 9 | dois_veiculos | Caso mínimo | 2 |
| 10 | tres_veiculos | Caso intermediário | 3 |

---

## Como Executar

### Pré-requisitos

```bash
# Ativar ambiente virtual
source ../venv_maspy/bin/activate

# Instalar matplotlib (opcional para gráficos)
pip install matplotlib numpy
```

### Opção 1: Executar com Cenário Padrão (RECOMENDADO)

```bash
cd Trabalho_02_Aprendizado
python cruzamento_maspy_learning.py
```

**Saída gerada:**
- Relatório de métricas no terminal
- resultados/YYYYMMDD_HHMMSS/metricas_aprendizado.csv
- resultados/YYYYMMDD_HHMMSS/graficos/ (5 gráficos PNG)
- resultados/YYYYMMDD_HHMMSS/info_execucao.txt
- resultados/ultima_execucao/ (symlink)

### Opção 2: Executar Cenário Específico

```bash
python cruzamento_maspy_learning.py --experimento base
python cruzamento_maspy_learning.py --experimento emergencias
python cruzamento_maspy_learning.py --experimento extremos
```

### Opção 3: Configurar Parâmetros

```bash
# Alterar episódios (default: 100)
python cruzamento_maspy_learning.py --episodios 200

# Modo silencioso
python cruzamento_maspy_learning.py --quiet

# Combinação
python cruzamento_maspy_learning.py --experimento base --episodios 150 --reward 200
```

**Parâmetros disponíveis:**
- --experimento: Nome do cenário
- --episodios: Número de episódios (default: 100)
- --reward: Recompensa por acerto (default: 100)
- --penalidade: Multiplicador de penalidade (default: 1.5)
- --quiet: Modo silencioso
- --step: Modo step-by-step

### Opção 4: Comparar Múltiplos Cenários

```bash
# Comparar cenários específicos
python comparar_cenarios.py --cenarios base emergencias pesados --episodios 100

# Comparar TODOS os cenários
python comparar_cenarios.py --cenarios todos --episodios 100

# Modo verbose
python comparar_cenarios.py --cenarios todos --verbose
```

### Opção 5: Executar Suite de Testes

```bash
# Executar todos os 28 testes
python executar_testes.py
```

**Validações:**
- Sintaxe Python
- Imports e dependências
- MetricsCollector
- Função de utilidade
- Cálculos estatísticos
- Documentação PEAS/SART
- 10 cenários
- Exportação CSV
- Matplotlib (opcional)

---

## Metodologias

### PEAS (Performance, Environment, Actuators, Sensors)

Documentação integrada ao código (linhas 182-370).

**Performance:**
- Função de utilidade: U = 0.5×taxa_acerto + 0.3×convergência + 0.2×recompensa
- Recompensa acumulada
- Taxa de convergência
- Eficiência temporal

**Environment:**
- 10 cenários de teste
- Veículos com prioridades (1-100)
- Sistema de recompensas proporcional

**Actuators:**
- escolher_veiculo(id)
- iniciar_aprendizado()

**Sensors:**
- v{N}_passou (estados booleanos)
- Métricas coletadas

### SART (States, Actions, Rewards, Transitions)

**States:** Configuração de veículos que não atravessaram
**Actions:** Escolha de qual veículo atravessa
**Rewards:** +100 ótimo, penalidade proporcional
**Transitions:** Determinísticas (escolher → atravessado)

---

## Visualizações (5 tipos de gráficos)

1. Recompensa por episódio (linha)
2. Recompensa acumulada (crescimento)
3. Média móvel (tendência - janela=5)
4. Comparação de desempenho (barras duplas)
5. Análise de convergência (regressão linear)

---

## Resultados e Validação

### Sistema de Organização
- Cada execução salva em resultados/YYYYMMDD_HHMMSS/
- Symlink ultima_execucao para acesso rápido
- Arquivo info_execucao.txt com metadados completos

### Taxa de Sucesso dos Testes
- 28/28 testes passaram (100% sucesso)
- Relatório completo: RELATORIO_TESTES.md
- Conformidade com requisitos: CONFORMIDADE_TRABALHO02.md

---

## Tecnologias

- Linguagem: Python 3.13
- Framework: MASPY 2025.06.07 com Q-Learning
- Paradigma: BDI + Aprendizado por Reforço
- Bibliotecas:
  - Core: argparse, sys, signal, os, enum
  - Visualização: matplotlib, numpy (opcional)
  - Análise: csv

---

## Documentação Adicional

- [README_MELHORIAS.md](README_MELHORIAS.md) - Documentação detalhada das 5 melhorias
- [RELATORIO_TESTES.md](RELATORIO_TESTES.md) - Relatório de validação (28 testes)
- [CONFORMIDADE_TRABALHO02.md](CONFORMIDADE_TRABALHO02.md) - Análise de conformidade

---

## Comparação com Trabalho 01

| Aspecto | Trabalho 01 | Trabalho 02 |
|---------|-------------|-------------|
| Abordagem | Negociação direta | Aprendizado Q-Learning |
| Protocolo | Oferta → Decisão | Exploração → Política ótima |
| Agentes | VeiculoAgent + CoordenadorAgent | VeiculoLearningAgent + CoordenadorLearningAgent |
| Decisão | Baseada em prioridades | Aprendida via reforço |
| Cenários | 6 cenários | 10 cenários |
| Métricas | Vencedores, tempo | 15+ métricas, função utilidade |
| Visualização | Logs textuais | 5 tipos de gráficos matplotlib |

---

## Histórico de Versões

### v1.0 (2025-11-30) - ATUAL
- Implementação completa de Q-Learning
- 10 cenários de teste
- Função de utilidade PEAS
- Metodologia SART documentada
- Sistema de organização por timestamp
- 5 tipos de gráficos matplotlib
- 28 testes automatizados (100% sucesso)
- ScenarioComparator para análise

---

## Autores

- Guilherme T. S. Abreu - guiabr@alunos.utfpr.com.br
- Maria Eduarda S. Freitas - mariaeduardafreitas@alunos.utfpr.edu.br
