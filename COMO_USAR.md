# Como Usar o Sistema de Experimentos

## Início Rápido

### 1. Coletar Dados Automaticamente (RECOMENDADO)

```bash
# Executa experimentos e gera arquivos com timestamp automaticamente
./coletar_dados.sh
```

Este script:
- ✅ Executa todos os 6 experimentos
- ✅ Gera arquivos com timestamp (AAAAMMDD_HHMMSS)
- ✅ Cria resumo e lista de vencedores
- ✅ Analisa os resultados automaticamente

### 2. Executar Manualmente

```bash
# Ativar ambiente virtual
source venv_maspy/bin/activate

# Executar todos os 6 experimentos
python run_all_experiments.py
```

### 3. Coletar Dados/Logs Manualmente

#### Salvar output completo em arquivo:
```bash
source venv_maspy/bin/activate
python run_all_experiments.py > "resultados_experimentos_$(date +%Y%m%d_%H%M%S).txt" 2>&1
```

#### Salvar apenas resumo:
```bash
source venv_maspy/bin/activate
python run_all_experiments.py 2>&1 | grep -E "(EXPERIMENTO|VENCEDOR|OK|CONCLUIDO)" > "resumo_$(date +%Y%m%d_%H%M%S).txt"
```

### 3. Executar Experimento Específico

```bash
# Exemplo: Executar apenas experimento 1
source venv_maspy/bin/activate
python -c "from experimentos_cruzamento import experimento_1_base; experimento_1_base()"
```

## Estrutura dos Dados Gerados

Cada experimento gera:

1. **Cabeçalho**: Número e descrição do experimento
2. **Configuração**: Lista de veículos com tipo e prioridade
3. **Negociação**:
   - Propostas enviadas por cada veículo
   - Avaliação do coordenador
   - Listagem de todas as propostas recebidas
4. **Decisão**: Anúncio do veículo vencedor
5. **Confirmações**: Mensagens de cada veículo (vencedor e perdedores)

## Exemplos de Coleta de Dados

### Para análise estatística:
```bash
# Extrai apenas os vencedores
python run_all_experiments.py 2>&1 | grep ">>> VENCEDOR:" > "vencedores_$(date +%Y%m%d_%H%M%S).txt"
```

### Para análise de prioridades:
```bash
# Extrai propostas e decisões
python run_all_experiments.py 2>&1 | grep -E "(Proposta:|Prioridade:)" > "prioridades_$(date +%Y%m%d_%H%M%S).txt"
```

### Para relatório completo com timestamp:
```bash
# Salva com data/hora no formato: experimento_20251019_152430.log
python run_all_experiments.py > "experimento_$(date +%Y%m%d_%H%M%S).log" 2>&1
```

## Validação dos Resultados

Após executar, verifique:

1. ✅ Todos os 6 experimentos devem mostrar `[OK]`
2. ✅ Experimento 1: Ambulância deve vencer
3. ✅ Experimento 2: Ambulancia1 (prio=100) deve vencer
4. ✅ Experimento 3: Qualquer carro pode vencer (mesma prioridade)
5. ✅ Experimento 4: Caminhão (prio=50) deve vencer
6. ✅ Experimento 5: Ambulância deve vencer
7. ✅ Experimento 6: Veiculo10 (prio=100) deve vencer

## Personalizar Experimentos

Para criar novos experimentos, edite [experimentos_cruzamento.py](experimentos_cruzamento.py):

```python
def experimento_7_customizado():
    """Seu experimento customizado"""
    veiculos = [
        {'nome': 'MeuVeiculo1', 'tipo': 'carro', 'prioridade': 50},
        {'nome': 'MeuVeiculo2', 'tipo': 'moto', 'prioridade': 10},
        # ... adicione mais veículos
    ]
    executar_experimento(
        7,
        "Meu Experimento Customizado",
        veiculos
    )
```

Depois execute:
```bash
python -c "from experimentos_cruzamento import experimento_7_customizado; experimento_7_customizado()"
```

## Troubleshooting

### Problema: "Agent not connected"
**Solução**: Execute cada experimento em processo separado usando `run_all_experiments.py`

### Problema: Timeout
**Solução**: Aumente o timeout em [run_all_experiments.py](run_all_experiments.py):
```python
result = subprocess.run(cmd, shell=True, check=True, timeout=20)  # Aumentar de 10 para 20
```

### Problema: Ambiente virtual não ativa
**Solução**:
```bash
cd /home/dachii/Projetos/MESTRADO/MASPY_cruzamento
source venv_maspy/bin/activate
```

## Arquivos de Saída Recomendados

### Formato com Timestamp (Recomendado)

Todos os comandos abaixo geram arquivos com data/hora no nome (formato: AAAAMMDD_HHMMSS):

1. **resultados_experimentos_20251019_153211.txt**: Log completo
2. **resumo_20251019_153211.txt**: Apenas informações principais
3. **vencedores_20251019_153211.txt**: Lista de vencedores

### Exemplo Completo de Coleta

```bash
# Ativa ambiente
source venv_maspy/bin/activate

# Executa e salva com timestamp
python run_all_experiments.py > "resultados_$(date +%Y%m%d_%H%M%S).txt" 2>&1

# Analisa os resultados (usa o arquivo mais recente)
python analisar_resultados.py resultados_*.txt
```

## Formato dos Dados

Os dados são gerados em formato texto com códigos ANSI de cores. Para remover cores:

```bash
python run_all_experiments.py 2>&1 | sed 's/\x1b\[[0-9;]*m//g' > "dados_limpos_$(date +%Y%m%d_%H%M%S).txt"
```

## Integração com Análise

Os dados podem ser parseados usando:
- Python (regex)
- Shell scripts (grep, awk, sed)
- Ferramentas de análise de logs

Exemplo de parsing em Python:
```python
import re

with open('resultados_experimentos.txt', 'r') as f:
    content = f.read()
    vencedores = re.findall(r'>>> VENCEDOR: (\w+)', content)
    print(f"Vencedores: {vencedores}")
```
