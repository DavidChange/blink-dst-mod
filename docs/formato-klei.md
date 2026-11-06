# Notas sobre o formato de animação do Don't Starve Together

O que aprendemos (às vezes do jeito difícil) ao compilar assets sem o *Mod Tools*. Implementação em [`art/klei_anim.py`](../art/klei_anim.py) (escrita) e [`art/klei_read.py`](../art/klei_read.py) (leitura).

## Build (`build.bin`, BILD versão 6)

Estrutura, em sequência:
1. `BILD`, versão, número de símbolos, total de quadros;
2. nome do build;
3. nomes dos atlas;
4. os símbolos, cada um com o hash do nome e a lista de quadros. Cada quadro tem: número, duração, caixa (x, y, largura, altura), índice e quantidade de vértices;
5. a lista de vértices, com 6 floats cada: x, y, z, u, v, w (y cresce para baixo; v = 1 no topo da textura);
6. a tabela de nomes (hash → texto).

- **Hash:** *sdbm* sobre o texto em minúsculas: `h = (c + (h << 6) + (h << 16) - h) & 0xffffffff`.
- ⚠️ **Os símbolos precisam estar em ordem crescente de hash.** Fora de ordem, o jogo não encontra o símbolo e a peça simplesmente não aparece, sem erro. Isso deixou a Dagger invisível na água e o corpo inteiro invisível numa versão.
- **Quadros por intervalo:** um quadro com número `n` e duração `d` cobre os pedidos de `n` até `n + d - 1`. As animações do jogador pedem quadros específicos (por exemplo, `swap_object` 0, 1, 2, 5, 6 e outros), e o build precisa cobri-los, senão a mão fica vazia.
- **Item boiando:** a peça de "boiar" precisa ficar num **build separado** do item, como fazem as armas oficiais (por exemplo, `swap_ham_bat`).

## Textura (`atlas-0.tex`, KTEX)

- Cabeçalho: `KTEX` + um inteiro com os bits `(formato << 4) | (1 << 9) | (mips << 13) | (3 << 18) | (4095 << 20)`, seguido dos cabeçalhos dos mipmaps (largura, altura, pitch, tamanho).
- **Atlas de animação:** DXT5 (formato 2), com a cadeia completa de mipmaps, guardado **de baixo para cima**.
- **Texturas de interface** (ícones, retratos, nomes): RGBA sem compressão (formato 4), 1 mip.
- ⚠️ **Alfa pré-multiplicado** em todas. Sem isso aparece um contorno branco em volta dos ícones.

## Animação (`anim.bin`, versão 4)

Cada elemento de um quadro traz: hash do símbolo, quadro do build, hash da camada e a matriz `a, b, c, d, tx, ty` mais `z`. O renderizador de prévia ([`art/corpo/compor.py`](../art/corpo/compor.py)) aplica essas transformações para montar o personagem exatamente como o jogo faz.

## Outras descobertas

- A **skin padrão** (`<personagem>_none`) define o fantasma pelo `ghost_skin`. Ela tem prioridade sobre `inst.ghostbuild`.
- O **retrato oval** da tela de seleção vem de `bigportraits/<personagem>.xml`, com o elemento `<personagem>_none_oval.tex` e as coordenadas de textura dos retratos oficiais.
- O **nome dourado** vem de `images/names_gold_<personagem>.xml`.
- O `modinfo.lua` só recebe o código de idioma oficial do jogo (`locale`). Um jogo traduzido por mod aparece como inglês nessa tela.
