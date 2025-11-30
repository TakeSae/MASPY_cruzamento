import subprocess
import sys
import time
from datetime import datetime

def run_experiment(name, func_name):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Executando {name}...")
    cmd = f"python -c 'from experimentos_cruzamento import {func_name}; {func_name}()'"

    start_time = time.time()
    try:
        result = subprocess.run(cmd, shell=True, check=True, timeout=10)
        elapsed = time.time() - start_time
        print(f"  {name} concluido com sucesso! (Tempo: {elapsed:.3f}s)")
        return True, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"  ERRO: {name} excedeu o tempo limite! (Tempo: {elapsed:.3f}s)")
        return False, elapsed
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"  ERRO ao executar {name}: {e} (Tempo: {elapsed:.3f}s)")
        return False, elapsed

if __name__ == "__main__":
    inicio_total = time.time()
    timestamp_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"Inicio da execucao: {timestamp_inicio}")
    print("\nExecutando 6 experimentos separadamente...")

    experimentos = [
        ("Experimento 1 - Cenario Base", "experimento_1_base"),
        ("Experimento 2 - Multiplas Emergencias", "experimento_2_multiplas_emergencias"),
        ("Experimento 3 - Prioridades Iguais", "experimento_3_prioridades_iguais"),
        ("Experimento 4 - Cargas Pesadas", "experimento_4_cargas_pesadas"),
        ("Experimento 5 - Cenario Misto", "experimento_5_misto"),
        ("Experimento 6 - Teste de Estresse", "experimento_6_estresse"),
    ]

    resultados = []
    for nome, func in experimentos:
        sucesso, tempo = run_experiment(nome, func)
        resultados.append((nome, sucesso, tempo))

    tempo_total = time.time() - inicio_total
    timestamp_fim = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print("\n" + "="*80)
    print("RESUMO DA EXECUCAO")
    print("="*80)

    for nome, sucesso, tempo in resultados:
        status = "OK" if sucesso else "FALHOU"
        print(f"  [{status}] {nome} - {tempo:.3f}s")

    total_sucesso = sum(1 for _, s, _ in resultados if s)

    print("\n" + "="*80)
    print(f"Termino da execucao: {timestamp_fim}")
    print(f"Tempo total: {tempo_total:.3f}s")
    print("="*80)

    if total_sucesso == len(experimentos):
        print("TODOS OS EXPERIMENTOS CONCLUIDOS COM SUCESSO!")
        sys.exit(0)
    else:
        print(f"ALGUNS EXPERIMENTOS FALHARAM: {total_sucesso}/{len(experimentos)} concluidos")
        sys.exit(1)
