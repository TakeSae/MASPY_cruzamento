#!/bin/bash
# Script para coletar dados dos experimentos com timestamp automático
# Organiza resultados em pastas por data/hora

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
echo "COLETA DE DADOS - Sistema de Negociação em Cruzamento"
echo "================================================================================================"
echo ""
echo "Data: $DATA"
echo "Hora: $HORA"
echo "Pasta de destino: $PASTA_SESSAO"
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
INFORMAÇÕES DA SESSÃO DE EXPERIMENTOS
================================================================================================
Data: $DATA
Hora de início: $HORA
Timestamp: $TIMESTAMP
Diretório: $PASTA_SESSAO
Sistema: $(uname -s)
Python: $(python --version 2>&1)
================================================================================================
EOF

# Executa experimentos e salva
python run_all_experiments.py > "$ARQUIVO_RESULTADOS" 2>&1

echo "Resultados completos salvos em: $ARQUIVO_RESULTADOS"
echo ""

# Extrai resumo
grep -E "(EXPERIMENTO|VENCEDOR|OK|CONCLUIDO|RESUMO|Tempo)" "$ARQUIVO_RESULTADOS" > "$ARQUIVO_RESUMO"
echo "Resumo salvo em: $ARQUIVO_RESUMO"
echo ""

# Extrai vencedores
grep ">>> VENCEDOR:" "$ARQUIVO_RESULTADOS" | sed 's/\x1b\[[0-9;]*m//g' > "$ARQUIVO_VENCEDORES"
echo "Vencedores salvos em: $ARQUIVO_VENCEDORES"
echo ""

# Extrai métricas de tempo
grep -E "(Tempo:|concluido com sucesso)" "$ARQUIVO_RESULTADOS" | sed 's/\x1b\[[0-9;]*m//g' > "$ARQUIVO_METRICAS"
echo "Métricas de tempo salvas em: $ARQUIVO_METRICAS"
echo ""

# Analisa resultados (se o script existir)
if [ -f "analisar_resultados.py" ]; then
    echo "Analisando resultados..."
    echo ""
    python analisar_resultados.py "$ARQUIVO_RESULTADOS" > "${PASTA_SESSAO}/analise.txt" 2>&1
    echo "Análise salva em: ${PASTA_SESSAO}/analise.txt"
    echo ""
fi

# Cria link simbólico para a última execução
ln -sfn "$PASTA_SESSAO" "${PASTA_RESULTADOS}/ultima_execucao"

echo ""
echo "================================================================================================"
echo "COLETA CONCLUÍDA COM SUCESSO!"
echo "================================================================================================"
echo ""
echo "Pasta da sessão: $PASTA_SESSAO"
echo ""
echo "Arquivos gerados:"
echo "  1. info_sessao.txt      (Informações da sessão)"
echo "  2. resultados_completos.txt (Log completo)"
echo "  3. resumo.txt           (Resumo dos experimentos)"
echo "  4. vencedores.txt       (Lista de vencedores)"
echo "  5. metricas.txt         (Métricas de tempo)"
if [ -f "${PASTA_SESSAO}/analise.txt" ]; then
    echo "  6. analise.txt          (Análise dos resultados)"
fi
echo ""
echo "Atalho criado: ${PASTA_RESULTADOS}/ultima_execucao -> $PASTA_SESSAO"
echo ""
