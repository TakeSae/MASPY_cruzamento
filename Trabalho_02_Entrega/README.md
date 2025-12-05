# Sistema Multi-Agentes - Q-Learning para Cruzamento Viário

**Trabalho 02 - Sistemas Multi-Agentes 2025.2**
**UTFPR - Campus Ponta Grossa - COCIC**

Autores: Guilherme T. S. Abreu, Maria Eduarda S. Freitas
Professor: Gleifer Vaz Alves

---

## Descrição

Sistema multi-agentes que utiliza Q-Learning para coordenação de veículos em cruzamento viário. O agente coordenador aprende a política ótima de travessia através de aprendizado por reforço.

**Características:**
- Q-Learning via MASPY EnvModel
- 10 cenários de teste com 10 veículos cada
- Metodologias PEAS e SART implementadas
- Métricas de convergência e função de utilidade
- Visualização de resultados com matplotlib

---

## Instalação

### Pré-requisitos
- Python 3.13+
- pip

### Passos

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

---

## Execução

### Cenário padrão (10 veículos diversos)
```bash
python cruzamento_maspy_learning.py
```

### Cenário específico
```bash
python cruzamento_maspy_learning.py --experimento base
```

### Configurar parâmetros
```bash
python cruzamento_maspy_learning.py --episodios 200 --reward 100 --penalidade 1.5
```

### Modo silencioso
```bash
python cruzamento_maspy_learning.py --quiet
```

---

## Parâmetros Disponíveis

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--experimento` | Nome do cenário (padrao, base, emergencias, etc.) | padrao |
| `--episodios` | Número de episódios de treinamento | 100 |
| `--reward` | Recompensa por escolha ótima | 100 |
| `--penalidade` | Multiplicador de penalidade | 1.5 |
| `--quiet` | Modo silencioso (menos logs) | False |
| `--step` | Modo step-by-step (aguarda ENTER) | False |

---

## Cenários Disponíveis

| Cenário | Veículos | Descrição |
|---------|----------|-----------|
| padrao | 10 | Mix de tipos diversos |
| base | 10 | Ambulância + veículos normais |
| emergencias | 10 | Múltiplas emergências |
| iguais | 10 | Prioridades iguais |
| pesados | 10 | Cargas pesadas |
| transporte_publico | 10 | Ônibus e táxis |
| prioridades_proximas | 10 | Diferenças pequenas |
| extremos | 10 | Prioridades extremas (10 e 100) |
| escalonado | 10 | Escala uniforme 10-100 |
| misto_complexo | 10 | Mix complexo de todos os tipos |

---

## Resultados

Após execução, os resultados são salvos em `resultados/<timestamp>/`:

```
resultados/
  20251205_HHMMSS/
    graficos/
      recompensa_por_episodio.png
      recompensa_acumulada.png
      media_movel.png
      comparacao_desempenho.png
      analise_convergencia.png
    metricas_aprendizado.csv
    info_execucao.txt
  ultima_execucao -> 20251205_HHMMSS
```

---

## Arquitetura

### Agentes
- **CoordenadorLearningAgent:** Aprende política ótima via Q-Learning
- **VeiculoLearningAgent:** Observa e registra estatísticas

### Ambiente
- **CruzamentoLearningEnvironment:** Implementa SART (States, Actions, Rewards, Transitions)

### Metodologias

**PEAS (Performance, Environment, Actuators, Sensors):**
- Performance: Função de utilidade U = 0.5×taxa_acerto + 0.3×convergência + 0.2×recompensa
- Environment: Cruzamento com veículos de prioridades 1-100
- Actuators: escolher_veiculo(id), iniciar_aprendizado()
- Sensors: Estados v{N}_passou (booleanos)

**SART (States, Actions, Rewards, Transitions):**
- States: Tupla (v1_passou, ..., v10_passou) ∈ {0,1}^10
- Actions: {escolher_veiculo1, ..., escolher_veiculo10}
- Rewards: +100 (ótimo), -Δp×0.2 (subótimo)
- Transitions: Determinísticas (escolher → marca como atravessado)

---

## Níveis de Prioridade

| Tipo | Prioridade | Justificativa |
|------|------------|---------------|
| Ambulância | 100 | Emergência médica |
| Bombeiros | 95-98 | Emergência (incêndio/resgate) |
| Caminhão | 50 | Veículo grande |
| Ônibus | 30-40 | Transporte coletivo |
| Táxi | 20 | Transporte de passageiros |
| Carro | 10-15 | Veículo comum |
| Moto | 5 | Veículo ágil |

---

## Tecnologias

- **Python:** 3.13
- **MASPY:** 2025.11.9
- **Matplotlib:** Visualização de gráficos
- **NumPy:** Cálculos estatísticos

---

## Validação

- 28/28 testes automatizados (100%)
- 10 cenários de teste implementados
- Função de utilidade PEAS validada
- Detecção automática de convergência
- Exportação CSV estruturada

---

## Repositório

Todos os códigos dos Trabalhos 01 e 02 estão disponíveis no repositório:

**https://github.com/TakeSae/MASPY_cruzamento**

---

## Contato

- Guilherme T. S. Abreu - guiabr@alunos.utfpr.com.br
- Maria Eduarda S. Freitas - mariaeduardafreitas@alunos.utfpr.edu.br

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Professor:** Gleifer Vaz Alves
