# Metodologia SART - Sistema Multi-Agentes com Q-Learning

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Trabalho 02:** Aprendizado por Reforço
**Autores:** Guilherme T. S. Abreu, Maria Eduarda S. Freitas

---

## Introdução

A metodologia SART (Situation, Agent, Reinforcement learning, Task) é um framework para especificar sistemas multi-agentes que utilizam aprendizado por reforço.

Este documento aplica SART ao nosso sistema de gerenciamento de cruzamento com Q-Learning.

---

## S - Situation (Situação/Problema)

### Descrição do Problema

**Domínio:** Gerenciamento inteligente de cruzamento de veículos em ambiente urbano.

**Desafio:** Determinar a ordem ótima de passagem de veículos no cruzamento respeitando prioridades, mas sem protocolo fixo - o sistema deve **aprender** a política ideal através de experiência.

### Contexto

**Cenário Real:**
- Cruzamento de via única
- Múltiplos veículos chegam simultaneamente
- Veículos têm diferentes prioridades (emergência, carga, transporte público, particular)
- Decisão deve ser rápida e justa

**Problema de Otimização:**
```
Maximizar: Soma de satisfação × prioridade
Sujeito a:
  - Um veículo por vez
  - Ordem fixa após decisão
  - Tempo limitado para decidir
```

### Motivação para Aprendizado

**Por que Q-Learning?**

1. **Adaptabilidade:** Sistema aprende padrões sem programação explícita
2. **Escalabilidade:** Funciona com número variável de veículos
3. **Generalização:** Política aprendida aplica-se a novos cenários
4. **Exploração:** Descobre soluções não óbvias

**Limitações de Abordagens Tradicionais:**
- Protocolos fixos não se adaptam
- Regras manuais não escalam
- Difícil codificar todas as situações

---

## A - Agent (Agentes)

### Arquitetura Multi-Agentes

```
                    ┌─────────────────────────┐
                    │   CoordenadorLearning   │
                    │   (Agente Aprendiz)     │
                    │   - Q-Learning          │
                    │   - Toma Decisões       │
                    └───────────┬─────────────┘
                                │
                   ┌────────────┼────────────┐
                   │            │            │
         ┌─────────▼───┐  ┌────▼──────┐  ┌─▼──────────┐
         │ Veiculo_1   │  │ Veiculo_2 │  │ Veiculo_N  │
         │ (Observador)│  │(Observador)│  │(Observador)│
         └─────────────┘  └───────────┘  └────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  CruzamentoLearning    │
                    │  Environment           │
                    │  - Estados             │
                    │  - Recompensas         │
                    └────────────────────────┘
```

### 1. Agente Coordenador (CoordenadorLearningAgent)

**Tipo:** Agente cognitivo com aprendizado

**Características BDI (Belief-Desire-Intention):**

```python
# Beliefs (Crenças)
- Q-table: {estado: {acao: valor_q}}
- veiculos_disponiveis: Lista de veículos
- prioridades: {veiculo_id: prioridade}

# Desires (Desejos)
- Maximizar recompensa acumulada
- Aprender política ótima

# Intentions (Intenções)
- Escolher veículo com base em Q-table
- Atualizar Q-table com experiência
- Convergir para política ótima
```

**Ciclo de Raciocínio:**
1. Perceber estado atual (veículos disponíveis)
2. Consultar Q-table
3. Escolher ação (ε-greedy implícito)
4. Executar ação
5. Receber recompensa
6. Atualizar Q-table
7. Repetir até convergência

**Propriedades:**
- **Reativo:** Responde a mudanças de estado
- **Proativo:** Busca maximizar recompensa futura
- **Social:** Interage com veículos e ambiente
- **Adaptativo:** Melhora com experiência

### 2. Agentes de Veículo (VeiculoLearningAgent)

**Tipo:** Agente reativo simples (observador passivo)

**Características:**
- Não toma decisões de ordenação
- Registra quando é escolhido
- Mantém estatísticas próprias

**Papel no Sistema:**
- Fornecer informação (prioridade)
- Validar decisões do coordenador
- Coletar métricas individuais

### 3. Ambiente (CruzamentoLearningEnvironment)

**Função:** Mediador e provedor de feedback

**Responsabilidades:**
- Gerenciar estados
- Calcular recompensas
- Validar ações
- Prover interface para Q-Learning (MASPY EnvModel)

---

## R - Reinforcement Learning (Aprendizado por Reforço)

### Técnica Utilizada: Q-Learning

**Definição:** Algoritmo off-policy de diferença temporal para aprender função valor-ação ótima.

### Formulação Matemática

**Função Valor-Ação (Q-function):**
```
Q*(s, a) = valor esperado de recompensa acumulada
           começando no estado s, tomando ação a,
           e seguindo política ótima depois
```

**Equação de Atualização (Bellman):**
```
Q(s_t, a_t) ← Q(s_t, a_t) + α[r_t + γ max_a' Q(s_t+1, a') - Q(s_t, a_t)]

Onde:
- α = taxa de aprendizado (learning rate)
- γ = fator de desconto (discount factor)
- r_t = recompensa imediata
- s_t = estado atual
- a_t = ação tomada
- s_t+1 = próximo estado
- max_a' Q(s_t+1, a') = melhor valor Q no próximo estado
```

### Componentes do Aprendizado

#### 1. Estados (S)

**Representação:**
```python
Estado = (veiculos_restantes, ordem_atual)

Exemplo:
s_0 = {Ambulancia(100), Carro(10), Moto(5)}
s_1 = {Carro(10), Moto(5)}  # após escolher Ambulancia
s_2 = {Moto(5)}             # após escolher Carro
s_3 = {}                    # terminal
```

**Espaço de Estados:**
- Tamanho: 2^N estados possíveis (onde N = número de veículos)
- Exemplo com 10 veículos: até 1024 estados
- Redução: Estados simétricos tratados como equivalentes

#### 2. Ações (A)

**Definição:**
```python
A(s) = {escolher v | v ∈ veiculos_disponiveis(s)}
```

**Espaço de Ações:**
- Varia por estado
- No estado inicial: N ações possíveis
- Diminui conforme veículos são processados

#### 3. Recompensas (R)

**Função de Recompensa:**
```python
R(s, a) = {
    +100                           se escolheu maior prioridade
    -(diferenca_prioridade × 0.2)  se escolheu menor prioridade
}

Onde:
diferenca_prioridade = prioridade_maxima - prioridade_escolhida
```

**Exemplos:**
```
Estado: {Ambulancia(100), Carro(10)}

Ação: escolher Ambulancia → R = +100 ✓
Ação: escolher Carro      → R = -(100-10)×0.2 = -18 ✗
```

**Justificativa:**
- Recompensa positiva incentiva escolha correta
- Penalidade proporcional desencoraja erros graves
- Erros pequenos penalizados menos (aprendizado gradual)

#### 4. Política (π)

**Política Aleatória Inicial:**
```python
π_0(s) = escolher ação aleatória de A(s)
```

**Política Ótima Aprendida:**
```python
π*(s) = argmax_a Q*(s, a)
       = escolher ação com maior valor Q
```

**Convergência:**
```
π_0 → π_1 → π_2 → ... → π*

Onde π* sempre escolhe veículo de maior prioridade
```

#### 5. Hiperparâmetros

**Configuração Padrão (MASPY):**
```python
α (learning_rate) = 0.1     # Taxa de aprendizado
γ (discount_factor) = 0.9   # Fator de desconto
ε (exploration_rate) = 0.1  # Taxa de exploração (ε-greedy)
```

**Ajustes possíveis:**
- α ↑ = aprendizado mais rápido, menos estável
- γ ↑ = valoriza mais recompensas futuras
- ε ↑ = mais exploração, menos exploitação

### Processo de Aprendizado

**Fase 1: Exploração Inicial**
```
Episódios 1-20:
- Alta aleatoriedade
- Descoberta do espaço de estados
- Construção inicial da Q-table
- Taxa de acerto: ~50-70%
```

**Fase 2: Ajuste Fino**
```
Episódios 21-50:
- Menos aleatoriedade
- Refinamento de valores Q
- Política se estabiliza
- Taxa de acerto: ~80-95%
```

**Fase 3: Convergência**
```
Episódios 51+:
- Mínima exploração
- Q-values estáveis
- Política ótima consistente
- Taxa de acerto: ~95-100%
```

### Integração com MASPY

**Framework MASPY-ML:**
```python
from maspy.learning import qlearning, EnvModel

# 1. Criar modelo do ambiente
model = EnvModel.learn_model(
    env=CruzamentoLearningEnvironment,
    num_schedules=2,  # Explorações iniciais
    action_generator=lambda env: env.available_actions()
)

# 2. Executar Q-Learning
model.learn(qlearning, num_episodes=100)

# 3. Política aprendida armazenada em model.q_table
```

**Vantagens da Integração:**
- API simplificada
- Q-table gerenciada automaticamente
- Exploração/Exploitação balanceada
- Compatível com arquitetura BDI

---

## T - Task (Tarefa)

### Objetivo da Tarefa

**Tarefa Principal:**
> Aprender política de ordenação de veículos que maximize satisfação geral (veículos prioritários passam primeiro) sem conhecimento prévio das regras.

### Especificação Formal

**Entrada:**
- N veículos com prioridades {p_1, p_2, ..., p_N}
- Episódios de treinamento: E

**Saída:**
- Política π: S → A
- Taxa de acerto ≥ 95%

**Critério de Sucesso:**
```python
sucesso = (
    taxa_acerto ≥ 0.95 AND
    convergencia_detectada AND
    politica_estavel
)
```

### Decomposição da Tarefa

**1. Treinamento (model.learn)**
- Subtarefa: Explorar espaço de estados
- Subtarefa: Construir Q-table
- Subtarefa: Refinar valores Q
- Duração: E episódios

**2. Validação (episódios de teste)**
- Subtarefa: Aplicar política aprendida
- Subtarefa: Medir desempenho
- Subtarefa: Verificar convergência
- Duração: E episódios (igual ao treinamento)

**3. Coleta de Métricas**
- Subtarefa: Registrar recompensas
- Subtarefa: Calcular taxa de acerto
- Subtarefa: Gerar gráficos
- Duração: Tempo de processamento

### Variações da Tarefa

**Cenários de Teste:**

1. **Simples:** Poucos veículos, prioridades muito diferentes
2. **Médio:** 10 veículos, prioridades variadas
3. **Difícil:** Prioridades muito próximas
4. **Extremo:** Todos com mesma prioridade

**Parâmetros Variáveis:**
- Número de veículos: [2, 5, 10, 15, 20]
- Número de episódios: [50, 100, 200, 500]
- Distribuição de prioridades: uniforme, escalonada, extremos

### Métricas de Avaliação da Tarefa

| Métrica | Fórmula | Meta |
|---------|---------|------|
| Taxa de Acerto | `corretas / total × 100` | ≥ 95% |
| Recompensa Média | `∑r / E` | Próximo ao máximo |
| Episódios p/ Convergência | Primeiro ep com 95% acerto | ≤ 50% de E |
| Tempo de Execução | wall-clock time | ≤ 5s para 10 veículos |
| Estabilidade | std(recompensas últimos 10 eps) | ≤ 5% |

---

## Fluxo Completo SART

```
┌─────────────────────────────────────────────────┐
│ S - SITUATION                                   │
│ Problema: Ordenação ótima de veículos          │
│ Desafio: Sem regras fixas, aprender política   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ A - AGENTS                                      │
│ Coordenador: Aprende política (Q-Learning)      │
│ Veículos: Observam e registram                  │
│ Ambiente: Provê estados e recompensas           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ R - REINFORCEMENT LEARNING                      │
│ Técnica: Q-Learning (off-policy TD)             │
│ Equação: Q(s,a) ← Q + α[r + γ max Q(s',a') - Q]│
│ Estados: Conjuntos de veículos disponíveis      │
│ Ações: Escolher próximo veículo                 │
│ Recompensas: +100 correto, -Δp×0.2 incorreto    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ T - TASK                                        │
│ Objetivo: π* que maximiza satisfação            │
│ Sucesso: Taxa acerto ≥ 95%                      │
│ Resultado: Política converge em ≤50 episódios   │
└─────────────────────────────────────────────────┘
```

---

## Comparação: Trabalho 1 vs Trabalho 2

| Aspecto | Trabalho 1 | Trabalho 2 (SART) |
|---------|------------|-------------------|
| **S - Situação** | Negociação com protocolo fixo | Aprendizado de política |
| **A - Agentes** | Coordenador + Veículos negociadores | Coordenador aprendiz + Veículos observadores |
| **R - Aprendizado** | N/A (sem aprendizado) | Q-Learning (reforço) |
| **T - Tarefa** | Ordenar segundo regras | Descobrir regras ótimas |
| **Adaptabilidade** | Nula (regras fixas) | Alta (aprende/adapta) |
| **Desempenho Inicial** | 100% (conhece regras) | ~50% (aleatório) |
| **Desempenho Final** | 100% (constante) | ~100% (aprendido) |

---

## Conclusão

A metodologia SART demonstra que nosso sistema:

1. **S:** Enfrenta problema real de otimização sem solução codificada
2. **A:** Arquitetura multi-agentes bem definida com papéis claros
3. **R:** Implementa Q-Learning corretamente com todos os componentes necessários
4. **T:** Tarefa mensurável com critérios claros de sucesso

O framework SART valida que o sistema atende aos requisitos de aprendizado por reforço em sistemas multi-agentes, demonstrando capacidade de aprender política ótima através de experiência.

---

**Data:** 04/12/2025
**Versão:** 1.0
