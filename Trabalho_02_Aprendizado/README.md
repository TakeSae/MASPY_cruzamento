# Trabalho 02 - Sistema de Aprendizado Q-Learning Multi-Agentes

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Professor:** Gleifer Vaz Alves
**Tema:** Aprendizagem por reforço em sistema de cruzamento viário

---

## Descrição

Sistema multi-agentes com aprendizado por reforço (Q-Learning) para otimização de decisões em cruzamento viário. Implementado com MASPY usando arquitetura BDI + Reinforcement Learning.

**Extensão do Trabalho 01:** Mantém o domínio (cruzamento de veículos) mas substitui negociação direta por aprendizado de política ótima.

## Recursos Principais

- **Q-Learning com MASPY:** Integração completa de aprendizado por reforço com framework BDI
- **10 Cenários Pré-configurados:** Diferentes situações de tráfego (emergências, cargas, prioridades)
- **Sistema de Análise Avançada:** Consolidação automática de métricas com visualizações comparativas
- **Organização por Timestamp:** Resultados individuais preservados com symlink para última execução
- **11 Tipos de Gráficos:** 5 individuais + 6 comparativos (incluindo heatmap)
- **Relatórios Automatizados:** Markdown, CSV e JSON para análise posterior
- **Metodologias Documentadas:** PEAS e SART completas com diagramas UML
- **Testes Automatizados:** Suite de validação em test_scripts/
- **Análise Estatística:** Convergência, quartis, regressão linear, distribuição

---

## Estrutura de Arquivos

```
Trabalho_02_Aprendizado/
├── cruzamento_maspy_learning.py    # Sistema principal Q-Learning
├── executar_todos_cenarios.py      # Executa todos os cenários automaticamente
├── comparar_cenarios.py            # Comparador de múltiplos cenários
├── analisar_comparacao.py          # Análise comparativa avançada
├── testar_analise.py               # Script de teste do sistema de análise
├── requirements_analise.txt        # Dependências para análise avançada
├── cruzamento_maspy_gui.py         # Tentativa de GUI (descontinuada)
├── README_ANALISE_COMPARATIVA.md   # Documentação do sistema de análise
├── docs/                           # Documentação
│   ├── PEAS.md                     # Metodologia PEAS completa
│   ├── SART.md                     # Metodologia SART completa
│   ├── RELATORIO_TESTES.md         # Relatório de validação (28/28 testes)
│   ├── CONFORMIDADE_TRABALHO02.md  # Análise de conformidade com requisitos
│   ├── DIAGRAMAS_UML.md            # 8 diagramas UML
│   ├── COMPARACAO_TRABALHO1_VS_TRABALHO2.md  # Comparação entre trabalhos
│   ├── ARTIGO_SBC.md               # Artigo em formato SBC
│   ├── APRESENTACAO_SLIDES.md      # Apresentação de slides (30 slides)
│   └── dificuldades_encontradas.md # Registro de problemas e soluções
├── resultados/                     # Resultados organizados por timestamp
│   ├── YYYYMMDD_HHMMSS/
│   │   ├── metricas_aprendizado.csv
│   │   ├── info_execucao.txt
│   │   └── graficos/
│   │       ├── recompensa_por_episodio.png
│   │       ├── recompensa_acumulada.png
│   │       ├── media_movel.png
│   │       ├── comparacao_desempenho.png
│   │       └── analise_convergencia.png
│   └── ultima_execucao -> YYYYMMDD_HHMMSS
├── analise_comparativa/            # Análise consolidada de todos os cenários
│   ├── RELATORIO_COMPARATIVO.md    # Relatório principal
│   ├── metricas_consolidadas.csv   # Todas as métricas em CSV
│   ├── ranking_cenarios.json       # Ranking detalhado
│   └── graficos/                   # 6 visualizações comparativas
│       ├── 1_recompensa_media_por_cenario.png
│       ├── 2_evolucao_aprendizado_comparada.png
│       ├── 3_distribuicao_recompensas.png
│       ├── 4_taxa_convergencia.png
│       ├── 5_heatmap_metricas.png
│       └── 6_tempo_execucao.png
└── test_scripts/                   # Scripts de teste
    ├── executar_testes.py          # Suite de 28 testes automatizados
    └── testar_graficos.py          # Teste rápido de matplotlib
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

### AnalisadorComparativo
Sistema de análise comparativa avançada (analisar_comparacao.py).

**Funcionalidades:**
- Consolida métricas de múltiplas execuções
- Calcula estatísticas avançadas (média, desvio, convergência)
- Gera 6 tipos de visualizações comparativas
- Cria relatório markdown detalhado
- Exporta ranking JSON e CSV consolidado
- Análise de heatmap de métricas normalizadas

---

## Experimentos (10 cenários)

| # | Nome | Descrição | Veículos |
|---|------|-----------|----------|
| 1 | padrao | Cenário padrão com 10 veículos diversos | 10 |
| 2 | base | Ambulância contra veículos normais | 10 |
| 3 | emergencias | Múltiplas emergências | 10 |
| 4 | iguais | Todas as prioridades iguais | 10 |
| 5 | pesados | Cargas pesadas variadas | 10 |
| 6 | transporte_publico | Ônibus e táxis | 10 |
| 7 | prioridades_proximas | Diferenças pequenas entre prioridades | 10 |
| 8 | extremos | Prioridades extremas (10 e 100) | 10 |
| 9 | escalonado | Escala uniforme de 10 até 100 | 10 |
| 10 | misto_complexo | Mix de todos os tipos | 10 |

**Nota:** Todos os cenários têm 10 veículos para garantir comparabilidade.

---

## Fluxo de Trabalho Recomendado

### Para Análise Completa (Recomendado)
1. Execute todos os cenários: `python executar_todos_cenarios.py`
2. Sistema executa automaticamente:
   - 10 cenários com 1000 episódios cada
   - Salva resultados individuais em resultados/TIMESTAMP/
   - Gera análise comparativa em analise_comparativa/
3. Consulte o relatório: `analise_comparativa/RELATORIO_COMPARATIVO.md`
4. Visualize gráficos comparativos em `analise_comparativa/graficos/`

### Para Teste Rápido
1. Execute cenário individual: `python cruzamento_maspy_learning.py --episodios 100`
2. Verifique resultados em `resultados/ultima_execucao/`

### Para Desenvolvimento
1. Execute testes: `cd test_scripts && python executar_testes.py`
2. Teste análise: `python testar_analise.py`
3. Execute cenário específico: `python cruzamento_maspy_learning.py --experimento base --episodios 100`

---

## Como Executar

### Pré-requisitos

```bash
# Ativar ambiente virtual
source ../venv_maspy/bin/activate

# Instalar dependências básicas (opcional para gráficos)
pip install matplotlib numpy

# Instalar dependências para análise avançada (opcional)
pip install -r requirements_analise.txt
# ou manualmente: pip install numpy matplotlib seaborn
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

### Opção 5: Análise Comparativa Avançada

```bash
# Executar todos os cenários E análise comparativa automática
python executar_todos_cenarios.py

# Análise de resultados existentes
python analisar_comparacao.py --resultados resultados/20251204_* --output minha_analise

# Testar sistema de análise
python testar_analise.py
```

**Saída gerada em analise_comparativa/:**
- RELATORIO_COMPARATIVO.md: Relatório detalhado
- metricas_consolidadas.csv: Todas as métricas
- ranking_cenarios.json: Ranking estruturado
- graficos/: 6 visualizações comparativas

**Documentação completa:** [README_ANALISE_COMPARATIVA.md](README_ANALISE_COMPARATIVA.md)

### Opção 6: Executar Suite de Testes

```bash
# Executar todos os testes
cd test_scripts
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

Documentação completa em **[docs/PEAS.md](docs/PEAS.md)**

**Resumo:**
- **Performance:** Função de utilidade, recompensa acumulada, taxa de convergência
- **Environment:** Cruzamento determinístico, totalmente observável, multi-agente
- **Actuators:** escolher_veiculo(), atualizar_q(), exploração vs exploitação
- **Sensors:** Estados dos veículos, prioridades, recompensas, Q-table

### SART (Situation, Agent, Reinforcement learning, Task)

Documentação completa em **[docs/SART.md](docs/SART.md)**

**Resumo:**
- **Situation:** Gerenciamento de cruzamento sem protocolo fixo
- **Agent:** Coordenador (aprendiz) + Veículos (observadores) + Ambiente
- **Reinforcement Learning:** Q-Learning com equação de Bellman
- **Task:** Aprender política ótima com ≥95% de acerto

---

## Visualizações

### Gráficos Individuais (5 tipos)
Por execução em resultados/TIMESTAMP/graficos/:

1. Recompensa por episódio (linha)
2. Recompensa acumulada (crescimento)
3. Média móvel (tendência - janela=5)
4. Comparação de desempenho (barras duplas)
5. Análise de convergência (regressão linear)

### Gráficos Comparativos (6 tipos)
Análise consolidada em analise_comparativa/graficos/:

1. Recompensa média por cenário (barras ordenadas)
2. Evolução de aprendizado comparada (curvas múltiplas)
3. Distribuição de recompensas (boxplot)
4. Taxa de convergência (barras)
5. Heatmap de métricas normalizadas
6. Tempo de execução (barras horizontais)

---

## Resultados e Validação

### Sistema de Organização
- Cada execução salva em resultados/YYYYMMDD_HHMMSS/
- Symlink ultima_execucao para acesso rápido
- Arquivo info_execucao.txt com metadados completos

### Taxa de Sucesso dos Testes
- Testes automatizados disponíveis em test_scripts/
- Relatório completo: [docs/RELATORIO_TESTES.md](docs/RELATORIO_TESTES.md)
- Conformidade com requisitos: [docs/CONFORMIDADE_TRABALHO02.md](docs/CONFORMIDADE_TRABALHO02.md)

### Análise Comparativa
- Sistema completo de análise em analisar_comparacao.py
- Consolida resultados de múltiplas execuções
- Gera relatórios e visualizações avançadas
- Documentação: [README_ANALISE_COMPARATIVA.md](README_ANALISE_COMPARATIVA.md)

---

## Tecnologias

- Linguagem: Python 3.13
- Framework: MASPY 2025.06.07 com Q-Learning
- Paradigma: BDI + Aprendizado por Reforço
- Bibliotecas:
  - Core: argparse, sys, signal, os, enum, datetime
  - Visualização: matplotlib, numpy (opcional)
  - Análise avançada: seaborn (opcional)
  - Dados: csv, json

---

## Documentação Adicional

Toda a documentação está organizada na pasta **[docs/](docs/)**:

### Metodologias
- **[docs/PEAS.md](docs/PEAS.md)** - Metodologia PEAS completa (Performance, Environment, Actuators, Sensors)
- **[docs/SART.md](docs/SART.md)** - Metodologia SART completa (Situation, Agent, Reinforcement learning, Task)

### Análises e Comparações
- **[docs/DIAGRAMAS_UML.md](docs/DIAGRAMAS_UML.md)** - 8 diagramas UML (classes, sequência, estados, componentes, deployment)
- **[docs/COMPARACAO_TRABALHO1_VS_TRABALHO2.md](docs/COMPARACAO_TRABALHO1_VS_TRABALHO2.md)** - Análise comparativa detalhada entre negociação e aprendizado

### Validação e Conformidade
- **[docs/RELATORIO_TESTES.md](docs/RELATORIO_TESTES.md)** - Relatório de validação (28/28 testes passaram)
- **[docs/CONFORMIDADE_TRABALHO02.md](docs/CONFORMIDADE_TRABALHO02.md)** - Checklist de conformidade com requisitos do trabalho

### Documentação Acadêmica
- **[docs/ARTIGO_SBC.md](docs/ARTIGO_SBC.md)** - Artigo em formato SBC (template para LaTeX)
- **[docs/APRESENTACAO_SLIDES.md](docs/APRESENTACAO_SLIDES.md)** - Apresentação de slides (30 slides, conversível para Marp/reveal.js)

### Desenvolvimento
- **[docs/dificuldades_encontradas.md](docs/dificuldades_encontradas.md)** - Registro de problemas encontrados e soluções implementadas

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
| Visualização | Logs textuais | 11 tipos de gráficos (5 individuais + 6 comparativos) |
| Análise | Manual | Sistema automatizado de análise comparativa |
| Resultados | Pasta única | Organizados por timestamp + análise consolidada |

---

## Histórico de Versões

### v1.1 (2025-12-05) - ATUAL
- Sistema de análise comparativa avançada (AnalisadorComparativo)
- 6 novos tipos de gráficos comparativos
- Heatmap de métricas normalizadas
- Relatório comparativo automatizado
- Exportação de ranking JSON e CSV consolidado
- Documentação README_ANALISE_COMPARATIVA.md
- Script de teste do sistema de análise
- Requirements separado para análise avançada

### v1.0 (2025-11-30)
- Implementação completa de Q-Learning
- 10 cenários de teste
- Função de utilidade PEAS
- Metodologia SART documentada
- Sistema de organização por timestamp
- 5 tipos de gráficos matplotlib
- Testes automatizados
- ScenarioComparator para análise básica

---

## Autores

- Guilherme T. S. Abreu - guiabr@alunos.utfpr.com.br
- Maria Eduarda S. Freitas - mariaeduardafreitas@alunos.utfpr.edu.br
