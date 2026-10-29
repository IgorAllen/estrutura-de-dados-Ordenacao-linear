# Ordenação adaptativa

`ordenar(v)` olha a lista, escolhe sozinho entre **inserção, intercalação, rápida (pivô aleatório),
híbrida, contagem e base**, e executa. O relatório completo (tabelas, regras, custo, caso de erro)
está em [`RELATORIO.md`](RELATORIO.md).

Tudo em Python 3 puro (só a biblioteca padrão; `matplotlib` apenas para os gráficos).

## Estrutura

```
ordenacao/
  metodos.py       os seis métodos (cada um devolve uma NOVA lista)
  escolhedor.py    escolher(v) e ordenar(v)
tests/
  test_ordenacao.py   vazia, um elemento, todos iguais, ordenada, invertida, negativos, fuzz…
benchmarks/
  cenarios.py         geradores dos 4 cenários
  medir.py            tabela principal: ordenar × 6 métodos × 4 cenários  (+ gráfico)
  calibrar.py         de onde vêm os limiares (A–D)
  calibrar_extra.py   limiares finos (E–H)
  custo_escolher.py   quanto custa o escolher
  cenario_erro.py     procura de cenários em que o escolher erra
  tudo.sh             refaz todas as medições
resultados/            saídas já geradas (md, csv, png, logs)
```

## Uso

```python
from ordenacao import ordenar, escolher

ordenar([5, -3, 9, 0])        # [-3, 0, 5, 9]
escolher(lista).__name__      # 'base', 'contagem', 'insercao' ou 'hibrida'
```

`ordenar` não altera a lista recebida. Para tipos não inteiros (floats, strings, tuplas) ele usa
a híbrida; elementos incomparáveis levantam `TypeError`, como em `sorted`.

## Testes

```
python -m unittest discover -s tests -v
```

## Como refazer as medições

Da raiz do repositório (precisa de `pip install matplotlib` só para o gráfico):

```
python benchmarks/medir.py            # tabela principal  → resultados/principal.{md,csv}, grafico_cenarios.png
python benchmarks/custo_escolher.py   # custo do escolher → resultados/custo.md
python benchmarks/cenario_erro.py     # caso de erro      → resultados/erro.md
python benchmarks/calibrar.py         # limiares          → resultados/calibracao.md
python benchmarks/calibrar_extra.py   #                   → resultados/calibracao_extra.md
sh benchmarks/tudo.sh                 # tudo, em sequência (≈ 10–15 min)
```

Notas para medir direito:

- Rode **uma medição por vez** e com a máquina ociosa; os scripts usam a mediana de várias execuções,
  desligam o coletor de lixo durante a cronometragem e usam as mesmas listas e a mesma semente de pivôs
  para todos os métodos.
- A inserção em 20 mil elementos aleatórios leva ~5 s por execução, então ela é medida uma única vez
  nesses cenários (o script avisa o número de execuções).
- Os tempos absolutos dependem da máquina; o que deve se reproduzir é **quem vence cada cenário** e a
  **ordem de grandeza** das razões. A máquina usada está registrada no topo de cada arquivo em `resultados/`.

## Autores

Igor Costa | Moesio
