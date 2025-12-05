# Sistema Multi-Agentes com Aprendizado por Reforço para Gerenciamento de Travessias em Cruzamentos Viários

**Trabalhos 01 e 02 - Sistemas Multi-Agentes 2025.2**
**UTFPR - Campus Ponta Grossa - COCIC**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![MASPY](https://img.shields.io/badge/MASPY-2025.11.9-green.svg)](https://github.com/laca-is/MASPY)
[![Status](https://img.shields.io/badge/Status-Completo-success.svg)]()

---

## Descrição

Sistema multi-agentes para coordenação de veículos em cruzamento implementado com MASPY, apresentando duas abordagens:

**Trabalho 01 - Negociação:** Protocolo de negociação baseado em prioridades com arquitetura BDI.

**Trabalho 02 - Aprendizado:** Q-Learning para aprender política ótima de travessia.

---

## Navegação Rápida

### Trabalhos
- **[Trabalho 01 - Negociação](Trabalho_01_Negociacao/)** - Sistema de negociação BDI
- **[Trabalho 02 - Q-Learning](Trabalho_02_Aprendizado/)** - Sistema de aprendizado por reforço

### Documentação Trabalho 02
- [PEAS](Trabalho_02_Aprendizado/docs/PEAS.md) - Metodologia PEAS completa
- [SART](Trabalho_02_Aprendizado/docs/SART.md) - Metodologia SART completa
- [Diagramas UML](Trabalho_02_Aprendizado/docs/DIAGRAMAS_UML.md) - 9 diagramas + autômato
- [Comparação T1 vs T2](Trabalho_02_Aprendizado/docs/COMPARACAO_TRABALHO1_VS_TRABALHO2.md) - Análise comparativa
- [Relatório de Testes](Trabalho_02_Aprendizado/docs/RELATORIO_TESTES.md) - 28/28 testes passaram
- [Dificuldades Encontradas](Trabalho_02_Aprendizado/docs/dificuldades_encontradas.md) - Problemas e soluções

---

## Estrutura do Projeto

```
MASPY_cruzamento/
├── Trabalho_01_Negociacao/         # Trabalho 01 - Negociação
│   ├── cruzamento_maspy_v3.py      # Sistema principal (RECOMENDADO)
│   ├── experiments/                # Suite de experimentos
│   └── resultados/                 # Resultados por timestamp
│
├── Trabalho_02_Aprendizado/        # Trabalho 02 - Q-Learning
│   ├── cruzamento_maspy_learning.py   # Sistema principal
│   ├── executar_todos_cenarios.py     # Executor batch
│   ├── comparar_cenarios.py           # Comparador
│   ├── executar_testes.py             # Suite de 28 testes
│   ├── docs/                          # Documentação completa
│   └── resultados/                    # Resultados + gráficos
│
└── venv_maspy/                     # Ambiente virtual
```

---

## Experimentos

### Trabalho 01 - Negociação (6 cenários)

| Cenário | Veículos | Objetivo |
|---------|----------|----------|
| Base | 4 | Validar priorização de emergência |
| Múltiplas Emergências | 4 | Desempate entre emergências |
| Prioridades Iguais | 4 | Comportamento em empate |
| Cargas Pesadas | 4 | Priorização de veículos grandes |
| Misto | 6 | Teste com diversidade |
| Estresse | 10 | Avaliar escalabilidade |

### Trabalho 02 - Aprendizado (10 cenários)

| Cenário | Veículos | Descrição |
|---------|----------|-----------|
| padrao | 10 | Veículos diversos |
| base | 10 | Ambulância vs normais |
| emergencias | 10 | Múltiplas emergências |
| iguais | 10 | Prioridades iguais |
| pesados | 10 | Cargas pesadas |
| transporte_publico | 10 | Ônibus e táxis |
| prioridades_proximas | 10 | Diferenças pequenas |
| extremos | 10 | Prioridades extremas (10 e 100) |
| escalonado | 10 | Escala uniforme 10-100 |
| misto_complexo | 10 | Mix de todos os tipos |

---

## Como Executar

### Pré-requisitos

```bash
# Ativar ambiente virtual
source venv_maspy/bin/activate

# Verificar instalação
python -c "import maspy; print('MASPY OK')"

# Instalar dependências opcionais (Trabalho 02)
pip install matplotlib numpy
```

### Trabalho 01 - Negociação

```bash
cd Trabalho_01_Negociacao

# Coletar dados (RECOMENDADO)
./scripts/coletar_dados_v3.sh

# Ou executar experimentos
python experiments/experimentos_cruzamento_v3.py

# Ou executar sistema principal
python cruzamento_maspy_v3.py
```

### Trabalho 02 - Aprendizado

```bash
cd Trabalho_02_Aprendizado

# Execução padrão
python cruzamento_maspy_learning.py

# Cenário específico
python cruzamento_maspy_learning.py --experimento base

# Configurar parâmetros
python cruzamento_maspy_learning.py --episodios 200 --quiet

# Comparar cenários
python comparar_cenarios.py --cenarios base emergencias pesados

# Executar testes
python executar_testes.py
```

**Parâmetros disponíveis (Trabalho 02):**
- `--experimento` - Nome do cenário
- `--episodios` - Número de episódios (default: 100)
- `--reward` - Recompensa por acerto (default: 100)
- `--penalidade` - Multiplicador de penalidade (default: 1.5)
- `--quiet` - Modo silencioso
- `--step` - Modo step-by-step

---

## Arquitetura

### Trabalho 01 - Negociação

**Agentes:**
- **VeiculoAgent:** Envia proposta com prioridade
- **CoordenadorAgent:** Decide vencedor (maior prioridade)

**Ambiente:**
- **CruzamentoEnvironment:** Gerencia estado do cruzamento

**Protocolo:**
1. Veículos enviam propostas
2. Coordenador coleta todas
3. Decide por maior prioridade (FIFO em empate)
4. Notifica vencedor e perdedores

### Trabalho 02 - Aprendizado

**Agentes:**
- **CoordenadorLearningAgent:** Aprende política ótima via Q-Learning
- **VeiculoLearningAgent:** Observa e registra estatísticas

**Ambiente:**
- **CruzamentoLearningEnvironment:** SART (States, Actions, Rewards, Transitions)

**Sistemas de Suporte:**
- **MetricsCollector:** Coleta 15+ métricas, detecta convergência, gera 5 gráficos
- **ScenarioComparator:** Compara cenários e identifica melhor configuração

**Metodologias:**
- **PEAS:** Performance, Environment, Actuators, Sensors
- **SART:** States, Actions, Rewards, Transitions

---

## Tecnologias

- **Linguagem:** Python 3.13
- **Framework:** MASPY 2025.11.9
- **Paradigma:** BDI (Trabalho 01) / BDI + Reinforcement Learning (Trabalho 02)
- **Bibliotecas:** matplotlib, numpy (opcional), csv, argparse

---

## Níveis de Prioridade

| Tipo | Prioridade | Justificativa |
|------|------------|---------------|
| Ambulância | 100 | Emergência médica |
| Bombeiros | 95-98 | Emergência (incêndio/resgate) |
| Caminhão | 50 | Veículo grande |
| Ônibus | 30-40 | Transporte coletivo |
| Táxi | 20 | Transporte de passageiros |
| Carro | 10-15 | Veículo comum |
| Moto | 5 | Veículo ágil |

---

## Validação

**Trabalho 01:**
- 6/6 experimentos validados (100%)
- Sistema de logging configurável (SILENT, ERROR, INFO, DEBUG)
- Logs 90% mais limpos que v2

**Trabalho 02:**
- 28/28 testes automatizados (100%)
- Função de utilidade PEAS implementada
- Detecção automática de convergência
- 5 tipos de gráficos matplotlib
- Exportação CSV estruturada

---

## Autores

- **Guilherme T. S. Abreu** - guiabr@alunos.utfpr.com.br
- **Maria Eduarda S. Freitas** - mariaeduardafreitas@alunos.utfpr.edu.br

**Professor:** Gleifer Vaz Alves

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
