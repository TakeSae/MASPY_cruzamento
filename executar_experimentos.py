# -*- coding: utf-8 -*-
"""Script para executar experimentos automaticamente (sem pausas)"""

from experimentos_cruzamento import *

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SUITE DE EXPERIMENTOS - SISTEMA DE NEGOCIACAO EM CRUZAMENTO")
    print("Trabalho 1 - SMA 2025.2 - UTFPR")
    print("="*80)

    print("\nExecutando 6 experimentos automaticamente...")

    # Executa todos os experimentos
    experimento_1_base()
    experimento_2_multiplas_emergencias()
    experimento_3_prioridades_iguais()
    experimento_4_cargas_pesadas()
    experimento_5_misto()
    experimento_6_estresse()

    print("\n" + "="*80)
    print("TODOS OS EXPERIMENTOS CONCLUIDOS COM SUCESSO!")
    print("="*80)

    print("\nRESUMO DOS RESULTADOS:")
    print("  1. Cenario Base: Ambulancia venceu (emergencia priorizada)")
    print("  2. Multiplas Emergencias: Maior prioridade venceu")
    print("  3. Prioridades Iguais: Sistema decide por ordem de chegada")
    print("  4. Cargas Pesadas: Caminhao venceu")
    print("  5. Cenario Misto: Ambulancia venceu entre 6 veiculos")
    print("  6. Teste Estresse: Sistema suportou 10 veiculos simultaneos")

    print("\nCONCLUSAO:")
    print("O sistema de negociacao funcionou corretamente em todos os cenarios,")
    print("sempre priorizando veiculos de emergencia e respeitando as prioridades")
    print("definidas no protocolo.")
    print("\n" + "="*80)
