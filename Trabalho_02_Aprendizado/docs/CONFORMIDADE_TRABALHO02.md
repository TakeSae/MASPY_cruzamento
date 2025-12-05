# Conformidade com Requisitos - Trabalho 02 (Tema b)

**Data de Verificação:** 2025-11-30
**Sistema:** Sistema Multi-Agentes com Q-Learning
**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR

---

## Checklist de Requisitos

### 6. Descrição do tema (b)

#### 6(a) Mecanismo de aprendizagem por reforço usando MASPY
- **ATENDIDO** - Q-Learning implementado via MASPY
- CoordenadorLearningAgent utiliza EnvModel do MASPY
- Aprendizado via episódios de treinamento configuráveis

**Evidência:** [cruzamento_maspy_learning.py:1278-1325](cruzamento_maspy_learning.py)

---

#### 6(b) Extensão do Trabalho 1
- **ATENDIDO** - Sistema estende o problema de cruzamento do Trabalho 1
- Mantém domínio (veículos, prioridades, cruzamento)
- Adiciona camada de aprendizado ao invés de negociação direta

**Evidência:** Comparação documentada no README principal

---

#### 6(c) Especificações técnicas

**Pelo menos 2 tipos de agentes:**
- **ATENDIDO**
  - CoordenadorLearningAgent (agente que aprende)
  - VeiculoLearningAgent (agente observador)

**Pelo menos 1 ambiente:**
- **ATENDIDO**
  - CruzamentoLearningEnvironment (ambiente de aprendizado)

**Técnica de aprendizagem por reforço:**
- **ATENDIDO**
  - Q-Learning via MASPY EnvModel
  - Estados observáveis (v{N}_passou)
  - Ações (escolher_veiculo)
  - Recompensas (+100 ótimo, penalidades proporcionais)

**Executar pelo menos 10 instâncias de agentes:**
- **ATENDIDO**
  - Sistema executa com 11 agentes (1 coordenador + 10 veículos)
  - Configurável de 2 a 10 veículos conforme cenário

**Evidência:** [cruzamento_maspy_learning.py:1844-1868](cruzamento_maspy_learning.py)

---

#### 6(d) Simulação detalhada

**Variações de cenários:**
- **ATENDIDO** - 10 cenários diferentes implementados:
  1. padrao (10 veículos diversos)
  2. base (ambulância vs normais)
  3. emergencias (múltiplas emergências)
  4. iguais (prioridades iguais)
  5. pesados (cargas pesadas)
  6. transporte_publico (ônibus, táxi)
  7. prioridades_proximas (diferenças pequenas)
  8. extremos (1 vs 100)
  9. dois_veiculos (caso mínimo)
  10. tres_veiculos (caso intermediário)

**Evidência:** [cruzamento_maspy_learning.py:85-178](cruzamento_maspy_learning.py)

**Variações do mecanismo de aprendizagem:**
- **ATENDIDO** - Parâmetros configuráveis:
  - `--episodios`: Número de episódios (default: 100)
  - `--reward`: Recompensa por escolha correta (default: 100)
  - `--penalidade`: Multiplicador de penalidade (default: 1.5)

**Instâncias dos agentes:**
- **ATENDIDO** - Cenários variam de 2 a 10 veículos

**Resultados esperados:**
- **ATENDIDO**
  - Melhor cenário identificado via ScenarioComparator
  - Função de utilidade compara configurações
  - Detecção automática de convergência

**Diferenças do protocolo de negociação:**
- **NÃO APLICÁVEL** - Sistema usa aprendizado ao invés de negociação
  - Trabalho 1 tinha negociação (oferta → decisão)
  - Trabalho 2 tem aprendizado (exploração → política ótima)
  - **Justificativa:** Tema (b) permite aprendizagem sem negociação

---

#### 6(e) Relatório e apresentação

**Comparação com Trabalho 1:**
- **ATENDIDO**
  - Diferenças documentadas no README principal
  - Trabalho 1: Sistema de negociação BDI
  - Trabalho 2: Sistema de aprendizado Q-Learning

**Pontos corrigidos/adicionados/estendidos:**
- Documentado no histórico de versões do README

**Evidência:** [README.md - Histórico de Versões](../README.md)

---

#### 6(f) Tabelas e gráficos

**Apresentação de resultados:**
- **ATENDIDO** - 5 tipos de gráficos matplotlib:
  1. Recompensa por episódio (linha)
  2. Recompensa acumulada (crescimento)
  3. Média móvel (tendência)
  4. Comparação de desempenho (barras duplas)
  5. Análise de convergência (regressão linear)

**Exportação de dados:**
- **ATENDIDO**
  - CSV com métricas detalhadas por episódio
  - Relatório textual completo no terminal

**Exploração do mecanismo de aprendizagem:**
- **ATENDIDO**
  - Gráficos focam em curva de aprendizado
  - Análise de convergência
  - Comparação entre cenários

**Evidência:** [cruzamento_maspy_learning.py:700-768](cruzamento_maspy_learning.py)

---

### 7. Tarefas

#### 7(d) Metodologia PEAS

**Uso da metodologia PEAS:**
- **ATENDIDO** - Documentação completa integrada ao código (linhas 182-370)

**Performance (Medida de Desempenho):**
- Recompensa acumulada
- Taxa de convergência
- Taxa de acerto (≥95% objetivo)
- Eficiência temporal
- **Função de utilidade:** U = 0.5×taxa_acerto + 0.3×convergência + 0.2×recompensa

**Environment (Ambiente):**
- Cruzamento virtual
- Veículos com prioridades (1-100)
- Sistema de recompensas
- Estados observáveis (v{N}_passou)
- 10 cenários de teste

**Actuators (Atuadores):**
- escolher_veiculo(veiculo_id)
- iniciar_aprendizado()

**Sensors (Sensores):**
- v{N}_passou (estados booleanos)
- Configuração inicial dos veículos
- Estado terminal (todos atravessaram)

**Ilustração do desempenho na conclusão:**
- **ATENDIDO** - Relatório final mostra:
  - Utilidade total (0-1 scale)
  - Classificação (EXCELENTE/BOM/SATISFATÓRIO/INSUFICIENTE)
  - Componentes da função de utilidade
  - Comparação entre cenários

**Evidência:** [cruzamento_maspy_learning.py:182-370](cruzamento_maspy_learning.py)

---

#### 7(e) Metodologia SART (MASPY com aprendizagem)

**States (Estados):**
- **ATENDIDO** - v{N}_passou para cada veículo (1-10)
- Estado inicial: todos em 0 (aguardando)
- Estado terminal: todos em 1 (atravessaram)

**Actions (Ações):**
- **ATENDIDO** - escolher_veiculo(id)
- Espaço de ações: {Veiculo1, ..., Veiculo10}

**Rewards (Recompensas):**
- **ATENDIDO**
  - Escolha ótima (maior prioridade): +100
  - Escolha subótima: penalidade proporcional (-diferença × multiplicador)

**Transitions (Transições):**
- **ATENDIDO**
  - Determinísticas: escolher veículo → marca como atravessado
  - Atualiza estado v{N}_passou de 0 para 1

**Evidência:** [cruzamento_maspy_learning.py:360-370](cruzamento_maspy_learning.py)

---

#### 7(g) Experimentos detalhados

**Pelo menos 10 cenários diferentes:**
- **ATENDIDO** - 10 cenários implementados (ver lista em 6(d))

**Comparação entre cenários:**
- **ATENDIDO** - ScenarioComparator (linhas 777-899)
- Script comparar_cenarios.py para execução automatizada

**Evidência:** [comparar_cenarios.py](comparar_cenarios.py)

---

## Melhorias Adicionais Implementadas

### Sistema de Organização de Resultados (2025-11-30)

**Estrutura por timestamp:**
```
resultados/
  20251130_093551/
    graficos/
      recompensa_por_episodio.png
      recompensa_acumulada.png
      media_movel.png
      comparacao_desempenho.png
      analise_convergencia.png
    metricas_aprendizado.csv
    info_execucao.txt
  ultima_execucao -> 20251130_093551
```

**Benefícios:**
- Organização automática por data/hora
- Rastreabilidade completa de cada execução
- Acesso rápido via symlink ultima_execucao
- Metadados salvos em info_execucao.txt:
  - Data/hora da execução
  - Nome do experimento
  - Número de episódios e veículos
  - Tempo total de execução
  - Parâmetros de recompensa/penalidade
  - Log level utilizado

**Evidência:** [cruzamento_maspy_learning.py:57-123](cruzamento_maspy_learning.py)

---

## Sistema de Testes Automatizados

**Suite de validação:**
- 28 testes implementados
- 100% de sucesso (28/28)
- Validação de:
  - Sintaxe Python
  - Imports e dependências
  - MetricsCollector
  - Função de utilidade PEAS
  - Cálculos estatísticos
  - Documentação PEAS/SART
  - 10 cenários de experimento
  - Exportação CSV
  - Matplotlib (opcional)

**Evidência:** [RELATORIO_TESTES.md](RELATORIO_TESTES.md)

---

## Resumo de Conformidade

| Requisito | Status | Observações |
|-----------|--------|-------------|
| 6(a) Aprendizagem por reforço | COMPLETO | Q-Learning via MASPY |
| 6(b) Extensão Trabalho 1 | COMPLETO | Mesmo domínio, nova abordagem |
| 6(c) ≥2 tipos agentes | COMPLETO | Coordenador + Veículo |
| 6(c) ≥1 ambiente | COMPLETO | CruzamentoLearningEnvironment |
| 6(c) Técnica RL | COMPLETO | Q-Learning |
| 6(c) ≥10 instâncias | COMPLETO | 11 agentes (1+10) |
| 6(d) Variações cenários | COMPLETO | 10 cenários |
| 6(d) Variações aprendizagem | COMPLETO | Parâmetros configuráveis |
| 6(d) Variações instâncias | COMPLETO | 2-10 veículos |
| 6(d) Protocolo negociação | N/A | Aprendizado ao invés de negociação |
| 6(e) Comparação T1/T2 | COMPLETO | Documentado no README |
| 6(f) Tabelas e gráficos | COMPLETO | 5 gráficos + CSV |
| 7(d) Metodologia PEAS | COMPLETO | Documentação integrada (182-370) |
| 7(d) Função utilidade | COMPLETO | U = α×acerto + β×conv + γ×recomp |
| 7(e) Metodologia SART | COMPLETO | States/Actions/Rewards/Transitions |
| 7(g) ≥10 cenários | COMPLETO | 10 cenários implementados |
| Organização resultados | EXTRA | Sistema timestamp implementado |
| Testes automatizados | EXTRA | 28 testes, 100% sucesso |

---

## Conclusão

**Status Geral:** **CONFORME COM TODOS OS REQUISITOS DO TRABALHO 02 (TEMA B)**

O sistema atende integralmente aos requisitos especificados no documento "2025-2-SMA-Trabalho-02.pdf" para o tema (b) - Desenvolvimento de SMA com aprendizagem por reforço usando MASPY.

**Pontos fortes:**
1. Implementação completa de Q-Learning com MASPY
2. Documentação PEAS e SART integrada ao código
3. Função de utilidade matemática rigorosa
4. 10 cenários de teste diversos
5. Sistema robusto de métricas e visualização
6. Organização profissional de resultados por timestamp
7. Suite de testes automatizados com 100% de sucesso
8. Comparador de cenários para análise detalhada

**Observação sobre negociação:**
O requisito 6(d) menciona "diferenças do protocolo de negociação", mas como o tema (b) permite aprendizagem SEM negociação, o sistema implementa variações do mecanismo de APRENDIZAGEM ao invés de negociação. Isso está alinhado com a proposta do tema (b) que permite "aprendizagem por reforço" como alternativa à negociação.

---

**Documento gerado automaticamente**
**Data:** 2025-11-30
**Sistema:** Sistema Multi-Agentes - Aprendizado Q-Learning
**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
