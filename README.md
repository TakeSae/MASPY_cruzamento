# Sistema Multi-Agentes de Negociação em Cruzamento

Trabalho 1 - Sistemas Multi-Agentes 2025.2
UTFPR - Campus Ponta Grossa - COCIC

## Descrição

Sistema de negociação entre veículos em um cruzamento de 4 vias implementado usando o framework MASPY. O sistema utiliza agentes inteligentes para decidir qual veículo tem prioridade para atravessar o cruzamento.

## Arquivos Principais

- **cruzamento_maspy_v2.py**: Implementação principal do sistema (versão funcional)
- **experimentos_cruzamento.py**: Suite de 6 experimentos diferentes
- **run_all_experiments.py**: Script Python para executar todos os experimentos
- **run_all_experiments.sh**: Script shell para executar todos os experimentos

## Estrutura do Sistema

### Agentes

1. **VeiculoAgent**: Representa um veículo no cruzamento
   - Envia propostas ao coordenador
   - Recebe decisão sobre quem venceu a negociação

2. **CoordenadorAgent**: Gerencia a negociação
   - Coleta propostas de todos os veículos
   - Avalia prioridades
   - Decide o vencedor
   - Notifica todos os veículos

### Ambiente

**CruzamentoEnvironment**: Representa o cruzamento
- Mantém estado (livre/ocupado)
- Registra veículos aguardando
- Gerencia travessias

## Experimentos Disponíveis

### 1. Cenário Base
- 1 ambulância (prioridade 100) vs 3 veículos normais
- **Resultado esperado**: Ambulância vence

### 2. Múltiplas Emergências
- 2 ambulâncias + bombeiros + carro normal
- **Resultado esperado**: Ambulância com maior prioridade vence

### 3. Prioridades Iguais
- 4 carros com mesma prioridade
- **Resultado esperado**: Sistema decide por ordem de processamento

### 4. Cargas Pesadas
- Caminhão vs Ônibus vs Moto vs Carro
- **Resultado esperado**: Caminhão (maior prioridade) vence

### 5. Cenário Misto
- 6 veículos de tipos variados
- **Resultado esperado**: Ambulância vence entre todos

### 6. Teste de Estresse
- 10 veículos simultâneos
- **Resultado esperado**: Sistema suporta carga e decide corretamente

## Como Executar

### Pré-requisitos

```bash
# Ativar ambiente virtual
source venv_maspy/bin/activate

# Verificar instalação do MASPY
python -c "import maspy; print('MASPY instalado com sucesso')"
```

### Opção 1: Coletar Dados com Timestamp (MAIS RECOMENDADO)

```bash
# Executa experimentos e gera arquivos com timestamp automaticamente
./coletar_dados.sh
```

Este script gera automaticamente:
- `resultados_experimentos_AAAAMMDD_HHMMSS.txt` (log completo)
- `resumo_AAAAMMDD_HHMMSS.txt` (resumo)
- `vencedores_AAAAMMDD_HHMMSS.txt` (lista de vencedores)

### Opção 2: Executar Todos os Experimentos

```bash
# Usando script Python
python run_all_experiments.py

# OU usando script shell
./run_all_experiments.sh
```

### Opção 3: Executar Experimento Individual

```bash
# Experimento 1
python -c "from experimentos_cruzamento import experimento_1_base; experimento_1_base()"

# Experimento 2
python -c "from experimentos_cruzamento import experimento_2_multiplas_emergencias; experimento_2_multiplas_emergencias()"

# Experimento 3
python -c "from experimentos_cruzamento import experimento_3_prioridades_iguais; experimento_3_prioridades_iguais()"

# Experimento 4
python -c "from experimentos_cruzamento import experimento_4_cargas_pesadas; experimento_4_cargas_pesadas()"

# Experimento 5
python -c "from experimentos_cruzamento import experimento_5_misto; experimento_5_misto()"

# Experimento 6
python -c "from experimentos_cruzamento import experimento_6_estresse; experimento_6_estresse()"
```

### Opção 4: Executar Sistema Principal

```bash
python cruzamento_maspy_v2.py
```

## Protocolo de Negociação

1. Veículos chegam ao cruzamento e enviam propostas ao Coordenador
2. Coordenador coleta todas as propostas (aguarda todos os veículos)
3. Coordenador avalia propostas por prioridade (maior prioridade vence)
4. Coordenador notifica todos os veículos via broadcast
5. Veículo vencedor atravessa o cruzamento
6. Todos os agentes encerram seus ciclos

## Níveis de Prioridade

- **Ambulância**: 100 (emergência máxima)
- **Bombeiros**: 95-98 (emergência alta)
- **Caminhão**: 50 (carga pesada)
- **Ônibus**: 30-40 (transporte coletivo)
- **Táxi**: 20 (transporte individual prioritário)
- **Carro**: 10-15 (veículo padrão)
- **Moto**: 5 (veículo leve)

## Saída Esperada

Cada experimento mostra:
1. Configuração dos veículos participantes
2. Propostas enviadas por cada veículo
3. Avaliação do coordenador
4. Decisão do vencedor
5. Confirmação de todos os veículos

## Tecnologias

- **Python 3.13**
- **MASPY Framework** (Multi-Agent System in Python)
- **Paradigma BDI** (Beliefs, Desires, Intentions)

## Status

✅ Sistema funcionando corretamente
✅ Todos os 6 experimentos validados
✅ Protocolo de negociação implementado
✅ Agentes seguem arquitetura BDI

## Observações

- Cada experimento roda em um processo Python separado para evitar conflitos no MASPY
- O sistema sempre prioriza veículos de emergência (ambulância, bombeiros)
- Em caso de empate, o primeiro veículo processado vence
- O tempo de execução de todos os experimentos é aproximadamente 20-30 segundos
