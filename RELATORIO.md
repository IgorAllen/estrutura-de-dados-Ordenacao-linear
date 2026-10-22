# RELATÓRIO — Ordenação adaptativa

`ordenar(v)` chama `escolher(v)`, que inspeciona a lista de forma barata e devolve um dos seis métodos
do semestre (inserção, intercalação, rápida com pivô aleatório, híbrida, contagem, base).
Código em `ordenacao/`, testes em `tests/`, medições em `benchmarks/` (como refazer: `README.md`).

Todos os métodos estão em Python puro e devolvem uma lista nova; os tempos são **medianas** de várias
execuções, com as mesmas listas e a mesma semente de pivôs para todos. Máquina: Python 3.12.3, Linux x86_64, 1 CPU.
O ruído de medição é de alguns por cento (ver as ressalvas no fim): diferenças menores que ~10% não significam nada.

## 1. Tabela: quatro cenários × seis métodos

Cenários: (1) 20.000 inteiros aleatórios em [0, 10⁹]; (2) 20.000 inteiros em [0, 100]; (3) 20.000 inteiros
quase ordenados (lista ordenada + 200 trocas entre posições a no máximo 10 de distância); (4) lista de 10 elementos.
As colunas `ordenar` e `sorted` ficam fora da disputa pelo “melhor método fixo”: a primeira é o que está sendo
avaliado, a segunda (Timsort, escrito em C) é só régua.

_Python 3.12.3 · Linux x86_64 · 1 CPU_

#### Cenários 1–3: tempo mediano (ms)

| Cenário | inserção | intercalação | rápida | híbrida | contagem | base | ordenar | sorted (ref.) | `escolher` pegou |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Aleatório, chaves grandes (n=20.000, 0..10^9) | 5841.95 | 29.62 | 30.75 | 22.00 | estoura | **6.70** | 6.49 | 2.96 | base |
| Faixa estreita (n=20.000, 0..100) | 5152.63 | 27.50 | 7.57 | 7.23 | **0.94** | 1.53 | 1.13 | 2.18 | contagem |
| Quase ordenado (n=20.000, 1% de trocas locais) | **1.45** | 21.58 | 26.53 | 16.15 | estoura | 6.66 | 1.49 | 0.20 | insercao |

#### Cenário 4: lista minúscula, tempo por lista (µs)

| Cenário | inserção | intercalação | rápida | híbrida | contagem | base | ordenar | sorted (ref.) | `escolher` pegou |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Lista minúscula (n=10) | **1.73** | 6.63 | 7.15 | 1.80 | 25.93 | 67.80 | 1.77 | 0.30 | insercao |

_Negrito = melhor dos seis métodos fixos. “estoura” = a contagem recusou a faixa (precisaria de 10^9 contadores). `sorted` (Timsort em C) é só referência, fora da disputa._

#### Razão ao melhor método fixo de cada cenário (1,00 = empatou com o melhor)

| Método | Cen. 1 | Cen. 2 | Cen. 3 | Cen. 4 | Pior | Média geométrica |
|---|---:|---:|---:|---:|---:|---:|
| inserção | 872.33× | 5496.22× | 1.00× | 1.00× | 5496.22× | 46.79× |
| intercalação | 4.42× | 29.33× | 14.87× | 3.84× | 29.33× | 9.28× |
| rápida | 4.59× | 8.08× | 18.28× | 4.14× | 18.28× | 7.28× |
| híbrida | 3.29× | 7.72× | 11.13× | 1.04× | 11.13× | 4.14× |
| contagem | falha | 1.00× | falha | 15.02× | falha | — |
| base | 1.00× | 1.64× | 4.59× | 39.27× | 39.27× | 4.14× |
| ordenar | 0.97× | 1.21× | 1.03× | 1.02× | 1.21× | 1.05× |
| sorted (ref.) | 0.44× | 2.32× | 0.14× | 0.17× | 2.32× | 0.39× |

![Tempo por cenário](resultados/grafico_cenarios.png)

## 2. Quem venceu cada cenário, e por quê

| Cenário | Vencedor | Por quê |
|---|---|---|
| 1. Aleatório, chaves grandes | **base** (6,70 ms; híbrida 22,0 ms; intercalação 29,6 ms) | Chaves de até 30 bits são só 4 passadas lineares. A contagem **estoura**: precisaria de 10⁹ contadores (~8 GB) e recusa a faixa. A inserção leva 5,8 **segundos** (O(n²)). |
| 2. Faixa estreita (0..100) | **contagem** (0,94 ms; base 1,53 ms; híbrida 7,23 ms) | Faixa 200× menor que n: O(n + k) ≈ O(n) com 101 contadores. Híbrida e rápida são ~4× mais rápidas que a intercalação aqui porque a partição em três (menores/iguais/maiores) absorve os duplicados. |
| 3. Quase ordenado | **inserção** (1,45 ms; base 6,66 ms; híbrida 16,15 ms) | Custa O(n + inversões), e com trocas locais cada elemento só se desloca poucas posições. Os métodos O(n log n) e a base ignoram a ordem que já existe. |
| 4. Lista minúscula (n=10) | **inserção** (1,73 µs; híbrida 1,80 µs) | Sem recursão, sem pivô, sem cestos. A base paga 256 cestos por passada (67,8 µs) e a contagem aloca contadores (25,9 µs): 15× a 39× mais lentas. A híbrida empata porque, abaixo do corte, ela *é* a inserção. |

Nenhum método fixo vence em todos os cenários: a **linha do `ordenar`** na tabela de razões acima mostra o que importa.
Pior caso do `ordenar` = **1,21×** o melhor método de cada cenário (média geométrica **1,05×**), contra
**11,1×** da híbrida (a melhor escolha fixa única, mas que perde de 3,3× a 11× em todos os cenários grandes), 39× da base,
18× da rápida, 29× da intercalação, 5.496× da inserção e **falha** da contagem (estoura no cenário 1).

> **Nota de honestidade sobre “ganhar de qualquer escolha fixa”.** Em cada cenário isolado, o `ordenar` não pode ser
> *mais rápido* que o melhor método fixo, porque ele executa esse mesmo método (mais a inspeção). As razões 0,97× e 1,02× da
> tabela são ruído (ou a faixa já calculada sendo reaproveitada), não ganho real. O que as medições mostram é que, **somando os
> cenários**, nenhuma escolha fixa chega perto: toda escolha fixa perde ≥ 11× em algum cenário (a contagem nem roda), e
> o `ordenar` perde no máximo 1,21×. Isso é evidência empírica em quatro cenários, não uma prova formal.

Uma observação à parte: no Python puro, `sorted` (em C) é 2× mais rápido que o melhor método no cenário 1 e ~7× no cenário 3, mas **perde
para a contagem** no cenário 2 (2,18 ms contra 0,94 ms). A comparação de linguagens não era o objetivo; ela só lembra que
as razões entre métodos valem para este código e este interpretador.

## 3. As regras do `escolher` e de onde vieram

O `escolher` aplica estas regras, na ordem (constantes em `ordenacao/escolhedor.py`):

| # | Regra | Limiar | De onde veio |
|---|---|---|---|
| 1 | `n ≤ 28` → **inserção**, sem inspecionar | `N_PEQUENO = 28` | Calibração A (`resultados/calibracao.md`): inserção vence a híbrida até n≈24 (6,5 µs contra 7,4 µs) e perde a partir de n≈32 (11,0 contra 9,7 µs); inspecionar custa 3 µs (+30% em n=29), então abaixo disso não vale olhar. |
| 2 | **quase ordenada** → **inserção** | ≤ 25% de descidas na amostra e nenhuma “longe de casa” (deslocamento > 16) | Aula de inserção: O(n + inversões). Calibração D: com trocas locais (w=10) a inserção ainda vence com 30% de descidas (3,25 ms contra 5,88 ms da base); com trocas a distância 1000 ela já empata com 1% de descidas e perde com 2% (11,5 ms contra 5,9 ms); com trocas a distância ~n perde mesmo com 0,2% (11,3 ms contra 6,4 ms). Por isso as descidas sozinhas não bastam: o teste de profundidade separa os dois mundos. |
| 3 | inteiros com **k = máx − mín + 1 ≤ 2n** (e k ≤ 2·10⁷) → **contagem** | `FATOR_CONTAGEM = 2`, `LIMITE_CONTADORES = 2·10⁷` | Aula 13: O(n + k). Calibração G: contagem vence a base até k/n ≈ 1,5 (n=20 mil), ≈ 2,5 (n=2 mil), ≈ 3,5 (n=200 mil). O teto de 2·10⁷ (~160 MB de ponteiros) é a **previsão de memória** que o enunciado pede: a decisão é tomada com `min`/`max` *antes* de alocar, e a própria `contagem` recusa (`MemoryError`) por segurança. |
| 4 | inteiros com `n ≥ 300` e chaves de até **64 bits** → **base** | `N_BASE = 300`, `PASSADAS_MAX = 8` | Aula 13: O(d·n). Calibração E: a base paga 256 cestos por passada e só passa a híbrida em n≈300–380 (262 µs contra 251 µs em n=256; 308 contra 314 µs em n=384). Calibrações C e F: ela vence a híbrida até 12 passadas (96 bits) com n=20 mil e perde em 16 (128 bits); em n=2 mil a vantagem com 8 passadas já é mínima (1,79 ms contra 2,00 ms), então 8 é o limite conservador. |
| 5 | resto → **híbrida** | corte = 20 | Atividade anterior (a híbrida com corte 20 foi a melhor medida, faixa boa 16–50). Serve para floats, strings, tuplas e inteiros gigantes. |

Detalhes que a tabela não mostra:

- **A intercalação e a rápida pura nunca são escolhidas.** Nas calibrações A e C a híbrida foi igual ou melhor que as duas
  (e na B, melhor que a intercalação), em todos os tamanhos e distribuições testados; elas ficam no repositório como linhas de base.
- **Tipos:** `contagem`/`base` só valem para `int` exato. O `escolher` confere o tipo do mínimo e do máximo; se um float ficar
  escondido no meio, a contagem/base falha com `TypeError` e `ordenar` cai na híbrida (há teste para isso). Listas de strings, tuplas, floats
  vão direto para a comparação.
- **Negativos:** contagem e base deslocam tudo por `mín`, então valores negativos funcionam (testados).

## 4. Quanto custa rodar o `escolher`? Ele compensa?

O `escolher` faz: `min` e `max` (2 passadas em C) e uma amostra de ~1000 pares adjacentes por fatiamento com passo (também em C).
**Nunca** percorre a lista inteira em laço Python. Além disso, o `ordenar` entrega o (mín, máx) já calculado à contagem/base para
elas não refazerem a conta.

Para n = 20.000 (inteiros em [0, 10⁹]; base = 6,15 ms, híbrida = 20,1 ms):

| Forma de inspecionar | Tempo | % da base |
|---|---:|---:|
| `min` + `max`, 2 passadas em C (usado) | 348 µs | 5,7% |
| amostra de ~1000 pares adjacentes (usado) | 48 µs | 0,8% |
| contar **todas** as descidas em C | 372 µs | 6,1% |
| `min`/`max` num laço Python (1 passada) | 341 µs | 5,5% |
| descidas num laço Python (1 passada) | 530 µs | 8,6% |
| `min`/`max` + descidas, **2 laços Python** | 959 µs | **15,6%** |

O aviso do enunciado se confirma: duas passadas em Python puro custariam ~16% do tempo da base (e, no cenário 2, custariam tanto
quanto a própria contagem (0,94 ms)). A amostragem custa menos de 1%.

**Custo líquido** (`ordenar` ÷ o mesmo método rodando sozinho − 1; a diferença é o que o `escolher` acrescenta de fato):

| Situação | Custo líquido |
|---|---:|
| n = 20.000, chaves grandes (base) | +1,0% (+2,3% na outra medição) |
| n = 20.000, faixa estreita (contagem) | +7,8% |
| n = 20.000, quase ordenado (inserção) | −8,3% (ruído: o `escolher` não pode economizar tempo) |
| n = 200.000 (base) | −3,4% (ruído) |
| n = 300 a 1.000 (base) | +4% a +14% (de 10 a 60 µs) |
| n = 29 a 100 (híbrida) | +17% a +31% (3 a 7 µs) |
| n = 10 (caminho curto: `len(v) <= 28` → inserção) | +1,4% |

**Compensa?** Sim, mas por razões diferentes em cada faixa:

- **Listas grandes:** custa de ~1% a ~8% e evita perdas de 3× a 5.000× (ou uma falha de memória).
- **Listas pequenas (29–1.000):** o custo relativo sobe a 15–30%, porém são poucos microssegundos; é o preço de não errar quando essa
  chamada se repete milhões de vezes sobre listas variadas. Para quem *sabe* que só ordena listas de ~50 inteiros aleatórios, a híbrida fixa é um pouco melhor.
- **Listas minúsculas:** não custa nada relevante, porque nem inspeciona.

## 5. Um cenário em que o `escolher` erra a decisão

**Ordenada, com 10% dos blocos de 30 elementos embaralhados por dentro** (`benchmarks/cenario_erro.py`, candidato E; n = 20.000).

- O `escolher` escolhe a **base em 15 das 15 listas**; o melhor método era a **inserção em 15 das 15**.
- A escolha ficou **3,06× mais lenta** na mediana e **5,44×** no pior caso

**Por quê.** A regra 2 rejeita a inserção se *qualquer* descida amostrada envolver um elemento com deslocamento maior que 16
posições. Num bloco embaralhado de 30, isso acontece. Mas o custo da inserção depende de *quantos* elementos estão longe de casa,
e aqui são poucos (10% dos blocos: estimativa de ~0,7 inversões por elemento). O teste é binário e conservador demais: confunde “existe desordem
a longa distância” com “há desordem demais”. Um conserto seria estimar o número de inversões pela fração das descidas amostradas
que são “longe” (aceitando a inserção se a estimativa ficar abaixo de ~2n), ao custo de mais código na inspeção. Não foi feito para
manter o `escolher` simples; fica registrado como limitação.

Outros candidatos testados (mesma tabela, `resultados/erro.md`):

| Candidato | Resultado |
|---|---|
| A. ordenada + 5 elementos jogados longe | escolheu inserção 10×, base 5×; pior razão 1,63× |
| B. ordenada + 20 elementos jogados longe | escolheu base 13×, **inserção 2× (erro: até 2,85× mais lenta)** — a amostra de 1000 pares perdeu os poucos elementos longe |
| C, D. 40 e 200 elementos jogados longe | acertou a base nas 30 listas (razão 1,00×) |
| F. faixa estreita com 1 outlier de 10⁹ | acertou: a contagem seria impossível e a base é a melhor (razão 1,00×) |

O caso B mostra o outro tipo de erro: como a amostra usa um deslocamento aleatório, **listas na fronteira podem receber
decisões diferentes em execuções diferentes**.

## 6. Testes

`python -m unittest discover -s tests -v` (15 testes, todos passando): para os seis métodos e para `ordenar`, lista **vazia**, **um elemento**,
**todos iguais**, **já ordenada**, **invertida**, **valores negativos** (e mistos), duplicados, chaves enormes, comparação com `sorted`
em 150 listas aleatórias, hibrida com vários cortes, entrada não alterada, floats/strings/tuplas, float escondido no meio de inteiros,
`TypeError` para tipos incomparáveis, e checagens das decisões do `escolher` (inclusive “faixa enorme nunca vai para a contagem e não estoura a memória”).

## 7. Ressalvas

- **Python puro.** Os limiares (28, 300, 64 bits, k ≤ 2n) vêm das constantes deste interpretador; em C ou Java a inserção vale até tamanhos
  diferentes e a base não é tão boa. O que deve se manter é a estrutura das regras, não os números.
- **Ruído.** Os custos líquidos negativos (−8%, −3%) são impossíveis na prática e indicam ruído de uns ±8%. A inserção em 20.000 elementos aleatórios
  é medida uma única vez (leva ~5 s), nos cenários 1 e 2.
- **Quatro cenários e uma máquina.** As conclusões qualitativas são robustas (diferenças de ordens de grandeza), as quantitativas finas, não.
- **Calibração com poucas amostras de desordem.** A regra 2 foi calibrada com trocas aleatórias, não com todos os padrões de “quase ordenado”
  (a seção 5 mostra um que escapa).
