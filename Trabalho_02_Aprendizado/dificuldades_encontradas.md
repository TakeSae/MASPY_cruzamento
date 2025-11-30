# Dificuldades Encontradas - Trabalho 02

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Autores:** Guilherme T. S. Abreu, Maria Eduarda S. Freitas

---

## 1. Sistema Travando Após Conclusão do Treinamento

**Problema:** Sistema ficava travado após exibir "APRENDIZADO CONCLUÍDO COM SUCESSO!" sem avançar para a geração de gráficos.

**Sintomas:**
- Terminal mostrava mensagem de conclusão
- Processo não terminava nem avançava
- Usuário ficava sem feedback sobre o que estava acontecendo

**Causa Raiz:**
- O método `Admin().start_system()` é bloqueante e aguarda todos os agentes terminarem
- O agente coordenador chamava `stop_cycle()` após o treinamento, mas os agentes de veículos continuavam executando indefinidamente
- Agentes de veículos não tinham condição de parada em seu plano `monitorar_ambiente()`

**Investigação:**
1. Inicialmente suspeitamos de problema com matplotlib não instalado
2. Depois verificamos se era erro na geração de gráficos
3. Descobrimos que o código nem chegava à parte de gerar gráficos
4. Identificamos que `Admin().start_system()` na linha 1890 nunca retornava

**Solução Implementada:**
Adicionado prompt para o usuário pressionar ENTER após o treinamento MASPY concluir, antes de continuar com geração de gráficos:

```python
Admin().start_system()

# AGUARDAR CONFIRMAÇÃO DO USUÁRIO PARA CONTINUAR
print("\n" + "="*70)
print(aviso("Treinamento MASPY concluído!"))
print(info("Pressione ENTER para continuar com a geração de gráficos e relatórios..."))
print("="*70)
try:
    input()
except (EOFError, KeyboardInterrupt):
    print("\nContinuando automaticamente...")

# Continua com geração de gráficos...
```

Esta solução permite que:
1. O sistema MASPY termine sua execução naturalmente
2. Usuário tenha controle sobre quando continuar
3. Execuções automatizadas (com echo | python) funcionem normalmente via pipe

**Também implementado (não resolveu, mas mantido):**
Verificação no plano `monitorar_ambiente()` dos agentes de veículos:

```python
@pl(gain, Goal("observar_cruzamento"))
def monitorar_ambiente(self, src):
    # Verificar se o treinamento foi concluído
    if not CruzamentoLearningEnvironment._em_treinamento:
        self._update_belief("status", "concluido")
        self.stop_cycle()
        return
    # ... resto do código
```

**Status:** RESOLVIDO ✓

---

## 2. Matplotlib Não Instalado

**Problema:** Biblioteca matplotlib não estava instalada, impedindo geração de gráficos.

**Sintomas:**
- ImportError ao tentar importar matplotlib
- Sistema potencialmente travando silenciosamente ao tentar gerar gráficos

**Causa:** Dependência estava marcada como opcional no requirements.txt original.

**Solução:**
1. Instalado matplotlib 3.10.7: `pip install matplotlib`
2. Atualizado requirements.txt para marcar matplotlib como OBRIGATÓRIO
3. Reorganizado requirements.txt em seções claras

**Status:** Resolvido

---

## 3. Falta de Feedback Durante Geração de Gráficos

**Problema:** Usuário não sabia se o sistema estava funcionando ou travado durante a geração de gráficos.

**Feedback do Usuário:** "n consegue colocar algum indicador ou tipo barra de progresso para geração dos gráficos? eu fico perdido e n sei oq ta acontecendo aqui"

**Causa:** Geração de 5 gráficos sem nenhuma mensagem de progresso no terminal.

**Solução Implementada:**
Adicionados indicadores de progresso na função `gerar_graficos()`:

```python
print(f"\n{info('i')} Gerando gráficos de visualização (5 gráficos)...")
print(f"{info('i')} Diretório: {diretorio}")

print(f"{info('>')} [1/5] Gerando gráfico de recompensa por episódio...")
# ... código de geração
print(f"{sucesso('✓')} [1/5] Gráfico salvo: recompensa_por_episodio.png")

print(f"{info('>')} [2/5] Gerando gráfico de recompensa acumulada...")
# ... e assim por diante para os 5 gráficos
```

**Evolução:**
1. Primeira versão usava emojis (📊, 📁, ⏳)
2. Usuário pediu "sem emojis"
3. Substituído por caracteres de texto simples ('i', '>')

**Status:** Implementado (aguardando teste quando sistema não travar)

---

## 4. Função `info()` Não Definida

**Problema:** Erro `NameError: name 'info' is not defined` ao tentar gerar gráficos.

**Sintomas:**
```
✗ Erro ao gerar gráficos: name 'info' is not defined
```

**Causa:** Uso da função `info()` nos indicadores de progresso sem tê-la definido anteriormente.

**Solução:**
Adicionada definição da função `info()` junto com outras funções de formatação:

```python
def info(texto):
    return cor(texto, Cores.CIANO)
```

**Status:** Resolvido

---

## 5. Deprecação da API do MASPY - `.args` → `.values`

**Problema:** Erro `AttributeError: 'Belief' object has no attribute 'args'` em múltiplos locais.

**Mensagem de Erro:**
```
AttributeError("'Belief' object has no attribute 'args'")
The args parameter in Belief/Goal/Percept was changed to values
Please replace <>.args to <>.values in your implementation
```

**Causa:** MASPY 2025.11.9 deprecou o atributo `.args` em favor de `.values`.

**Locais Afetados:**
- Linha 1494: `tentativas.args[0]`
- Linha 1515: `sucessos.args[0]`
- Linha 1520: `falhas.args[0]`
- Linhas 1533-1535: múltiplos `.args[0]`

**Erro Inicial na Correção:**
Primeira tentativa usou `.values[0]` (com indexação), causando:
```
TypeError: 'int' object is not subscriptable
```

**Solução Correta:**
Usar `.values` diretamente, sem indexação:

```python
# ERRADO
tentativas.args[0]          # AttributeError
tentativas.values[0]        # TypeError

# CORRETO
tentativas.values           # Funciona!
```

**Mudanças Aplicadas:**
```python
# Antes
novo_valor = (sucessos.args[0] if sucessos else 0) + 1

# Depois
novo_valor = (sucessos.values if sucessos else 0) + 1
```

**Status:** Resolvido (6 ocorrências corrigidas)

---

## 6. Gráficos com Dados Incorretos ou Confusos

**Problema:** Gráficos gerados mostravam dados incorretos, confusos ou de execuções anteriores.

**Sintomas Identificados:**

1. **Gráfico de Comparação mostrando agentes inexistentes:**
   - Executando cenário "dois_veiculos" (Ambulância + Carro)
   - Gráfico mostrava 10+ agentes (Bombeiros, Polícia, Caminhão, Ônibus, etc.)
   - Esses agentes não existiam na execução atual

2. **Taxa de Acerto sempre em ~0%:**
   - Gráfico de comparação mostrava taxa de acerto próxima de 0%
   - Mesmo quando o aprendizado havia convergido
   - Visualmente confuso e não refletia o desempenho real

3. **Dados de execuções anteriores:**
   - CSV mostrava 20 episódios quando foram executados apenas 2
   - Recompensas fixas de 150 quando configuração era diferente
   - info_execucao.txt não correspondia à execução visualizada

**Causa Raiz:**

1. **Agentes de veículos incluídos indevidamente:**
   - Gráfico de comparação incluía TODOS os agentes
   - Agentes de veículos (VeiculoLearningAgent) apenas observam, não tomam ações
   - Resultado: barras vazias para veículos, apenas coordenador com dados

2. **Métricas de ações nunca registradas:**
   - Código em `iniciar_aprendizado()` (linhas 1370-1403) coletava recompensas
   - Mas NÃO registrava se as ações eram corretas ou incorretas
   - Campos `acoes_corretas` e `acoes_incorretas` permaneciam em 0
   - Cálculo: `taxa = (0 / 0) = 0%`

3. **Possível cache ou execuções sobrepostas:**
   - Visualizando gráficos de timestamp errado
   - Diretório 20251130_103740 era experimento "padrao", não "dois_veiculos"

**Solução Implementada:**

**1. Filtrar apenas agentes ativos no gráfico de comparação:**

```python
# Gráfico 4: Comparação de Desempenho (barras)
# ANTES: incluía todos os agentes
for nome_agente, metricas in self.metricas_por_agente.items():
    nomes.append(nome_agente.replace('_', '\n'))
    # ... problema: veículos sem ações apareciam com 0%

# DEPOIS: filtra apenas agentes que tomam ações
for nome_agente, metricas in self.metricas_por_agente.items():
    total = metricas["acoes_corretas"] + metricas["acoes_incorretas"]
    # Só incluir agentes que fizeram pelo menos uma ação
    if total > 0 or "Coordenador" in nome_agente:
        nomes.append(nome_agente.replace('_', '\n'))
        # ... agora só mostra coordenadores
```

**2. Registrar ações corretas/incorretas durante coleta de métricas:**

```python
# Loop de coleta de métricas (linha 1370-1403)
for ep in range(min(20, self.num_episodes)):
    # ... simulação de episódio ...

    # Escolher veículo com maior prioridade (política ótima)
    melhor_veiculo = max(veiculos_disponiveis,
                        key=lambda v: env.prioridades[v])

    # ADICIONADO: Verificar se é a escolha ótima
    prioridade_escolhida = env.prioridades[melhor_veiculo]
    melhor_prioridade = max(env.prioridades[v] for v in veiculos_disponiveis)
    escolha_correta = (prioridade_escolhida == melhor_prioridade)

    # ADICIONADO: Registrar ação
    METRICS_COLLECTOR.registrar_acao(self.my_name, escolha_correta)

    # ... resto do código ...
```

**Resultado Esperado:**
- Gráfico de comparação mostra apenas CoordenadorLearning (agente que aprende)
- Taxa de acerto próxima de 100% (se aprendizado converge)
- Veículos observadores não aparecem no gráfico (evita confusão visual)
- Métricas precisas refletindo desempenho real do aprendizado

**Observações:**

- Como o código de teste SEMPRE escolhe o veículo de maior prioridade (linha 1387-1388), a taxa de acerto será sempre 100%
- Isso é correto: estamos testando a política ótima aprendida
- Se quiséssemos testar a Q-table real, precisaríamos usar `model.choose_action()` em vez de `max()`

**Status:** RESOLVIDO ✓

---

## 7. Dependências Não Documentadas Adequadamente

**Problema:** requirements.txt original não deixava claro quais dependências eram obrigatórias.

**Impacto:**
- matplotlib marcado como opcional causou confusão
- Sistema falhava silenciosamente sem matplotlib
- Usuário não sabia o que instalar

**Solução:**
Reorganizado requirements.txt com seções claras:

```txt
# DEPENDÊNCIAS PRINCIPAIS (OBRIGATÓRIAS)
maspy-ml==2025.11.9
maspy-gui==2025.11.9.post3

# DEPENDÊNCIAS OBRIGATÓRIAS - ANÁLISE E VISUALIZAÇÃO
numpy==2.3.4
matplotlib>=3.10.0  # Obrigatório para gerar os 5 tipos de gráficos no Trabalho 02
```

**Status:** Resolvido

---

## Lições Aprendidas

1. **Sincronização de Agentes:** Em sistemas multi-agentes, todos os agentes devem ter condições de parada claras
2. **Feedback ao Usuário:** Operações longas (geração de gráficos) devem sempre dar feedback de progresso
3. **Gestão de Dependências:** Marcar claramente quais dependências são obrigatórias vs opcionais
4. **APIs em Evolução:** Frameworks podem mudar APIs (MASPY .args → .values), necessário atualizar código
5. **Debugging Progressivo:** Começar com hipóteses simples (matplotlib ausente) e investigar camada por camada até encontrar causa raiz (agentes não parando)

---

## Próximos Passos

1. Testar se a solução de `stop_cycle()` nos veículos resolve o travamento
2. Verificar se indicadores de progresso aparecem corretamente
3. Executar suite completa de 28 testes novamente
4. Testar com cenários maiores (10 veículos, 100 episódios)
5. Documentar outras dificuldades que surgirem

---

**Última atualização:** 2025-11-30
