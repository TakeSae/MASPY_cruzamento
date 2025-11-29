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
├── cruzamento_maspy_v3.py          # Sistema principal (RECOMENDADO)
├── experimentos_cruzamento_v3.py   # Suite de experimentos v3
├── coletar_dados_v3.sh             # Script de coleta v3
│
├── cruzamento_maspy_v2.py          # Sistema v2 (legado)
├── experimentos_cruzamento.py      # Experimentos v2
├── coletar_dados.sh                # Script v2
│
├── run_all_experiments.py          # Executor de experimentos
├── analisar_resultados.py          # Analisador de resultados
│
├── resultados/                     # Resultados organizados por timestamp
│   ├── 20251024_023513/            # Sessão de exemplo
│   │   ├── info_sessao.txt
│   │   ├── resultados_completos.txt
│   │   ├── resumo.txt
│   │   ├── vencedores.txt
│   │   ├── metricas.txt
│   │   └── analise.txt
│   └── ultima_execucao -> 20251024_023513/
│
```

---

## Arquitetura do Sistema

### **Agentes**

#### **1. VeiculoAgent** (Agente Veículo)
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

#### **2. CoordenadorAgent** (Agente Coordenador)
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

### **Ambiente**

#### **CruzamentoEnvironment**
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

## Experimentos Disponíveis

| # | Nome | Veículos | Objetivo | Tempo Médio |
|---|------|----------|----------|-------------|
| 1 | Cenário Base | 4 | Validar priorização de emergência | 1.368s |
| 2 | Múltiplas Emergências | 4 | Desempate entre emergências | 1.367s |
| 3 | Prioridades Iguais | 4 | Comportamento em empate | 1.367s |
| 4 | Cargas Pesadas | 4 | Priorização de veículos grandes | 1.318s |
| 5 | Cenário Misto | 6 | Teste com diversidade | 1.370s |
| 6 | Teste de Estresse | 10 | Avaliar escalabilidade | 1.372s |


---

## Como Executar

### **Pré-requisitos**

```bash
# Ativar ambiente virtual
source venv_maspy/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação do MASPY
python -c "import maspy; print('MASPY instalado')"
```

### **Opção 1: Coletar Dados v3 (RECOMENDADO)**

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

### **Opção 2: Executar Bateria de Experimentos**

```bash
# v3 (RECOMENDADO - logs limpos)
python experimentos_cruzamento_v3.py

# v2 (legado - logs completos)
python experimentos_cruzamento.py
```

### **Opção 3: Executar Sistema Principal**

```bash
# v3 (RECOMENDADO)
python cruzamento_maspy_v3.py

# v2 (legado)
python cruzamento_maspy_v2.py
```

### **Opção 4: Executar Experimento Individual**

```bash
# Exemplo: Experimento 1
python -c "from experimentos_cruzamento_v3 import experimento_1_base; experimento_1_base()"
```

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

- **Linguagem:** Python 3.13
- **Framework:** MASPY 2025.06.07 (Multi-Agent System in Python)
- **Paradigma:** BDI (Beliefs, Desires, Intentions)
- **Bibliotecas:** enum, subprocess, time, sys

---

## Documentação

### **Documentação PEAS**

A versão 3 inclui documentação PEAS completa:
- **Performance:** Medidas de desempenho do sistema
- **Environment:** Características do ambiente (Russell & Norvig, 2010)
- **Actuators:** Ações disponíveis aos agentes
- **Sensors:** Percepções dos agentes

Localização: `cruzamento_maspy_v3_analise_PEAS.md`

---

## Autores

- **Guilherme T. S. Abreu** - guiabr@alunos.utfpr.com.br
- **Maria Eduarda S. Freitas** - mariaeduardafreitas@alunos.utfpr.edu.br

**Professor:** Gleifer Vaz Alves

---

## Histórico de Versões

### **v3.0** (2024-10-24) - ATUAL ⭐
- Sistema de LogLevel (SILENT, ERROR, INFO, DEBUG)
- Documentação PEAS completa (~200 linhas)
- Uso efetivo do ambiente (call_env_method)
- Tratamento robusto de erros (try-except)
- Logs 90% mais limpos (20KB → 2KB)
- Performance 20% melhor
- Organização de resultados por timestamp
- Comparação automática v2 vs v3

### **v2.0** (2024-10-20)
- Sistema funcional completo
- 6 experimentos validados
- Protocolo de negociação implementado
- Arquitetura BDI

### **v1.0** (2024-10-17)
- Implementação inicial

