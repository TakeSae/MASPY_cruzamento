# Resumo Final - Sistema de Negociação em Cruzamento
## Trabalho 1 - Sistemas Multi-Agentes 2025.2

**Data:** 17/10/2025
**Instituição:** UTFPR - Campus Ponta Grossa
**Disciplina:** Sistemas Multi-Agentes
**Professor:** Gleifer Vaz Alves

---

## ✅ STATUS DO PROJETO

### Implementação: **100% COMPLETA**

Todos os requisitos técnicos do trabalho foram atendidos e testados com sucesso.

---

## 📁 ARQUIVOS ENTREGUES

### 1. **cruzamento_maspy_v2.py** - Sistema Principal ✅
**Conteúdo:**
- 2 tipos de agentes (VeiculoAgent + CoordenadorAgent)
- 1 ambiente (CruzamentoEnvironment)
- 5 instâncias de agentes (1 coordenador + 4 veículos)
- Protocolo de negociação completo
- Análise PEAS documentada
- Arquitetura BDI implementada
- **FUNCIONA E ENCERRA CORRETAMENTE**

**Como executar:**
```bash
python cruzamento_maspy_v2.py
```

**Saída esperada:**
- Ambulância (prioridade 100) vence a negociação
- Sistema encerra automaticamente
- Tempo de execução: ~2 segundos

---

### 2. **teste_individual.py** - Suite de Testes ✅
**Conteúdo:**
- 6 experimentos individuais
- Testa diferentes cenários de negociação
- Cada experimento executa independentemente

**Como executar:**
```bash
python teste_individual.py [1-6]
```

**Experimentos disponíveis:**
1. **Cenário Base:** 1 ambulância vs 3 normais → Ambulância vence
2. **Múltiplas Emergências:** 3 emergências competindo → Maior prioridade vence
3. **Prioridades Iguais:** 4 carros iguais → Ordem de processamento decide
4. **Cargas Pesadas:** Caminhão vs outros → Caminhão (prio=50) vence
5. **Cenário Misto:** 6 veículos variados → Ambulância vence
6. **Teste de Estresse:** 10 veículos simultâneos → Veiculo10 (prio=100) vence

**TODOS OS 6 EXPERIMENTOS TESTADOS E FUNCIONANDO!**

---

### 3. **experimentos_cruzamento.py** - Código dos Experimentos
Contém as funções de cada experimento para referência e documentação.

---

### 4. **demonstracao_experimentos.md** - Guia de Experimentos
Manual detalhado explicando:
- Cada experimento
- Configurações utilizadas
- Resultados esperados
- Como coletar dados para o artigo

---

### 5. **VERIFICACAO_REQUISITOS.md** - Checklist Completo
Verificação ponto a ponto de todos os requisitos do PDF do trabalho.

---

## 🎯 VERIFICAÇÃO DE CONFORMIDADE

### Tarefa (b) - Requisitos de Implementação:

| Requisito | Status | Evidência |
|-----------|--------|-----------|
| ✅ 2 tipos de agentes | **ATENDE** | VeiculoAgent + CoordenadorAgent |
| ✅ 5+ instâncias | **ATENDE** | 1 coordenador + 4 veículos = 5 |
| ✅ 1 ambiente | **ATENDE** | CruzamentoEnvironment (linhas 45-80) |
| ✅ Protocolo negociação | **ATENDE** | 6 fases documentadas (linhas 22-27) |

### Tarefa (c) - PEAS:
✅ **DOCUMENTADO** no código (linhas 16-20)

### Tarefa (e) - Implementação:
✅ **COMPLETA E FUNCIONAL**

### Tarefa (f) - Experimentos:
✅ **6 EXPERIMENTOS IMPLEMENTADOS E TESTADOS**

---

## 🧪 RESULTADOS DOS EXPERIMENTOS

### Experimento 1: Cenário Base ✅
- **Vencedor:** Ambulância (prioridade 100)
- **Status:** Passou
- **Conclusão:** Emergências são corretamente priorizadas

### Experimento 2: Múltiplas Emergências ✅
- **Vencedor:** Ambulancia1 (prioridade 100)
- **Status:** Passou
- **Conclusão:** Desempate entre emergências funciona

### Experimento 3: Prioridades Iguais ✅
- **Vencedor:** Primeiro processado
- **Status:** Passou
- **Conclusão:** Critério de desempate consistente

### Experimento 4: Cargas Pesadas ✅
- **Vencedor:** Caminhão (prioridade 50)
- **Status:** Passou
- **Conclusão:** Diferentes tipos são suportados

### Experimento 5: Cenário Misto ✅
- **Vencedor:** Ambulância (prioridade 100)
- **Status:** Passou
- **Conclusão:** Sistema escala para 6 veículos

### Experimento 6: Teste de Estresse ✅
- **Vencedor:** Veiculo10 (prioridade 100)
- **Status:** Passou
- **Conclusão:** Sistema suporta 10 veículos simultâneos

**TAXA DE SUCESSO: 6/6 (100%)**

---

## 🏗️ ARQUITETURA BDI

### VeiculoAgent
**Beliefs:**
- Tipo do veículo
- Prioridade

**Goals:**
- Atravessar o cruzamento

**Plans:**
- `enviar_proposta`: Envia dados ao coordenador
- `receber_decisao`: Reage à decisão

### CoordenadorAgent
**Beliefs:**
- Propostas dos veículos

**Goals:**
- Decidir vencedor

**Plans:**
- `coletar_propostas`: Recebe propostas
- `decidir_vencedor`: Avalia e decide

---

## 📊 PROTOCOLO DE NEGOCIAÇÃO

**Fases do Protocolo:**
1. Veículos enviam propostas (tell) ao Coordenador
2. Coordenador coleta todas as propostas
3. Coordenador avalia prioridades
4. Coordenador decide vencedor (maior prioridade)
5. Coordenador notifica todos (broadcast)
6. Veículos reagem à decisão

**Tipo de Protocolo:** Leilão de primeiro preço com anunciador central

---

## 🔧 TECNOLOGIAS UTILIZADAS

- **Framework:** MASPY 2025.6.7
- **Linguagem:** Python 3.x
- **Paradigma:** Programação Orientada a Agentes (BDI)
- **Comunicação:** Troca de mensagens assíncrona (tell, broadcast)

---

## 📈 ANÁLISE PEAS

**Performance:**
- Minimizar tempo de espera no cruzamento
- Priorizar veículos de emergência
- Garantir segurança (um por vez)

**Environment:**
- Cruzamento de 4 vias
- Dinâmico (veículos chegam assincronamente)
- Multiagente (vários veículos simultâneos)
- Observável parcialmente (cada agente vê suas informações)

**Actuators:**
- Enviar propostas
- Decidir vencedor
- Atravessar cruzamento
- Notificar decisões

**Sensors:**
- Receber propostas (coordenador)
- Detectar decisão (veículos)
- Perceber chegada de novos veículos

---

## ⏭️ PRÓXIMAS ETAPAS

### Para completar o trabalho:

1. **Diagramas UML** (Tarefa d)
   - Diagrama de classes dos agentes
   - Diagrama do ambiente
   - Diagrama de sequência do protocolo

2. **Artigo SBC** (Tarefa g)
   - Introdução
   - Trabalhos relacionados
   - Modelagem (PEAS + Diagramas)
   - Implementação
   - Experimentos e resultados
   - Conclusão

3. **Slides** (Tarefa h)
   - Apresentação de 10-15 slides
   - Demonstração ao vivo

---

## 🎓 USO DE IA

**Ferramenta utilizada:** Claude (Anthropic)

**Áreas onde IA foi usada:**
- Implementação do código MASPY
- Estruturação dos experimentos
- Documentação técnica
- Debugging e otimizações

**Observação:** Conforme requisito do trabalho, o uso de IA está sendo declarado.

---

## 📞 SUPORTE

**Arquivos importantes:**
- `cruzamento_maspy_v2.py` - Execute este para demonstração básica
- `teste_individual.py [1-6]` - Execute para experimentos específicos
- `VERIFICACAO_REQUISITOS.md` - Checklist completo

**Em caso de dúvidas:**
1. Verifique `demonstracao_experimentos.md` para instruções detalhadas
2. Todos os experimentos foram testados e funcionam
3. Código está bem documentado com comentários

---

## ✨ CONCLUSÃO

O sistema de negociação em cruzamento foi implementado com sucesso utilizando o framework MASPY. Todos os requisitos técnicos foram atendidos:

✅ Arquitetura BDI completa
✅ Protocolo de negociação funcional
✅ Ambiente definido
✅ Múltiplos agentes interagindo
✅ 6 experimentos validados
✅ Sistema robusto e escalável

**O código está pronto para uso no trabalho acadêmico.**

---

**Última atualização:** 17/10/2025
**Status:** ✅ PRONTO PARA ENTREGA
