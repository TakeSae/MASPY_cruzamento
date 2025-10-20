#!/bin/bash
# Script para coletar dados dos experimentos com timestamp automático

# Ativa ambiente virtual
source venv_maspy/bin/activate

# Gera timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "================================================================================================"
echo "COLETA DE DADOS - Sistema de Negociação em Cruzamento"
echo "================================================================================================"
echo ""
echo "Timestamp: $TIMESTAMP"
echo "Executando experimentos..."
echo ""

# Arquivo principal
ARQUIVO_RESULTADOS="resultados_experimentos_${TIMESTAMP}.txt"

# Executa experimentos e salva
python run_all_experiments.py > "$ARQUIVO_RESULTADOS" 2>&1

echo "✓ Resultados salvos em: $ARQUIVO_RESULTADOS"
echo ""

# Extrai resumo
ARQUIVO_RESUMO="resumo_${TIMESTAMP}.txt"
grep -E "(EXPERIMENTO|VENCEDOR|OK|CONCLUIDO)" "$ARQUIVO_RESULTADOS" > "$ARQUIVO_RESUMO"
echo "✓ Resumo salvo em: $ARQUIVO_RESUMO"
echo ""

# Extrai vencedores
ARQUIVO_VENCEDORES="vencedores_${TIMESTAMP}.txt"
grep ">>> VENCEDOR:" "$ARQUIVO_RESULTADOS" | sed 's/\x1b\[[0-9;]*m//g' > "$ARQUIVO_VENCEDORES"
echo "✓ Vencedores salvos em: $ARQUIVO_VENCEDORES"
echo ""

# Analisa resultados
echo "Analisando resultados..."
echo ""
python analisar_resultados.py "$ARQUIVO_RESULTADOS"

echo ""
echo "================================================================================================"
echo "COLETA CONCLUÍDA COM SUCESSO!"
echo "================================================================================================"
echo ""
echo "Arquivos gerados:"
echo "  1. $ARQUIVO_RESULTADOS (Log completo)"
echo "  2. $ARQUIVO_RESUMO (Resumo)"
echo "  3. $ARQUIVO_VENCEDORES (Lista de vencedores)"
echo ""
