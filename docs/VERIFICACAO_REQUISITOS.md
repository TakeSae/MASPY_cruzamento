# Verificação de Requisitos - Trabalho 1 SMA
## Sistema de Negociação em Cruzamento com MASPY

**Data:** 17/10/2025
**Disciplina:** Sistemas Multi-Agentes 2025.2
**Professor:** Gleifer Vaz Alves
**Instituição:** UTFPR - Campus Ponta Grossa - COCIC

---

## ✅ CHECKLIST DE REQUISITOS

### Tarefa (a): Escolha de Tema ✅
- **Tema escolhido:** Mecanismo de negociação entre veículos em um cruzamento
- **Cenário:** Cruzamento de 4 vias onde veículos negociam prioridade de passagem

### Tarefa (b): Investigação e Especificação ✅

#### Requisitos Obrigatórios:
- ✅ **Pelo menos 2 tipos de agentes**
  - `VeiculoAgent`: Representa veículos que chegam ao cruzamento
  - `CoordenadorAgent`: Gerencia a negociação e decide prioridades

- ✅ **Pelo menos 5 instâncias de agentes**
  - 1 Coordenador
  - 4 Veículos (carro, ambulância, ônibus, moto)
  - **Total: 5 agentes**

- ✅ **Definir pelo menos um ambiente**
  - `CruzamentoEnvironment`: Representa o cruzamento físico
  - Mantém estado (livre/ocupado)
  - Registra veículos aguardando
  - Monitora travessias

- ✅ **Protocolo de negociação definido**
  - **Fase 1:** Veículos enviam propostas (tell) ao Coordenador
  - **Fase 2:** Coordenador coleta todas as propostas
  - **Fase 3:** Coordenador avalia prioridades
  - **Fase 4:** Coordenador decide vencedor
  - **Fase 5:** Coordenador notifica todos (broadcast)
  - **Fase 6:** Veículos reagem à decisão

### Tarefa (c): Metodologia PEAS ✅

Documentado no código `cruzamento_maspy_v2.py`:

```
ANALISE PEAS (Performance, Environment, Actuators, Sensors):
- Performance: Minimizar tempo de espera, priorizar emergencias
- Environment: Cruzamento de 4 vias, dinamico, multiagente
- Actuators: Enviar propostas, decidir vencedor, atravessar
- Sensors: Receber propostas, detectar decisao do coordenador
```

### Tarefa (d): Diagramas UML ⏳
- **Status:** A ser elaborado no artigo
- Diagramas necessários:
  - Diagrama de classes dos agentes
  - Diagrama do ambiente
  - Diagrama de sequência do protocolo de negociação

### Tarefa (e): Implementação ✅

**Arquivos implementados:**
1. `cruzamento_maspy_v2.py` - Sistema completo
   - Agentes: VeiculoAgent, CoordenadorAgent
   - Ambiente: CruzamentoEnvironment
   - Protocolo de negociação implementado
   - Sistema funciona e encerra corretamente

### Tarefa (f): Experimentos ✅

**Arquivo:** `experimentos_cruzamento.py`

**6 Experimentos implementados:**

1. **Experimento 1 - Cenário Base**
   - 1 ambulância vs 3 veículos normais
   - Objetivo: Verificar priorização de emergências
   - Resultado esperado: Ambulância vence

2. **Experimento 2 - Múltiplas Emergências**
   - 2 ambulâncias + 1 bombeiro + 1 carro
   - Objetivo: Testar desempate entre emergências
   - Resultado esperado: Maior prioridade vence

3. **Experimento 3 - Prioridades Iguais**
   - 4 carros com prioridade = 10
   - Objetivo: Verificar critério de desempate
   - Resultado esperado: Ordem de chegada

4. **Experimento 4 - Cargas Pesadas**
   - Caminhão, ônibus, moto, carro
   - Objetivo: Testar diferentes tipos de veículos
   - Resultado esperado: Caminhão (maior prioridade) vence

5. **Experimento 5 - Cenário Misto**
   - 6 veículos de tipos variados
   - Objetivo: Teste de escala
   - Resultado esperado: Ambulância vence

6. **Experimento 6 - Teste de Estresse**
   - 10 veículos simultâneos
   - Objetivo: Verificar escalabilidade
   - Resultado esperado: Sistema suporta carga

### Tarefa (g): Artigo 📝
- **Status:** A ser escrito
- **Formato:** Template SBC
- **Conteúdo:** Descrição detalhada de todos os itens acima

### Tarefa (h): Slides 📊
- **Status:** A ser preparado
- **Conteúdo:** Apresentação dos resultados

---

## 📊 ARQUITETURA BDI IMPLEMENTADA

### VeiculoAgent (BDI)
- **Beliefs:**
  - `meu_tipo`: Tipo do veículo (carro, ambulância, etc.)
  - `minha_prioridade`: Valor de prioridade
  - `decisao`: Resultado da negociação

- **Desires/Goals:**
  - `atravessar`: Objetivo de atravessar o cruzamento

- **Intentions/Plans:**
  - `enviar_proposta`: Envia dados ao coordenador
  - `receber_decisao`: Reage à decisão

### CoordenadorAgent (BDI)
- **Beliefs:**
  - `proposta`: Propostas recebidas dos veículos

- **Desires/Goals:**
  - `decidir`: Objetivo de escolher vencedor

- **Intentions/Plans:**
  - `coletar_propostas`: Recebe propostas dos veículos
  - `decidir_vencedor`: Avalia e decide

---

## 🚀 COMO EXECUTAR

### Sistema Principal:
```bash
python cruzamento_maspy_v2.py
```

### Suite de Experimentos:
```bash
python experimentos_cruzamento.py
```

---

## 📋 RESUMO DE CONFORMIDADE

| Requisito | Status | Arquivo/Localização |
|-----------|--------|---------------------|
| 2 tipos de agentes | ✅ | `cruzamento_maspy_v2.py` |
| 5+ instâncias | ✅ | `cruzamento_maspy_v2.py:241-245` |
| 1 ambiente | ✅ | `cruzamento_maspy_v2.py:45-80` |
| Protocolo negociação | ✅ | `cruzamento_maspy_v2.py:22-27` |
| Análise PEAS | ✅ | `cruzamento_maspy_v2.py:16-20` |
| Implementação completa | ✅ | `cruzamento_maspy_v2.py` |
| Experimentos | ✅ | `experimentos_cruzamento.py` |
| Diagramas UML | ⏳ | A fazer no artigo |
| Artigo SBC | ⏳ | A escrever |
| Slides | ⏳ | A preparar |

**Legenda:**
✅ Completo | ⏳ Pendente | ❌ Não atende

---

## 🎯 CONCLUSÃO

O sistema atende **TODOS os requisitos de implementação (tarefas a-f)**:
- ✅ Tema definido e relevante
- ✅ Sistema totalmente funcional
- ✅ Todos os requisitos técnicos atendidos
- ✅ Experimentos abrangentes implementados

**Pendências:**
- Elaboração dos diagramas UML (tarefa d)
- Escrita do artigo no formato SBC (tarefa g)
- Preparação dos slides (tarefa h)

**Data de entrega:** 24/10/2025
