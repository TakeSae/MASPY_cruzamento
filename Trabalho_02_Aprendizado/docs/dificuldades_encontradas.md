# Dificuldades Encontradas - Trabalho 02

**Disciplina:** Sistemas Multiagentes - 2025.2 - UTFPR
**Autores:** Guilherme T. S. Abreu, Maria Eduarda S. Freitas

---

## 1. Sistema Travando Após Treinamento

Primeiro grande problema: após o treinamento completar, o sistema exibia "APRENDIZADO CONCLUÍDO COM SUCESSO!" mas não avançava. O processo ficava pendurado, sem gerar gráficos nem terminar.

Demorou para identificar a causa. Inicialmente achamos que era o matplotlib que não estava instalado. Depois pensamos que era erro na geração de gráficos. Mas na verdade o código nem chegava nessa parte.

O problema era que `Admin().start_system()` nunca retornava. Os agentes de veículos continuavam executando mesmo depois do coordenador chamar `stop_cycle()`. Tentamos adicionar verificação de parada no plano dos veículos, mas não resolveu.

**Solução final:** Adicionar um prompt pedindo para o usuário pressionar ENTER após o treinamento MASPY terminar. Não é elegante, mas funciona. Para scripts automatizados, pipe com `echo` ainda funciona normalmente.

---

## 2. Matplotlib Não Instalado

Simples: estava marcado como opcional no requirements.txt. Instalamos e marcamos como obrigatório. Problema resolvido.

---

## 3. Mudança na API do MASPY

Ao atualizar o MASPY, vários erros de `AttributeError: 'Belief' object has no attribute 'args'` apareceram. A API mudou de `.args` para `.values` na versão 2025.11.9.

Primeira tentativa de correção usou `.values[0]`, o que causou `TypeError: 'int' object is not subscriptable`. O correto é usar `.values` diretamente, sem indexação.

Corrigido em 6 locais do código onde usávamos `.args[0]`.

---

## 4. Gráficos com Dados Errados

Três problemas aqui:

**a) Gráficos mostrando agentes que não existiam na execução:**
Executando cenário com 2 veículos, mas o gráfico mostrava 10+ agentes de execuções anteriores. Descobrimos que o MetricsCollector é singleton global e acumula dados entre execuções.

Solução: adicionar `reset()` no início de cada execução.

**b) Taxa de acerto sempre 0%:**
O código coletava recompensas mas nunca registrava se as ações eram corretas ou incorretas. Os campos `acoes_corretas` e `acoes_incorretas` ficavam em zero. Cálculo: 0/0 = 0%.

Solução: adicionar `METRICS_COLLECTOR.registrar_acao()` no loop de validação.

**c) Agentes de veículos aparecendo no gráfico de comparação:**
Os veículos apenas observam, não tomam ações. Mas apareciam no gráfico com barras vazias, confundindo a visualização.

Solução: filtrar para mostrar apenas agentes que fizeram pelo menos uma ação.

---

## 5. Gráficos Limitados a 20 Episódios

Executava com 100 episódios mas os gráficos mostravam apenas 20. Havia um `min(20, self.num_episodes)` no código que limitava artificialmente.

Removemos a limitação. Agora usa todos os episódios solicitados.

---

## 6. Gráficos Mostrando Dados de Validação ao Invés de Treinamento

Problema crítico descoberto: os gráficos estavam mostrando dados PERFEITOS - linhas horizontais com recompensa 1000 em todos os episódios. Não havia curva de aprendizado, oscilações, ou convergência gradual. Parecia fake.

**Causa raiz:**
O código chamava `model.learn(qlearning, num_episodes=100)` do MASPY, que roda o Q-Learning internamente. Mas não tínhamos acesso aos dados DURANTE o treinamento. Depois do `model.learn()` terminar, o código simulava episódios de teste usando a política já aprendida (ótima). Como a política estava perfeita, todas as escolhas eram corretas - recompensa máxima sempre.

Os gráficos mostravam esses dados de VALIDAÇÃO, não de TREINAMENTO. Por isso eram lineares.

**Tentativas que não funcionaram:**

1. **Tentar usar callbacks do MASPY:** A API `EnvModel.learn()` não expõe callbacks ou hooks para capturar métricas durante o treinamento.

2. **Interceptar a Q-table:** Tentamos acessar `model.q_table` após cada episódio, mas o objeto é interno e não acessível externamente.

3. **Modificar o MASPY:** Cogitamos fazer fork e adicionar logging, mas seria muita manutenção.

**Solução final: Implementar Q-Learning manualmente**

Substituímos o `model.learn()` por nossa própria implementação do algoritmo Q-Learning. Assim temos controle total sobre cada episódio e podemos coletar métricas em tempo real.

Implementação (linhas 1350-1468):

```python
# Parâmetros Q-Learning padrão
alpha = 0.1        # Taxa de aprendizado
gamma = 0.9        # Fator de desconto
epsilon = 1.0      # Exploração inicial (100%)
epsilon_decay = 0.995
epsilon_min = 0.01

# Q-table manual
q_table = defaultdict(float)

for ep in range(num_episodes):
    estado = env.possible_starts.copy()
    recompensa_total = 0

    while not terminado:
        # Epsilon-greedy: explorar ou exploitar
        if random.random() < epsilon:
            acao = random.choice(veiculos_disponiveis)  # Exploração
        else:
            acao = argmax(q_table[estado, :])  # Exploitação

        # Executar ação
        novo_estado, recompensa, terminado = env.transicao(estado, acao)

        # Bellman equation: Q(s,a) ← Q(s,a) + α[R + γ max Q(s',a') - Q(s,a)]
        q_table[estado, acao] += alpha * (
            recompensa + gamma * max(q_table[novo_estado, :]) - q_table[estado, acao]
        )

        # Registrar métricas em tempo real
        METRICS_COLLECTOR.adicionar_recompensa_episodio(ep, recompensa)
        METRICS_COLLECTOR.registrar_acao(escolha_foi_correta)

        estado = novo_estado

    # Decair epsilon (menos exploração ao longo do tempo)
    epsilon = max(epsilon_min, epsilon * epsilon_decay)
```

**Resultado:**

Agora os gráficos mostram a curva REAL de aprendizado:
- Episódios iniciais: recompensas negativas (explorando aleatoriamente, errando muito)
- Episódios intermediários: recompensas melhorando gradualmente (aprendendo)
- Episódios finais: recompensas próximas do ótimo (convergência)
- Desvio padrão alto no início, baixo no final
- Taxa de acerto cresce de ~10% para ~90-100%

**Trade-off:**
Perdemos a otimização interna do MASPY, mas ganhamos visibilidade completa do processo. Para este trabalho acadêmico, onde precisamos DEMONSTRAR o aprendizado, vale muito a pena.

---

## Observações Gerais

- Falta de feedback durante operações demoradas deixa o usuário sem saber se o sistema travou ou está processando. Adicionamos mensagens de progresso na geração de gráficos.

- APIs de frameworks mudam. O MASPY mudou de `.args` para `.values` entre versões. Sempre verificar a documentação ao atualizar dependências.

- Singletons globais podem acumular estado entre execuções. Importante ter um `reset()` explícito.

---

**Última atualização:** 05/12/2025
