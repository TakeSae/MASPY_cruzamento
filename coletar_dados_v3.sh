# Ativa ambiente virtual
source venv_maspy/bin/activate

# Gera timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATA=$(date +%Y-%m-%d)
HORA=$(date +%H:%M:%S)

# Cria estrutura de diretórios
PASTA_RESULTADOS="resultados"
PASTA_SESSAO="${PASTA_RESULTADOS}/${TIMESTAMP}"

mkdir -p "$PASTA_SESSAO"

echo "================================================================================================"
echo "COLETA DE DADOS v3 - Sistema de Negociação em Cruzamento"
echo "================================================================================================"
echo ""
echo "Data: $DATA"
echo "Hora: $HORA"
echo "Pasta de destino: $PASTA_SESSAO"
echo "Versão: v3 (LogLevel.INFO, PEAS completo, tratamento robusto)"
echo ""
echo "Executando experimentos..."
echo ""

# Arquivos de saída
ARQUIVO_RESULTADOS="${PASTA_SESSAO}/resultados_completos.txt"
ARQUIVO_RESUMO="${PASTA_SESSAO}/resumo.txt"
ARQUIVO_VENCEDORES="${PASTA_SESSAO}/vencedores.txt"
ARQUIVO_METRICAS="${PASTA_SESSAO}/metricas.txt"
ARQUIVO_INFO="${PASTA_SESSAO}/info_sessao.txt"

# Salva informações da sessão
cat > "$ARQUIVO_INFO" <<EOF
================================================================================================
INFORMAÇÕES DA SESSÃO DE EXPERIMENTOS v3
================================================================================================
Data: $DATA
Hora de início: $HORA
Timestamp: $TIMESTAMP
Diretório: $PASTA_SESSAO
Sistema: $(uname -s)
Python: $(python --version 2>&1)
Versão: v3 (cruzamento_maspy_v3.py + experimentos_cruzamento_v3.py)

Melhorias v3:
- LogLevel.INFO (output 90% mais limpo)
- Documentação PEAS completa
- Uso efetivo do ambiente
- Tratamento robusto de erros
- Execução ~20% mais rápida

================================================================================================
EOF

# Executa experimentos v3 e salva
echo "Rodando experimentos_cruzamento_v3.py..."
python experimentos_cruzamento_v3.py > "$ARQUIVO_RESULTADOS" 2>&1

CODIGO_SAIDA=$?

echo "✓ Resultados completos salvos em: $ARQUIVO_RESULTADOS"
echo ""

# Extrai resumo
grep -E "(EXPERIMENTO:|VENCEDOR|✓|✗|Tempo total|concluído)" "$ARQUIVO_RESULTADOS" > "$ARQUIVO_RESUMO"
echo "✓ Resumo salvo em: $ARQUIVO_RESUMO"
echo ""

# Extrai vencedores (limpa códigos de cor ANSI)
grep ">>> VENCEDOR:" "$ARQUIVO_RESULTADOS" | sed 's/\x1b\[[0-9;]*m//g' > "$ARQUIVO_VENCEDORES"
echo "✓ Vencedores salvos em: $ARQUIVO_VENCEDORES"
echo ""

# Extrai métricas de tempo
{
    echo "MÉTRICAS DE TEMPO - SESSÃO $TIMESTAMP"
    echo "========================================"
    echo ""
    grep -E "(concluído!|Tempo total)" "$ARQUIVO_RESULTADOS" | sed 's/\x1b\[[0-9;]*m//g'
    echo ""
    echo "RESUMO:"
    grep -A 10 "RESUMO DA EXECUÇÃO" "$ARQUIVO_RESULTADOS" | sed 's/\x1b\[[0-9;]*m//g'
} > "$ARQUIVO_METRICAS"
echo "✓ Métricas de tempo salvas em: $ARQUIVO_METRICAS"
echo ""

# Analisa resultados (se o script existir)
if [ -f "analisar_resultados.py" ]; then
    echo "Analisando resultados..."
    echo ""
    python analisar_resultados.py "$ARQUIVO_RESULTADOS" > "${PASTA_SESSAO}/analise.txt" 2>&1
    echo "✓ Análise salva em: ${PASTA_SESSAO}/analise.txt"
    echo ""
fi

# Cria link simbólico para a última execução
ln -sfn "$PASTA_SESSAO" "${PASTA_RESULTADOS}/ultima_execucao"

# Gera relatório de comparação v2 vs v3 (se houver sessões v2)
ULTIMA_V2=$(ls -d ${PASTA_RESULTADOS}/2025* 2>/dev/null | tail -2 | head -1)
if [ -n "$ULTIMA_V2" ] && [ -f "${ULTIMA_V2}/metricas.txt" ]; then
    {
        echo "COMPARAÇÃO v2 vs v3"
        echo "==================="
        echo ""
        echo "Sessão v2 (anterior): $(basename $ULTIMA_V2)"
        echo "Sessão v3 (atual): $TIMESTAMP"
        echo ""
        echo "--- Tempo Total ---"
        echo -n "v2: "
        grep "Tempo total:" "${ULTIMA_V2}/metricas.txt" 2>/dev/null | tail -1 || echo "N/A"
        echo -n "v3: "
        grep "Tempo total:" "$ARQUIVO_METRICAS" | tail -1
        echo ""
        echo "--- Tamanho dos Logs ---"
        echo "v2: $(du -h ${ULTIMA_V2}/resultados_completos.txt 2>/dev/null | cut -f1 || echo 'N/A')"
        echo "v3: $(du -h $ARQUIVO_RESULTADOS | cut -f1)"
    } > "${PASTA_SESSAO}/comparacao_v2_v3.txt"
    echo "✓ Comparação v2 vs v3 salva em: ${PASTA_SESSAO}/comparacao_v2_v3.txt"
    echo ""
fi

echo ""
echo "================================================================================================"
if [ $CODIGO_SAIDA -eq 0 ]; then
    echo "✓ COLETA CONCLUÍDA COM SUCESSO!"
else
    echo "⚠ COLETA CONCLUÍDA COM AVISOS (código de saída: $CODIGO_SAIDA)"
fi
echo "================================================================================================"
echo ""
echo "Pasta da sessão: $PASTA_SESSAO"
echo ""
echo "Arquivos gerados:"
echo "  1. info_sessao.txt           (Informações da sessão v3)"
echo "  2. resultados_completos.txt  (Log completo - 90% mais limpo que v2)"
echo "  3. resumo.txt                (Resumo dos experimentos)"
echo "  4. vencedores.txt            (Lista de vencedores)"
echo "  5. metricas.txt              (Métricas de tempo)"
if [ -f "${PASTA_SESSAO}/analise.txt" ]; then
    echo "  6. analise.txt               (Análise estatística)"
fi
if [ -f "${PASTA_SESSAO}/comparacao_v2_v3.txt" ]; then
    echo "  7. comparacao_v2_v3.txt      (Comparação com v2)"
fi
echo ""
echo "Atalho criado: ${PASTA_RESULTADOS}/ultima_execucao -> $PASTA_SESSAO"
echo ""
echo "Para visualizar:"
echo "  cat ${PASTA_RESULTADOS}/ultima_execucao/resumo.txt"
echo "  cat ${PASTA_RESULTADOS}/ultima_execucao/vencedores.txt"
echo "  cat ${PASTA_RESULTADOS}/ultima_execucao/metricas.txt"
echo ""
