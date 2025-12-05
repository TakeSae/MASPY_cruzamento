# Diagramas UML - Sistema Multi-Agentes com Q-Learning

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Trabalho 02:** Aprendizado por Reforço
**Autores:** Guilherme T. S. Abreu, Maria Eduarda S. Freitas

---

## 1. Diagrama de Classes

```mermaid
classDiagram
    class Agent {
        <<abstract>>
        +agt_name: str
        +log_level: int
        +reasoning()
    }

    class Environment {
        <<abstract>>
        +get(percept)
        +set(percept, value)
        +available_actions()
    }

    class EnvModel {
        +q_table: dict
        +learn(algorithm, episodes)
        +get_best_action(state)
        +update_q_value(s, a, r, s_next)
    }

    class LoggableAgent {
        +log_level: int
        +log(message, level)
        +info(message)
        +debug(message)
        +warning(message)
        +error(message)
    }

    class CoordenadorLearningAgent {
        -status: str
        -episodio_atual: int
        -recompensa_total: float
        -num_episodes: int
        -verbose: bool
        +iniciar_aprendizado()
        +escolher_veiculo()
        +reasoning()
    }

    class VeiculoLearningAgent {
        -veiculo_id: str
        -prioridade: int
        -status: str
        -tentativas: int
        -sucessos: int
        -falhas: int
        +observar_cruzamento()
        +registrar_resultado(escolhido, recompensa)
        +reasoning()
    }

    class CruzamentoLearningEnvironment {
        -veiculos_config: list
        -verbose: bool
        -reward_correto: int
        -penalidade_multiplicador: float
        -episodio_atual: int
        -em_treinamento: bool
        +escolher_veiculo1()
        +escolher_veiculo2()
        +escolher_veiculo10()
        +calcular_recompensa(escolhido)
        +available_actions()
        +reset()
    }

    class MetricsCollector {
        -metricas_por_agente: dict
        +registrar_episodio(agente, episodio, recompensa)
        +registrar_acao(agente, correta)
        +calcular_estatisticas()
        +calcular_funcao_utilidade(agente)
        +detectar_convergencia()
        +gerar_relatorio()
        +exportar_csv(caminho)
        +criar_graficos(diretorio)
    }

    class ScenarioComparator {
        -cenarios_executados: list
        +adicionar_cenario(nome, metricas)
        +comparar_todos()
        +identificar_melhor()
        +gerar_relatorio_comparativo()
        +criar_graficos_comparativos()
    }

    Agent <|-- LoggableAgent
    LoggableAgent <|-- CoordenadorLearningAgent
    LoggableAgent <|-- VeiculoLearningAgent
    Environment <|-- CruzamentoLearningEnvironment

    CoordenadorLearningAgent --> EnvModel : usa
    CoordenadorLearningAgent --> MetricsCollector : registra
    VeiculoLearningAgent --> MetricsCollector : registra
    CruzamentoLearningEnvironment --> MetricsCollector : notifica
    MetricsCollector --> ScenarioComparator : alimenta
```

---

## 2. Diagrama de Sequência - Processo de Aprendizado

```mermaid
sequenceDiagram
    participant Main
    participant Coordenador as CoordenadorLearningAgent
    participant Env as CruzamentoLearningEnvironment
    participant Model as EnvModel (Q-Learning)
    participant Metrics as MetricsCollector
    participant Veiculos as VeiculoLearningAgent[1..N]

    Main->>+Env: configurar ambiente
    Main->>+Coordenador: criar agente
    Main->>+Veiculos: criar N veículos

    Note over Main,Veiculos: Fase de Treinamento

    Main->>Coordenador: ativar Goal("aprender")
    activate Coordenador

    Coordenador->>Model: EnvModel.learn_model(env, schedules=2)
    activate Model

    Note over Model: Exploração Inicial (schedules)
    loop Para cada schedule
        Model->>Env: explorar ações aleatórias
        Env-->>Model: estados e recompensas
    end

    Model-->>Coordenador: modelo criado
    deactivate Model

    Coordenador->>Model: model.learn(qlearning, episodes=N)
    activate Model

    Note over Model: Treinamento (N episódios)
    loop Para cada episódio (1 a N)
        Model->>Env: reset()
        Env-->>Model: estado inicial

        loop Até estado terminal
            Model->>Env: escolher_veiculo(id)
            Env->>Env: calcular_recompensa()
            Env-->>Model: recompensa + próximo estado
            Model->>Model: atualizar Q(s,a)
            Model->>Metrics: registrar_episodio()
        end
    end

    Model-->>Coordenador: treinamento completo
    deactivate Model

    Note over Main,Veiculos: Fase de Validação

    loop Para cada episódio de validação
        Coordenador->>Env: reset()
        Env-->>Coordenador: estado inicial

        loop Até estado terminal
            Coordenador->>Model: get_best_action(estado)
            Model-->>Coordenador: melhor ação
            Coordenador->>Env: escolher_veiculo(melhor)
            Env->>Env: calcular_recompensa()
            Env-->>Coordenador: recompensa
            Env->>Veiculos: notificar(escolhido, recompensa)
            Coordenador->>Metrics: registrar_acao()
            Veiculos->>Metrics: registrar_resultado()
        end
    end

    deactivate Coordenador

    Main->>Metrics: gerar_relatorio()
    Metrics-->>Main: relatório completo

    Main->>Metrics: exportar_csv()
    Main->>Metrics: criar_graficos()
```

---

## 3. Diagrama de Sequência - Escolha de Veículo (Decisão)

```mermaid
sequenceDiagram
    participant Coord as CoordenadorLearningAgent
    participant Model as EnvModel (Q-table)
    participant Env as CruzamentoLearningEnvironment
    participant V1 as Veiculo1Agent
    participant V2 as Veiculo2Agent
    participant VN as VeiculoNAgent
    participant Metrics as MetricsCollector

    Note over Coord,Metrics: Estado: [V1, V2, ..., VN] disponíveis

    Coord->>Env: perceber estado atual
    Env-->>Coord: {v1_passou=0, v2_passou=0, ..., vN_passou=0}

    Coord->>Model: consultar Q-table(estado)
    Model->>Model: avaliar Q(s, escolher_V1)
    Model->>Model: avaliar Q(s, escolher_V2)
    Model->>Model: avaliar Q(s, escolher_VN)
    Model-->>Coord: melhor_acao = escolher_V2

    Coord->>Env: escolher_veiculo2()
    activate Env

    Env->>Env: obter prioridade(V2)
    Env->>Env: obter maior_prioridade([V1,V2,...,VN])

    alt Escolha Ótima (V2 tem maior prioridade)
        Env->>Env: recompensa = +100
        Env->>Metrics: registrar_acao(Coord, correta=True)
    else Escolha Subótima
        Env->>Env: diff = maior_prioridade - prioridade(V2)
        Env->>Env: recompensa = -(diff × 0.2)
        Env->>Metrics: registrar_acao(Coord, correta=False)
    end

    Env->>Env: set(v2_passou, 1)
    Env-->>Coord: recompensa
    deactivate Env

    Coord->>V2: notificar(escolhido=True, recompensa)
    V2->>Metrics: registrar_resultado(True, recompensa)

    Coord->>V1: notificar(escolhido=False)
    Coord->>VN: notificar(escolhido=False)

    Coord->>Metrics: registrar_episodio(episodio, recompensa)

    Note over Coord,Metrics: Próximo estado: [V1, V3, ..., VN]
```

---

## 4. Diagrama de Estados - Ciclo de Aprendizado

```mermaid
stateDiagram-v2
    [*] --> Inicializacao

    Inicializacao --> ExploraoInicial: criar ambiente

    ExploraoInicial --> Treinamento: modelo criado
    note right of ExploraoInicial
        Exploração aleatória
        para construir modelo
        (2 schedules)
    end note

    Treinamento --> Treinamento: episódio N
    note right of Treinamento
        Q-Learning:
        Q(s,a) ← Q + α[r + γ max Q(s',a') - Q]

        ε-greedy:
        - exploração aleatória
        - exploitação da política
    end note

    Treinamento --> Validacao: N episódios completos

    Validacao --> Validacao: episódio de teste
    note right of Validacao
        Usar política aprendida
        (sempre melhor ação)

        Sem exploração,
        só exploitação
    end note

    Validacao --> AnalisaConvergencia: todos episódios validados

    AnalisaConvergencia --> Convergiu: taxa acerto ≥ 95%
    AnalisaConvergencia --> NaoConvergiu: taxa acerto < 95%

    Convergiu --> GeraRelatorio
    NaoConvergiu --> GeraRelatorio

    GeraRelatorio --> ExportaDados
    ExportaDados --> CriaGraficos
    CriaGraficos --> [*]

    note left of GeraRelatorio
        Métricas:
        - Recompensa total
        - Taxa de acerto
        - Convergência
        - Função de utilidade
    end note
```

---

## 5. Diagrama de Componentes - Arquitetura do Sistema

```mermaid
graph TB
    subgraph "Interface do Usuário"
        CLI[CLI - cruzamento_maspy_learning.py]
        Args[Argumentos<br/>--experimento<br/>--episodios<br/>--reward<br/>--penalidade]
    end

    subgraph "Camada de Agentes"
        Coord[CoordenadorLearningAgent<br/>Goal: aprender<br/>Plan: iniciar_aprendizado]
        V1[VeiculoLearningAgent 1<br/>Goal: observar<br/>Prioridade: X]
        V2[VeiculoLearningAgent 2]
        VN[VeiculoLearningAgent N]
    end

    subgraph "Camada de Ambiente"
        Env[CruzamentoLearningEnvironment<br/>States: v1_passou...vN_passou<br/>Actions: escolher_veiculo1...N<br/>Rewards: +100 ou penalidade]
    end

    subgraph "Camada de Aprendizado MASPY"
        Model[EnvModel<br/>Q-table<br/>Q-Learning Algorithm]
        QL[qlearning function<br/>Bellman Equation<br/>ε-greedy]
    end

    subgraph "Camada de Análise"
        Metrics[MetricsCollector<br/>Recompensas<br/>Convergência<br/>Utilidade]
        Comp[ScenarioComparator<br/>Comparações<br/>Melhor cenário]
    end

    subgraph "Camada de Saída"
        CSV[metricas_aprendizado.csv]
        Graphs[5 Gráficos PNG]
        Report[Relatório Textual]
        Info[info_execucao.txt]
    end

    CLI --> Args
    Args --> Coord
    Args --> Env

    Coord --> Model
    Coord --> Env

    V1 --> Env
    V2 --> Env
    VN --> Env

    Env --> Model
    Model --> QL

    Coord --> Metrics
    V1 --> Metrics
    V2 --> Metrics
    VN --> Metrics

    Metrics --> Comp

    Metrics --> CSV
    Metrics --> Graphs
    Metrics --> Report
    Metrics --> Info
```

---

## 6. Diagrama de Deployment - Organização de Resultados

```mermaid
graph LR
    subgraph "Sistema de Arquivos"
        subgraph "Trabalho_02_Aprendizado/"
            Main[cruzamento_maspy_learning.py]
            Exec[executar_todos_cenarios.py]
            Comp[comparar_cenarios.py]

            subgraph "resultados/"
                TS1[20251204_130354/]
                TS2[20251204_140522/]
                TSN[YYYYMMDD_HHMMSS/]
                Sym[ultima_execucao →]

                subgraph "20251204_130354/"
                    CSV1[metricas_aprendizado.csv]
                    Info1[info_execucao.txt]

                    subgraph "graficos/"
                        G1[recompensa_por_episodio.png]
                        G2[recompensa_acumulada.png]
                        G3[media_movel.png]
                        G4[comparacao_desempenho.png]
                        G5[analise_convergencia.png]
                    end
                end
            end

            subgraph "docs/"
                PEAS[PEAS.md]
                SART[SART.md]
                REL[RELATORIO_TESTES.md]
                CONF[CONFORMIDADE_TRABALHO02.md]
                DIF[dificuldades_encontradas.md]
                UML[DIAGRAMAS_UML.md]
            end
        end
    end

    Main -->|executa| TS1
    Main -->|executa| TS2
    Main -->|executa| TSN
    Sym -.->|aponta para| TSN

    TS1 --> CSV1
    TS1 --> Info1
    TS1 --> graficos/
```

---

## 7. Diagrama de Atividades - Fluxo de Execução Principal

```mermaid
flowchart TD
    Start([Início]) --> ParseArgs[Parsear argumentos CLI]

    ParseArgs --> LoadExp[Carregar configuração<br/>do experimento]

    LoadExp --> ConfigEnv[Configurar ambiente<br/>CruzamentoLearningEnvironment]

    ConfigEnv --> CreateAgents[Criar agentes:<br/>1 Coordenador + N Veículos]

    CreateAgents --> CreateDir[Criar diretório de resultados<br/>resultados/YYYYMMDD_HHMMSS/]

    CreateDir --> InitMetrics[Inicializar MetricsCollector]

    InitMetrics --> StartSim[Iniciar simulação MASPY]

    StartSim --> ActivateGoal[Coordenador: Goal aprender ativo]

    ActivateGoal --> ExplorePhase{Fase de exploração}

    ExplorePhase -->|2 schedules| LearnModel[EnvModel.learn_model<br/>exploração aleatória]

    LearnModel --> TrainPhase[Fase de treinamento<br/>model.learn qlearning]

    TrainPhase --> Loop1{Episódios < N?}

    Loop1 -->|Sim| Episode[Executar episódio]

    Episode --> Reset[Reset ambiente]
    Reset --> Loop2{Estado terminal?}

    Loop2 -->|Não| ChooseAction[Escolher ação<br/>ε-greedy]
    ChooseAction --> Execute[Executar ação<br/>escolher_veiculo]
    Execute --> CalcReward[Calcular recompensa]
    CalcReward --> UpdateQ[Atualizar Q-table]
    UpdateQ --> RecordMetrics[Registrar métricas]
    RecordMetrics --> Loop2

    Loop2 -->|Sim| Loop1

    Loop1 -->|Não| ValidationPhase[Fase de validação]

    ValidationPhase --> Loop3{Episódios < N?}

    Loop3 -->|Sim| ValidEpisode[Episódio de validação<br/>só exploitação]
    ValidEpisode --> Loop3

    Loop3 -->|Não| CalcStats[Calcular estatísticas]

    CalcStats --> CheckConv{Convergiu?}

    CheckConv -->|Sim| MarkConverged[Marcar episódio<br/>de convergência]
    CheckConv -->|Não| NoConv[Sem convergência]

    MarkConverged --> GenReport[Gerar relatório]
    NoConv --> GenReport

    GenReport --> ExportCSV[Exportar CSV]
    ExportCSV --> CreateGraphs[Criar 5 gráficos]
    CreateGraphs --> SaveInfo[Salvar info_execucao.txt]
    SaveInfo --> CreateSymlink[Criar symlink<br/>ultima_execucao]
    CreateSymlink --> End([Fim])
```

---

## 8. Diagrama de Classes - MetricsCollector (Detalhado)

```mermaid
classDiagram
    class MetricsCollector {
        -metricas_por_agente: dict~str, dict~
        -convergencia_threshold: float
        -convergencia_window: int

        +registrar_episodio(nome_agente, episodio, recompensa)
        +registrar_acao(nome_agente, correta)
        +calcular_estatisticas()
        +detectar_convergencia(nome_agente, threshold, window)
        +calcular_funcao_utilidade(nome_agente, alpha, beta, gamma)
        +gerar_relatorio() str
        +exportar_csv(caminho_arquivo)
        +criar_graficos(diretorio_saida)
        -_criar_grafico_recompensas(ax, dados)
        -_criar_grafico_acumulado(ax, dados)
        -_criar_grafico_media_movel(ax, dados, janela)
        -_criar_grafico_comparacao(ax, dados)
        -_criar_grafico_convergencia(ax, dados)
    }

    class MetricasAgente {
        <<structure>>
        +recompensas_por_episodio: list~float~
        +recompensa_total: float
        +recompensa_media: float
        +desvio_padrao: float
        +acoes_corretas: int
        +acoes_incorretas: int
        +melhor_episodio: dict
        +pior_episodio: dict
        +convergencia: dict
        +utilidade: dict
    }

    class ConvergenciaInfo {
        <<structure>>
        +convergiu: bool
        +episodio_convergencia: int
        +threshold: float
        +window: int
    }

    class UtilidadeInfo {
        <<structure>>
        +total: float
        +taxa_acerto: float
        +fator_convergencia: float
        +fator_recompensa: float
        +pesos: dict
    }

    MetricsCollector "1" --> "*" MetricasAgente : gerencia
    MetricasAgente "1" --> "1" ConvergenciaInfo : contém
    MetricasAgente "1" --> "0..1" UtilidadeInfo : contém
```

---

## 9. Autômato SART - Sistema de Cruzamento (Exemplo com 3 veículos)

### Especificação SART Completa

**S - States (Estados):**
- Representação: tupla (v1_passou, v2_passou, v3_passou) onde cada elemento ∈ {0,1}
- Estado inicial: (0,0,0) - todos os veículos aguardando
- Estados intermediários: (1,0,0), (0,1,0), etc. - alguns veículos atravessaram
- Estado terminal: (1,1,1) - todos os veículos atravessaram
- Total de estados possíveis: 2^3 = 8 estados

**A - Actions (Ações):**
- escolher_veiculo1: Seleciona veículo 1 para atravessar (só disponível se v1_passou=0)
- escolher_veiculo2: Seleciona veículo 2 para atravessar (só disponível se v2_passou=0)
- escolher_veiculo3: Seleciona veículo 3 para atravessar (só disponível se v3_passou=0)
- Ações disponíveis variam conforme estado atual

**R - Rewards (Recompensas):**
- Escolha ótima (maior prioridade entre disponíveis): +100
- Escolha subótima: -Δp × 0.2, onde Δp = diferença de prioridade

**T - Transitions (Transições):**
- Determinísticas: escolher_veiculo(i) leva de (v1,...,vi=0,...,vN) para (v1,...,vi=1,...,vN)
- Exemplo: escolher_veiculo2 em estado (0,0,1) → (0,1,1)

### Autômato Visual

```
Configuração do Exemplo:
- Veículo 1: Prioridade = 50 (Carro comum)
- Veículo 2: Prioridade = 100 (Ambulância)
- Veículo 3: Prioridade = 30 (Carro comum)

Legenda:
→ : Transição com ação e recompensa
◎ : Estado terminal (duplo círculo)
○ : Estado intermediário
▸ : Estado inicial


                            ┌────────────────────────────────────┐
                            │                                    │
                            │    Estados do Cruzamento           │
                            │    (v1_passou, v2_passou, v3_passou)│
                            └────────────────────────────────────┘


                                  ▸ (0,0,0)
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
         escolher_v1│           escolher_v2      escolher_v3
             <-10>  │             <+100>             <-14>
                    │                │                │
                    ↓                ↓                ↓
                 (1,0,0)          (0,1,0)          (0,0,1)
                    │                │                │
              ┌─────┴─────┐    ┌─────┴─────┐    ┌─────┴─────┐
              │           │    │           │    │           │
    escolher_v2  escolher_v3  escolher_v1  escolher_v3  escolher_v1  escolher_v2
       <+100>      <-4>       <-10>        <-14>       <-4>        <+100>
              │           │    │           │    │           │
              ↓           ↓    ↓           ↓    ↓           ↓
           (1,1,0)     (1,0,1) (1,1,0)   (0,1,1) (1,0,1)   (0,1,1)
              │           │    │           │    │           │
              │           │    │           │    │           │
      escolher_v3  escolher_v2  escolher_v3  escolher_v1  escolher_v2  escolher_v1
         <+100>      <+100>      <+100>      <+100>      <+100>      <+100>
              │           │    │           │    │           │
              └───────┬───┴────┴─────┬─────┴────┴───────────┘
                      │              │
                      ↓              ↓
                   ◎ (1,1,1)      ◎ (1,1,1)


Análise de Recompensas:
- escolher_v1 <-10>: V1 tem prioridade 50, V2 tem 100 → Δp=50 → -50×0.2 = -10
- escolher_v2 <+100>: V2 tem maior prioridade (100)
- escolher_v3 <-14>: V3 tem prioridade 30, V2 tem 100 → Δp=70 → -70×0.2 = -14
- escolher_v2 <+100>: V2 ainda tem maior prioridade entre {V1,V2}
- escolher_v3 <-4>: V3 tem prioridade 30, V1 tem 50 → Δp=20 → -20×0.2 = -4
- No estado final, última escolha sempre recebe +100 (única opção disponível)


Caminho Ótimo Aprendido:
┌─────────────────────────────────────────────────────────────┐
│  (0,0,0) ──[escolher_v2 <+100>]──▶ (0,1,0)                  │
│                                        │                     │
│                            [escolher_v1 <+100>]              │
│                                        │                     │
│                                        ↓                     │
│                                     (1,1,0)                  │
│                                        │                     │
│                            [escolher_v3 <+100>]              │
│                                        │                     │
│                                        ↓                     │
│                                    ◎ (1,1,1)                 │
│                                                              │
│  Recompensa Total: +300 (máximo possível)                   │
└─────────────────────────────────────────────────────────────┘
```

### Q-Table Convergida (Exemplo Simplificado)

Para o estado inicial (0,0,0):

| Estado | Ação | Q-valor | Explicação |
|--------|------|---------|------------|
| (0,0,0) | escolher_v1 | ~280 | Subótimo: -10 + 100 + 100 + γ × futuro |
| (0,0,0) | escolher_v2 | ~300 | Ótimo: +100 + 100 + 100 + γ × futuro |
| (0,0,0) | escolher_v3 | ~276 | Subótimo: -14 + 100 + 100 + γ × futuro |

Após convergência, o agente sempre escolhe escolher_v2 (maior Q-valor).

### Escalabilidade para N Veículos

Para o sistema real com N=10 veículos:
- Estados possíveis: 2^10 = 1024 estados
- Ações máximas por estado: 10 (todas no estado inicial)
- Complexidade da Q-table: O(2^N × N)
- Espaço de busca: Exponencial, mas Q-Learning converge eficientemente

### Propriedades do Autômato

**Tipo:** Autômato Finito Determinístico (AFD) com recompensas
**Características:**
- Determinístico: cada ação leva a exatamente um próximo estado
- Totalmente observável: agente sempre conhece estado atual completo
- Episódico: cada episódio termina em estado (1,1,...,1)
- Recompensas imediatas: feedback instantâneo após cada ação

**Política Ótima (π*):**
Em qualquer estado s, escolher o veículo com maior prioridade entre os disponíveis:
```
π*(s) = argmax prioridade(i) para todo i tal que vi_passou = 0
```

**Valor Ótimo (V*):**
```
V*((0,0,...,0)) = N × 100 = recompensa máxima possível
```

---

## Convenções e Notas

### Padrões de Nomenclatura
- **Agentes:** Sufixo `Agent` (ex: `CoordenadorLearningAgent`)
- **Ambiente:** Sufixo `Environment`
- **Métodos públicos:** `snake_case`
- **Métodos privados:** prefixo `_`
- **Beliefs BDI:** `snake_case` (ex: `veiculo_id`, `prioridade`)
- **Goals BDI:** `Goal("string")` (ex: `Goal("aprender")`)

### Ciclo BDI
1. **Beliefs:** Estado interno do agente (prioridades, recompensas, etc.)
2. **Desires:** Goals ativos (ex: "aprender", "observar_cruzamento")
3. **Intentions:** Plans executados (ex: `iniciar_aprendizado()`)

### Q-Learning
- **Equação de Bellman:** `Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]`
- **Parâmetros padrão:** α=0.1, γ=0.9, ε=0.1
- **Política:** ε-greedy durante treino, greedy durante validação

### Função de Utilidade PEAS
```
U = 0.5 × taxa_acerto + 0.3 × fator_convergencia + 0.2 × fator_recompensa
```

Onde:
- `taxa_acerto = corretas / (corretas + incorretas)`
- `fator_convergencia = 1 / max(1, episodio_convergencia)`
- `fator_recompensa = recompensa_media / recompensa_maxima_teorica`

---

## Referências

- **MASPY Framework:** [Documentação oficial](https://github.com/lsa-pucrs/maspy)
- **Q-Learning:** Sutton & Barto - Reinforcement Learning: An Introduction
- **PEAS:** Russell & Norvig - Artificial Intelligence: A Modern Approach
- **SART:** Metodologia específica para RL em sistemas multi-agentes

---

**Data:** 04/12/2025
**Versão:** 1.0
