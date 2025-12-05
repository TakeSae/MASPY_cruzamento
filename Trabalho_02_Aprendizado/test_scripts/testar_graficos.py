#!/usr/bin/env python3
"""
Script de teste rápido para gerar gráficos matplotlib.
Não requer MASPY instalado - apenas matplotlib.
"""

import sys
import os

# Adicionar cores para output
class Cores:
    RESET = '\033[0m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    BOLD = '\033[1m'

def sucesso(texto):
    return f"{Cores.VERDE}{texto}{Cores.RESET}"

def titulo(texto):
    return f"{Cores.BOLD}{Cores.CIANO}{texto}{Cores.RESET}"

def aviso(texto):
    return f"{Cores.AMARELO}{texto}{Cores.RESET}"

print(titulo("="*70))
print(titulo("  TESTE DE GERAÇÃO DE GRÁFICOS MATPLOTLIB"))
print(titulo("="*70) + "\n")

# Verificar matplotlib
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    print(sucesso(f"Matplotlib {matplotlib.__version__} detectado"))
except ImportError as e:
    print(f"{aviso('✗')} Erro: {e}")
    print(f"\n{aviso('Solução:')} pip install matplotlib numpy")
    sys.exit(1)

# Configurar backend para não exibir janelas
matplotlib.use('Agg')

# Criar diretório de teste
test_dir = "graficos_teste"
if not os.path.exists(test_dir):
    os.makedirs(test_dir)
    print(sucesso(f"Diretório '{test_dir}/' criado"))

# Simular dados de aprendizado
print(f"\n{titulo('Gerando dados simulados...')}")
episodios = list(range(1, 21))
recompensas = [50 + i*2 + np.random.randint(-5, 5) for i in range(20)]
recompensas_acum = np.cumsum(recompensas)

print(f"  • Episódios: {len(episodios)}")
print(f"  • Recompensa média: {np.mean(recompensas):.2f}")
print(f"  • Recompensa total: {recompensas_acum[-1]:.2f}")

# Gráfico 1: Recompensa por Episódio
print(f"\n{titulo('Gerando gráficos...')}")
plt.figure(figsize=(10, 6))
plt.plot(episodios, recompensas, marker='o', linewidth=2, color='steelblue')
plt.xlabel('Episódio', fontsize=12)
plt.ylabel('Recompensa', fontsize=12)
plt.title('Recompensa por Episódio - Teste', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
caminho1 = os.path.join(test_dir, 'teste_recompensa_episodio.png')
plt.savefig(caminho1, dpi=300, bbox_inches='tight')
plt.close()
print(sucesso(f"Gráfico 1: {caminho1}"))

# Gráfico 2: Recompensa Acumulada
plt.figure(figsize=(10, 6))
plt.plot(episodios, recompensas_acum, marker='s', linewidth=2, color='orange')
plt.xlabel('Episódio', fontsize=12)
plt.ylabel('Recompensa Acumulada', fontsize=12)
plt.title('Recompensa Acumulada - Teste', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
caminho2 = os.path.join(test_dir, 'teste_recompensa_acumulada.png')
plt.savefig(caminho2, dpi=300, bbox_inches='tight')
plt.close()
print(sucesso(f"Gráfico 2: {caminho2}"))

# Gráfico 3: Média Móvel
janela = 5
media_movel = np.convolve(recompensas, np.ones(janela)/janela, mode='valid')
episodios_mm = episodios[janela-1:]

plt.figure(figsize=(10, 6))
plt.plot(episodios, recompensas, alpha=0.3, linewidth=1, label='Recompensa bruta')
plt.plot(episodios_mm, media_movel, marker='o', linewidth=2, color='green', label=f'Média móvel (janela={janela})')
plt.xlabel('Episódio', fontsize=12)
plt.ylabel('Recompensa', fontsize=12)
plt.title('Média Móvel - Teste', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
caminho3 = os.path.join(test_dir, 'teste_media_movel.png')
plt.savefig(caminho3, dpi=300, bbox_inches='tight')
plt.close()
print(sucesso(f"Gráfico 3: {caminho3}"))

# Gráfico 4: Comparação (barras duplas)
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

agentes = ['Agente A', 'Agente B', 'Agente C']
recomp_media = [75, 85, 65]
taxa_acerto = [85, 92, 78]

x = np.arange(len(agentes))
width = 0.35

bars1 = ax1.bar(x - width/2, recomp_media, width, label='Recompensa Média', color='steelblue', alpha=0.8)
bars2 = ax2.bar(x + width/2, taxa_acerto, width, label='Taxa de Acerto (%)', color='orange', alpha=0.8)

ax1.set_xlabel('Agente', fontsize=12)
ax1.set_ylabel('Recompensa Média', fontsize=12, color='steelblue')
ax2.set_ylabel('Taxa de Acerto (%)', fontsize=12, color='orange')
ax1.set_title('Comparação de Desempenho - Teste', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(agentes)
ax1.tick_params(axis='y', labelcolor='steelblue')
ax2.tick_params(axis='y', labelcolor='orange')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax1.grid(True, alpha=0.3, axis='y')

caminho4 = os.path.join(test_dir, 'teste_comparacao.png')
plt.savefig(caminho4, dpi=300, bbox_inches='tight')
plt.close()
print(sucesso(f"Gráfico 4: {caminho4}"))

# Gráfico 5: Análise de Convergência
plt.figure(figsize=(10, 6))
plt.plot(episodios, recompensas, alpha=0.3, linewidth=1, color='blue')

# Linha de tendência (regressão linear)
z = np.polyfit(episodios, recompensas, 1)
p = np.poly1d(z)
plt.plot(episodios, p(episodios), linewidth=2, color='red', label='Tendência (regressão linear)')

# Marcar ponto de convergência simulado
ep_convergencia = 12
plt.axvline(x=ep_convergencia, color='green', linestyle='--', alpha=0.7, linewidth=2, label=f'Convergência (ep {ep_convergencia})')

plt.xlabel('Episódio', fontsize=12)
plt.ylabel('Recompensa', fontsize=12)
plt.title('Análise de Convergência - Teste', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
caminho5 = os.path.join(test_dir, 'teste_convergencia.png')
plt.savefig(caminho5, dpi=300, bbox_inches='tight')
plt.close()
print(sucesso(f"Gráfico 5: {caminho5}"))

# Resumo
print(f"\n{titulo('='*70)}")
print(titulo("  TESTE CONCLUÍDO COM SUCESSO"))
print(titulo('='*70))
print(f"\n{sucesso} 5 gráficos gerados com sucesso!")
print(f"\n{aviso('Localização:')} {os.path.abspath(test_dir)}/")
print(f"\n{aviso('Arquivos gerados:')}")
print(f"  1. teste_recompensa_episodio.png")
print(f"  2. teste_recompensa_acumulada.png")
print(f"  3. teste_media_movel.png")
print(f"  4. teste_comparacao.png")
print(f"  5. teste_convergencia.png")
print(f"\n{aviso('Próximo passo:')} Executar sistema completo com MASPY")
print(f"  cd MASPY_learning")
print(f"  python cruzamento_maspy_learning.py --experimento base --episodios 20")
print()
