"""Os seis métodos de ordenação do semestre.

Todos recebem uma lista e devolvem uma NOVA lista ordenada (a entrada não é
alterada). Todos estão escritos em Python puro, para a comparação ser justa.
"""
import random

CORTE_PADRAO = 20                 # melhor corte medido na atividade da híbrida (16–50)
LIMITE_CONTADORES = 20_000_000    # ~160 MB de ponteiros: acima disso a contagem recusa


def insercao(v):
    """Ordenação por inserção. O(n + inversões): ótima se já está quase ordenada."""
    v = list(v)
    for i in range(1, len(v)):
        chave = v[i]
        j = i - 1
        while j >= 0 and v[j] > chave:
            v[j + 1] = v[j]
            j -= 1
        v[j + 1] = chave
    return v


def _intercalar(a, b):
    i = j = 0
    na, nb = len(a), len(b)
    saida = []
    ap = saida.append
    while i < na and j < nb:
        if a[i] <= b[j]:
            ap(a[i])
            i += 1
        else:
            ap(b[j])
            j += 1
    saida += a[i:]
    saida += b[j:]
    return saida


def intercalacao(v):
    """Ordenação por intercalação (merge sort). O(n log n) sempre, estável."""
    n = len(v)
    if n <= 1:
        return list(v)
    meio = n // 2
    return _intercalar(intercalacao(v[:meio]), intercalacao(v[meio:]))


def rapida(v):
    """Quicksort com pivô aleatório, separando em menores, iguais e maiores."""
    if len(v) <= 1:
        return list(v)
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return rapida(menores) + iguais + rapida(maiores)


def hibrida(v, corte=CORTE_PADRAO):
    """Rápida que passa para a inserção quando o pedaço tem menos que `corte` elementos."""
    if len(v) <= 1:
        return list(v)
    if len(v) < corte:
        return insercao(v)
    pivo = random.choice(v)
    menores = [x for x in v if x < pivo]
    iguais = [x for x in v if x == pivo]
    maiores = [x for x in v if x > pivo]
    return hibrida(menores, corte) + iguais + hibrida(maiores, corte)


def contagem(v, faixa=None):
    """Ordenação por contagem. O(n + k), k = max − min + 1. Só para inteiros.

    `faixa=(min, max)` evita recalcular o que o `escolher` já calculou.
    Recusa (MemoryError) faixas que exigiriam mais de LIMITE_CONTADORES contadores.
    """
    if not v:
        return []
    lo, hi = faixa if faixa else (min(v), max(v))
    k = hi - lo + 1
    if k > LIMITE_CONTADORES:
        raise MemoryError(f"faixa de {k} valores exigiria {k} contadores")
    cont = [0] * k            # TypeError se a faixa não for inteira (ex.: floats)
    for x in v:
        cont[x - lo] += 1
    saida = []
    for valor, c in enumerate(cont, lo):
        if c:
            saida += [valor] * c
    return saida


def base(v, faixa=None):
    """Ordenação por base (radix LSD), um byte (base 256) por passada. O(d·n). Só para inteiros.

    `faixa=(min, max)` evita recalcular o que o `escolher` já calculou."""
    if not v:
        return []
    lo, hi = faixa if faixa else (min(v), max(v))
    amplitude = hi - lo
    saida = list(v)
    deslocamento = 0
    while (amplitude >> deslocamento) > 0:    # TypeError se houver floats
        cestos = [[] for _ in range(256)]
        adicionar = [c.append for c in cestos]
        for x in saida:
            adicionar[((x - lo) >> deslocamento) & 255](x)
        saida = [x for c in cestos for x in c]
        deslocamento += 8
    return saida


METODOS = {
    "insercao": insercao,
    "intercalacao": intercalacao,
    "rapida": rapida,
    "hibrida": hibrida,
    "contagem": contagem,
    "base": base,
}
