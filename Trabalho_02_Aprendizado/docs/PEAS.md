# Metodologia PEAS - Sistema Multi-Agentes de Cruzamento com Q-Learning

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Trabalho 02:** Aprendizado por Reforço
**Autores:** Guilherme T. S. Abreu, Maria Eduarda S. Freitas

---

## Introdução

A metodologia PEAS (Performance, Environment, Actuators, Sensors) é utilizada para especificar completamente um agente inteligente, definindo seus objetivos, contexto de operação, capacidades de ação e percepção.

Este documento aplica PEAS ao nosso Sistema Multi-Agentes de gerenciamento de cruzamento com aprendizado por reforço (Q-Learning).

---

## PEAS - Agente Coordenador (CoordenadorLearningAgent)

### P - Performance (Medida de Desempenho)

**Objetivo:** Aprender a política ótima de ordenação de veículos baseada em prioridades.

**Métricas de Desempenho:**

1. **Taxa de Acerto:**
   - Porcentagem de escolhas corretas (veículo de maior prioridade)
   - Meta: ≥ 95% após convergência
   - Cálculo: `acertos / (acertos + erros) × 100`

2. **Recompensa Acumulada:**
   - Soma total de recompensas ao longo dos episódios
   - Recompensa por acerto: +100
   - Penalidade por erro: -(diferença de prioridade × 0.2)

3. **Convergência:**
   - Número de episódios até atingir 95% de acerto consistente
   - Média móvel (janela=10) de recompensas estável

4. **Tempo de Aprendizado:**
   - Tempo total para completar N episódios de treinamento
   - Eficiência computacional

**Função de Utilidade:**
```python
U(episodio) = (recompensa_acumulada / recompensa_maxima_possivel) × 100

Onde:
- recompensa_maxima_possivel = num_veiculos × recompensa_correta × episodio
- Valor ideal: U(episodio) → 100% após convergência
```

### E - Environment (Ambiente)

**Tipo de Ambiente:** `CruzamentoLearningEnvironment`

**Características:**

| Propriedade | Classificação | Justificativa |
|-------------|--------------|---------------|
| **Observabilidade** | Totalmente Observável | Agente tem acesso completo ao estado (prioridades de todos os veículos) |
| **Agentes** | Multi-Agente | Coordenador + múltiplos agentes de veículos |
| **Determinismo** | Determinístico | Mesmas ações no mesmo estado produzem mesmo resultado |
| **Episodicidade** | Episódico | Cada episódio é independente (resetado ao final) |
| **Dinamicidade** | Estático | Ambiente não muda enquanto agente decide |
| **Continuidade** | Discreto | Estados e ações são discretos (ordem finita de veículos) |
| **Conhecimento** | Conhecido | Regras do ambiente são conhecidas (prioridades) |

**Estados do Ambiente:**
- Estado = tupla de veículos ainda não processados
- Estado inicial: todos os veículos disponíveis
- Estado terminal: nenhum veículo disponível

**Dinâmica:**
```
Estado(t) → Ação(t) → Recompensa(t) → Estado(t+1)

Exemplo:
[Ambulancia(100), Carro(10), Moto(5)]
    → escolhe Ambulancia
    → +100 recompensa
    → [Carro(10), Moto(5)]
```

### A - Actuators (Atuadores)

**Ações Disponíveis:**

1. **Escolher Veículo:**
   - Ação: `escolher_veiculo(veiculo_id)`
   - Efeito: Define ordem de passagem no cruzamento
   - Espaço de ação: Conjunto de veículos disponíveis no estado atual

2. **Atualizar Q-Table:**
   - Ação interna: `atualizar_q(estado, acao, recompensa, proximo_estado)`
   - Efeito: Modifica valores Q baseado em experiência
   - Equação: `Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]`

3. **Exploração vs Exploitação:**
   - Ação: escolher estratégia (ε-greedy implícito no MASPY)
   - Exploração: testar ações aleatórias
   - Exploitação: usar melhor ação conhecida

**Efeitos das Ações:**
- Alteram o estado do ambiente (removem veículo da fila)
- Geram recompensa/penalidade
- Atualizam conhecimento (Q-table)
- Influenciam decisões futuras

### S - Sensors (Sensores)

**Percepções Disponíveis:**

1. **Estado Atual:**
   - Sensor: `perceber_veiculos_disponiveis()`
   - Retorna: Lista de veículos ainda na fila
   - Informação: `{veiculo_id: prioridade}`

2. **Prioridades:**
   - Sensor: `obter_prioridade(veiculo_id)`
   - Retorna: Valor numérico [1-100]
   - Sempre disponível e preciso

3. **Recompensa:**
   - Sensor: `receber_recompensa()`
   - Retorna: Valor numérico (positivo ou negativo)
   - Feedback após cada ação

4. **Histórico:**
   - Sensor: `consultar_q_table(estado, acao)`
   - Retorna: Valor Q aprendido
   - Memória de experiências passadas

**Ruído e Incerteza:**
- Sensores são precisos (sem ruído)
- Informação sempre disponível
- Sem percepções parciais ou ocultas

---

## PEAS - Agente de Veículo (VeiculoLearningAgent)

### P - Performance (Medida de Desempenho)

**Objetivo:** Observar e registrar o processo de aprendizado do coordenador.

**Métricas:**
- Número de vezes que foi escolhido
- Recompensa quando escolhido
- Estatísticas de sucesso/falha

*Nota: Veículos são observadores passivos, não têm objetivo de desempenho ativo.*

### E - Environment (Ambiente)

**Mesmo ambiente:** `CruzamentoLearningEnvironment`

**Papel diferente:**
- Não modifica o ambiente
- Apenas observa o estado

### A - Actuators (Atuadores)

**Ações Limitadas:**
- Registrar observação
- Atualizar beliefs internos
- **Não toma decisões de ordenação**

### S - Sensors (Sensores)

**Percepções:**
- Próprio status (aguardando/processado)
- Notificação quando escolhido
- Recompensa recebida (quando aplicável)

---

## Análise de Desempenho do Sistema

### Função de Utilidade Global

```python
U_sistema = (
    0.5 × taxa_acerto_final +
    0.3 × (1 - episodios_convergencia / episodios_totais) +
    0.2 × eficiencia_computacional
)

Onde:
- taxa_acerto_final ∈ [0, 1]
- episodios_convergencia = episódio onde atingiu 95% acerto
- eficiencia_computacional = 1 / tempo_execucao_normalizado
```

### Resultados Esperados

**Cenários Simples** (2-4 veículos, prioridades distintas):
- Taxa de acerto: 100%
- Convergência: < 10 episódios
- Tempo: < 1s

**Cenários Médios** (10 veículos, prioridades variadas):
- Taxa de acerto: ≥ 98%
- Convergência: 10-50 episódios
- Tempo: 1-3s

**Cenários Complexos** (10 veículos, prioridades próximas):
- Taxa de acerto: ≥ 95%
- Convergência: 50-100 episódios
- Tempo: 3-5s

### Comparação com Trabalho 1

| Aspecto | Trabalho 1 (Negociação) | Trabalho 2 (Q-Learning) |
|---------|------------------------|------------------------|
| **Decisão** | Protocolo fixo | Política aprendida |
| **Adaptação** | Não adaptativo | Aprende com experiência |
| **Desempenho inicial** | 100% (regras corretas) | ~50% (aleátorio) |
| **Desempenho final** | 100% (constante) | ~100% (após treino) |
| **Escalabilidade** | Linear | Melhora com treino |
| **Flexibilidade** | Baixa | Alta (ajusta-se) |

---

## Conclusão

A metodologia PEAS demonstra que nosso sistema:

1. **Performance:** Define métricas claras e mensuráveis
2. **Environment:** Opera em ambiente totalmente observável e determinístico
3. **Actuators:** Possui ações bem definidas que modificam estado
4. **Sensors:** Tem percepção completa e precisa do ambiente

A função de utilidade permite quantificar o sucesso do aprendizado, demonstrando que Q-Learning é efetivo para este domínio de aplicação.

---

**Data:** 04/12/2025
**Versão:** 1.0
