# Sistema Multi-Agentes de Negociação em Cruzamento

**Trabalhos 01 e 02 - Sistemas Multi-Agentes 2025.2**
**UTFPR - Campus Ponta Grossa - COCIC**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![MASPY](https://img.shields.io/badge/MASPY-2025.06.07-green.svg)](https://github.com/laca-is/MASPY)
[![Status](https://img.shields.io/badge/Status-Completo-success.svg)]()

---

## Descrição

Sistema multi-agentes que combina negociação e aprendizado por reforço (Q-Learning) para coordenação de veículos autônomos em cruzamento. Implementado com framework MASPY, apresenta duas vertentes principais:

**Trabalho 01 - Sistema de Negociação:**
- Protocolo de negociação centralizado baseado em prioridades
- Arquitetura BDI completa (Beliefs, Desires, Intentions)
- Sistema de logging configurável (SILENT, ERROR, INFO, DEBUG)
- Documentação PEAS integrada ao código
- 6 experimentos validados (taxa de sucesso: 100%)

**Trabalho 02 - Sistema de Aprendizado:**
- Aprendizado por reforço com Q-Learning
- 2 tipos de agentes (Coordenador + Veículo)
- 11 instâncias de agentes (1 coordenador + 10 veículos)
- 10 cenários de teste diferentes
- Metodologias PEAS e SART documentadas
- Função de utilidade para avaliação
- Análise estatística completa (desvio padrão, média móvel)
- Visualização gráfica com 5 tipos de gráficos
- Sistema de comparação entre cenários
- Taxa de sucesso dos testes: 100% (28/28 testes)

---

## Estrutura do Projeto

```
MASPY_cruzamento/
├── Trabalho 01 - Sistema de Negociacao/
│   ├── cruzamento_maspy_v3.py          # Sistema principal (RECOMENDADO)
│   ├── experimentos_cruzamento_v3.py   # Suite de experimentos v3
│   ├── coletar_dados_v3.sh             # Script de coleta v3
│   ├── cruzamento_maspy_v2.py          # Sistema v2 (legado)
│   ├── experimentos_cruzamento.py      # Experimentos v2
│   ├── coletar_dados.sh                # Script v2
│   ├── run_all_experiments.py          # Executor de experimentos
│   ├── analisar_resultados.py          # Analisador de resultados
│   └── resultados/                     # Resultados organizados por timestamp
│
├── Trabalho 02 - Sistema de Aprendizado (MASPY_learning)/
│   ├── cruzamento_maspy_learning.py    # Sistema Q-Learning (PRINCIPAL)
│   ├── comparar_cenarios.py            # Comparador de cenarios
│   ├── executar_testes.py              # Suite de testes automatizados
│   ├── README_MELHORIAS.md             # Documentacao detalhada
│   ├── RELATORIO_TESTES.md             # Relatorio de validacao
│   ├── metricas_aprendizado.csv        # Metricas exportadas
│   └── graficos/                       # Visualizacoes geradas
│       ├── recompensa_por_episodio.png
│       ├── recompensa_acumulada.png
│       ├── media_movel.png
│       ├── comparacao_desempenho.png
│       └── analise_convergencia.png
│
```

---

## Arquitetura do Sistema

### **Trabalho 01 - Sistema de Negociacao**

#### **Agentes**

**1. VeiculoAgent** (Agente Veículo)
Representa um veículo que participa da negociação.

**Arquitetura BDI:**
- **Beliefs (Crenças):** `tipo`, `prioridade`, `Belief("decisao", vencedor)`
- **Desires/Goals (Objetivos):** `Goal("atravessar")`
- **Intentions/Plans (Planos):**
  - `enviar_proposta()` - Envia proposta ao coordenador
  - `receber_decisao()` - Processa resultado da negociação

**Atributos:**
- `tipo`: String (carro, ambulancia, onibus, moto, caminhao, etc.)
- `prioridade`: Int (0-100, quanto maior mais urgente)
- `coordenador`: String (nome do agente coordenador)
- `log_level`: LogLevel (SILENT, ERROR, INFO, DEBUG)

**2. CoordenadorAgent** (Agente Coordenador)
Gerencia o processo de negociação.

**Arquitetura BDI:**
- **Beliefs (Crenças):** `Belief("proposta", dados)` (múltiplas instâncias)
- **Desires/Goals (Objetivos):** `Goal("decidir")`
- **Intentions/Plans (Planos):**
  - `coletar_propostas()` - Recebe e armazena propostas
  - `decidir_vencedor()` - Avalia prioridades e decide

**Algoritmo de decisão:**
```python
vencedor = max(propostas, key=lambda p: p['prio'])
```
Em caso de empate: ordem de processamento (FIFO)

#### **Ambiente**

**CruzamentoEnvironment**
Representa o cruzamento físico de 4 vias.

**Estado:**
- `cruzamento_livre`: Boolean (indica disponibilidade)
- `veiculos_aguardando`: List[Dict] (fila de veículos)
- `veiculo_atravessando`: String (ID do veículo atual)
- `historico_travessias`: List[String] (histórico completo)

**Métodos:**
- `registrar_chegada()` - Registra veículo no cruzamento
- `iniciar_travessia()` - Marca início da travessia
- `finalizar_travessia()` - Libera o cruzamento

---

### **Trabalho 02 - Sistema de Aprendizado**

#### **Agentes**

**1. CoordenadorLearningAgent** (Agente Coordenador com Q-Learning)
Agente que aprende a política ótima de escolha de veículos usando Q-Learning.

**Arquitetura BDI:**
- **Beliefs:** `status`, `episodio_atual`, `recompensa_total`
- **Goals:** `Goal("aprender")`
- **Plans:** `iniciar_aprendizado()` - Executa Q-Learning via EnvModel

**Parâmetros de Aprendizado:**
- `num_episodes`: Número de episódios de treinamento (default: 100)
- `reward_correto`: Recompensa por escolha ótima (+100)
- `penalidade_multiplicador`: Fator de penalização por erro (1.5)

**2. VeiculoLearningAgent** (Agente Veículo que Aprende)
Observa o processo de aprendizado e registra estatísticas.

**Arquitetura BDI:**
- **Beliefs:** `veiculo_id`, `prioridade`, `status`, `tentativas`, `sucessos`, `falhas`
- **Goals:** `Goal("observar_cruzamento")`
- **Plans:** `monitorar_ambiente()` - Observa passivamente

**Métricas Coletadas:**
- Histórico de ações (escolhido/não escolhido)
- Recompensa acumulada individual
- Taxa de sucesso/falha

#### **Ambiente**

**CruzamentoLearningEnvironment**
Ambiente de aprendizado por reforço (SART).

**Estados (States):**
- `v{N}_passou`: Boolean para cada veículo (1-10)
- Estado inicial: todos em 0 (aguardando)
- Estado terminal: todos em 1 (atravessaram)

**Ações (Actions):**
- `escolher_veiculo(id)`: Seleciona veículo para atravessar

**Recompensas (Rewards):**
- Escolha ótima (maior prioridade): +100
- Escolha subótima: penalidade proporcional à diferença

**Transições (Transitions):**
- Determinísticas: escolher veículo → marca como atravessado

#### **Sistemas de Suporte**

**MetricsCollector**
Sistema centralizado para coleta de métricas de aprendizado.

**Funcionalidades:**
- Registra recompensas por episódio
- Calcula função de utilidade (PEAS)
- Detecta convergência automaticamente
- Gera relatórios estatísticos completos
- Exporta dados para CSV
- Cria 5 tipos de gráficos matplotlib

**ScenarioComparator**
Sistema para comparação entre cenários de teste.

**Funcionalidades:**
- Compara múltiplos cenários simultaneamente
- Identifica melhor configuração
- Gera relatórios comparativos
- Exporta comparações para CSV
- Cria gráficos comparativos

---

## Experimentos Disponíveis

### **Trabalho 01 - Negociacao (6 cenarios)**

| # | Nome | Veículos | Objetivo | Tempo Médio |
|---|------|----------|----------|-------------|
| 1 | Cenário Base | 4 | Validar priorização de emergência | 1.368s |
| 2 | Múltiplas Emergências | 4 | Desempate entre emergências | 1.367s |
| 3 | Prioridades Iguais | 4 | Comportamento em empate | 1.367s |
| 4 | Cargas Pesadas | 4 | Priorização de veículos grandes | 1.318s |
| 5 | Cenário Misto | 6 | Teste com diversidade | 1.370s |
| 6 | Teste de Estresse | 10 | Avaliar escalabilidade | 1.372s |

### **Trabalho 02 - Aprendizado (10 cenarios)**

| # | Nome | Descrição | Veículos |
|---|------|-----------|----------|
| 1 | padrao | 10 veículos diversos | 10 |
| 2 | base | Ambulância vs veículos normais | 4 |
| 3 | emergencias | Múltiplas emergências (ambulância, bombeiros, polícia) | 4 |
| 4 | iguais | Prioridades iguais (desempate) | 4 |
| 5 | pesados | Cargas pesadas (caminhões) | 4 |
| 6 | transporte_publico | Ônibus, táxi, van | 6 |
| 7 | prioridades_proximas | Diferenças pequenas (10-20) | 5 |
| 8 | extremos | Diferenças grandes (1 vs 100) | 2 |
| 9 | dois_veiculos | Caso mínimo | 2 |
| 10 | tres_veiculos | Caso intermediário | 3 |

---

## Como Executar

### **Pré-requisitos**

```bash
# Ativar ambiente virtual
source venv_maspy/bin/activate

# Instalar dependências básicas
pip install -r requirements.txt

# Verificar instalação do MASPY
python -c "import maspy; print('MASPY instalado')"

# Instalar dependências opcionais para visualização (Trabalho 02)
pip install matplotlib numpy
```

---

### **Trabalho 01 - Sistema de Negociacao**

#### **Opção 1: Coletar Dados v3 (RECOMENDADO)**

```bash
./coletar_dados_v3.sh
```

**Gera automaticamente:**
- Pasta `resultados/YYYYMMDD_HHMMSS/` organizada
- `info_sessao.txt` - Metadados da sessão
- `resultados_completos.txt` - Log completo (90% mais limpo que v2)
- `resumo.txt` - Resumo dos experimentos
- `vencedores.txt` - Lista de vencedores
- `metricas.txt` - Tempos de execução
- `analise.txt` - Análise estatística
- `comparacao_v2_v3.txt` - Comparação de performance

**Visualizar resultados:**
```bash
cat resultados/ultima_execucao/resumo.txt
cat resultados/ultima_execucao/metricas.txt
cat resultados/ultima_execucao/vencedores.txt
```

#### **Opção 2: Executar Bateria de Experimentos**

```bash
# v3 (RECOMENDADO - logs limpos)
python experimentos_cruzamento_v3.py

# v2 (legado - logs completos)
python experimentos_cruzamento.py
```

#### **Opção 3: Executar Sistema Principal**

```bash
# v3 (RECOMENDADO)
python cruzamento_maspy_v3.py

# v2 (legado)
python cruzamento_maspy_v2.py
```

#### **Opção 4: Executar Experimento Individual**

```bash
# Exemplo: Experimento 1
python -c "from experimentos_cruzamento_v3 import experimento_1_base; experimento_1_base()"
```

---

### **Trabalho 02 - Sistema de Aprendizado Q-Learning**

#### **Opção 1: Executar com cenário padrão (RECOMENDADO)**

```bash
cd MASPY_learning
python cruzamento_maspy_learning.py
```

**Saída gerada:**
- Relatório de métricas no terminal
- `metricas_aprendizado.csv` - Dados exportados
- `graficos/` - 5 visualizações PNG

#### **Opção 2: Executar cenário específico**

```bash
cd MASPY_learning

# Exemplos de cenários disponíveis:
python cruzamento_maspy_learning.py --experimento base
python cruzamento_maspy_learning.py --experimento emergencias
python cruzamento_maspy_learning.py --experimento pesados
python cruzamento_maspy_learning.py --experimento extremos
```

#### **Opção 3: Configurar parâmetros de treinamento**

```bash
cd MASPY_learning

# Alterar número de episódios (default: 100)
python cruzamento_maspy_learning.py --episodios 200

# Modo silencioso (sem logs detalhados)
python cruzamento_maspy_learning.py --quiet

# Modo step-by-step (para debugging)
python cruzamento_maspy_learning.py --step

# Combinação de parâmetros
python cruzamento_maspy_learning.py --experimento base --episodios 150 --reward 200
```

**Parâmetros disponíveis:**
- `--experimento`: Nome do cenário (padrao, base, emergencias, etc.)
- `--episodios`: Número de episódios de treinamento (default: 100)
- `--reward`: Recompensa por escolha correta (default: 100)
- `--penalidade`: Multiplicador de penalidade (default: 1.5)
- `--quiet`: Modo silencioso (sem logs verbose)
- `--step`: Modo step-by-step para debugging

#### **Opção 4: Comparar múltiplos cenários**

```bash
cd MASPY_learning

# Comparar cenários específicos
python comparar_cenarios.py --cenarios base emergencias pesados --episodios 100

# Comparar TODOS os cenários
python comparar_cenarios.py --cenarios todos --episodios 100

# Modo verbose (mostrar logs detalhados)
python comparar_cenarios.py --cenarios todos --verbose
```

**Saída gerada pelo comparador:**
- Relatórios individuais de cada cenário
- Relatório comparativo final
- Métricas agregadas em CSV
- Gráficos comparativos

#### **Opção 5: Executar suite de testes**

```bash
cd MASPY_learning

# Executar todos os 28 testes
python executar_testes.py
```

**Validações realizadas:**
- Sintaxe Python
- Imports e dependências
- MetricsCollector
- Função de utilidade
- Cálculos estatísticos
- Documentação PEAS/SART
- Cenários de experimento
- Exportação CSV
- Matplotlib (se disponível)

---

## Sistema de Logging (v3)

A v3 introduz níveis de verbosidade configuráveis:

```python
from cruzamento_maspy_v3 import LogLevel

# Níveis disponíveis:
LogLevel.SILENT  # Sem output (benchmarks)
LogLevel.ERROR   # Apenas erros
LogLevel.INFO    # Informações importantes (RECOMENDADO)
LogLevel.DEBUG   # Tudo (modo v2)
```

**Configurar no código:**
```python
GLOBAL_LOG_LEVEL = LogLevel.INFO  # Linha 147
```

**Impacto:**
- Tamanho dos logs: 20KB → 2KB (90% menor)
- Tempo de execução: ~20% mais rápido
- Resultados mais legíveis

---

## Protocolo de Negociação

**Fases do protocolo:**

1. **Inicialização**
   - Veículos chegam e ganham `Goal("atravessar")`

2. **Envio de Propostas**
   - Cada veículo envia `Belief("proposta", {id, tipo, prio})` via `tell`

3. **Coleta**
   - Coordenador recebe e armazena propostas
   - Contador incrementado a cada proposta

4. **Trigger de Decisão**
   - Quando `contador == num_veiculos`, adiciona `Goal("decidir")`

5. **Avaliação**
   - Coordenador busca todas propostas
   - Calcula `max(prioridade)`

6. **Decisão**
   - Seleciona vencedor (maior prioridade)
   - Empate: ordem de processamento (FIFO)

7. **Notificação**
   - Coordenador envia `Belief("decisao", vencedor_id)` via `broadcast`

8. **Reação**
   - Vencedor: atravessa e notifica ambiente
   - Perdedores: aguardam

9. **Finalização**
   - Todos agentes chamam `stop_cycle()`

**Complexidade:** O(n) mensagens (n = número de veículos)

---

## Níveis de Prioridade

| Tipo de Veículo | Prioridade | Justificativa |
|-----------------|------------|---------------|
| **Ambulância** | 100 | Emergência médica (vidas em risco) |
| **Bombeiros** | 95-98 | Emergência (incêndios, resgates) |
| **Caminhão** | 50 | Veículo grande (dificulta tráfego) |
| **Ônibus** | 30-40 | Transporte coletivo |
| **Táxi** | 20 | Transporte de passageiros |
| **Carro** | 10-15 | Veículo comum |
| **Moto** | 5 | Veículo pequeno (mais ágil) |

**Critério de desempate:** Ordem de processamento (FIFO)

---

## Tecnologias

### **Trabalho 01 - Negociacao**
- **Linguagem:** Python 3.13
- **Framework:** MASPY 2025.06.07 (Multi-Agent System in Python)
- **Paradigma:** BDI (Beliefs, Desires, Intentions)
- **Bibliotecas:** enum, subprocess, time, sys

### **Trabalho 02 - Aprendizado**
- **Linguagem:** Python 3.13
- **Framework:** MASPY 2025.06.07 com Q-Learning
- **Paradigma:** BDI + Aprendizado por Reforço
- **Bibliotecas:**
  - Core: argparse, sys, signal, os, enum
  - Visualização: matplotlib, numpy (opcional)
  - Análise: csv (exportação de dados)

---

## Documentação

### **Trabalho 01 - Documentação PEAS**

A versão 3 inclui documentação PEAS completa:
- **Performance:** Medidas de desempenho do sistema
- **Environment:** Características do ambiente (Russell & Norvig, 2010)
- **Actuators:** Ações disponíveis aos agentes
- **Sensors:** Percepções dos agentes

Localização: `cruzamento_maspy_v3_analise_PEAS.md`

### **Trabalho 02 - Documentação PEAS e SART**

A implementação Q-Learning inclui documentação completa integrada ao código:

**PEAS (linhas 181-299 em cruzamento_maspy_learning.py):**
- Performance: Função de utilidade U = α×taxa_acerto + β×convergência + γ×recompensa
- Environment: 10 cenários de teste diferentes
- Actuators: escolher_veiculo(), iniciar_aprendizado()
- Sensors: v{N}_passou (estados observáveis), métricas coletadas

**SART (metodologia de RL):**
- States: Configuração de veículos que ainda não atravessaram
- Actions: Escolha de qual veículo atravessa
- Rewards: +100 por escolha ótima, penalidade proporcional por erro
- Transitions: Determinísticas (escolher → marcar como atravessado)

**Arquivos de documentação:**
- `MASPY_learning/README_MELHORIAS.md` - Documentação completa das 5 melhorias
- `MASPY_learning/RELATORIO_TESTES.md` - Relatório de validação (28 testes)

---

## Tentativas de Interface Gráfica

Durante o desenvolvimento do projeto, foram realizadas tentativas de implementação de interface gráfica para visualização do sistema multi-agentes em tempo real.

**Bibliotecas testadas:**
- **Pygame:** Tentativa de criar visualização 2D do cruzamento com veículos animados
- **Tkinter:** Interface básica para controle de parâmetros e visualização de logs

**Problemas encontrados:**
- Conflito entre loop do MASPY e loop de renderização gráfica
- Dificuldade de sincronização entre ciclos de agentes e frames de animação
- Performance degradada ao adicionar camada gráfica
- Complexidade de manter estado consistente entre agentes e visualização

**Decisão final:**
Optou-se por focar em visualização via gráficos estáticos (matplotlib) ao invés de animação em tempo real, priorizando:
- Análise estatística robusta
- Exportação de dados estruturados (CSV)
- Gráficos de alta qualidade para relatórios
- Melhor performance do sistema de aprendizado

**Visualizações implementadas (Trabalho 02):**
1. Recompensa por episódio (linhas)
2. Recompensa acumulada (crescimento)
3. Média móvel (tendência)
4. Comparação de desempenho (barras)
5. Análise de convergência (regressão linear)

---

## Autores

- **Guilherme T. S. Abreu** - guiabr@alunos.utfpr.com.br
- **Maria Eduarda S. Freitas** - mariaeduardafreitas@alunos.utfpr.edu.br

**Professor:** Gleifer Vaz Alves

---

## Histórico de Versões

### **Trabalho 02 - Sistema de Aprendizado** (2025-11-29) - ATUAL
- Implementação completa de Q-Learning com MASPY
- CoordenadorLearningAgent com aprendizado por reforço
- VeiculoLearningAgent para observação e métricas individuais
- MetricsCollector com 15+ métricas de desempenho
- Função de utilidade PEAS (U = α×acerto + β×convergência + γ×recompensa)
- ScenarioComparator para análise comparativa
- 10 cenários de teste diferentes (2-10 veículos)
- Documentação PEAS completa integrada ao código (linhas 181-299)
- Documentação SART (States, Actions, Rewards, Transitions)
- Sistema de exportação CSV
- 5 tipos de gráficos matplotlib:
  1. Recompensa por episódio
  2. Recompensa acumulada
  3. Média móvel (janela=5)
  4. Comparação de desempenho (barras duplas)
  5. Análise de convergência (regressão linear)
- Análise estatística (desvio padrão, média móvel)
- Detecção automática de convergência
- Comparador de múltiplos cenários (comparar_cenarios.py)
- Suite de 28 testes automatizados (100% sucesso)
- Relatório de validação completo (RELATORIO_TESTES.md)
- Argumentos de linha de comando configuráveis
- Modos de execução: padrão, quiet, step-by-step

### **Trabalho 01 - v3.0** (2024-10-24)
- Sistema de LogLevel (SILENT, ERROR, INFO, DEBUG)
- Documentação PEAS completa (~200 linhas)
- Uso efetivo do ambiente (call_env_method)
- Tratamento robusto de erros (try-except)
- Logs 90% mais limpos (20KB → 2KB)
- Performance 20% melhor
- Organização de resultados por timestamp
- Comparação automática v2 vs v3

### **Trabalho 01 - v2.0** (2024-10-20)
- Sistema funcional completo
- 6 experimentos validados
- Protocolo de negociação implementado
- Arquitetura BDI

### **Trabalho 01 - v1.0** (2024-10-17)
- Implementação inicial

