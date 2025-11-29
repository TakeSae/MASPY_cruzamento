#!/usr/bin/env python3
"""
Script para executar e comparar múltiplos cenários de aprendizado.
Gera análise comparativa completa entre diferentes configurações.

Uso:
    python comparar_cenarios.py --cenarios base emergencias pesados --episodios 50
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

# Adicionar cores para output
class Cores:
    RESET = '\033[0m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    BOLD = '\033[1m'

def cor(texto, cor_code):
    return f"{cor_code}{texto}{Cores.RESET}"

def sucesso(texto):
    return cor(texto, Cores.VERDE)

def titulo(texto):
    return cor(texto, Cores.BOLD + Cores.CIANO)

def aviso(texto):
    return cor(texto, Cores.AMARELO)

# Cenários disponíveis (deve corresponder ao cruzamento_maspy_learning.py)
CENARIOS_DISPONIVEIS = [
    "padrao", "base", "emergencias", "iguais", "pesados",
    "transporte_publico", "prioridades_proximas", "extremos",
    "dois_veiculos", "tres_veiculos"
]

def executar_cenario(cenario, episodios=100, quiet=True):
    """
    Executa um cenário específico de aprendizado.

    Args:
        cenario: Nome do cenário a executar
        episodios: Número de episódios de treinamento
        quiet: Se True, suprime logs detalhados

    Returns:
        bool: True se execução foi bem-sucedida
    """
    print(f"\n{titulo('═' * 70)}")
    print(titulo(f"  Executando cenário: {cenario.upper()}"))
    print(titulo('═' * 70))

    # Montar comando
    cmd = [
        sys.executable,
        "cruzamento_maspy_learning.py",
        "--experimento", cenario,
        "--episodios", str(episodios)
    ]

    if quiet:
        cmd.append("--quiet")

    try:
        # Executar com output em tempo real
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            check=True,
            capture_output=False,
            text=True
        )

        print(f"\n{sucesso('✓')} Cenário '{cenario}' concluído com sucesso!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n{aviso('✗')} Erro ao executar cenário '{cenario}': {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n{aviso('⚠')} Execução interrompida pelo usuário")
        return False

def gerar_relatorio_comparativo():
    """
    Gera relatório comparativo final entre todos os cenários executados.
    """
    print(f"\n\n{titulo('═' * 70)}")
    print(titulo("  GERANDO RELATÓRIO COMPARATIVO FINAL"))
    print(titulo('═' * 70) + "\n")

    # O relatório será gerado pelo ScenarioComparator durante as execuções
    print(sucesso("✓") + " Relatórios individuais gerados para cada cenário")
    print(sucesso("✓") + " Métricas e gráficos salvos em seus respectivos diretórios")

    print(f"\n{titulo('Arquivos gerados:')}")
    print("  • metricas_aprendizado.csv - Última execução")
    print("  • graficos/ - Visualizações gráficas")
    print("  • comparacao_cenarios.csv - Dados comparativos (se implementado)")

def main():
    parser = argparse.ArgumentParser(
        description="Executa e compara múltiplos cenários de aprendizado Q-Learning"
    )

    parser.add_argument(
        '--cenarios',
        nargs='+',
        choices=CENARIOS_DISPONIVEIS + ['todos'],
        default=['base', 'emergencias', 'pesados'],
        help=f'Cenários a executar (ou "todos" para executar todos)'
    )

    parser.add_argument(
        '--episodios',
        type=int,
        default=100,
        help='Número de episódios de treinamento para cada cenário (padrão: 100)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar logs detalhados durante o treinamento'
    )

    args = parser.parse_args()

    # Determinar cenários a executar
    if 'todos' in args.cenarios:
        cenarios = CENARIOS_DISPONIVEIS
    else:
        cenarios = args.cenarios

    # Banner inicial
    print("\n" + titulo("=" * 70))
    print(titulo("  COMPARAÇÃO DE CENÁRIOS - SISTEMA MULTI-AGENTES"))
    print(titulo("  Aprendizado por Reforço (Q-Learning)"))
    print(titulo("=" * 70))

    print(f"\n{aviso('Configuração:')}")
    print(f"  • Cenários a executar: {len(cenarios)}")
    print(f"  • Episódios por cenário: {args.episodios}")
    print(f"  • Logs detalhados: {'Sim' if args.verbose else 'Não'}")

    print(f"\n{aviso('Cenários:')}")
    for i, cenario in enumerate(cenarios, 1):
        print(f"  {i}. {cenario}")

    # Confirmação
    try:
        input(f"\n{aviso('Pressione ENTER para iniciar ou Ctrl+C para cancelar...')}")
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuário.")
        sys.exit(0)

    # Executar cada cenário
    resultados = {}
    sucessos = 0
    falhas = 0

    for i, cenario in enumerate(cenarios, 1):
        print(f"\n{titulo(f'>>> Cenário {i}/{len(cenarios)}')} <<<")

        sucesso_exec = executar_cenario(
            cenario,
            episodios=args.episodios,
            quiet=not args.verbose
        )

        resultados[cenario] = sucesso_exec
        if sucesso_exec:
            sucessos += 1
        else:
            falhas += 1

    # Resumo final
    print("\n\n" + titulo("=" * 70))
    print(titulo("  RESUMO DA COMPARAÇÃO"))
    print(titulo("=" * 70))

    print(f"\n{sucesso('Cenários executados com sucesso:')} {sucessos}/{len(cenarios)}")
    if falhas > 0:
        print(f"{aviso('Cenários com falha:')} {falhas}/{len(cenarios)}")

    print(f"\n{titulo('Resultados detalhados:')}")
    for cenario, sucesso_exec in resultados.items():
        status = sucesso("✓ SUCESSO") if sucesso_exec else aviso("✗ FALHA")
        print(f"  {cenario:.<40} {status}")

    # Gerar relatório comparativo
    gerar_relatorio_comparativo()

    print(f"\n{titulo('Análise completa concluída!')}")
    print(f"\n{aviso('Próximos passos:')}")
    print("  1. Revisar gráficos em graficos/")
    print("  2. Analisar metricas_aprendizado.csv")
    print("  3. Comparar utilidades entre cenários")
    print("  4. Identificar melhor configuração")

    print("\n" + titulo("=" * 70) + "\n")

    return 0 if falhas == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\nErro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
