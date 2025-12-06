"""
Sistema de Coleta e Análise de Métricas
Contém classes para coletar métricas de aprendizado e comparar cenários.

Extraído de: cruzamento_maspy_learning.py (linhas 351-1060)
"""

from .utils import cor, titulo, sucesso, erro, aviso, info, destaque


# SISTEMA DE COLETA DE MÉTRICAS

class MetricsCollector:
    """
    Sistema centralizado para coleta de métricas de aprendizado.
    Coleta dados de múltiplos agentes durante o treinamento.
    """

    def __init__(self):
        self.metricas_por_agente = {}  # {nome_agente: {...}}
        self.metricas_globais = {
            "episodios_totais": 0,
            "tempo_inicio": None,
            "tempo_fim": None
        }
        self.dir_execucao = None  # Diretório da execução atual

    def reset(self):
        """
        Reseta todas as métricas para uma nova execução.
        IMPORTANTE: Deve ser chamado no início de cada execução para evitar
        acúmulo de dados de execuções anteriores.
        """
        self.metricas_por_agente.clear()
        self.metricas_globais = {
            "episodios_totais": 0,
            "tempo_inicio": None,
            "tempo_fim": None
        }
        self.dir_execucao = None

    def registrar_agente(self, nome_agente):
        """Registra um novo agente para coleta de métricas."""
        if nome_agente not in self.metricas_por_agente:
            self.metricas_por_agente[nome_agente] = {
                "recompensas_por_episodio": [],
                "acoes_corretas": 0,
                "acoes_incorretas": 0,
                "recompensa_total": 0,
                "recompensa_media": 0,
                "melhor_episodio": {"episodio": 0, "recompensa": float('-inf')},
                "pior_episodio": {"episodio": 0, "recompensa": float('inf')},
                "convergencia": {
                    "convergiu": False,
                    "episodio_convergencia": None,
                    "threshold": 0.95  # 95% de escolhas corretas
                }
            }

    def adicionar_recompensa_episodio(self, nome_agente, episodio, recompensa):
        """Adiciona recompensa de um episódio para um agente."""
        if nome_agente not in self.metricas_por_agente:
            self.registrar_agente(nome_agente)

        metricas = self.metricas_por_agente[nome_agente]
        metricas["recompensas_por_episodio"].append({
            "episodio": episodio,
            "recompensa": recompensa
        })
        metricas["recompensa_total"] += recompensa

        # Atualizar melhor e pior episódio
        if recompensa > metricas["melhor_episodio"]["recompensa"]:
            metricas["melhor_episodio"] = {"episodio": episodio, "recompensa": recompensa}

        if recompensa < metricas["pior_episodio"]["recompensa"]:
            metricas["pior_episodio"] = {"episodio": episodio, "recompensa": recompensa}

    def registrar_acao(self, nome_agente, correta):
        """Registra se uma ação foi correta ou incorreta."""
        if nome_agente not in self.metricas_por_agente:
            self.registrar_agente(nome_agente)

        metricas = self.metricas_por_agente[nome_agente]
        if correta:
            metricas["acoes_corretas"] += 1
        else:
            metricas["acoes_incorretas"] += 1

    def verificar_convergencia(self, nome_agente, janela=10):
        """
        Verifica se o agente convergiu baseado na taxa de acerto.
        Considera uma janela dos últimos N episódios.
        """
        if nome_agente not in self.metricas_por_agente:
            return False

        metricas = self.metricas_por_agente[nome_agente]
        recompensas = metricas["recompensas_por_episodio"]

        if len(recompensas) < janela:
            return False

        # Pegar últimos N episódios
        ultimos = recompensas[-janela:]
        recompensa_media_janela = sum(ep["recompensa"] for ep in ultimos) / janela

        # Considerando que recompensa máxima por episódio é proporcional ao número de veículos
        # Threshold de convergência: média dos últimos episódios >= 95% da recompensa ótima
        recompensa_otima_estimada = 100 * 10  # Assumindo 10 veículos e reward=100 por escolha correta
        threshold = metricas["convergencia"]["threshold"]

        convergiu = recompensa_media_janela >= (recompensa_otima_estimada * threshold)

        if convergiu and not metricas["convergencia"]["convergiu"]:
            metricas["convergencia"]["convergiu"] = True
            metricas["convergencia"]["episodio_convergencia"] = len(recompensas)

        return convergiu

    def calcular_estatisticas(self):
        """Calcula estatísticas finais de todos os agentes."""
        for nome_agente, metricas in self.metricas_por_agente.items():
            num_episodios = len(metricas["recompensas_por_episodio"])
            if num_episodios > 0:
                metricas["recompensa_media"] = metricas["recompensa_total"] / num_episodios

            # Calcular desvio padrão das recompensas
            if num_episodios > 1:
                recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]
                media = metricas["recompensa_media"]
                variancia = sum((r - media) ** 2 for r in recompensas) / num_episodios
                metricas["desvio_padrao"] = variancia ** 0.5
            else:
                metricas["desvio_padrao"] = 0.0

    def calcular_funcao_utilidade(self, nome_agente, alpha=0.5, beta=0.3, gamma=0.2):
        """
        Calcula a função de utilidade para um agente.

        Função de Utilidade (ver docs/PEAS.md para detalhes):
        U(agente) = α × taxa_acerto + β × fator_convergencia + γ × fator_recompensa

        Parâmetros:
            nome_agente: Nome do agente para calcular utilidade
            alpha: Peso da taxa de acerto (0-1) [default: 0.5]
            beta: Peso do fator de convergência (0-1) [default: 0.3]
            gamma: Peso do fator de recompensa (0-1) [default: 0.2]

        Retorna:
            float: Valor de utilidade normalizado (0-1), onde 1 = desempenho ótimo
        """
        if nome_agente not in self.metricas_por_agente:
            return 0.0

        metricas = self.metricas_por_agente[nome_agente]

        # 1. Taxa de acerto normalizada (0-1)
        total_acoes = metricas["acoes_corretas"] + metricas["acoes_incorretas"]
        taxa_acerto = (metricas["acoes_corretas"] / total_acoes) if total_acoes > 0 else 0.0

        # 2. Fator de convergência (0-1)
        if metricas["convergencia"]["convergiu"]:
            ep_conv = metricas["convergencia"]["episodio_convergencia"]
            # Normalizar: convergência em episódio 1 = 1.0, episódio 100 = 0.01
            fator_convergencia = 1.0 / max(1, ep_conv)
            # Escalar para ficar entre 0 e 1 (assumindo max 100 episódios)
            fator_convergencia = min(1.0, fator_convergencia * 10)
        else:
            fator_convergencia = 0.0

        # 3. Fator de recompensa normalizado (0-1)
        # Normalizar pela recompensa máxima teórica
        num_veiculos = 10  # Assumindo máximo de 10 veículos
        recompensa_maxima_teorica = 100 * num_veiculos  # 100 por escolha correta × 10 veículos
        if metricas["recompensa_media"] > 0:
            fator_recompensa = min(1.0, metricas["recompensa_media"] / recompensa_maxima_teorica)
        else:
            fator_recompensa = 0.0

        # Calcular utilidade ponderada
        utilidade = (alpha * taxa_acerto) + (beta * fator_convergencia) + (gamma * fator_recompensa)

        # Garantir que está no intervalo [0, 1]
        utilidade = max(0.0, min(1.0, utilidade))

        # Armazenar componentes para análise
        metricas["utilidade"] = {
            "total": utilidade,
            "taxa_acerto": taxa_acerto,
            "fator_convergencia": fator_convergencia,
            "fator_recompensa": fator_recompensa,
            "pesos": {"alpha": alpha, "beta": beta, "gamma": gamma}
        }

        return utilidade

    def gerar_relatorio(self):
        """Gera relatório textual das métricas coletadas com análise estatística completa."""
        self.calcular_estatisticas()

        # Calcular função de utilidade para todos os agentes
        for nome_agente in self.metricas_por_agente.keys():
            self.calcular_funcao_utilidade(nome_agente)

        relatorio = []
        relatorio.append("\n" + "="*70)
        relatorio.append("RELATÓRIO DE MÉTRICAS DE APRENDIZADO")
        relatorio.append("="*70 + "\n")

        for nome_agente, metricas in self.metricas_por_agente.items():
            relatorio.append(f"\n{titulo(f'Agente: {nome_agente}')}")
            relatorio.append("-"*70)

            num_episodios = len(metricas["recompensas_por_episodio"])
            total_acoes = metricas["acoes_corretas"] + metricas["acoes_incorretas"]
            taxa_acerto = (metricas["acoes_corretas"] / total_acoes * 100) if total_acoes > 0 else 0

            # Métricas básicas
            relatorio.append(f"\n  {destaque('Métricas de Desempenho:')}")
            relatorio.append(f"    Episódios executados: {num_episodios}")
            relatorio.append(f"    Recompensa total: {sucesso(f'{metricas["recompensa_total"]:.2f}')}")
            relatorio.append(f"    Recompensa média: {sucesso(f'{metricas["recompensa_media"]:.2f}')}")
            relatorio.append(f"    Desvio padrão: {metricas['desvio_padrao']:.2f}")
            relatorio.append(f"    Ações corretas: {sucesso(str(metricas['acoes_corretas']))}")
            relatorio.append(f"    Ações incorretas: {erro(str(metricas['acoes_incorretas']))}")
            relatorio.append(f"    Taxa de acerto: {sucesso(f'{taxa_acerto:.2f}%')}")

            # Estatísticas de episódios
            relatorio.append(f"\n  {destaque('Análise de Episódios:')}")
            melhor = metricas["melhor_episodio"]
            pior = metricas["pior_episodio"]
            relatorio.append(f"    Melhor episódio: {melhor['episodio']} (recompensa: {sucesso(f'{melhor["recompensa"]:.2f}')})")
            relatorio.append(f"    Pior episódio: {pior['episodio']} (recompensa: {erro(f'{pior["recompensa"]:.2f}')})")

            # Análise de convergência
            relatorio.append(f"\n  {destaque('Convergência:')}")
            conv = metricas["convergencia"]
            if conv["convergiu"]:
                relatorio.append(f"    Status: {sucesso('CONVERGIU')}")
                relatorio.append(f"    Episódio de convergência: {conv['episodio_convergencia']}")
                relatorio.append(f"    Threshold: {conv['threshold']*100:.0f}%")
            else:
                relatorio.append(f"    Status: {aviso('NÃO CONVERGIU')}")
                relatorio.append(f"    (Threshold requerido: {conv['threshold']*100:.0f}%)")

            # Função de Utilidade (ver docs/PEAS.md)
            if "utilidade" in metricas:
                util = metricas["utilidade"]
                relatorio.append(f"\n  {destaque('Função de Utilidade:')}")
                relatorio.append(f"    Utilidade Total: {sucesso(f'{util["total"]:.4f}')} (0-1 scale)")
                relatorio.append(f"    Componentes:")
                relatorio.append(f"      • Taxa de Acerto: {util['taxa_acerto']:.4f} (peso α={util['pesos']['alpha']})")
                relatorio.append(f"      • Convergência: {util['fator_convergencia']:.4f} (peso β={util['pesos']['beta']})")
                relatorio.append(f"      • Recompensa: {util['fator_recompensa']:.4f} (peso γ={util['pesos']['gamma']})")

                # Classificação qualitativa
                u_total = util["total"]
                if u_total >= 0.9:
                    classificacao = sucesso("EXCELENTE")
                elif u_total >= 0.75:
                    classificacao = sucesso("BOM")
                elif u_total >= 0.6:
                    classificacao = aviso("SATISFATÓRIO")
                else:
                    classificacao = erro("INSUFICIENTE")
                relatorio.append(f"    Classificação: {classificacao}")

            relatorio.append("")

        # Resumo comparativo se houver múltiplos agentes
        if len(self.metricas_por_agente) > 1:
            relatorio.append("\n" + "="*70)
            relatorio.append(titulo("ANÁLISE COMPARATIVA"))
            relatorio.append("="*70 + "\n")

            # Ranking por utilidade
            ranking = sorted(
                self.metricas_por_agente.items(),
                key=lambda x: x[1].get("utilidade", {}).get("total", 0),
                reverse=True
            )

            relatorio.append(f"  {destaque('Ranking por Utilidade:')}")
            for i, (nome, metricas) in enumerate(ranking, 1):
                util = metricas.get("utilidade", {}).get("total", 0)
                relatorio.append(f"    {i}. {nome}: {sucesso(f'{util:.4f}')}")

            relatorio.append("")

        relatorio.append("="*70 + "\n")

        return "\n".join(relatorio)

    def exportar_csv(self, caminho=None):
        """
        Exporta métricas para arquivo CSV.
        Se dir_execucao estiver definido, salva no diretório timestampado.
        """
        import csv
        import os

        # Determinar caminho do CSV
        if caminho is None:
            if self.dir_execucao:
                caminho = os.path.join(self.dir_execucao, "metricas_aprendizado.csv")
            else:
                caminho = "metricas_aprendizado.csv"

        with open(caminho, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Agente", "Episodio", "Recompensa", "Recompensa_Acumulada"
            ])

            for nome_agente, metricas in self.metricas_por_agente.items():
                recompensa_acum = 0
                for ep_data in metricas["recompensas_por_episodio"]:
                    recompensa_acum += ep_data["recompensa"]
                    writer.writerow([
                        nome_agente,
                        ep_data["episodio"],
                        ep_data["recompensa"],
                        recompensa_acum
                    ])

        print(f"\n{sucesso('✓')} Métricas exportadas para: {caminho}")

    def gerar_graficos(self, diretorio=None):
        """
        Gera gráficos de visualização das métricas de aprendizado.
        Cria múltiplos gráficos para análise detalhada.
        Se dir_execucao estiver definido, salva no diretório timestampado.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import os

            # Determinar diretório dos gráficos
            if diretorio is None:
                if self.dir_execucao:
                    diretorio = os.path.join(self.dir_execucao, "graficos")
                else:
                    diretorio = "graficos"

            # Criar diretório se não existir
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)

            print(f"\n{info('i')} Gerando gráficos de visualização (5 gráficos)...")
            print(f"{info('i')} Diretório: {diretorio}")

            # Gráfico 1: Recompensa por Episódio (todos os agentes)
            print(f"{info('>')} [1/5] Gerando gráfico de recompensa por episódio...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"]:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]
                    plt.plot(episodios, recompensas, marker='o', label=nome_agente, linewidth=2)

            plt.xlabel('Episódio de Treinamento', fontsize=12)
            plt.ylabel('Recompensa', fontsize=12)
            plt.title('Recompensa por Episódio - Treinamento Q-Learning', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico1 = os.path.join(diretorio, 'recompensa_por_episodio.png')
            plt.savefig(caminho_grafico1, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [1/5] Gráfico salvo: recompensa_por_episodio.png")

            # Gráfico 2: Recompensa Acumulada
            print(f"{info('>')} [2/5] Gerando gráfico de recompensa acumulada...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"]:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas_acum = np.cumsum([ep["recompensa"] for ep in metricas["recompensas_por_episodio"]])
                    plt.plot(episodios, recompensas_acum, marker='o', label=nome_agente, linewidth=2)

            plt.xlabel('Episódio de Treinamento', fontsize=12)
            plt.ylabel('Recompensa Acumulada', fontsize=12)
            plt.title('Recompensa Acumulada - Treinamento Q-Learning', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico2 = os.path.join(diretorio, 'recompensa_acumulada.png')
            plt.savefig(caminho_grafico2, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [2/5] Gráfico salvo: recompensa_acumulada.png")

            # Gráfico 3: Média Móvel (janela=5)
            print(f"{info('>')} [3/5] Gerando gráfico de média móvel...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"] and len(metricas["recompensas_por_episodio"]) >= 5:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]

                    # Calcular média móvel
                    janela = 5
                    media_movel = np.convolve(recompensas, np.ones(janela)/janela, mode='valid')
                    episodios_mm = episodios[janela-1:]

                    plt.plot(episodios_mm, media_movel, marker='o', label=f'{nome_agente} (MM)', linewidth=2)

            plt.xlabel('Episódio de Validação', fontsize=12)
            plt.ylabel('Recompensa (Média Móvel)', fontsize=12)
            plt.title('Média Móvel da Recompensa (janela=5) - Validação', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico3 = os.path.join(diretorio, 'media_movel.png')
            plt.savefig(caminho_grafico3, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [3/5] Gráfico salvo: media_movel.png")

            # Gráfico 4: Comparação de Desempenho (barras)
            print(f"{info('>')} [4/5] Gerando gráfico de comparação de desempenho...")
            plt.figure(figsize=(10, 6))
            nomes = []
            recompensas_medias = []
            taxas_acerto = []

            # Filtrar apenas agentes que realmente tomam ações (coordenadores)
            for nome_agente, metricas in self.metricas_por_agente.items():
                total = metricas["acoes_corretas"] + metricas["acoes_incorretas"]
                # Só incluir agentes que fizeram pelo menos uma ação
                if total > 0 or "Coordenador" in nome_agente:
                    nomes.append(nome_agente.replace('_', '\n'))
                    recompensas_medias.append(metricas["recompensa_media"])
                    taxa = (metricas["acoes_corretas"] / total * 100) if total > 0 else 0
                    taxas_acerto.append(taxa)

            x = np.arange(len(nomes))
            width = 0.35

            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = ax1.twinx()

            bars1 = ax1.bar(x - width/2, recompensas_medias, width, label='Recompensa Média', color='steelblue', alpha=0.8)
            bars2 = ax2.bar(x + width/2, taxas_acerto, width, label='Taxa de Acerto (%)', color='orange', alpha=0.8)

            ax1.set_xlabel('Agente', fontsize=12)
            ax1.set_ylabel('Recompensa Média', fontsize=12, color='steelblue')
            ax2.set_ylabel('Taxa de Acerto (%)', fontsize=12, color='orange')
            ax1.set_title('Comparação de Desempenho dos Agentes', fontsize=14, fontweight='bold')
            ax1.set_xticks(x)
            ax1.set_xticklabels(nomes, fontsize=9)
            ax1.tick_params(axis='y', labelcolor='steelblue')
            ax2.tick_params(axis='y', labelcolor='orange')
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            ax1.grid(True, alpha=0.3, axis='y')

            caminho_grafico4 = os.path.join(diretorio, 'comparacao_desempenho.png')
            plt.savefig(caminho_grafico4, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [4/5] Gráfico salvo: comparacao_desempenho.png")

            # Gráfico 5: Convergência (se houver dados suficientes)
            print(f"{info('>')} [5/5] Gerando gráfico de análise de convergência...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"] and len(metricas["recompensas_por_episodio"]) >= 10:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]

                    plt.plot(episodios, recompensas, alpha=0.3, linewidth=1)

                    # Linha de tendência (regressão linear)
                    z = np.polyfit(episodios, recompensas, 1)
                    p = np.poly1d(z)
                    plt.plot(episodios, p(episodios), linewidth=2, label=f'{nome_agente} (tendência)')

                    # Marcar ponto de convergência se houver
                    if metricas["convergencia"]["convergiu"]:
                        ep_conv = metricas["convergencia"]["episodio_convergencia"]
                        plt.axvline(x=ep_conv, color='red', linestyle='--', alpha=0.5,
                                   label=f'Convergência {nome_agente} (ep {ep_conv})')

            plt.xlabel('Episódio de Validação', fontsize=12)
            plt.ylabel('Recompensa', fontsize=12)
            plt.title('Análise de Convergência - Validação (Política Aprendida)', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico5 = os.path.join(diretorio, 'analise_convergencia.png')
            plt.savefig(caminho_grafico5, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [5/5] Gráfico salvo: analise_convergencia.png")

            print(f"\n{sucesso('✓')} Todos os 5 gráficos foram salvos com sucesso!")
            print(f"{info('i')} Localização: {diretorio}/")

        except ImportError:
            print(f"\n{aviso('⚠')} matplotlib não está instalado. Pulando geração de gráficos.")
            print("   Instale com: pip install matplotlib")
        except Exception as e:
            print(f"\n{erro('✗')} Erro ao gerar gráficos: {e}")


# Instância global do coletor de métricas
METRICS_COLLECTOR = MetricsCollector()



# SISTEMA DE COMPARAÇÃO ENTRE CENÁRIOS

class ScenarioComparator:
    """
    Sistema para comparar resultados entre diferentes cenários de teste.
    Permite análise comparativa de configurações e parâmetros.
    """

    def __init__(self):
        self.resultados_cenarios = {}  # {nome_cenario: {metricas...}}

    def adicionar_resultado(self, nome_cenario, metrics_collector):
        """
        Adiciona resultado de um cenário para comparação.

        Args:
            nome_cenario: Nome identificador do cenário
            metrics_collector: Instância de MetricsCollector com dados
        """
        # Copiar métricas relevantes
        metricas_resumo = {}

        for nome_agente, metricas in metrics_collector.metricas_por_agente.items():
            metricas_resumo[nome_agente] = {
                "recompensa_media": metricas.get("recompensa_media", 0),
                "recompensa_total": metricas.get("recompensa_total", 0),
                "desvio_padrao": metricas.get("desvio_padrao", 0),
                "taxa_acerto": (metricas["acoes_corretas"] / (metricas["acoes_corretas"] + metricas["acoes_incorretas"]) * 100)
                    if (metricas["acoes_corretas"] + metricas["acoes_incorretas"]) > 0 else 0,
                "convergiu": metricas["convergencia"]["convergiu"],
                "episodio_convergencia": metricas["convergencia"].get("episodio_convergencia", None),
                "utilidade": metricas.get("utilidade", {}).get("total", 0),
                "num_episodios": len(metricas["recompensas_por_episodio"])
            }

        self.resultados_cenarios[nome_cenario] = {
            "metricas_agentes": metricas_resumo,
            "tempo_execucao": metrics_collector.metricas_globais.get("tempo_fim", 0) -
                             metrics_collector.metricas_globais.get("tempo_inicio", 0)
        }

    def gerar_relatorio_comparativo(self):
        """Gera relatório comparativo entre todos os cenários."""
        if not self.resultados_cenarios:
            return "Nenhum cenário para comparar."

        relatorio = []
        relatorio.append("\n" + "="*80)
        relatorio.append(titulo("RELATÓRIO COMPARATIVO ENTRE CENÁRIOS"))
        relatorio.append("="*80 + "\n")

        # Tabela comparativa de cenários
        relatorio.append(destaque("Resumo Geral dos Cenários:\n"))
        relatorio.append(f"{'Cenário':<30} {'Utilidade':<12} {'Taxa Acerto':<15} {'Convergiu':<12} {'Tempo (s)':<10}")
        relatorio.append("-" * 80)

        for nome_cenario, dados in self.resultados_cenarios.items():
            # Pegar métrica do coordenador (primeiro agente)
            coordenador_metricas = next(iter(dados["metricas_agentes"].values()), {})

            utilidade = coordenador_metricas.get("utilidade", 0)
            taxa = coordenador_metricas.get("taxa_acerto", 0)
            conv = "SIM" if coordenador_metricas.get("convergiu", False) else "NÃO"
            tempo = dados.get("tempo_execucao", 0)

            utilidade_str = sucesso(f"{utilidade:.4f}") if utilidade >= 0.75 else aviso(f"{utilidade:.4f}")
            taxa_str = sucesso(f"{taxa:.2f}%") if taxa >= 90 else aviso(f"{taxa:.2f}%")
            conv_str = sucesso(conv) if conv == "SIM" else erro(conv)

            relatorio.append(f"{nome_cenario:<30} {utilidade_str:<20} {taxa_str:<23} {conv_str:<20} {tempo:.2f}")

        # Análise do melhor cenário
        melhor_cenario = max(
            self.resultados_cenarios.items(),
            key=lambda x: next(iter(x[1]["metricas_agentes"].values())).get("utilidade", 0)
        )

        relatorio.append("\n" + destaque("Análise de Melhor Desempenho:"))
        relatorio.append(f"  {sucesso('★')} Melhor cenário: {sucesso(melhor_cenario[0])}")

        melhor_metricas = next(iter(melhor_cenario[1]["metricas_agentes"].values()))
        relatorio.append(f"    • Utilidade: {melhor_metricas.get('utilidade', 0):.4f}")
        relatorio.append(f"    • Taxa de acerto: {melhor_metricas.get('taxa_acerto', 0):.2f}%")
        relatorio.append(f"    • Convergência: {'Episódio ' + str(melhor_metricas.get('episodio_convergencia')) if melhor_metricas.get('convergiu') else 'Não convergiu'}")

        # Recomendações
        relatorio.append("\n" + destaque("Recomendações:"))

        # Identificar cenários que não convergiram
        nao_convergiram = [
            nome for nome, dados in self.resultados_cenarios.items()
            if not next(iter(dados["metricas_agentes"].values())).get("convergiu", False)
        ]

        if nao_convergiram:
            relatorio.append(f"  {aviso('⚠')} Cenários sem convergência ({len(nao_convergiram)}):")
            for nome in nao_convergiram:
                relatorio.append(f"    - {nome}")
            relatorio.append("    Sugestão: Aumentar número de episódios ou ajustar parâmetros de reward")

        # Identificar cenários com baixa performance
        baixa_util = [
            nome for nome, dados in self.resultados_cenarios.items()
            if next(iter(dados["metricas_agentes"].values())).get("utilidade", 0) < 0.6
        ]

        if baixa_util:
            relatorio.append(f"\n  {aviso('⚠')} Cenários com utilidade < 0.6 ({len(baixa_util)}):")
            for nome in baixa_util:
                relatorio.append(f"    - {nome}")
            relatorio.append("    Sugestão: Revisar configuração de prioridades ou multiplicador de penalidade")

        relatorio.append("\n" + "="*80 + "\n")

        return "\n".join(relatorio)

    def exportar_comparacao_csv(self, caminho="comparacao_cenarios.csv"):
        """Exporta comparação de cenários para CSV."""
        import csv

        with open(caminho, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Cenario", "Agente", "Utilidade", "Taxa_Acerto_%", "Recompensa_Media",
                "Desvio_Padrao", "Convergiu", "Ep_Convergencia", "Num_Episodios", "Tempo_Exec_s"
            ])

            for nome_cenario, dados in self.resultados_cenarios.items():
                tempo = dados.get("tempo_execucao", 0)
                for nome_agente, metricas in dados["metricas_agentes"].items():
                    writer.writerow([
                        nome_cenario,
                        nome_agente,
                        f"{metricas.get('utilidade', 0):.4f}",
                        f"{metricas.get('taxa_acerto', 0):.2f}",
                        f"{metricas.get('recompensa_media', 0):.2f}",
                        f"{metricas.get('desvio_padrao', 0):.2f}",
                        "SIM" if metricas.get("convergiu", False) else "NAO",
                        metricas.get("episodio_convergencia", "N/A"),
                        metricas.get("num_episodios", 0),
                        f"{tempo:.2f}"
                    ])

        print(f"{sucesso('✓')} Comparação exportada para: {caminho}")

    def gerar_grafico_comparativo(self, diretorio="graficos"):
        """Gera gráficos comparativos entre cenários."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import os

            if not os.path.exists(diretorio):
                os.makedirs(diretorio)

            # Preparar dados
            cenarios = list(self.resultados_cenarios.keys())
            utilidades = []
            taxas_acerto = []
            tempos = []

            for nome_cenario in cenarios:
                dados = self.resultados_cenarios[nome_cenario]
                metricas = next(iter(dados["metricas_agentes"].values()))
                utilidades.append(metricas.get("utilidade", 0))
                taxas_acerto.append(metricas.get("taxa_acerto", 0))
                tempos.append(dados.get("tempo_execucao", 0))

            # Gráfico de barras comparativo
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))

            # Subplot 1: Utilidade
            axes[0].bar(range(len(cenarios)), utilidades, color='steelblue', alpha=0.8)
            axes[0].set_xlabel('Cenário', fontsize=12)
            axes[0].set_ylabel('Utilidade (0-1)', fontsize=12)
            axes[0].set_title('Comparação de Utilidade por Cenário', fontsize=14, fontweight='bold')
            axes[0].set_xticks(range(len(cenarios)))
            axes[0].set_xticklabels([c[:15] for c in cenarios], rotation=45, ha='right', fontsize=9)
            axes[0].axhline(y=0.75, color='green', linestyle='--', alpha=0.5, label='Threshold "Bom"')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3, axis='y')

            # Subplot 2: Taxa de Acerto
            axes[1].bar(range(len(cenarios)), taxas_acerto, color='orange', alpha=0.8)
            axes[1].set_xlabel('Cenário', fontsize=12)
            axes[1].set_ylabel('Taxa de Acerto (%)', fontsize=12)
            axes[1].set_title('Comparação de Taxa de Acerto', fontsize=14, fontweight='bold')
            axes[1].set_xticks(range(len(cenarios)))
            axes[1].set_xticklabels([c[:15] for c in cenarios], rotation=45, ha='right', fontsize=9)
            axes[1].axhline(y=95, color='green', linestyle='--', alpha=0.5, label='Meta 95%')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3, axis='y')

            # Subplot 3: Tempo de Execução
            axes[2].bar(range(len(cenarios)), tempos, color='purple', alpha=0.8)
            axes[2].set_xlabel('Cenário', fontsize=12)
            axes[2].set_ylabel('Tempo (s)', fontsize=12)
            axes[2].set_title('Tempo de Execução por Cenário', fontsize=14, fontweight='bold')
            axes[2].set_xticks(range(len(cenarios)))
            axes[2].set_xticklabels([c[:15] for c in cenarios], rotation=45, ha='right', fontsize=9)
            axes[2].grid(True, alpha=0.3, axis='y')

            plt.tight_layout()
            caminho_grafico = os.path.join(diretorio, 'comparacao_cenarios.png')
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"{sucesso('✓')} Gráfico comparativo salvo: {caminho_grafico}")

        except ImportError:
            print(f"{aviso('⚠')} matplotlib não disponível para gráficos comparativos")
        except Exception as e:
            print(f"{erro('✗')} Erro ao gerar gráfico comparativo: {e}")


# Instância global do comparador de cenários
SCENARIO_COMPARATOR = ScenarioComparator()
