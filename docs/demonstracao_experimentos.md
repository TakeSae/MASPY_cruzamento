# Demonstração de Experimentos
## Sistema de Negociação em Cruzamento - MASPY

Este documento descreve os 6 experimentos planejados e como executá-los.

---

## 🧪 EXPERIMENTOS PLANEJADOS

### Experimento 1: Cenário Base
**Objetivo:** Verificar funcionamento básico com veículo de emergência

**Configuração:**
```python
Carro1:      prioridade = 10
Ambulancia:  prioridade = 100  ← DEVE VENCER
Moto1:       prioridade = 5
Onibus1:     prioridade = 30
```

**Resultado Esperado:** Ambulância vence (emergência tem prioridade)

**Como executar:**
```bash
python cruzamento_maspy_v2.py
```

---

### Experimento 2: Múltiplas Emergências
**Objetivo:** Testar desempate entre veículos de emergência

**Configuração:**
```python
Ambulancia1: prioridade = 100  ← DEVE VENCER
Ambulancia2: prioridade = 95
Bombeiros:   prioridade = 98
Carro1:      prioridade = 10
```

**Resultado Esperado:** Ambulancia1 vence (maior prioridade entre emergências)

**Como executar:** Editar `cruzamento_maspy_v2.py` linhas 241-245 com essa configuração

---

### Experimento 3: Prioridades Iguais
**Objetivo:** Verificar critério de desempate quando prioridades são iguais

**Configuração:**
```python
Carro1: prioridade = 10
Carro2: prioridade = 10
Carro3: prioridade = 10
Carro4: prioridade = 10
```

**Resultado Esperado:** Sistema decide por ordem de processamento das mensagens

**Como executar:** Editar configuração no arquivo principal

---

### Experimento 4: Cargas Pesadas
**Objetivo:** Testar diferentes tipos de veículos com prioridades variadas

**Configuração:**
```python
Caminhao1: prioridade = 50  ← DEVE VENCER
Onibus1:   prioridade = 40
Moto1:     prioridade = 5
Carro1:    prioridade = 10
```

**Resultado Esperado:** Caminhão vence (maior prioridade)

---

### Experimento 5: Cenário Misto
**Objetivo:** Teste de escala com 6 veículos

**Configuração:**
```python
Moto1:      prioridade = 5
Carro1:     prioridade = 15
Onibus1:    prioridade = 35
Caminhao1:  prioridade = 45
Taxi1:      prioridade = 20
Ambulancia: prioridade = 100  ← DEVE VENCER
```

**Resultado Esperado:** Ambulância vence mesmo com mais competidores

---

### Experimento 6: Teste de Estresse
**Objetivo:** Verificar escalabilidade do sistema

**Configuração:**
```python
Veiculo1:  prioridade = 10
Veiculo2:  prioridade = 20
Veiculo3:  prioridade = 30
...
Veiculo10: prioridade = 100  ← DEVE VENCER
```

**Resultado Esperado:** Sistema suporta 10 veículos simultâneos

---

## 📊 TEMPLATE PARA COLETA DE DADOS

### Para cada experimento, registre:

**Experimento N:** [Nome]

| Medida | Valor |
|--------|-------|
| Número de veículos | X |
| Veículo vencedor | Y |
| Prioridade vencedora | Z |
| Tempo de execução | T segundos |
| Sistema encerrou corretamente? | Sim/Não |

**Observações:**
- [Comportamentos notados]
- [Resultados inesperados]

---

## 🎯 INSTRUÇÕES PARA EXECUTAR CADA EXPERIMENTO

### Método 1: Modificar arquivo principal
1. Abrir `cruzamento_maspy_v2.py`
2. Modificar linhas 241-245 (criação dos veículos)
3. Executar: `python cruzamento_maspy_v2.py`
4. Registrar resultados
5. Repetir para próximo experimento

### Método 2: Executar experimentos individuais
```python
# No terminal Python
from experimentos_cruzamento import *
experimento_1_base()  # Executar um de cada vez
```

**IMPORTANTE:** Devido a limitações do MASPY, executar APENAS UM experimento por vez.
Não tente executar todos sequencialmente no mesmo processo.

---

## 📝 COLETA DE DADOS PARA O ARTIGO

### Dados a coletar:

1. **Funcionalidade**
   - ✅ Sistema negocia corretamente?
   - ✅ Prioridades são respeitadas?
   - ✅ Sistema encerra automaticamente?

2. **Escalabilidade**
   - Quantos veículos o sistema suporta?
   - Tempo de negociação aumenta linearmente?

3. **Robustez**
   - Sistema lida com empates?
   - Sistema lida com múltiplas emergências?

4. **Protocolo de Negociação**
   - Todas as fases são executadas?
   - Mensagens chegam corretamente?
   - Broadcast funciona?

---

## 🔬 RESULTADOS ESPERADOS (RESUMO)

| Experimento | Vencedor Esperado | Justificativa |
|-------------|-------------------|---------------|
| 1. Base | Ambulância | Emergência tem máxima prioridade |
| 2. Múltiplas Emerg. | Ambulancia1 (100) | Maior valor entre emergências |
| 3. Prioridades Iguais | Primeiro processado | Critério de desempate |
| 4. Cargas Pesadas | Caminhão (50) | Maior prioridade do grupo |
| 5. Misto (6 veículos) | Ambulância (100) | Emergência prevalece |
| 6. Estresse (10 veic.) | Veiculo10 (100) | Maior prioridade |

---

## 💡 DICAS PARA O ARTIGO

**Seção de Experimentos deve incluir:**

1. **Metodologia**
   - Descrição de cada experimento
   - Configurações utilizadas
   - Critérios de sucesso

2. **Resultados**
   - Tabela com resultados de cada teste
   - Gráficos (se aplicável)
   - Prints/logs das execuções

3. **Análise**
   - Sistema atendeu expectativas?
   - Protocolo funciona corretamente?
   - Limitações identificadas

4. **Discussão**
   - Comparação com outros protocolos
   - Vantagens da abordagem BDI
   - Possíveis melhorias

---

**Arquivo criado em:** 17/10/2025
**Para uso no:** Trabalho 1 - SMA 2025.2 - UTFPR
