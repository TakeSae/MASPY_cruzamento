# Trabalho 01 - Sistema de Negociação Multi-Agentes

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Professor:** Gleifer Vaz Alves
**Tema:** Sistema de negociação entre veículos em cruzamento

---

## Descrição

Sistema multi-agentes para gerenciamento de cruzamento viário utilizando protocolo de negociação baseado em prioridades. Implementado com o framework MASPY usando arquitetura BDI.

---

## Estrutura de Arquivos

```
Trabalho_01_Negociacao/
├── cruzamento_maspy_v3.py              # Sistema principal (RECOMENDADO)
├── cruzamento_maspy_v2.py              # Versão legado
├── cruzamento_maspy_v3_analise_PEAS.md # Documentação PEAS completa
├── experiments/
│   ├── experimentos_cruzamento_v3.py   # Suite de experimentos v3
│   ├── experimentos_cruzamento.py      # Suite v2 (legado)
│   └── run_all_experiments.py          # Executor de todos experimentos
├── scripts/
│   ├── coletar_dados_v3.sh             # Script de coleta v3 (RECOMENDADO)
│   └── coletar_dados.sh                # Script v2 (legado)
├── analysis/
│   └── analisar_resultados.py          # Analisador de resultados
└── resultados/                         # Resultados organizados por timestamp
    ├── YYYYMMDD_HHMMSS/
    │   ├── info_sessao.txt
    │   ├── resultados_completos.txt
    │   ├── resumo.txt
    │   ├── metricas.txt
    │   └── vencedores.txt
    └── ultima_execucao -> YYYYMMDD_HHMMSS
```

---

## Agentes

### 1. VeiculoAgent
Representa um veículo que participa da negociação.

**Arquitetura BDI:**
- Beliefs: tipo, prioridade, decisao
- Goals: Goal("atravessar")
- Plans: enviar_proposta(), receber_decisao()

### 2. CoordenadorAgent
Gerencia o processo de negociação.

**Arquitetura BDI:**
- Beliefs: Belief("proposta", dados)
- Goals: Goal("decidir")
- Plans: coletar_propostas(), decidir_vencedor()

**Algoritmo:** vencedor = max(propostas, key=lambda p: p['prio'])

---

## Ambiente

### CruzamentoEnvironment
Representa o cruzamento físico de 4 vias.

**Estados:**
- cruzamento_livre: Boolean
- veiculos_aguardando: List[Dict]
- veiculo_atravessando: String
- historico_travessias: List[String]

**Métodos:**
- registrar_chegada()
- iniciar_travessia()
- finalizar_travessia()

---

## Experimentos (6 cenários)

| # | Nome | Veículos | Objetivo |
|---|------|----------|----------|
| 1 | Cenário Base | 4 | Validar priorização de emergência |
| 2 | Múltiplas Emergências | 4 | Desempate entre emergências |
| 3 | Prioridades Iguais | 4 | Comportamento em empate |
| 4 | Cargas Pesadas | 4 | Priorização de veículos grandes |
| 5 | Cenário Misto | 6 | Teste com diversidade |
| 6 | Teste de Estresse | 10 | Avaliar escalabilidade |

---

## Como Executar

### Opção 1: Coletar Dados v3 (RECOMENDADO)

```bash
cd Trabalho_01_Negociacao
./scripts/coletar_dados_v3.sh
```

**Gera automaticamente:**
- Pasta resultados/YYYYMMDD_HHMMSS/ organizada
- info_sessao.txt - Metadados da sessão
- resultados_completos.txt - Log completo (90% mais limpo que v2)
- resumo.txt - Estatísticas consolidadas
- metricas.txt - Métricas detalhadas
- vencedores.txt - Histórico de vencedores

### Opção 2: Executar Sistema Principal

```bash
cd Trabalho_01_Negociacao
python cruzamento_maspy_v3.py  # v3 (RECOMENDADO)
python cruzamento_maspy_v2.py  # v2 (legado)
```

### Opção 3: Executar Bateria de Experimentos

```bash
cd Trabalho_01_Negociacao
python experiments/experimentos_cruzamento_v3.py  # v3 (RECOMENDADO)
python experiments/experimentos_cruzamento.py     # v2 (legado)
```

---

## Prioridades de Veículos

| Tipo | Prioridade | Justificativa |
|------|------------|---------------|
| Ambulância | 100 | Emergência médica |
| Bombeiros | 98 | Emergência de incêndio |
| Polícia | 95 | Segurança pública |
| Caminhão | 50 | Carga pesada |
| Ônibus | 40 | Transporte coletivo |
| Táxi | 25 | Transporte particular |
| Carro | 10-20 | Veículo comum |
| Moto | 5 | Veículo pequeno |

**Critério de desempate:** Ordem de processamento (FIFO)

---

## Metodologia PEAS

Documentação completa em: [cruzamento_maspy_v3_analise_PEAS.md](cruzamento_maspy_v3_analise_PEAS.md)

**Performance:** Medidas de desempenho do sistema
**Environment:** Características do ambiente
**Actuators:** Ações disponíveis aos agentes
**Sensors:** Percepções dos agentes

---

## Tecnologias

- Linguagem: Python 3.13
- Framework: MASPY 2025.06.07
- Paradigma: BDI (Beliefs, Desires, Intentions)
- Bibliotecas: enum, subprocess, time, sys

---

## Versões

### v3.0 (2024-10-24) - ATUAL
- Sistema de LogLevel (SILENT, ERROR, INFO, DEBUG)
- Documentação PEAS completa
- Uso efetivo do ambiente (call_env_method)
- Logs 90% mais limpos (20KB → 2KB)
- Performance 20% melhor
- Organização de resultados por timestamp

### v2.0 (2024-10-20)
- Sistema funcional completo
- 6 experimentos validados
- Protocolo de negociação implementado

---

## Autores

- Guilherme T. S. Abreu - guiabr@alunos.utfpr.com.br
- Maria Eduarda S. Freitas - mariaeduardafreitas@alunos.utfpr.edu.br
