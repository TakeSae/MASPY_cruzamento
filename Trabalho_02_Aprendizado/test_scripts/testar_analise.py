#!/usr/bin/env python3
"""
Script de teste para o sistema de análise comparativa.
Testa com resultados existentes no diretório 'resultados/'.
"""

import os
import sys
from pathlib import Path

def main():
    print("="*70)
    print("TESTE DO SISTEMA DE ANÁLISE COMPARATIVA")
    print("="*70 + "\n")

    # Verificar dependências
    print("1. Verificando dependências...")
    try:
        import numpy
        print("   [OK] numpy")
    except ImportError:
        print("   [ERRO] numpy - Execute: pip install numpy")
        return False

    try:
        import matplotlib
        print("   [OK] matplotlib")
    except ImportError:
        print("   [ERRO] matplotlib - Execute: pip install matplotlib")
        return False

    try:
        import seaborn
        print("   [OK] seaborn")
    except ImportError:
        print("   [ERRO] seaborn - Execute: pip install seaborn")
        print("\n   SOLUÇÃO: Execute o comando abaixo:")
        print("   pip install -r requirements_analise.txt")
        return False

    print("\n2. Verificando módulo de análise...")
    try:
        from analisar_comparacao import AnalisadorComparativo
        print("   [OK] analisar_comparacao.py")
    except ImportError as e:
        print(f"   [ERRO] Erro ao importar: {e}")
        return False

    # Verificar diretório de resultados
    print("\n3. Verificando diretório de resultados...")
    resultados_dir = Path("resultados")

    if not resultados_dir.exists():
        print(f"   [ERRO] Diretório 'resultados/' não encontrado")
        print("   Execute primeiro alguns cenários com:")
        print("   python cruzamento_maspy_learning.py --experimento base --episodios 100")
        return False

    # Listar diretórios de resultados
    subdirs = [d for d in resultados_dir.iterdir() if d.is_dir() and d.name != "ultima_execucao"]

    if not subdirs:
        print(f"   [ERRO] Nenhum resultado encontrado em 'resultados/'")
        return False

    print(f"   [OK] Encontrados {len(subdirs)} diretórios de resultados")

    # Listar alguns
    print("\n   Últimos resultados:")
    for d in sorted(subdirs)[-5:]:
        print(f"      - {d.name}")

    # Executar teste de análise com os resultados disponíveis
    print("\n4. Executando análise comparativa de teste...")
    print(f"   Analisando {min(len(subdirs), 3)} resultados...\n")

    # Pegar até 3 resultados para teste
    dirs_teste = [str(d) for d in sorted(subdirs)[-3:]]

    try:
        analisador = AnalisadorComparativo(
            resultados_dirs=dirs_teste,
            output_dir="teste_analise_comparativa"
        )
        analisador.executar_analise_completa()

        print("\n" + "="*70)
        print("[SUCESSO] TESTE CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print("\nResultados do teste salvos em: teste_analise_comparativa/")
        print("\nVerifique:")
        print("  - teste_analise_comparativa/RELATORIO_COMPARATIVO.md")
        print("  - teste_analise_comparativa/graficos/")
        print("  - teste_analise_comparativa/metricas_consolidadas.csv")
        print("\n" + "="*70 + "\n")
        return True

    except Exception as e:
        print(f"\n[ERRO] Erro durante análise: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
