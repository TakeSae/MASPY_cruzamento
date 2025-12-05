# Relatório Comparativo de Cenários

## Análise de Aprendizado por Reforço (Q-Learning)

**Data da Análise:** 05/12/2025 18:22:09

**Total de Execuções Analisadas:** 10

**Cenários Comparados:** 10

---

## Ranking de Desempenho

| Posição | Cenário | Score Total | Recompensa Média | Taxa Convergência | Melhoria Q1→Q4 |
|---------|---------|-------------|------------------|-------------------|----------------|
| 1 | escalonado | 1540.42 | 737.2 | 3408.2% | 746.8 |
| 2 | pesados | 622.71 | 796.8 | 356.3% | 587.1 |
| 3 | transporte_publico | 602.27 | 815.7 | 293.5% | 532.0 |
| 4 | iguais | 500.00 | 1000.0 | 0.0% | 0.0 |
| 5 | prioridades_proximas | 462.86 | 669.6 | 177.0% | 374.9 |
| 6 | extremos | 26.21 | 671.9 | -1492.6% | 690.0 |
| 7 | emergencias | -202.37 | 741.7 | -2425.0% | 771.4 |
| 8 | padrao | -315.68 | 659.9 | -2630.3% | 717.2 |
| 9 | misto_complexo | -680.91 | 728.9 | -4020.2% | 803.4 |
| 10 | base | -743.67 | 772.6 | -4236.4% | 704.7 |

---

## Análise Detalhada por Cenário

### base

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 772.65 ± 0.00
- **Recompensa Total Média:** 772650.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** -4236.4%
- **Melhoria Q1→Q4:** 704.7

### emergencias

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 741.73 ± 0.00
- **Recompensa Total Média:** 741728.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** -2425.0%
- **Melhoria Q1→Q4:** 771.4

### escalonado

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 737.25 ± 0.00
- **Recompensa Total Média:** 737250.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** 3408.2%
- **Melhoria Q1→Q4:** 746.8

### extremos

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 671.94 ± 0.00
- **Recompensa Total Média:** 671944.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** -1492.6%
- **Melhoria Q1→Q4:** 690.0

### iguais

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 1000.00 ± 0.00
- **Recompensa Total Média:** 1000000.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** 0.0%
- **Melhoria Q1→Q4:** 0.0

### misto_complexo

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 728.92 ± 0.00
- **Recompensa Total Média:** 728924.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** -4020.2%
- **Melhoria Q1→Q4:** 803.4

### padrao

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 659.94 ± 0.00
- **Recompensa Total Média:** 659942.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** -2630.3%
- **Melhoria Q1→Q4:** 717.2

### pesados

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 796.80 ± 0.00
- **Recompensa Total Média:** 796805.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** 356.3%
- **Melhoria Q1→Q4:** 587.1

### prioridades_proximas

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 669.58 ± 0.00
- **Recompensa Total Média:** 669578.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** 177.0%
- **Melhoria Q1→Q4:** 374.9

### transporte_publico

- **Número de Execuções:** 1
- **Episódios:** 1000
- **Recompensa Média:** 815.66 ± 0.00
- **Recompensa Total Média:** 815660.0
- **Tempo Médio de Execução:** 1.0s (0.0 min)
- **Taxa de Convergência:** 293.5%
- **Melhoria Q1→Q4:** 532.0

---

## Visualizações

### Gráficos Comparativos Gerados:

1. **Recompensa Média por Cenário** - `graficos/1_recompensa_media_por_cenario.png`
2. **Evolução de Aprendizado Comparada** - `graficos/2_evolucao_aprendizado_comparada.png`
3. **Distribuição de Recompensas** - `graficos/3_distribuicao_recompensas.png`
4. **Taxa de Convergência** - `graficos/4_taxa_convergencia.png`
5. **Heatmap de Métricas** - `graficos/5_heatmap_metricas.png`
6. **Tempo de Execução** - `graficos/6_tempo_execucao.png`

---

## Insights e Conclusões

### Melhor Cenário: **escalonado**

- Score Total: **1540.42**
- Recompensa Média: **737.2**
- Taxa de Convergência: **3408.2%**

### Recomendações:

1. Utilizar cenários com alta taxa de convergência para treinamento eficiente
2. Analisar cenários com baixa variância para maior estabilidade
3. Considerar trade-off entre tempo de execução e desempenho

---

**Relatório gerado automaticamente pelo sistema de análise comparativa**

*Sistemas Multiagentes - 2025.2 - UTFPR*
*Trabalho 02 - Aprendizado por Reforço*
