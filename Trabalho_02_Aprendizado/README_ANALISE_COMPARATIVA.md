# Sistema de Análise Comparativa de Cenários

## Visão Geral

Sistema completo para execução, comparação e análise avançada de múltiplos cenários de aprendizado por reforço (Q-Learning) em um sistema multi-agentes de negociação em cruzamento.

**Autores:** Guilherme T. S. Abreu, Maria Eduarda S. Freitas
**Curso:** Sistemas Multiagentes - 2025.2 - UTFPR
**Trabalho:** 02 - Aprendizado por Reforço

---

## Estrutura de Arquivos

```
Trabalho_02_Aprendizado/
├── cruzamento_maspy_learning.py      # Sistema principal de aprendizado
├── executar_todos_cenarios.py        # Execução automática de todos os cenários
├── comparar_cenarios.py              # Comparação de cenários específicos
├── analisar_comparacao.py            # Módulo de análise comparativa avançada
├── testar_analise.py                 # Script de teste do sistema de análise
├── requirements_analise.txt          # Dependências para análise avançada
│
├── resultados/                       # Resultados individuais por execução
│   ├── 20251204_130354/
│   │   ├── info_execucao.txt
│   │   ├── metricas_aprendizado.csv
│   │   └── graficos/
│   ├── ...
│   └── ultima_execucao -> symlink
│
├── analise_comparativa/              # Análise consolidada de todos os cenários
│   ├── RELATORIO_COMPARATIVO.md      # Relatório principal
│   ├── metricas_consolidadas.csv     # Todas as métricas em CSV
│   ├── ranking_cenarios.json         # Ranking detalhado
│   └── graficos/                     # 6 visualizações comparativas
│       ├── 1_recompensa_media_por_cenario.png
│       ├── 2_evolucao_aprendizado_comparada.png
│       ├── 3_distribuicao_recompensas.png
│       ├── 4_taxa_convergencia.png
│       ├── 5_heatmap_metricas.png
│       └── 6_tempo_execucao.png
│
└── comparacao_cenarios.csv           # Tabela básica de comparação
```

---

## Instalação e Configuração

### 1. Ativar ambiente virtual MASPY

```bash
source ../venv_maspy/bin/activate
```

### 2. Instalar dependências da análise avançada

```bash
pip install -r requirements_analise.txt
```

Ou manualmente:
```bash
pip install numpy matplotlib seaborn
```

### 3. Verificar instalação

```bash
python testar_analise.py
```

---

## Cenários Disponíveis

O sistema oferece **10 cenários** pré-configurados:

| Cenário | Descrição | Veículos |
|---------|-----------|----------|
| `padrao` | Cenário padrão com prioridades variadas | 10 |
| `base` | Ambulância vs veículos normais | 10 |
| `emergencias` | Múltiplas emergências competindo | 10 |
| `iguais` | Todos com mesma prioridade | 10 |
| `pesados` | Foco em cargas pesadas (caminhões) | 10 |
| `transporte_publico` | Ônibus vs Táxi vs particulares | 10 |
| `prioridades_proximas` | Diferenças pequenas (desafio) | 10 |
| `extremos` | Grande diferença (1 vs 100) | 10 |
| `escalonado` | Escala uniforme 10-100 | 10 |
| `misto_complexo` | Mix complexo de todos os tipos | 10 |

---

## Como Usar

### Opção 1: Executar Todos os Cenários (Automático)

**Recomendado para análise completa**

```bash
python executar_todos_cenarios.py
```

**O que faz:**
1. Executa **10 cenários × 1000 episódios** cada
2. Salva resultados individuais em `resultados/TIMESTAMP/`
3. Gera tabela comparativa básica: `comparacao_cenarios.csv`
4. **Executa análise comparativa avançada automaticamente**
5. Gera relatório completo em `analise_comparativa/`

**Tempo estimado:** ~2-4 horas (depende do hardware)

---

### Opção 2: Comparar Cenários Específicos

```bash
# Comparar 3 cenários específicos
python comparar_cenarios.py --cenarios base emergencias pesados --episodios 1000

# Executar todos os cenários disponíveis
python comparar_cenarios.py --cenarios todos --episodios 1000

# Com logs detalhados
python comparar_cenarios.py --cenarios base emergencias --episodios 1000 --verbose
```

---

### Opção 3: Executar Cenário Individual

```bash
python cruzamento_maspy_learning.py --experimento base --episodios 1000
```

---

### Opção 4: Análise Avançada de Resultados Existentes

Se você já executou cenários e tem resultados em `resultados/`, pode executar apenas a análise:

```bash
python analisar_comparacao.py --resultados resultados/20251204_* --output minha_analise
```

---

## Análises Geradas

### 1. **Relatório Principal** (`RELATORIO_COMPARATIVO.md`)

Relatório em Markdown com:
- Ranking de desempenho dos cenários
- Análise detalhada por cenário
- Insights e conclusões
- Recomendações

### 2. **Gráficos Comparativos** (6 visualizações)

#### 1. Recompensa Média por Cenário
- Gráfico de barras ordenado por desempenho
- Mostra qual cenário teve melhor aprendizado

#### 2. Evolução de Aprendizado Comparada
- Curvas de aprendizado de todos os cenários
- Média móvel de 50 episódios para suavização
- Compara convergência ao longo do tempo

#### 3. Distribuição de Recompensas (Boxplot)
- Mostra dispersão e quartis
- Identifica outliers
- Compara estabilidade entre cenários

#### 4. Taxa de Convergência
- Melhoria do início para o fim do treinamento
- Valores positivos = aprendizado efetivo
- Ordenado por taxa de convergência

#### 5. Heatmap de Métricas Normalizadas
- Visão consolidada de múltiplas métricas
- Normalizado 0-1 (1.0 = melhor)
- Facilita identificação de trade-offs

#### 6. Tempo de Execução
- Gráfico horizontal comparando tempo
- Útil para avaliar custo computacional

### 3. **Dados Consolidados**

#### `metricas_consolidadas.csv`
CSV com todas as métricas para análise posterior:
- Cenário
- Timestamp
- Número de episódios
- Recompensas (média, total, min, max, desvio)
- Taxa de convergência
- Melhoria Q1→Q4
- Tempo de execução

#### `ranking_cenarios.json`
JSON com ranking detalhado e scores

---

## Métricas Calculadas

### Métricas Básicas
- **Recompensa Média:** Média de todas as recompensas
- **Recompensa Total:** Soma de todas as recompensas
- **Recompensa Min/Max:** Limites observados
- **Desvio Padrão:** Variabilidade das recompensas

### Métricas de Convergência
- **Taxa de Convergência:** `(média_final_10% - média_inicial_10%) / média_inicial_10% × 100`
- **Melhoria Q1→Q4:** Diferença entre último e primeiro quartil
- **Média Móvel:** Suavização para identificar tendências

### Score de Ranking
Combinação ponderada:
- **50%** Recompensa média
- **30%** Taxa de convergência
- **20%** Melhoria Q1→Q4

---

## Testando o Sistema

### Teste Completo
```bash
python testar_analise.py
```

**Verifica:**
1. Dependências instaladas
2. Módulo de análise funcionando
3. Resultados disponíveis
4. Executa análise de teste com últimos 3 resultados

**Output:** `teste_analise_comparativa/`

---

## Configurações

### Modificar número de episódios

**Em `executar_todos_cenarios.py` (linha 59):**
```python
EPISODIOS_CONFIGS = [1000]  # Altere para [500, 1000, 2000] para comparar diferentes quantidades
```

### Adicionar novos cenários

**Em `cruzamento_maspy_learning.py` (dicionário `EXPERIMENTOS`):**
```python
"meu_cenario": {
    "titulo": "Meu Cenário Personalizado",
    "descricao": "Descrição do cenário",
    "veiculos": [
        {"nome": "Veiculo1", "tipo": "carro", "prioridade": 50},
        # ... mais veículos
    ]
}
```

Depois adicione em `executar_todos_cenarios.py` (lista `CENARIOS`):
```python
CENARIOS = [
    # ... cenários existentes
    "meu_cenario"
]
```

---

## Dicas de Uso

### Para Trabalhos Acadêmicos
1. Execute `executar_todos_cenarios.py` para gerar dados completos
2. Analise o relatório `RELATORIO_COMPARATIVO.md`
3. Use os gráficos gerados em apresentações/artigos
4. Consulte `metricas_consolidadas.csv` para tabelas

### Para Debugging
1. Execute cenário individual com logs: `python cruzamento_maspy_learning.py --experimento base --episodios 100`
2. Use `--verbose` no `comparar_cenarios.py`
3. Verifique `resultados/TIMESTAMP/info_execucao.txt`

### Para Análise Estatística
1. Importe `metricas_consolidadas.csv` em Excel/Python/R
2. Use `ranking_cenarios.json` para análises programáticas
3. Scripts customizados podem importar `AnalisadorComparativo`

---

## Solução de Problemas

### Erro: "No module named 'seaborn'"
```bash
pip install seaborn
# ou
pip install -r requirements_analise.txt
```

### Erro: "Nenhum resultado para gerar tabela"
Execute primeiro alguns cenários:
```bash
python cruzamento_maspy_learning.py --experimento base --episodios 100
```

### Gráficos não são gerados
Verifique se matplotlib está instalado:
```bash
pip install matplotlib
```

### Análise muito lenta
Reduza número de episódios ou cenários:
```python
EPISODIOS_CONFIGS = [100]  # Ao invés de 1000
CENARIOS = ["base", "emergencias"]  # Ao invés de todos
```

---

## Referências

- **MASPY Framework:** Sistema multi-agentes Python
- **Q-Learning:** Algoritmo de aprendizado por reforço
- **Matplotlib:** Biblioteca de visualização
- **Seaborn:** Visualizações estatísticas avançadas

---

## Contribuições

**Desenvolvido por:**
- Guilherme T. S. Abreu
- Maria Eduarda S. Freitas

**Disciplina:** Sistemas Multiagentes
**Semestre:** 2025.2
**Instituição:** UTFPR

---

## Licença

Trabalho acadêmico desenvolvido para fins educacionais.

---

## Trabalho 02 - Aprendizado por Reforço

Este sistema é parte do Trabalho 02 da disciplina de Sistemas Multiagentes, focado em:
- Implementação de aprendizado por reforço (Q-Learning)
- Sistema multi-agentes de negociação
- Análise comparativa de diferentes cenários
- Visualização e interpretação de resultados

**Data:** Dezembro 2025
