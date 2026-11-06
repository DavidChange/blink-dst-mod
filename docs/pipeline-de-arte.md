# Pipeline de arte

Como os assets do BLINK são gerados e compilados. Tudo é Python (Pillow, numpy, scipy; o fantasma usa também OpenCV). O *Don't Starve Mod Tools* **não** é usado: a compilação é feita por [`art/klei_anim.py`](../art/klei_anim.py) (ver [formato-klei.md](formato-klei.md)).

> **Arquivos do jogo.** Algumas etapas leem arquivos do próprio Don't Starve Together (builds e animações em `Don't Starve Together/data/anim/*.zip`, retratos em `data/bigportraits`). Eles **não estão neste repositório** (são da Klei). Copie-os da sua instalação para uma pasta local, por exemplo `jogo/`, e passe os caminhos nos comandos abaixo.

## Ferramentas comuns

| Script | Função |
|---|---|
| `art/klei_anim.py` | Compila peças PNG + pivô em um build do jogo (`build.bin` + `atlas-0.tex`, DXT5, alfa pré-multiplicado, símbolos em ordem de hash). |
| `art/klei_read.py` | O inverso: extrai um build do jogo para peças PNG + `.txt` (pivô e duração). `python3 art/klei_read.py jogo/wilson.zip pecas_wilson/` |
| `art/corpo/compor.py` | Monta um quadro de animação real do jogo com uma pasta de peças. Usado para as prévias e para comparar com o Wilson na mesma pose. |

Formato das peças: `simbolo-quadro.png` + `simbolo-quadro.txt` contendo `pivo_x pivo_y duracao`.

## 1. Corpo do personagem (`blink/anim/blink.zip`)

1. **Folhas de IA** (já no repositório): `art/corpo_v2/folhas/`
   - `f0_mestre.jpg`: folha mestre, referência;
   - `f1_cabecas.jpg`: frente, perfil e costas;
   - `f2_expr.jpg` e `f3_expr.jpg`: 12 expressões de frente cada;
   - `f4_perfis.jpg`: 6 expressões de perfil;
   - `f5_pecas.jpg`: tronco, cintura, braços, mãos, pernas e botas.
2. **Moldes do jogo:** extraia `wilson.zip` e `wolfgang.zip` com `klei_read.py`. Eles dão tamanho, pivô e quadros de cada peça.
3. **Peças base:** descompacte `art/corpo/pecas_base.zip`. São as peças da primeira rodada, ainda usadas para a caveira do choque e alguns quadros especiais.
4. **Montagem:**
   ```bash
   python3 art/corpo_v2/montar_v2.py art/corpo_v2/folhas pecas_base pecas_wilson pecas_wolfgang pecas_v2
   ```
   Gera as peças em `pecas_v2/` e uma imagem `conferencia_rostos.png` com as 33 expressões para conferência visual.
5. **Bochechas de comer:**
   ```bash
   python3 art/corpo_v2/bochechas/gerar_bochechas.py 1.0 0 12 pecas_wilson pecas_v2 jogo/player_actions_eat.zip previa_comer.png
   ```
6. **Compilação:**
   ```bash
   python3 art/corpo/compilar_corpo.py pecas_v2 blink/anim/blink.zip
   ```
   As peças da versão publicada estão em `art/corpo/pecas_v2.zip`.
7. **Conferência com chapéus:**
   ```bash
   python3 art/corpo_v2/ver_chapeu.py pecas_v2 pecas_wilson jogo/player_idles.zip previa.png jogo/hat_football.zip
   ```

## 2. Fantasma (`blink/anim/ghost_blink_build.zip`)

Copia o fantasma do jogo e troca só o `ghost_Hat` pela silhueta do cabelo do BLINK:
```bash
python3 art/corpo_v2/fantasma.py jogo/ghost_wilson_build.zip art/corpo_v2/folhas/f1_cabecas.jpg blink/anim/ghost_blink_build.zip previa_fantasma.png
```

## 3. Dagger e Runa Elétrica

- `art/gerar_arte.py`: arte da Dagger (mão, chão, ícone) a partir do recorte da referência, gerando a pasta `art/v063/`.
- `art/nova_runa.py`: Runa Elétrica (arte da 0.12) e Dagger 12% menor, gerando `art/v0120/`.
  ```bash
  python3 art/nova_runa.py art/referencias/runa_v012_frente.png art/referencias/runa_v012_folha.png art/v063 art/v0120
  ```
- `art/compilar_anim.py`: compila `blink_dagger.zip`, `blink_dagger_float.zip` (item boiando, build separado) e `blink_impeto.zip`.
  ```bash
  python3 art/compilar_anim.py art/v0120 blink/anim blink/anim/blink_dagger.zip
  ```
  O terceiro argumento fornece o `anim.bin` já existente da Dagger.

## 4. Tela de seleção

`art/selecao/retrato.py` encaixa uma ilustração na moldura oval (`frame.png` e `inner.npy`, recortados de retratos oficiais) e grava o nome dourado (`blink_name.png`, montado com letras originais dos nomes do jogo):
```bash
python3 art/selecao/retrato.py art/selecao/retrato_ia.jpg saida cena 0.06
```
Copie `saida/bigportraits/*` e `saida/images/names_*` para `blink/`.

## 5. Interface

`art/build_ui_textures.py` e `art/build_item_assets.py` geram texturas de interface (RGBA, alfa pré-multiplicado).

## Depois de qualquer mudança

```bash
python3 tests/run_tests.py
```
Os testes verificam a ordem de hash dos símbolos, a cobertura de quadros e as texturas pré-multiplicadas. Esses são exatamente os erros que já deixaram peças invisíveis no jogo.
