#!/usr/bin/env python3
"""
Módulo de análise comparativa avançada para múltiplos cenários de aprendizado.
Gera gráficos consolidados, análises estatísticas e relatórios comparativos.

Sistemas Multiagentes - 2025.2 - UTFPR
Trabalho 02 - Aprendizado por Reforço
Autores: Guilherme T. S. Abreu, Maria Eduarda S. Freitas
"""

import os
import csv
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

# Configurar estilo dos gráficos
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class AnalisadorComparativo:
    """
    Classe para análise comparativa avançada de múltiplos cenários.
    """

    def __init__(self, resultados_dirs: List[str], output_dir: str = "analise_comparativa"):
        """
        Inicializa o analisador comparativo.

        Args:
            resultados_dirs: Lista de diretórios de resultados a analisar
            output_dir: Diretório para salvar análises consolidadas
        """
        self.resultados_dirs = resultados_dirs
        self.output_dir = output_dir
        self.dados_consolidados = []
        self.metricas_por_cenario = defaultdict(list)

        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "graficos"), exist_ok=True)

    def coletar_dados(self):
        """
        Coleta dados de todos os diretórios de resultados.
        """
        print("\n" + "="*70)
        print("COLETANDO DADOS DOS CENÁRIOS")
        print("="*70 + "\n")

        for dir_resultado in self.resultados_dirs:
            dir_path = Path(dir_resultado)

            if not dir_path.exists():
                print(f"[AVISO] Diretório não encontrado: {dir_resultado}")
                continue

            # Ler informações da execução
            info_path = dir_path / "info_execucao.txt"
            metricas_path = dir_path / "metricas_aprendizado.csv"

            dados = {
                'diretorio': str(dir_resultado),
                'timestamp': dir_path.name,
            }

            # Ler info_execucao.txt
            if info_path.exists():
                with open(info_path, 'r') as f:
                    for linha in f:
                        if ':' in linha:
                            chave, valor = linha.split(':', 1)
                            chave = chave.strip()
                            valor = valor.strip()

                            if chave == "Experimento":
                                dados['experimento'] = valor
                            elif chave == "Número de episódios":
                                dados['episodios'] = int(valor)
                            elif chave == "Número de veículos":
                                dados['num_veiculos'] = int(valor)
                            elif chave == "Tempo total de execução (s)":
                                dados['tempo_execucao'] = float(valor)
                            elif chave == "Recompensa por escolha correta":
                                dados['recompensa_correta'] = int(valor)

            # Ler metricas_aprendizado.csv
            if metricas_path.exists():
                recompensas = []
                episodios_lista = []

                with open(metricas_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for linha in reader:
                        recompensas.append(float(linha['Recompensa']))
                        episodios_lista.append(int(linha['Episodio']))

                if recompensas:
                    dados['recompensas'] = recompensas
                    dados['episodios_lista'] = episodios_lista
                    dados['recompensa_media'] = np.mean(recompensas)
                    dados['recompensa_total'] = sum(recompensas)
                    dados['recompensa_min'] = min(recompensas)
                    dados['recompensa_max'] = max(recompensas)
                    dados['recompensa_std'] = np.std(recompensas)

                    # Métricas de convergência
                    # Dividir em quartis e verificar melhoria
                    q1 = recompensas[:len(recompensas)//4]
                    q4 = recompensas[3*len(recompensas)//4:]
                    dados['melhoria_q1_q4'] = np.mean(q4) - np.mean(q1) if q1 and q4 else 0

                    # Taxa de convergência (últimos 10% vs primeiros 10%)
                    n = len(recompensas)
                    inicio = recompensas[:max(1, n//10)]
                    fim = recompensas[-max(1, n//10):]
                    dados['taxa_convergencia'] = (np.mean(fim) - np.mean(inicio)) / np.mean(inicio) * 100 if np.mean(inicio) != 0 else 0

            if 'experimento' in dados:
                self.dados_consolidados.append(dados)
                self.metricas_por_cenario[dados['experimento']].append(dados)
                print(f"[OK] Coletado: {dados['experimento']} ({dados.get('episodios', '?')} episódios)")
            else:
                print(f"[AVISO] Dados incompletos em: {dir_resultado}")

        print(f"\n[OK] Total de {len(self.dados_consolidados)} execuções coletadas")
        print(f"[OK] {len(self.metricas_por_cenario)} cenários diferentes\n")

        return self.dados_consolidados

    def gerar_graficos_consolidados(self):
        """
        Gera gráficos comparativos consolidados.
        """
        print("\n" + "="*70)
        print("GERANDO GRÁFICOS CONSOLIDADOS")
        print("="*70 + "\n")

        graficos_dir = os.path.join(self.output_dir, "graficos")

        # 1. Gráfico de barras - Recompensa média por cenário
        self._grafico_recompensa_media(graficos_dir)

        # 2. Gráfico de evolução - Curvas de aprendizado comparadas
        self._grafico_evolucao_comparada(graficos_dir)

        # 3. Boxplot - Distribuição de recompensas
        self._grafico_boxplot_recompensas(graficos_dir)

        # 4. Gráfico de convergência
        self._grafico_convergencia(graficos_dir)

        # 5. Heatmap de métricas
        self._grafico_heatmap_metricas(graficos_dir)

        # 6. Comparação de tempo de execução
        self._grafico_tempo_execucao(graficos_dir)

        print(f"\n[OK] Gráficos salvos em: {graficos_dir}/\n")

    def _grafico_recompensa_media(self, output_dir):
        """Gráfico de barras com recompensa média por cenário."""
        plt.figure(figsize=(14, 8))

        cenarios = []
        medias = []
        stds = []
        cores = []

        # Cores do seaborn
        palette = sns.color_palette("husl", len(self.metricas_por_cenario))

        for i, (cenario, dados_list) in enumerate(sorted(self.metricas_por_cenario.items())):
            # Calcular média entre todas as execuções do mesmo cenário
            recompensas_medias = [d['recompensa_media'] for d in dados_list if 'recompensa_media' in d]

            if recompensas_medias:
                cenarios.append(cenario)
                medias.append(np.mean(recompensas_medias))
                stds.append(np.std(recompensas_medias))
                cores.append(palette[i])

        # Ordenar por média (decrescente)
        indices_ordenados = np.argsort(medias)[::-1]
        cenarios = [cenarios[i] for i in indices_ordenados]
        medias = [medias[i] for i in indices_ordenados]
        stds = [stds[i] for i in indices_ordenados]
        cores = [cores[i] for i in indices_ordenados]

        # Plotar
        bars = plt.bar(range(len(cenarios)), medias, yerr=stds, capsize=5,
                       color=cores, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Adicionar valores nas barras
        for i, (bar, media) in enumerate(zip(bars, medias)):
            altura = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., altura,
                    f'{media:.1f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.xlabel('Cenário', fontsize=12, fontweight='bold')
        plt.ylabel('Recompensa Média', fontsize=12, fontweight='bold')
        plt.title('Comparação de Recompensa Média por Cenário\n(ordenado por desempenho)',
                 fontsize=14, fontweight='bold', pad=20)
        plt.xticks(range(len(cenarios)), cenarios, rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        plt.savefig(os.path.join(output_dir, "1_recompensa_media_por_cenario.png"), dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Gráfico: Recompensa média por cenário")

    def _grafico_evolucao_comparada(self, output_dir):
        """Gráfico de linhas comparando evolução de aprendizado."""
        plt.figure(figsize=(16, 10))

        # Usar média móvel para suavizar curvas
        janela = 50

        for cenario, dados_list in sorted(self.metricas_por_cenario.items()):
            # Usar a primeira (ou média) execução de cada cenário
            for dados in dados_list[:1]:  # Pegar apenas primeira execução
                if 'recompensas' in dados and 'episodios_lista' in dados:
                    recompensas = dados['recompensas']
                    episodios = dados['episodios_lista']

                    if len(recompensas) >= janela:
                        # Calcular média móvel
                        media_movel = np.convolve(recompensas, np.ones(janela)/janela, mode='valid')
                        episodios_mm = episodios[janela-1:]

                        plt.plot(episodios_mm, media_movel, label=cenario, linewidth=2, alpha=0.8)

        plt.xlabel('Episódio', fontsize=12, fontweight='bold')
        plt.ylabel('Recompensa (Média Móvel)', fontsize=12, fontweight='bold')
        plt.title(f'Evolução do Aprendizado - Comparação entre Cenários\n(Média móvel de {janela} episódios)',
                 fontsize=14, fontweight='bold', pad=20)
        plt.legend(loc='best', framealpha=0.9, fontsize=9)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        plt.savefig(os.path.join(output_dir, "2_evolucao_aprendizado_comparada.png"), dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Gráfico: Evolução de aprendizado comparada")

    def _grafico_boxplot_recompensas(self, output_dir):
        """Boxplot comparando distribuição de recompensas."""
        plt.figure(figsize=(14, 8))

        dados_boxplot = []
        labels = []

        for cenario, dados_list in sorted(self.metricas_por_cenario.items()):
            # Coletar todas as recompensas de todas as execuções
            todas_recompensas = []
            for dados in dados_list:
                if 'recompensas' in dados:
                    todas_recompensas.extend(dados['recompensas'])

            if todas_recompensas:
                dados_boxplot.append(todas_recompensas)
                labels.append(cenario)

        # Criar boxplot
        bp = plt.boxplot(dados_boxplot, labels=labels, patch_artist=True,
                        notch=True, showmeans=True,
                        meanprops=dict(marker='D', markerfacecolor='red', markersize=6))

        # Colorir boxes
        cores = sns.color_palette("husl", len(dados_boxplot))
        for patch, cor in zip(bp['boxes'], cores):
            patch.set_facecolor(cor)
            patch.set_alpha(0.7)

        plt.xlabel('Cenário', fontsize=12, fontweight='bold')
        plt.ylabel('Recompensa', fontsize=12, fontweight='bold')
        plt.title('Distribuição de Recompensas por Cenário\n(diamante vermelho = média)',
                 fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        plt.savefig(os.path.join(output_dir, "3_distribuicao_recompensas.png"), dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Gráfico: Distribuição de recompensas (boxplot)")

    def _grafico_convergencia(self, output_dir):
        """Gráfico de taxa de convergência por cenário."""
        plt.figure(figsize=(14, 8))

        cenarios = []
        taxas = []
        cores = []

        palette = sns.color_palette("RdYlGn", len(self.metricas_por_cenario))

        for cenario, dados_list in sorted(self.metricas_por_cenario.items()):
            taxas_cenario = [d['taxa_convergencia'] for d in dados_list if 'taxa_convergencia' in d]

            if taxas_cenario:
                cenarios.append(cenario)
                taxa_media = np.mean(taxas_cenario)
                taxas.append(taxa_media)

        # Ordenar por taxa
        indices_ordenados = np.argsort(taxas)[::-1]
        cenarios = [cenarios[i] for i in indices_ordenados]
        taxas = [taxas[i] for i in indices_ordenados]

        # Cores baseadas no valor (verde = bom, vermelho = ruim)
        cores = [palette[min(len(palette)-1, max(0, int((taxa + 100) / 200 * len(palette))))] for taxa in taxas]

        bars = plt.bar(range(len(cenarios)), taxas, color=cores, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Adicionar valores
        for bar, taxa in zip(bars, taxas):
            altura = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., altura,
                    f'{taxa:.1f}%',
                    ha='center', va='bottom' if taxa >= 0 else 'top',
                    fontweight='bold', fontsize=9)

        plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
        plt.xlabel('Cenário', fontsize=12, fontweight='bold')
        plt.ylabel('Taxa de Convergência (%)', fontsize=12, fontweight='bold')
        plt.title('Taxa de Convergência por Cenário\n(melhoria dos 10% iniciais para 10% finais)',
                 fontsize=14, fontweight='bold', pad=20)
        plt.xticks(range(len(cenarios)), cenarios, rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        plt.savefig(os.path.join(output_dir, "4_taxa_convergencia.png"), dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Gráfico: Taxa de convergência")

    def _grafico_heatmap_metricas(self, output_dir):
        """Heatmap de múltiplas métricas normalizadas."""
        plt.figure(figsize=(14, 10))

        cenarios = []
        metricas_matriz = []
        nomes_metricas = ['Recomp. Média', 'Recomp. Total', 'Desvio Padrão',
                         'Convergência', 'Tempo (s)', 'Melhoria Q1→Q4']

        for cenario, dados_list in sorted(self.metricas_por_cenario.items()):
            cenarios.append(cenario)

            # Calcular médias das métricas
            recomp_media = np.mean([d.get('recompensa_media', 0) for d in dados_list])
            recomp_total = np.mean([d.get('recompensa_total', 0) for d in dados_list])
            desvio = np.mean([d.get('recompensa_std', 0) for d in dados_list])
            conv = np.mean([d.get('taxa_convergencia', 0) for d in dados_list])
            tempo = np.mean([d.get('tempo_execucao', 0) for d in dados_list])
            melhoria = np.mean([d.get('melhoria_q1_q4', 0) for d in dados_list])

            metricas_matriz.append([recomp_media, recomp_total, desvio, conv, tempo, melhoria])

        # Normalizar cada coluna (métrica) para [0, 1]
        metricas_array = np.array(metricas_matriz)
        metricas_norm = np.zeros_like(metricas_array)

        for i in range(metricas_array.shape[1]):
            col = metricas_array[:, i]
            min_val = col.min()
            max_val = col.max()
            if max_val - min_val > 0:
                # Tempo: quanto menor, melhor (inverter)
                if i == 4:  # índice do tempo
                    metricas_norm[:, i] = 1 - (col - min_val) / (max_val - min_val)
                else:
                    metricas_norm[:, i] = (col - min_val) / (max_val - min_val)
            else:
                metricas_norm[:, i] = 0.5

        # Criar heatmap
        sns.heatmap(metricas_norm, annot=True, fmt='.2f', cmap='RdYlGn',
                   xticklabels=nomes_metricas, yticklabels=cenarios,
                   cbar_kws={'label': 'Desempenho Normalizado (0-1)'},
                   linewidths=0.5, linecolor='gray')

        plt.title('Heatmap de Métricas Normalizadas por Cenário\n(1.0 = melhor desempenho, 0.0 = pior)',
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Métrica', fontsize=12, fontweight='bold')
        plt.ylabel('Cenário', fontsize=12, fontweight='bold')
        plt.tight_layout()

        plt.savefig(os.path.join(output_dir, "5_heatmap_metricas.png"), dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Gráfico: Heatmap de métricas normalizadas")

    def _grafico_tempo_execucao(self, output_dir):
        """Gráfico de tempo de execução por cenário."""
        plt.figure(figsize=(14, 8))

        cenarios = []
        tempos = []

        for cenario, dados_list in sorted(self.metricas_por_cenario.items()):
            tempos_cenario = [d.get('tempo_execucao', 0) for d in dados_list]

            if tempos_cenario:
                cenarios.append(cenario)
                tempos.append(np.mean(tempos_cenario))

        # Ordenar por tempo
        indices_ordenados = np.argsort(tempos)
        cenarios = [cenarios[i] for i in indices_ordenados]
        tempos = [tempos[i] for i in indices_ordenados]

        # Cores gradientes
        cores = plt.cm.viridis(np.linspace(0, 1, len(cenarios)))

        bars = plt.barh(range(len(cenarios)), tempos, color=cores, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Adicionar valores
        for bar, tempo in zip(bars, tempos):
            largura = bar.get_width()
            plt.text(largura, bar.get_y() + bar.get_height()/2.,
                    f' {tempo:.1f}s ({tempo/60:.1f}min)',
                    ha='left', va='center', fontweight='bold', fontsize=9)

        plt.ylabel('Cenário', fontsize=12, fontweight='bold')
        plt.xlabel('Tempo de Execução (segundos)', fontsize=12, fontweight='bold')
        plt.title('Tempo de Execução por Cenário\n(ordenado do mais rápido ao mais lento)',
                 fontsize=14, fontweight='bold', pad=20)
        plt.yticks(range(len(cenarios)), cenarios)
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()

        plt.savefig(os.path.join(output_dir, "6_tempo_execucao.png"), dpi=300, bbox_inches='tight')
        plt.close()
        print("[OK] Gráfico: Tempo de execução")

    def gerar_ranking(self):
        """
        Gera ranking de cenários baseado em múltiplos critérios.
        """
        print("\n" + "="*70)
        print("GERANDO RANKING DE CENÁRIOS")
        print("="*70 + "\n")

        scores = []

        for cenario, dados_list in self.metricas_por_cenario.items():
            # Calcular score agregado
            recomp_medias = [d.get('recompensa_media', 0) for d in dados_list]
            conv_taxas = [d.get('taxa_convergencia', 0) for d in dados_list]
            melhorias = [d.get('melhoria_q1_q4', 0) for d in dados_list]

            score_recompensa = np.mean(recomp_medias) if recomp_medias else 0
            score_convergencia = np.mean(conv_taxas) if conv_taxas else 0
            score_melhoria = np.mean(melhorias) if melhorias else 0

            # Score total (média ponderada)
            score_total = (score_recompensa * 0.5 +
                          score_convergencia * 0.3 +
                          score_melhoria * 0.2)

            scores.append({
                'cenario': cenario,
                'score_total': score_total,
                'recompensa_media': score_recompensa,
                'taxa_convergencia': score_convergencia,
                'melhoria': score_melhoria,
                'num_execucoes': len(dados_list)
            })

        # Ordenar por score total
        scores.sort(key=lambda x: x['score_total'], reverse=True)

        # Imprimir ranking
        print(f"{'Pos':<5} {'Cenário':<30} {'Score':<12} {'Recomp.':<12} {'Converg.':<12} {'Melhoria':<12}")
        print("-" * 90)

        for i, s in enumerate(scores, 1):
            print(f"{i:<5} {s['cenario']:<30} {s['score_total']:<12.2f} "
                  f"{s['recompensa_media']:<12.1f} {s['taxa_convergencia']:<12.1f}% "
                  f"{s['melhoria']:<12.1f}")

        print("\n")

        # Salvar ranking em JSON
        ranking_path = os.path.join(self.output_dir, "ranking_cenarios.json")
        with open(ranking_path, 'w') as f:
            json.dump(scores, f, indent=2)

        print(f"[OK] Ranking salvo em: {ranking_path}\n")

        return scores

    def gerar_relatorio_markdown(self, ranking):
        """
        Gera relatório consolidado em Markdown.
        """
        print("\n" + "="*70)
        print("GERANDO RELATÓRIO MARKDOWN")
        print("="*70 + "\n")

        relatorio_path = os.path.join(self.output_dir, "RELATORIO_COMPARATIVO.md")

        with open(relatorio_path, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("# Relatório Comparativo de Cenários\n\n")
            f.write("## Análise de Aprendizado por Reforço (Q-Learning)\n\n")
            f.write(f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            f.write(f"**Total de Execuções Analisadas:** {len(self.dados_consolidados)}\n\n")
            f.write(f"**Cenários Comparados:** {len(self.metricas_por_cenario)}\n\n")
            f.write("---\n\n")

            # Ranking
            f.write("## Ranking de Desempenho\n\n")
            f.write("| Posição | Cenário | Score Total | Recompensa Média | Taxa Convergência | Melhoria Q1→Q4 |\n")
            f.write("|---------|---------|-------------|------------------|-------------------|----------------|\n")

            for i, s in enumerate(ranking, 1):
                f.write(f"| {i} | {s['cenario']} | {s['score_total']:.2f} | "
                       f"{s['recompensa_media']:.1f} | {s['taxa_convergencia']:.1f}% | "
                       f"{s['melhoria']:.1f} |\n")

            f.write("\n---\n\n")

            # Análise detalhada por cenário
            f.write("## Análise Detalhada por Cenário\n\n")

            for cenario, dados_list in sorted(self.metricas_por_cenario.items()):
                f.write(f"### {cenario}\n\n")

                # Estatísticas agregadas
                recomp_medias = [d.get('recompensa_media', 0) for d in dados_list]
                recomp_totals = [d.get('recompensa_total', 0) for d in dados_list]
                tempos = [d.get('tempo_execucao', 0) for d in dados_list]
                episodios = [d.get('episodios', 0) for d in dados_list]

                f.write(f"- **Número de Execuções:** {len(dados_list)}\n")
                f.write(f"- **Episódios:** {episodios[0] if episodios else 'N/A'}\n")
                f.write(f"- **Recompensa Média:** {np.mean(recomp_medias):.2f} ± {np.std(recomp_medias):.2f}\n")
                f.write(f"- **Recompensa Total Média:** {np.mean(recomp_totals):.1f}\n")
                f.write(f"- **Tempo Médio de Execução:** {np.mean(tempos):.1f}s ({np.mean(tempos)/60:.1f} min)\n")

                # Métricas de convergência
                conv_taxas = [d.get('taxa_convergencia', 0) for d in dados_list]
                melhorias = [d.get('melhoria_q1_q4', 0) for d in dados_list]

                if conv_taxas:
                    f.write(f"- **Taxa de Convergência:** {np.mean(conv_taxas):.1f}%\n")
                if melhorias:
                    f.write(f"- **Melhoria Q1→Q4:** {np.mean(melhorias):.1f}\n")

                f.write("\n")

            f.write("---\n\n")

            # Gráficos
            f.write("## Visualizações\n\n")
            f.write("### Gráficos Comparativos Gerados:\n\n")
            f.write("1. **Recompensa Média por Cenário** - `graficos/1_recompensa_media_por_cenario.png`\n")
            f.write("2. **Evolução de Aprendizado Comparada** - `graficos/2_evolucao_aprendizado_comparada.png`\n")
            f.write("3. **Distribuição de Recompensas** - `graficos/3_distribuicao_recompensas.png`\n")
            f.write("4. **Taxa de Convergência** - `graficos/4_taxa_convergencia.png`\n")
            f.write("5. **Heatmap de Métricas** - `graficos/5_heatmap_metricas.png`\n")
            f.write("6. **Tempo de Execução** - `graficos/6_tempo_execucao.png`\n\n")

            # Conclusões
            f.write("---\n\n")
            f.write("## Insights e Conclusões\n\n")

            melhor_cenario = ranking[0]['cenario']
            melhor_score = ranking[0]['score_total']

            f.write(f"### Melhor Cenário: **{melhor_cenario}**\n\n")
            f.write(f"- Score Total: **{melhor_score:.2f}**\n")
            f.write(f"- Recompensa Média: **{ranking[0]['recompensa_media']:.1f}**\n")
            f.write(f"- Taxa de Convergência: **{ranking[0]['taxa_convergencia']:.1f}%**\n\n")

            f.write("### Recomendações:\n\n")
            f.write("1. Utilizar cenários com alta taxa de convergência para treinamento eficiente\n")
            f.write("2. Analisar cenários com baixa variância para maior estabilidade\n")
            f.write("3. Considerar trade-off entre tempo de execução e desempenho\n\n")

            # Rodapé
            f.write("---\n\n")
            f.write("**Relatório gerado automaticamente pelo sistema de análise comparativa**\n\n")
            f.write("*Sistemas Multiagentes - 2025.2 - UTFPR*\n")
            f.write("*Trabalho 02 - Aprendizado por Reforço*\n")

        print(f"[OK] Relatório salvo em: {relatorio_path}\n")

        return relatorio_path

    def gerar_csv_consolidado(self):
        """
        Gera CSV consolidado com todas as métricas.
        """
        csv_path = os.path.join(self.output_dir, "metricas_consolidadas.csv")

        campos = [
            'cenario', 'timestamp', 'episodios', 'num_veiculos',
            'recompensa_media', 'recompensa_total', 'recompensa_min', 'recompensa_max',
            'recompensa_std', 'taxa_convergencia', 'melhoria_q1_q4',
            'tempo_execucao', 'recompensa_correta'
        ]

        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()

            for dados in self.dados_consolidados:
                row = {campo: dados.get(campo, '') for campo in campos}
                writer.writerow(row)

        print(f"[OK] CSV consolidado salvo em: {csv_path}\n")

        return csv_path

    def executar_analise_completa(self):
        """
        Executa análise completa: coleta dados, gera gráficos, ranking e relatórios.
        """
        print("\n" + "="*70)
        print("ANÁLISE COMPARATIVA COMPLETA")
        print("Sistemas Multiagentes - Aprendizado por Reforço")
        print("="*70)

        # 1. Coletar dados
        self.coletar_dados()

        if not self.dados_consolidados:
            print("[AVISO] Nenhum dado encontrado para análise!")
            return

        # 2. Gerar gráficos
        self.gerar_graficos_consolidados()

        # 3. Gerar ranking
        ranking = self.gerar_ranking()

        # 4. Gerar relatório Markdown
        self.gerar_relatorio_markdown(ranking)

        # 5. Gerar CSV consolidado
        self.gerar_csv_consolidado()

        print("\n" + "="*70)
        print("[SUCESSO] ANÁLISE COMPLETA CONCLUÍDA!")
        print("="*70)
        print(f"\nResultados salvos em: {self.output_dir}/")
        print(f"\nArquivos gerados:")
        print(f"  - RELATORIO_COMPARATIVO.md (relatório principal)")
        print(f"  - metricas_consolidadas.csv (dados completos)")
        print(f"  - ranking_cenarios.json (ranking detalhado)")
        print(f"  - graficos/ (6 visualizações comparativas)")
        print("\n" + "="*70 + "\n")


def main():
    """
    Função principal para uso standalone do analisador.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Análise comparativa avançada de cenários de aprendizado Q-Learning"
    )
    parser.add_argument(
        '--resultados',
        nargs='+',
        required=True,
        help='Diretórios de resultados a analisar'
    )
    parser.add_argument(
        '--output',
        default='analise_comparativa',
        help='Diretório de saída para análises (padrão: analise_comparativa)'
    )

    args = parser.parse_args()

    # Criar analisador e executar
    analisador = AnalisadorComparativo(args.resultados, args.output)
    analisador.executar_analise_completa()


if __name__ == "__main__":
    main()
