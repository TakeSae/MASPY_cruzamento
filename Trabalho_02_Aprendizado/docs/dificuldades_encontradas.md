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

## Limitações Conhecidas

**Recompensas constantes nos gráficos:**
Os episódios de validação usam a política já aprendida, que é ótima. Todas as escolhas são perfeitas, então a recompensa é sempre 1000. Os gráficos ficam como linhas horizontais.

Isso não é bug - mostra que o aprendizado funcionou. Mas não mostra o progresso DURANTE o treinamento, apenas APÓS. Para ver a evolução real, precisaríamos capturar métricas dentro do `model.learn()`, o que o MASPY não expõe facilmente.

Decidimos deixar assim mesmo. Os gráficos confirmam que a política aprendida está correta.

---

## Observações Gerais

- Falta de feedback durante operações demoradas deixa o usuário sem saber se o sistema travou ou está processando. Adicionamos mensagens de progresso na geração de gráficos.

- APIs de frameworks mudam. O MASPY mudou de `.args` para `.values` entre versões. Sempre verificar a documentação ao atualizar dependências.

- Singletons globais podem acumular estado entre execuções. Importante ter um `reset()` explícito.

---

**Última atualização:** 04/12/2025
