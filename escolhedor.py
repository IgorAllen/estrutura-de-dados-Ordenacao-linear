"""`escolher(v)` olha a lista (de forma barata) e devolve o método mais adequado;
`ordenar(v)` chama `escolher` e executa.

Regras (limiares medidos em benchmarks/calibrar.py e calibrar_extra.py;
os números estão em resultados/calibracao.md e resultados/calibracao_extra.md):

  1. n ≤ N_PEQUENO                       → inserção   (sem olhar nada: inspecionar custaria mais que ordenar)
  2. quase ordenada (amostra de pares)   → inserção   (O(n + inversões))
  3. inteiros e faixa k ≤ 2·n            → contagem   (k também limitado por LIMITE_CONTADORES: não estoura a memória)
  4. inteiros, n ≥ N_BASE, chaves ≤ 64 bits → base
  5. caso contrário                      → híbrida    (comparação; serve para qualquer tipo comparável)

A inspeção é reaproveitada: o (min, max) calculado aqui é entregue à contagem/base por `ordenar`.

Custo da inspeção: `min` e `max` (2 passadas em C) + uma amostra de ~1000 pares adjacentes
por fatiamento com passo (também em C). Nunca há laço em Python sobre a lista inteira.
"""
import random
from itertools import compress
from operator import gt

from .metodos import insercao, hibrida, contagem, base, LIMITE_CONTADORES

N_PEQUENO = 28          # calibração A: a inserção vence a híbrida até ~24–32 elementos
FATOR_CONTAGEM = 2      # calibração G: contagem vence a base até k/n ≈ 1,5–3,5
N_BASE = 300            # calibração E: base só paga seus 256 cestos/passada a partir de ~300–380
PASSADAS_MAX = 8        # calibrações C e F: base vence até 12 passadas (n=20 mil); 8 = chaves de 64 bits, folga p/ n pequeno
AMOSTRA = 1000          # nº aproximado de pares adjacentes inspecionados
DESC_MAX = 0.25         # calibração D: com trocas locais a inserção ainda vence com ~30% de descidas
PROFUNDIDADE = 16       # deslocamento a partir do qual um elemento fora do lugar é considerado "longe"


def _quase_ordenada(v, n):
    """Amostra pares adjacentes (v[i] > v[i+1] é uma 'descida'). Aceita se há poucas descidas
    e nenhuma das amostradas envolve um elemento longe de casa."""
    passo = max(1, (n - 1) // AMOSTRA)
    desloc = random.randrange(passo)
    a = v[desloc::passo]
    b = v[desloc + 1::passo]
    total = len(b)
    descidas = list(compress(range(desloc, n, passo), map(gt, a, b)))
    if len(descidas) > DESC_MAX * total:
        return False
    for i in descidas[:32]:
        j = i + 1 + PROFUNDIDADE            # v[i] precisaria andar mais que PROFUNDIDADE p/ a direita?
        if j < n and v[i] > v[j]:
            return False
        j = i - PROFUNDIDADE                # v[i+1] precisaria andar mais que PROFUNDIDADE p/ a esquerda?
        if j >= 0 and v[i + 1] < v[j]:
            return False
    return True


def _decidir(v):
    """Devolve (método, faixa). `faixa` = (min, max) quando já foi calculada para contagem/base."""
    n = len(v)
    if n <= N_PEQUENO:
        return insercao, None
    try:
        if _quase_ordenada(v, n):
            return insercao, None
        lo, hi = min(v), max(v)
    except TypeError:
        return hibrida, None                # elementos incomparáveis: o erro sai no método escolhido
    if type(lo) is int and type(hi) is int:
        k = hi - lo + 1
        if k <= FATOR_CONTAGEM * n and k <= LIMITE_CONTADORES:
            return contagem, (lo, hi)
        if n >= N_BASE and (hi - lo).bit_length() <= 8 * PASSADAS_MAX:
            return base, (lo, hi)
    return hibrida, None


def escolher(v):
    """Devolve a função de ordenação mais adequada para a lista `v`."""
    return _decidir(v)[0]


def ordenar(v):
    """Ordena `v` (devolve nova lista) com o método escolhido por `escolher`."""
    if len(v) <= N_PEQUENO:                 # caminho mais curto possível para listas minúsculas
        return insercao(v)
    metodo, faixa = _decidir(v)
    try:
        return metodo(v, faixa) if faixa else metodo(v)
    except (TypeError, MemoryError):
        # `escolher` só olhou min/max: um elemento não inteiro escondido no meio faz
        # contagem/base falharem. Cai para a comparação (que levanta o erro certo, se houver).
        if faixa:
            return hibrida(v)
        raise
