"""Quicksort com pivô aleatório + inserção para pedaços pequenos (híbrida)."""
import random
import statistics
import time

CORTES = [1, 5, 10, 16, 20, 32, 50, 100, 200]
N = 20_000
REPETICOES = 30


def insercao(v):
    """Ordenação por inserção (devolve nova lista)."""
    v = list(v)
    for i in range(1, len(v)):
        chave = v[i]
        j = i - 1
        while j >= 0 and v[j] > chave:
            v[j + 1] = v[j]
            j -= 1
        v[j + 1] = chave
    return v


def rapida(v):
    """Quicksort puro: pivô aleatório, separa em menores / iguais / maiores."""
    if len(v) <= 1:
        return v
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return rapida(menores) + iguais + rapida(maiores)


def hibrida(v, corte):
    """Quicksort que chama a inserção quando o pedaço tem menos que `corte` elementos."""
    if len(v) <= 1:
        return v
    if len(v) < corte:
        return insercao(v)
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return hibrida(menores, corte) + iguais + hibrida(maiores, corte)


def medir(funcao, entradas, semente):
    tempos = []
    for k, dados in enumerate(entradas):
        random.seed(semente + k)          # mesma sequência de pivôs para todos os métodos
        t0 = time.perf_counter()
        saida = funcao(dados)
        tempos.append(time.perf_counter() - t0)
        assert saida == sorted(dados)
    return statistics.median(tempos), statistics.stdev(tempos)


if __name__ == "__main__":
    import csv
    rng = random.Random(42)
    entradas = [[rng.randint(0, 10 * N) for _ in range(N)] for _ in range(REPETICOES)]

    # aquecimento
    rapida(entradas[0]); hibrida(entradas[0], 16)

    metodos = {"pura": rapida}
    for c in CORTES:
        metodos[c] = (lambda v, c=c: hibrida(v, c))
    tempos = {k: [] for k in metodos}
    for i, dados in enumerate(entradas):
        esperado = sorted(dados)
        for k, f in metodos.items():
            random.seed(1000 + i)            # mesma sequência de pivôs
            t0 = time.perf_counter()
            saida = f(dados)
            tempos[k].append(time.perf_counter() - t0)
            assert saida == esperado
    mediana_pura = statistics.median(tempos["pura"])
    dp_pura = statistics.stdev(tempos["pura"])
    print(f"rapida pura: {mediana_pura*1000:.2f} ms (dp {dp_pura*1000:.2f})")
    resultados = []
    for c in CORTES:
        m, dp = statistics.median(tempos[c]), statistics.stdev(tempos[c])
        resultados.append((c, m, dp))
        print(f"corte={c:>3}: {m*1000:.2f} ms (dp {dp*1000:.2f})  ganho={(1-m/mediana_pura)*100:+.1f}%")

    with open("resultados.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["corte", "mediana_s", "desvio_s", "pura_mediana_s"])
        for c, m, dp in resultados:
            w.writerow([c, m, dp, mediana_pura])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cs = [r[0] for r in resultados]
    ms = [r[1] * 1000 for r in resultados]
    plt.figure(figsize=(8, 5))
    plt.plot(cs, ms, "o-", label="híbrida")
    plt.axhline(mediana_pura * 1000, color="r", ls="--", label="rápida pura")
    plt.xscale("log")
    plt.xticks(cs, [str(c) for c in cs])
    plt.xlabel("corte (escala log)")
    plt.ylabel("tempo mediano (ms)")
    plt.title(f"Tempo × corte — {N} elementos aleatórios, mediana de {REPETICOES} execuções")
    plt.grid(alpha=.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("grafico_tempo_corte.png", dpi=150)
