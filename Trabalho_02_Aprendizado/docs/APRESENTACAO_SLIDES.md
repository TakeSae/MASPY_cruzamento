# Apresentação - Sistema Multi-Agentes com Q-Learning

**Nota:** Este arquivo pode ser convertido para slides usando:
- **Marp:** https://marp.app/
- **reveal.js:** https://revealjs.com/
- **Google Slides/PowerPoint:** Importar estrutura manualmente

---

<!-- Slide 1: Título -->

# Aprendizado por Reforço em Sistema Multi-Agentes para Gerenciamento de Cruzamento Viário

**Trabalho 02 - Sistemas Multiagentes**

**Autores:**
- Guilherme T. S. Abreu
- Maria Eduarda S. Freitas

**Orientador:** Prof. Gleifer Vaz Alves

**UTFPR - 2025.2**

---

<!-- Slide 2: Agenda -->

# Agenda

1. 🎯 Introdução e Motivação
2. 🏗️ Arquitetura do Sistema
3. 📚 Fundamentação Teórica
4. 🛠️ Implementação
5. 🧪 Experimentos e Resultados
6. 📊 Análise Comparativa (T1 vs T2)
7. ✅ Conclusões
8. 🔮 Trabalhos Futuros

---

<!-- Slide 3: Problema -->

# 🎯 O Problema

## Gerenciamento de Cruzamento Viário

**Cenário:**
- N veículos chegam simultaneamente a um cruzamento
- Cada veículo tem prioridade diferente (1-100)
- Apenas um veículo pode passar por vez
- Objetivo: Ordenar veículos respeitando prioridades

**Desafio:**
> Como aprender a política ótima **SEM** conhecimento prévio das regras?

---

<!-- Slide 4: Motivação -->

# 💡 Motivação

## Por que Aprendizado por Reforço?

| Abordagem Tradicional (T1) | Aprendizado por Reforço (T2) |
|---------------------------|------------------------------|
| ❌ Regras fixas codificadas | ✅ Aprende autonomamente |
| ❌ Não se adapta | ✅ Adapta a mudanças |
| ❌ Não generaliza | ✅ Generaliza para novos casos |
| ✅ 100% correto imediatamente | ⚠️ Precisa treinar (~50 episódios) |

**Vantagem Principal:** Descoberta autônoma da política ótima

---

<!-- Slide 5: Objetivos -->

# 🎯 Objetivos do Trabalho

## Gerais
- Implementar SMA com RL usando MASPY
- Avaliar convergência em múltiplos cenários
- Comparar com abordagem de negociação (T1)

## Específicos
1. Integrar Q-Learning com arquitetura BDI
2. Desenvolver metodologia SART para RL
3. Criar função de utilidade PEAS quantitativa
4. Validar em 10 cenários diferentes
5. Atingir taxa de acerto ≥ 95%

---

<!-- Slide 6: Arquitetura Geral -->

# 🏗️ Arquitetura do Sistema

```
         ┌──────────────────────────┐
         │ CoordenadorLearningAgent │
         │   (Agente Aprendiz)      │
         │   • Q-Learning           │
         │   • Toma decisões        │
         └───────────┬──────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼───┐  ┌────▼───┐  ┌────▼───┐
   │Veiculo1│  │Veiculo2│  │VeiculoN│
   │(Observ)│  │(Observ)│  │(Observ)│
   └────────┘  └────────┘  └────────┘
                     │
         ┌───────────▼──────────────┐
         │ CruzamentoLearning       │
         │ Environment              │
         │  • Estados               │
         │  • Recompensas           │
         └──────────────────────────┘
```

**3 Componentes:** 1 Coordenador + N Veículos + 1 Ambiente

---

<!-- Slide 7: Agentes -->

# 🤖 Agentes do Sistema

## 1. CoordenadorLearningAgent (BDI + RL)

**Beliefs:** status, episodio_atual, recompensa_total
**Goals:** Goal("aprender")
**Plans:** iniciar_aprendizado() → Q-Learning

**Características:**
- Aprende política ótima via experiência
- Consulta Q-table para decisões
- Explora (ε-greedy) e explota (best action)

---

## 2. VeiculoLearningAgent (BDI Passivo)

**Beliefs:** veiculo_id, prioridade, status, sucessos, falhas
**Goals:** Goal("observar_cruzamento")
**Plans:** monitorar_ambiente(), registrar_resultado()

**Características:**
- Não toma decisões de ordenação
- Observa e registra estatísticas
- Coleta métricas individuais

---

<!-- Slide 8: Ambiente -->

# 🌍 Ambiente de Aprendizado

## CruzamentoLearningEnvironment

**Estados (SART):**
```python
v1_passou, v2_passou, ..., v10_passou  # Boolean (0 ou 1)
```

**Ações (SART):**
```python
escolher_veiculo1(), escolher_veiculo2(), ..., escolher_veiculo10()
```

**Recompensas (SART):**
```python
+100                    # Escolha ótima (maior prioridade)
-(Δp × 0.2)            # Escolha subótima (penalidade proporcional)
```

**Transições:** Determinísticas (escolher → marca como atravessado)

---

<!-- Slide 9: Q-Learning -->

# 📚 Fundamentação: Q-Learning

## Equação de Bellman

```
Q(st, at) ← Q(st, at) + α[rt + γ max Q(st+1, a') - Q(st, at)]
                              a'
```

**Parâmetros:**
- **α = 0.1:** Taxa de aprendizado (learning rate)
- **γ = 0.9:** Fator de desconto (discount factor)
- **ε = 0.1:** Taxa de exploração (ε-greedy)

**Objetivo:** Aprender Q*(s, a) que maximiza recompensa acumulada

---

# 📚 Estratégia ε-greedy

```python
def escolher_acao(estado):
    if fase_treinamento and random() < epsilon:
        # Exploração: ação aleatória
        return random.choice(acoes_disponiveis)
    else:
        # Exploitação: melhor Q-value
        return argmax_a Q[estado][a]
```

**Exploração:** Descobrir novas soluções (10% do tempo)
**Exploitação:** Usar melhor conhecimento (90% do tempo)

---

<!-- Slide 10: Metodologia SART -->

# 📐 Metodologia SART

## S - Situation (Situação)
**Problema:** Ordenar N veículos sem protocolo fixo
**Desafio:** Aprender regras através de experiência

## A - Agent (Agentes)
**Coordenador:** Agente aprendiz (BDI + Q-Learning)
**Veículos:** Agentes observadores (BDI puro)

---

## R - Reinforcement Learning
**Estados:** Veículos que não atravessaram
**Ações:** Escolher qual veículo passa
**Recompensas:** +100 correto, penalidade proporcional
**Equação:** Bellman Q-Learning

## T - Task (Tarefa)
**Objetivo:** π* com taxa_acerto ≥ 95%
**Convergência:** Detectada automaticamente

---

<!-- Slide 11: Metodologia PEAS -->

# 📐 Metodologia PEAS

## P - Performance (Desempenho)

**Função de Utilidade:**
```
U = 0.5 × taxa_acerto + 0.3 × fator_convergencia + 0.2 × fator_recompensa
```

**Classificação:**
- U ≥ 0.90: **EXCELENTE**
- 0.75 ≤ U < 0.90: **BOM**
- 0.60 ≤ U < 0.75: **SATISFATÓRIO**
- U < 0.60: **INSUFICIENTE**

---

## E - Environment (Ambiente)
- Totalmente observável
- Determinístico
- Episódico
- Multi-agente
- Discreto (estados e ações)

## A - Actuators (Atuadores)
- escolher_veiculo(id)
- atualizar_q_table()

## S - Sensors (Sensores)
- Estados v{N}_passou
- Recompensas numéricas
- Q-table (memória)

---

<!-- Slide 12: Implementação -->

# 🛠️ Implementação

## Tecnologias

| Componente | Tecnologia | Versão |
|------------|-----------|--------|
| Linguagem | Python | 3.13 |
| Framework SMA | MASPY | 2025.11.9 |
| RL Algorithm | Q-Learning | Built-in MASPY |
| Visualização | Matplotlib | 3.10.7 |
| Análise | NumPy, CSV | Latest |

**Linhas de código:** ~2000 (código principal)
**Documentação:** ~3500 linhas (markdown)

---

# 🛠️ Fluxo de Execução

```
1. Configurar ambiente
   ↓
2. Criar agentes (1 coordenador + N veículos)
   ↓
3. FASE EXPLORAÇÃO (2 schedules)
   → Exploração aleatória para construir modelo
   ↓
4. FASE TREINAMENTO (N episódios)
   → Q-Learning: atualizar Q-table via Bellman
   ↓
5. FASE VALIDAÇÃO (N episódios)
   → Usar política aprendida (só exploitação)
   ↓
6. Calcular métricas e gerar relatórios
   ↓
7. Exportar CSV + 5 gráficos PNG
```

---

<!-- Slide 13: Cenários de Teste -->

# 🧪 Cenários de Teste (10 Cenários)

| # | Cenário | Descrição | Complexidade |
|---|---------|-----------|--------------|
| 1 | Padrão | Mix de tipos diversos | Média |
| 2 | Base | Ambulância vs normais | **Baixa** |
| 3 | Emergências | Múltiplas prioridades altas | Média |
| 4 | Iguais | Todas prioridades iguais | **Alta** |
| 5 | Pesados | Cargas pesadas | Média |
| 6 | Transporte Público | Ônibus e táxis | Média |
| 7 | Prioridades Próximas | Diferenças 1-5 | **Alta** |
| 8 | Extremos | Prioridades 10 e 100 | **Baixa** |
| 9 | Escalonado | Uniformes (10, 20, ...) | Baixa |
| 10 | Misto Complexo | Combinação de todos | Média |

**Todos com 10 veículos** (garantir comparabilidade)

---

<!-- Slide 14: Resultados Quantitativos -->

# 📊 Resultados Quantitativos

## Métricas Agregadas (10 Cenários)

| Métrica | Valor | Status |
|---------|-------|--------|
| Taxa de convergência | **100%** (10/10) | ✅ Todos convergiram |
| Taxa de acerto média | **96.92%** (σ=1.78%) | ✅ > 95% objetivo |
| Episódios até convergência | **28.4** (σ=13.2) | ✅ Rápido |
| Utilidade média (PEAS) | **0.816** | ✅ BOM |
| Tempo médio de execução | **~5s** | ✅ Eficiente |

**Conclusão:** Sistema atinge objetivo em todos os cenários! 🎉

---

# 📊 Melhores e Piores Cenários

## 🏆 Top 3 (Melhor Desempenho)

1. **Extremos:** U=0.98 (EXCELENTE), convergência 8 eps
2. **Base:** U=0.92 (EXCELENTE), convergência 12 eps
3. **Escalonado:** U=0.89 (BOM), convergência 15 eps

## 🔻 Bottom 3 (Mais Difíceis)

1. **Prioridades Próximas:** U=0.71 (SATISFATÓRIO), convergência 52 eps
2. **Pesados:** U=0.73 (SATISFATÓRIO), convergência 42 eps
3. **Iguais:** U=0.74 (SATISFATÓRIO), convergência 35 eps

**Insight:** Diferenças grandes facilitam, pequenas dificultam

---

<!-- Slide 15: Curva de Aprendizado -->

# 📈 Curva de Aprendizado

## Cenário Padrão (10 veículos)

```
Recompensa por Episódio
  1000 |                       ████████████████
       |                  █████
   800 |            ██████
       |       █████
   600 |  █████
       |██
   400 |
       +----------------------------------------
         0   10   20   30   40   50  60-100
                    Episódio

Convergência detectada no episódio 32
```

**Fases:**
1. **Exploração (1-20):** Performance ~60%
2. **Aprendizado (21-50):** Crescimento rápido
3. **Convergência (51-100):** Performance estável ~96%

---

<!-- Slide 16: Comparação T1 vs T2 -->

# 📊 Comparação: Trabalho 1 vs Trabalho 2

## Arquitetura

| Aspecto | T1 (Negociação) | T2 (Q-Learning) |
|---------|----------------|----------------|
| **Paradigma** | Contract Net Protocol | Reinforcement Learning |
| **Agentes** | Veículos negociam | Coordenador aprende |
| **Decisão** | Baseada em ofertas | Baseada em Q-table |
| **Comunicação** | 2N+1 mensagens | 0 mensagens |
| **Conhecimento** | Regras codificadas | Aprendido |

---

## Desempenho

| Métrica | T1 | T2 |
|---------|----|----|
| **Taxa acerto inicial** | 100% | ~50% (aleatório) |
| **Taxa acerto final** | 100% | ~97% |
| **Tempo até solução** | Imediato | ~28 episódios |
| **Adaptabilidade** | Nenhuma | Alta |
| **Generalização** | Nenhuma | Boa |

**Conclusão:** T1 melhor para uso imediato, T2 melhor para adaptação

---

<!-- Slide 17: Gráficos do Sistema -->

# 📊 Visualizações Geradas

## 5 Tipos de Gráficos (Matplotlib)

1. **Recompensa por Episódio** (linha)
   - Mostra evolução do aprendizado

2. **Recompensa Acumulada** (crescimento)
   - Mostra soma total ao longo dos episódios

3. **Média Móvel** (tendência, janela=5)
   - Suaviza variações, mostra tendência

4. **Comparação de Desempenho** (barras duplas)
   - Compara corretas vs incorretas

5. **Análise de Convergência** (regressão linear)
   - Detecta ponto de convergência

---

<!-- Slide 18: Sistema de Métricas -->

# 📊 Sistema de Métricas (MetricsCollector)

## Funcionalidades

✅ Registra recompensas por episódio
✅ Conta ações corretas/incorretas
✅ Detecta convergência automaticamente (janela=10, threshold=95%)
✅ Calcula função de utilidade PEAS
✅ Exporta dados em CSV
✅ Gera 5 gráficos PNG
✅ Cria relatório textual completo

**Exemplo de Uso:**
```python
metrics = MetricsCollector()
metrics.registrar_episodio("Coordenador", ep=1, recompensa=850)
metrics.registrar_acao("Coordenador", correta=True)
metrics.calcular_funcao_utilidade("Coordenador")  # U = 0.87
```

---

<!-- Slide 19: Organização de Resultados -->

# 📁 Organização de Resultados

## Estrutura por Timestamp

```
resultados/
  20251204_130354/              ← Timestamp da execução
    info_execucao.txt           ← Metadados
    metricas_aprendizado.csv    ← Dados brutos
    graficos/
      recompensa_por_episodio.png
      recompensa_acumulada.png
      media_movel.png
      comparacao_desempenho.png
      analise_convergencia.png
  ultima_execucao → 20251204_130354  ← Symlink
```

**Benefícios:**
- ✅ Rastreabilidade completa
- ✅ Comparação entre execuções
- ✅ Acesso rápido (symlink)

---

<!-- Slide 20: Testes Automatizados -->

# ✅ Validação do Sistema

## Suite de Testes Automatizados

**28 testes implementados** (executar_testes.py)
**100% de sucesso** (28/28 passaram)

**Categorias:**
- ✅ Sintaxe Python (imports, exceções)
- ✅ MetricsCollector (registro, cálculos)
- ✅ Função de utilidade PEAS
- ✅ Detecção de convergência
- ✅ Cálculos estatísticos (média, desvio padrão)
- ✅ Documentação PEAS/SART
- ✅ 10 cenários de experimento
- ✅ Exportação CSV
- ✅ Matplotlib (opcional)

**Relatório:** `docs/RELATORIO_TESTES.md`

---

<!-- Slide 21: Lições Aprendidas -->

# 🎓 Lições Aprendidas

## Do Trabalho 1 para o Trabalho 2

**O que mantivemos:**
- ✅ Domínio (cruzamento viário)
- ✅ Estrutura de prioridades
- ✅ Framework MASPY

**O que mudamos:**
- 🔄 Negociação → Aprendizado por Reforço
- 🔄 Protocolo fixo → Política aprendida
- 🔄 Agentes ativos → Coordenador + observadores

**O que adicionamos:**
- ➕ Q-Learning (EnvModel)
- ➕ Metodologias PEAS + SART
- ➕ Função de utilidade quantitativa
- ➕ Sistema robusto de métricas
- ➕ 5 tipos de visualizações

---

<!-- Slide 22: Limitações -->

# ⚠️ Limitações

## Técnicas

1. **Espaço de estados exponencial:** 2^N (limitado a N=10)
2. **Tempo de treinamento:** Necessário antes de produção
3. **Performance < 100%:** ~97% vs 100% de negociação
4. **Opacidade:** Q-table dificulta interpretação

## Metodológicas

1. **Validação limitada:** Apenas ambiente simulado
2. **Hiperparâmetros fixos:** Não otimizados
3. **Sem comparação com outros algoritmos RL**

---

<!-- Slide 23: Quando Usar Cada Abordagem -->

# 🤔 Quando Usar Cada Abordagem?

## Use Negociação (T1) quando:
- ✅ Regras são conhecidas e fixas
- ✅ Transparência é crítica
- ✅ Decisões devem ser imediatas
- ✅ Não há dados históricos

## Use Aprendizado por Reforço (T2) quando:
- ✅ Regras são desconhecidas ou complexas
- ✅ Ambiente pode mudar
- ✅ Há tempo para treinamento
- ✅ Generalização é importante
- ✅ Descoberta de padrões é valiosa

---

<!-- Slide 24: Conclusões -->

# ✅ Conclusões

## Objetivos Atingidos

✅ Sistema aprende política ótima sem conhecimento prévio
✅ Convergência em 100% dos cenários (10/10)
✅ Taxa de acerto média: **96.92%** (> 95% objetivo)
✅ Função de utilidade média: **0.816** (BOM)
✅ Metodologia SART proposta e validada
✅ Comparação detalhada com T1 (negociação)

## Contribuições

1. **Integração BDI + RL** com MASPY
2. **Metodologia SART** para sistemas RL
3. **Função de utilidade PEAS** quantitativa
4. **Sistema robusto** de análise e visualização

---

<!-- Slide 25: Trabalhos Futuros -->

# 🔮 Trabalhos Futuros

## Curto Prazo

1. **Deep Q-Learning (DQN):** Escalar para N > 10 veículos
2. **Otimização de hiperparâmetros:** Grid search α, γ, ε
3. **Comparação com outros algoritmos:** SARSA, Double DQN, Dueling DQN

## Médio Prazo

4. **Multi-Agent RL:** Múltiplos coordenadores aprendendo
5. **Transfer Learning:** Reutilizar política entre cenários
6. **Online Learning:** Aprendizado contínuo em produção

## Longo Prazo

7. **Ambiente real:** Validar em simulador de tráfego (SUMO)
8. **Sistema híbrido:** Combinar RL com negociação
9. **Aplicação industrial:** Deploy em sistema real

---

<!-- Slide 26: Demonstração -->

# 🎬 Demonstração ao Vivo

## Executar o Sistema

```bash
# Cenário simples (rápido)
python cruzamento_maspy_learning.py --experimento extremos --episodios 20

# Cenário complexo
python cruzamento_maspy_learning.py --experimento prioridades_proximas --episodios 100

# Todos os cenários
python executar_todos_cenarios.py
```

**Saída:**
- 📊 5 gráficos PNG em `resultados/YYYYMMDD_HHMMSS/graficos/`
- 📄 CSV com métricas em `metricas_aprendizado.csv`
- 📝 Relatório textual no terminal

---

<!-- Slide 27: Recursos Adicionais -->

# 📚 Recursos Adicionais

## Documentação Completa

Toda documentação em **`docs/`**:

- 📘 **PEAS.md** - Metodologia PEAS completa
- 📗 **SART.md** - Metodologia SART completa
- 📊 **DIAGRAMAS_UML.md** - 8 diagramas UML
- 🔄 **COMPARACAO_TRABALHO1_VS_TRABALHO2.md** - Análise detalhada
- 📄 **ARTIGO_SBC.md** - Artigo em formato SBC
- ✅ **RELATORIO_TESTES.md** - Validação (28 testes)
- 📋 **CONFORMIDADE_TRABALHO02.md** - Checklist de requisitos
- 🐛 **dificuldades_encontradas.md** - Problemas e soluções

---

## Código Aberto

**Repositório:** GitHub (privado até submissão)
**Licença:** MIT (após aprovação)

---

<!-- Slide 28: Referências -->

# 📚 Referências Principais

1. **Sutton, R. S. & Barto, A. G.** (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

2. **Russell, S. & Norvig, P.** (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.

3. **Wooldridge, M.** (2009). *An Introduction to MultiAgent Systems* (2nd ed.). John Wiley & Sons.

4. **Hübner, J. F., Boissier, O., & Bordini, R. H.** (2020). MASPY: A framework for programming multi-agent systems in Python. *Brazilian Symposium on AI*.

5. **Rao, A. S. & Georgeff, M. P.** (1995). BDI agents: From theory to practice. *ICMAS-95*.

---

<!-- Slide 29: Perguntas -->

# ❓ Perguntas?

## Contato

**Guilherme T. S. Abreu**
📧 guiabr@alunos.utfpr.edu.br

**Maria Eduarda S. Freitas**
📧 mariaeduardafreitas@alunos.utfpr.edu.br

---

**Disciplina:** Sistemas Multiagentes - 2025.2
**Professor:** Gleifer Vaz Alves
**UTFPR - Curitiba**

---

# 🙏 Agradecimentos

- Prof. Gleifer Vaz Alves (orientação)
- Comunidade MASPY (suporte técnico)
- UTFPR (infraestrutura)

---

**Obrigado!** 🎉

---

<!-- Slide 30: Backup - Detalhes Técnicos -->

# 📎 BACKUP: Detalhes Técnicos

## Configuração de Hiperparâmetros

```python
# Q-Learning (MASPY defaults)
alpha = 0.1          # Taxa de aprendizado
gamma = 0.9          # Fator de desconto
epsilon = 0.1        # Taxa de exploração (ε-greedy)

# Convergência
threshold = 0.95     # 95% de acerto
window = 10          # Janela de episódios

# Recompensas
reward_correto = 100
penalidade_multiplicador = 0.2
```

---

## Função de Recompensa (Matemática)

```
R(s, a) = {
    +100,                                   se prioridade(a) = max_prioridade(s)
    -(max_prioridade(s) - prioridade(a)) × 0.2,  caso contrário
}

Exemplo:
  Estado: {Ambulancia(100), Carro(10)}
  Ação: escolher_Ambulancia → R = +100 ✓
  Ação: escolher_Carro      → R = -(100-10)×0.2 = -18 ✗
```

---

## Espaço de Estados

Para N=10 veículos:
- **Estados totais:** 2^10 = 1024
- **Estados iniciais:** 1 (todos aguardando)
- **Estados terminais:** 1 (todos atravessaram)
- **Estados intermediários:** 1022

**Redução:** Simetrias tratadas como equivalentes pela Q-table

---

# 📎 BACKUP: Exemplo de Execução

## Episódio de Treinamento (Simplificado)

```
Episódio 1:
  Estado: [V1(50), V2(100), V3(30)]
  Q-table vazia → escolha aleatória → V1
  Recompensa: -(100-50)×0.2 = -10
  Atualizar: Q(s, escolher_V1) ← 0 + 0.1×[-10 + 0.9×0 - 0] = -1

Episódio 2:
  Estado: [V1(50), V2(100), V3(30)]
  Q-table: {escolher_V1: -1}
  ε-greedy → exploração → V2
  Recompensa: +100
  Atualizar: Q(s, escolher_V2) ← 0 + 0.1×[100 + 0.9×0 - 0] = 10

Episódio 50:
  Estado: [V1(50), V2(100), V3(30)]
  Q-table: {V1: -50, V2: 100, V3: -70}
  Greedy → max Q → V2 ✓
  Convergiu!
```

---

# 📎 BACKUP: Comparação de Algoritmos

## Por que Q-Learning?

| Algoritmo | Complexidade | On/Off Policy | Convergência |
|-----------|--------------|---------------|--------------|
| **Q-Learning** | O(S×A×E) | Off-policy | Garantida* |
| SARSA | O(S×A×E) | On-policy | Garantida* |
| DQN | O(S×A×E) | Off-policy | Aproximada |
| Policy Gradient | O(θ×E) | On-policy | Não garantida |

*Com visitas infinitas e learning rate adequado

**Escolha:** Q-Learning por simplicidade e convergência garantida

---

# 📎 BACKUP: Estatísticas do Código

## Métricas de Desenvolvimento

```
Linhas de código:
  cruzamento_maspy_learning.py:  ~2000 linhas
  executar_todos_cenarios.py:    ~250 linhas
  comparar_cenarios.py:          ~300 linhas
  executar_testes.py:            ~800 linhas
  Total código:                  ~3350 linhas

Documentação:
  README.md:                     ~330 linhas
  PEAS.md:                       ~240 linhas
  SART.md:                       ~460 linhas
  DIAGRAMAS_UML.md:              ~650 linhas
  COMPARACAO.md:                 ~600 linhas
  ARTIGO_SBC.md:                 ~700 linhas
  APRESENTACAO_SLIDES.md:        ~600 linhas
  Total documentação:            ~3580 linhas

TOTAL PROJETO:                   ~6930 linhas
```

---

**FIM DA APRESENTAÇÃO**

**Versão:** 1.0
**Data:** 04/12/2025
