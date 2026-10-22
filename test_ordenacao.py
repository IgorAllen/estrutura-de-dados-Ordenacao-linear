"""Testes: python -m unittest discover -s tests -v   (a partir da raiz do repositório)"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ordenacao import (insercao, intercalacao, rapida, hibrida, contagem, base,
                       escolher, ordenar, LIMITE_CONTADORES)

METODOS = {"insercao": insercao, "intercalacao": intercalacao, "rapida": rapida,
           "hibrida": hibrida, "contagem": contagem, "base": base, "ordenar": ordenar}

_rng = random.Random(1)
CASOS = {
    "vazia": [],
    "um elemento": [42],
    "dois elementos": [2, 1],
    "todos iguais": [7] * 50,
    "todos iguais (grande)": [3] * 5000,
    "ja ordenada": list(range(100)),
    "ja ordenada (grande)": list(range(5000)),
    "invertida": list(range(100, 0, -1)),
    "invertida (grande)": list(range(5000, 0, -1)),
    "negativos": [-5, -1, -100, -3, -3, -50],
    "negativos e positivos": [3, -2, 0, -7, 9, -7, 1, 0],
    "so negativos grande": [_rng.randint(-10**6, -1) for _ in range(2000)],
    "muitos duplicados": [_rng.randint(0, 5) for _ in range(1000)],
    "aleatorio medio": [_rng.randint(-10**9, 10**9) for _ in range(1000)],
    "aleatorio grande, chaves enormes": [_rng.randint(0, 10**12) for _ in range(3000)],
}
# a contagem recusa faixas que estourariam a memória, por projeto
SEM_CONTAGEM = {"aleatorio medio", "aleatorio grande, chaves enormes"}


def lista(semente, n, lo, hi):
    r = random.Random(semente)
    return [r.randint(lo, hi) for _ in range(n)]


class TestMetodos(unittest.TestCase):
    def test_casos_contra_sorted(self):
        for nome_m, f in METODOS.items():
            for nome_c, caso in CASOS.items():
                if nome_m == "contagem" and nome_c in SEM_CONTAGEM:
                    continue
                with self.subTest(metodo=nome_m, caso=nome_c):
                    entrada = list(caso)
                    self.assertEqual(f(entrada), sorted(caso))
                    self.assertEqual(entrada, caso, "a entrada foi alterada")

    def test_fuzz(self):
        rng = random.Random(123)
        for _ in range(150):
            n = rng.choice([0, 1, 2, 3, 10, 27, 28, 29, 30, 100, 299, 300, 301, 700])
            lo = rng.choice([-10**6, -50, 0, 10**9])
            larg = rng.choice([0, 1, 10, 1000, 10**6])
            v = [lo + rng.randint(0, larg) for _ in range(n)]
            for nome_m, f in METODOS.items():
                with self.subTest(metodo=nome_m, n=n, lo=lo, larg=larg):
                    self.assertEqual(f(v), sorted(v))

    def test_hibrida_com_varios_cortes(self):
        v = lista(5, 500, -100, 100)
        for corte in [1, 5, 20, 100, 1000]:
            with self.subTest(corte=corte):
                self.assertEqual(hibrida(v, corte), sorted(v))

    def test_contagem_recusa_faixa_enorme(self):
        with self.assertRaises(MemoryError):
            contagem([0, LIMITE_CONTADORES + 5])


class TestEscolher(unittest.TestCase):
    def test_minuscula_vai_para_insercao(self):
        self.assertIs(escolher([3, 1, 2]), insercao)
        self.assertIs(escolher([]), insercao)

    def test_faixa_estreita_vai_para_contagem(self):
        v = lista(2, 5000, 0, 100)
        self.assertIs(escolher(v), contagem)

    def test_faixa_enorme_nunca_vai_para_contagem(self):
        v = lista(3, 5000, 0, 10**15)
        self.assertIsNot(escolher(v), contagem)
        self.assertEqual(ordenar(v), sorted(v))      # e não estoura a memória

    def test_chaves_grandes_vao_para_base(self):
        v = lista(4, 5000, 0, 10**9)
        self.assertIs(escolher(v), base)

    def test_ordenada_vai_para_insercao(self):
        v = [i * 1000 for i in range(5000)]          # faixa grande → não é contagem
        self.assertIs(escolher(v), insercao)

    def test_invertida_nao_vai_para_insercao(self):
        v = [i * 1000 for i in range(5000, 0, -1)]
        self.assertIsNot(escolher(v), insercao)

    def test_floats_e_strings_vao_para_comparacao(self):
        r6 = random.Random(6)
        self.assertIs(escolher([r6.random() for _ in range(2000)]), hibrida)
        r7 = random.Random(7)
        self.assertIs(escolher([str(r7.randint(0, 10**6)) for _ in range(2000)]), hibrida)


class TestOrdenar(unittest.TestCase):
    def test_tipos_nao_inteiros(self):
        r = random.Random(8)
        floats = [r.uniform(-5, 5) for _ in range(1000)]
        strings = [str(r.randint(0, 10**6)) for _ in range(1000)]
        tuplas = [(r.randint(0, 5), r.randint(0, 5)) for _ in range(1000)]
        for v in (floats, strings, tuplas):
            self.assertEqual(ordenar(v), sorted(v))

    def test_float_escondido_no_meio_de_inteiros(self):
        v = list(range(1000, 0, -1)) + [2.5] + list(range(500))
        self.assertEqual(ordenar(v), sorted(v))      # contagem/base falham → cai na comparação

    def test_nao_altera_a_entrada(self):
        v = [5, 3, 9, 1] * 100
        copia = list(v)
        ordenar(v)
        self.assertEqual(v, copia)

    def test_tipos_incomparaveis_levantam_typeerror_como_o_sorted(self):
        with self.assertRaises(TypeError):
            ordenar([1, "a"] * 50)


if __name__ == "__main__":
    unittest.main()
