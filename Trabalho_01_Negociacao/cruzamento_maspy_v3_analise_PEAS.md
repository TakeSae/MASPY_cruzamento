ANÁLISE PEAS

1. PERFORMANCE (Medida de Desempenho)
   Objetivos do sistema:
   - Priorizar corretamente veículos de emergência (ambulâncias, bombeiros)
   - Minimizar tempo total de espera dos veículos
   - Garantir travessia segura (apenas 1 veículo por vez)
   - Evitar deadlocks e starvation
   - Tempo de decisão < 1 segundo

   Critérios de sucesso:
   - Taxa de sucesso de priorização: 100%
   - Ausência de conflitos (2+ veículos no cruzamento simultaneamente)
   - Todos os veículos eventualmente atravessam (fairness)
   - Sistema encerra sem erros

2. ENVIRONMENT (Ambiente)
   Tipo: Cruzamento de 4 vias

   Características (Russell & Norvig, 2010):
   - Parcialmente observável: Veículos só percebem o cruzamento local
   - Determinístico: Decisões são previsíveis (maior prioridade sempre vence)
   - Sequencial: Ações afetam estado futuro do cruzamento
   - Dinâmico: Novos veículos podem chegar (extensão futura)
   - Discreto: Eventos bem definidos (chegada, proposta, decisão, travessia)
   - Multi-agente: Múltiplos veículos competindo por recurso compartilhado

   Estado do ambiente:
   - cruzamento_livre: Boolean (indica se cruzamento está livre/ocupado)
   - veiculos_aguardando: List[Dict] (fila de veículos esperando)
   - veiculo_atravessando: String (ID do veículo atualmente atravessando)

3. ACTUATORS (Atuadores)

   Agente Veículo (VeiculoAgent):
   - Enviar proposta de travessia ao coordenador (tell message)
   - Registrar chegada no ambiente (call_env_method)
   - Atravessar o cruzamento quando autorizado
   - Notificar ambiente sobre início de travessia
   - Aguardar quando outro veículo vence

   Agente Coordenador (CoordenadorAgent):
   - Receber e armazenar propostas dos veículos
   - Avaliar prioridades segundo critério max(prioridade)
   - Comunicar decisão via broadcast para todos os veículos
   - Atualizar contador de propostas recebidas
   - Adicionar objetivo de decidir quando todas propostas chegam

4. SENSORS (Sensores)

   Agente Veículo (percepções):
   - Detectar própria chegada ao cruzamento (gain Goal)
   - Receber mensagens do coordenador com decisão (gain Belief)
   - Conhecer tipo e prioridade próprios (atributos internos)
   - Perceber ID próprio (self.my_name)

   Agente Coordenador (percepções):
   - Receber mensagens de propostas dos veículos (gain Belief)
   - Contar número de propostas recebidas (contador interno)
   - Acessar lista de propostas armazenadas (get Belief)
   - Detectar quando todas as propostas chegaram (contador == num_veiculos)

ARQUITETURA BDI (Beliefs, Desires, Intentions)
-----------------------------------------------

VeiculoAgent:
- Beliefs (Crenças):
  * tipo: String - tipo do veículo (carro, ambulância, etc.)
  * prioridade: Int - valor de urgência (0-100)
  * Belief("decisao", vencedor_id) - resultado da negociação

- Desires/Goals (Objetivos):
  * Goal("atravessar") - objetivo de atravessar o cruzamento

- Intentions/Plans (Planos):
  * enviar_proposta() - trigger: gain Goal("atravessar")
    Ação: registra no ambiente e envia proposta ao coordenador
  * receber_decisao() - trigger: gain Belief("decisao", Any)
    Ação: reage à decisão (atravessa ou aguarda)

CoordenadorAgent:
- Beliefs (Crenças):
  * Belief("proposta", dados) - propostas recebidas (múltiplas instâncias)
  * contador_propostas: Int - número de propostas recebidas

- Desires/Goals (Objetivos):
  * Goal("decidir") - objetivo de escolher vencedor

- Intentions/Plans (Planos):
  * coletar_propostas() - trigger: gain Belief("proposta", Any)
    Ação: armazena proposta e incrementa contador
  * decidir_vencedor() - trigger: gain Goal("decidir")
    Ação: avalia propostas e decide por maior prioridade

PROTOCOLO DE NEGOCIAÇÃO

Tipo: Negociação centralizada com leilão de prioridades
Coordenador: CoordenadorAgent (árbitro central)
Participantes: VeiculoAgent (licitantes)

Fases da negociação:

1. INICIALIZAÇÃO
   - Sistema cria N veículos e 1 coordenador
   - Cada veículo ganha Goal("atravessar") automaticamente
   - Ambiente é inicializado com cruzamento_livre = True

2. ENVIO DE PROPOSTAS (Fase de licitação)
   - Trigger: gain Goal("atravessar") em cada veículo
   - Ação: Veículo registra chegada no ambiente
   - Mensagem: send("Coordenador_1", tell, Belief("proposta", dados))
   - Dados: {id: nome_agente, tipo: string, prio: int}

3. COLETA (Fase de recebimento)
   - Trigger: gain Belief("proposta", Any) no coordenador
   - Ação: Coordenador armazena proposta e incrementa contador
   - Condição: Se contador == num_veiculos → próxima fase

4. TRIGGER DE DECISÃO
   - Quando todas propostas recebidas
   - Coordenador adiciona Goal("decidir") a si mesmo

5. AVALIAÇÃO (Fase de análise)
   - Trigger: gain Goal("decidir") no coordenador
   - Ação: Busca todas as propostas armazenadas
   - Algoritmo: max_prio = max(proposta.prio for proposta in propostas)
   - Critério de desempate: Ordem de processamento (FIFO)

6. DECISÃO (Fase de escolha)
   - Coordenador seleciona vencedor (maior prioridade)
   - Valida que vencedor existe e é válido

7. NOTIFICAÇÃO (Fase de anúncio)
   - Mensagem: send(broadcast, tell, Belief("decisao", vencedor_id))
   - Todos os veículos recebem simultaneamente

8. REAÇÃO (Fase de resposta)
   - Trigger: gain Belief("decisao", vencedor_id) em cada veículo
   - Vencedor: Notifica ambiente e "atravessa"
   - Perdedores: Aguardam (em implementação futura podem renogociar)

9. FINALIZAÇÃO
   - Todos os agentes chamam stop_cycle()
   - Sistema encerra de forma limpa

Propriedades do protocolo:
- Completo: Sempre há um vencedor
- Determinístico: Mesmo input → mesmo output
- Eficiente: O(n) mensagens (n veículos)
- Justo: Prioridades refletem urgência real

PRIORIDADES DEFINIDAS

Tipo de Veículo     | Prioridade | Justificativa
--------------------|------------|----------------------------------
Ambulância          | 100        | Emergência médica (vidas em risco)
Bombeiros           | 95-98      | Emergência (incêndios, resgates)
Caminhão            | 50         | Veículo grande (dificulta tráfego)
Ônibus              | 30-40      | Transporte coletivo (múltiplos passageiros)
Táxi                | 20         | Transporte de passageiros
Carro               | 10-15      | Veículo comum
Moto                | 5          | Veículo pequeno (mais ágil, menor impacto)

Critério de desempate:
- Se prio(A) == prio(B): ordem de chegada (processamento FIFO)