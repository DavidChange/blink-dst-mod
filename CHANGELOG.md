# Changelog — BLINK

Histórico versão a versão, do mais recente para o mais antigo. As notas antigas foram mantidas como foram escritas na época, incluindo instruções de instalação e testes daquela versão; valores de equilíbrio mudaram ao longo do caminho (os atuais estão no [README](README.md)).

## 1.0.0
- Versao de publicacao: nome do mod "BLINK", autor "Projeto BLINK". Sem mudancas de jogo desde a 0.13.1.

## 0.13.1
- Equilibrio fixo: o menu do mod agora so tem o idioma. Valores da 0.13.0 sao os unicos (Dagger 38, dash 50/8 s, choque 50 x 5 saltos, forca 1,25/1,5/2, Dagger 150 usos com luz, Runa 30 usos, fraqueza a agua ligada).

## 0.13.0 (equilibrio)
- Vida 125, fome 200, sanidade 250.
- Forca pela fome: acima de 75% = 2x (e gasta fome 25% mais rapido); 30-75% = 1,5x; abaixo de 30% = 1,25x. Vale para todas as armas. Opcao "Forca maxima" (1,6x / 2x / 2,4x) escala as tres faixas.
- Dagger: dano 38, receita 2 silex + 1 salitre + 1 ouro no Motor de Alquimia.
- Dash: 50 de dano, recarga 8 s; funciona com a Dagger OU com a Runa.
- Runa Eletrica: 30 usos; sozinha da o dash (recarga normal); com a Dagger o dash fica sem recarga. Receita: 1 gema roxa + 3 rochas lunares + 4 ouros + 2 combustiveis de pesadelo (Manipulador das Sombras).
- Fraqueza a agua (opcao, ligada por padrao): acima de 15% de umidade faiscas e dano leve (metade do WX-78, com o tranco do WX); a partir de 50% sem dash e sem choque.
- HUD mostra a forca atual e o aviso de molhado.

## 0.12.0
- Runa Eletrica com a arte nova (pedra-raio com gemas, corda e corrente): corpo, chao e icone (art/nova_runa.py, art/v0120).
- Dagger na mao ~12% menor.

## 0.11.0
- Sem "ALPHA". Nome, descricao e opcoes do mod em ingles e portugues (segue o idioma do jogo).
- Nova opcao "Idioma / Language": Automatico, English, Portugues (BR).
- Falas proprias do BLINK, sarcasticas, em ingles e portugues (scripts/speech_blink_en.lua / _pt.lua); o que nao tem fala propria cai nas falas genericas do jogo, ja traduzidas.
- Tela de selecao, itens, receitas, HUD e menu de tecla (F6) nos dois idiomas (scripts/blink/lang.lua).
- Icone proprio na lista de mods (modicon).

## 0.10.3 (alpha)
- Comer: bochechas cheias voltaram (simbolo cheeks), como no Wilson; na 0.9 elas tinham ficado vazias.

## 0.10.2 (alpha)
- Icones pequenos com o rosto novo: avatar (menu de fabricacao, lista de jogadores), avatar de fantasma, auto-inspecao, mapa, slot de save e retrato pequeno da selecao.

## 0.10.1 (alpha)
- Chances de sobrevivencia: "Alta".
- Retrato final da tela de selecao (art/selecao/retrato_ia.jpg) na moldura oval do jogo: python3 art/selecao/retrato.py art/selecao/retrato_ia.jpg <saida> cena 0.06

## 0.10.0 (alpha)
- Tela de selecao no padrao dos personagens oficiais: nome "BLINK" montado com as letras originais dos nomes do jogo (Webber, Wilson, Wickerbottom), retrato no oval com a moldura do jogo (provisorio, da folha mestre; trocar pela arte final com art/selecao/retrato.py <arte> <saida> cena).
- Vida 300, fome 200, sanidade 200 aparecem na selecao; "Entra na Constante Com" mostra a Dagger.
- Descricao implicita como a dos oficiais; sobrevivencia "Poucas".

## 0.9.5 (alpha)
- Cabelo do fantasma refeito no estilo do fantasma do Wilson: silhueta cheia do alto da cabeca com as pontas grandes do cabelo do BLINK, contorno grosso so no topo, base da mesma cor do corpo.

## 0.9.4 (alpha)
- Fantasma do BLINK de fato ativo: a skin padrao (blink_none) ainda apontava ghost_skin para o fantasma do Wilson, e o jogo usa a skin antes do inst.ghostbuild.

## 0.9.3 (alpha)
- Recorte limpo: sem pontos/halo brancos no contorno do cabelo e das pecas (bolsoes de fundo entre as pontas do cabelo removidos; borda externa vira nanquim com transparencia).
- Maos com contorno mais grosso, igual ao resto do desenho.
- Cabeca centralizada pelo meio do rosto (antes o centro era medido incluindo esses bolsoes brancos, o que deslocava a cabeca); mesmo tamanho da 0.9.2.

## 0.9.2 (alpha)
- Maos: cada uma das 20 poses agora usa o desenho de pose do proprio jogo, repintado como a mao palida do BLINK (antes uma mao generica girada, que ficava ao contrario em varias poses).
- Cabeca 1,7x maior, na proporcao dos personagens do jogo (antes ficava pequena perto do Wilson).
- Corte do cabelo para chapeus na mesma altura nas 3 vistas (antes sumia a cabeca de costas com chapeu e sobravam pontinhos).
- Conferido com capacete de futebol e cartola (art/corpo_v2/ver_chapeu.py).

## 0.9.1 (alpha)
- Botas viradas para o lado certo (estavam com o bico para tras).
- Pernas sem o risco solto embaixo.

## 0.9.0 (alpha)
- Visual novo do BLINK no estilo Don't Starve (pele palida, olhos pretos com olheira, corpo magro), feito das folhas em `art/corpo_v2/folhas`.
- Cabeca, 33 rostos, tronco, cintura, bracos, maos, pernas e botas vem da arte nova (antes bracos/pernas eram o molde recolorido).
- Rostos recortados pelo interior do rosto (corrige o olho esquerdo apagado da 0.8.0); quadro 14 (brilho branco nos olhos) removido.
- Fantasma proprio (`anim/ghost_blink_build.zip`): fantasma do jogo com o cabelo do BLINK.
- Atributos e habilidades sem mudanca. Nao testado dentro do jogo.

# Versão 0.8.0 — BLINK com a arte do usuário

A cabeça, o cabelo, as 33 expressões e as roupas agora vêm das folhas geradas pelo usuário (`art/corpo_ia/folhas`), montadas por `art/corpo_ia/montar_ia.py`:
- **Cabeça:** de frente é a expressão neutra, de perfil é o perfil neutro e de costas vem do desenho de corpo inteiro. O cabelo faz parte da cabeça, exatamente como a IA desenhou.
- **Expressões:** são recortes do rosto alinhados sobre a cabeça neutra, com alinhamento de 91 a 96%. Ficam distribuídas nas 33 posições do jogo: piscar, falar, raiva, susto, dor, sono, tontura e as demais. O brilho das bochechas é o original do jogo.
- **Capacete:** a mesma cabeça com o topo do cabelo aparado, que fica escondido pelo chapéu.
- **Roupas:** túnica com capuz e cintura com cinto, fivela e bolsa da folha 6, ajustadas aos quadros de frente, lado e costas. O remendo em X foi tirado das costas.
- **Braços, mãos, pernas e pés:** continuam do molde, como na 0.7.2.

O brilho do rosto da 0.7.2 foi removido: o recorte do rosto inclui pele e ficaria mais claro que a cabeça à noite. Conferido renderizando, a partir das peças, as poses parado (frente, lado e costas), correndo e atacando, e as 33 expressões. Não testado no DST.

# Versão 0.7.2 — visual do BLINK, 2ª rodada

- **Cabelo próprio:** curto e espetado, em leque de frente, varrido para trás de perfil e com franja no alto da cabeça. Deixou de ser o cabelo do Wilson.
- **Olhos:** esclera clara com contorno fino, íris ciano grande e saturada e centro claro. O rosto ignora 40% da escuridão (`SetSymbolLightOverride`), então os olhos continuam visíveis à noite.
- **Capuz:** um rolo de tecido em volta do pescoço e dos ombros, de frente e de lado, e caído nas costas.
- **Contraste:** túnica mais escura, pele um pouco mais quente, faixas dos punhos mais largas e escuras e botas com cano dobrado.

Conferido renderizando, a partir do arquivo compilado, as poses parado (frente, lado e costas), correndo e atacando. Não testado no DST.

# Versão 0.7.1 — corpo visível (correção do compilador)

Na 0.7.0, quase todo o corpo ficou invisível no jogo. A causa: os builds do jogo guardam as peças em ordem crescente do código (hash) de cada nome, e o jogo procura as peças contando com essa ordem. O compilador próprio gravava fora de ordem. Era a mesma causa da Dagger invisível na água nas versões 0.6.8 e 0.6.9. O compilador (`art/klei_anim.py`) agora ordena as peças, e um teste garante isso em todos os builds. Não testado no DST.

# Versão 0.7.0 — visual próprio do BLINK (1ª rodada)

O BLINK deixou de usar a aparência provisória do Wolfgang. O novo build `anim/blink.zip` combina:
- **Cabeça, cabelo e rosto** no tamanho do Wilson, como pede a ficha: pele, cavanhaque, cabelo preto curto e espetado e olhos ciano brilhantes com órbitas escuras.
- **Corpo forte** do Wolfgang: braços nus e musculosos com faixas escuras nos punhos, túnica cinza-escura com barra rasgada, remendo em X, capuz, cinto de couro com fivela e bolsa lateral, calça escura e botas.

Foi feito pelo método padrão de mods de personagem: as peças do molde do jogo foram redesenhadas e recoloridas por `art/corpo/gerar_corpo.py` e compiladas por `art/corpo/compilar_corpo.py`. As animações continuam as nativas, e força, dash e demais mecânicas não mudaram. A montagem foi conferida renderizando, a partir do arquivo compilado, as poses parado, correndo e atacando. Não testado no DST.

Ficam para a 2ª rodada: olho escuro em algumas vistas de perfil, refino do cabelo e do capuz, retratos e ícone do mapa com o visual novo, e o fantasma.

# Versão 0.6.16 — Runa Elétrica, versão B (moldura dourada)

Entre três propostas, o usuário escolheu a B: pedra escura com borda de ouro, gemas vermelha, roxa e azul cravejadas em engastes de ouro e gravações ciano. O cordão de couro virou uma **corrente dourada**, que remete ao ouro da receita, no peito e no chão. Vale para o ícone, o corpo e o chão. As variantes A e C continuam em `art/desenhar_runa.py`. Não testado no DST.

# Versão 0.6.15 — Runa Elétrica redesenhada para o jogo

No jogo, a runa recortada da referência ficava ilegível no peito: o cinza-claro se confundia com a pele, as gemas viravam pontos e as cordas e gravações finas pareciam um recorte sujo. Ela foi redesenhada no estilo do DST, fiel à referência (`art/desenhar_runa.py`):
- **Silhueta:** a mesma do raio, com espessura de pedra e contorno preto grosso.
- **Pedra:** cinza-azulada mais escura, que contrasta com a pele.
- **Gemas:** as três, vermelha, roxa e azul, maiores e com brilho.
- **Detalhes:** gravações ciano no lugar das cordas e runas finas.
- **Tamanho:** cerca de 20% maior no peito (76 px de frente).

O redesenho vale para o ícone, o corpo e o chão. Não testado no DST.

# Versão 0.6.14 — Runa Elétrica exige o Manipulador das Sombras

A receita da Runa Elétrica agora exige o **Manipulador das Sombras** (`TECH.MAGIC_THREE`), a mesma estação do Amuleto Roxo. Funciona como os itens do jogo: na primeira vez, é preciso estar perto da máquina para prototipar; depois, a receita fica liberada em qualquer lugar. Ingredientes e exclusividade do BLINK não mudaram. A Dagger continua sem exigir estação. Não testado no DST.

# Versão 0.6.13 — Runa Elétrica: +10% de velocidade

Equipada, a Runa Elétrica aumenta a velocidade de movimento em 10%, pelo mesmo mecanismo da Bengala. A força do BLINK só anula penalidades de velocidade, então o bônus vale normalmente. O bônus não gasta usos da runa. Não testado no DST.

# Versão 0.6.12 — Runa Elétrica

A Pedra do Ímpeto passou a se chamar **Runa Elétrica** e ganhou a arte enviada pelo usuário (`art/referencias/runa_eletrica_referencia.png`): uma runa em forma de raio com as gemas vermelha, roxa e azul.
- **Ícone:** a runa recortada, com contorno escuro.
- **Corpo:** a runa pendurada pelo aro num cordão, nos 11 quadros do amuleto (frente, lado, costas, só pingente e só cordão).
- **Chão:** a runa deitada, presa pelo aro a um cordão em laço.
- **Textos:** nome, descrição, receita, HUD ("Runa Elétrica ativa") e mensagem de quebra.

Funcionamento, receita e usos não mudaram. O identificador interno (`blink_impeto`) foi mantido, então as pedras já existentes no mundo viram Runas Elétricas sem se perder. Não testado no DST.

# Versão 0.6.11 — Dagger silenciosa

O zumbido elétrico ao segurar a Dagger foi removido a pedido do usuário. A Dagger na água (0.6.10) foi confirmada no jogo. Com isso, a Dagger está concluída.

# Versão 0.6.10 — Dagger na água (terceira correção)

A comparação com a Clava de Presunto, que boia visível no mesmo lugar, mostrou que a quantidade de quadros não era o problema: a peça dela tem só 2. A diferença era que todas as armas do jogo guardam a peça de água num arquivo de animação **separado** do item (`swap_ham_bat`), e a Dagger usava o próprio arquivo. Agora a peça fica em `anim/blink_dagger_float.zip`, com a mesma estrutura da Clava. Não testado no DST.

# Versão 0.6.9 — Dagger na água (segunda correção)

Na 0.6.8 a Dagger continuou invisível na água. O arquivo estava correto, mas a peça de água tinha só 1 quadro. As evidências indicam que o jogo escolhe o quadro pela **posição na lista**: o amuleto original tem exatamente 11 quadros para os pedidos 0 a 10, e a animação de boiar pede a posição 2. A peça de água agora tem a mesma lista de 5 quadros da Lança original. Não testado no DST.

# Versão 0.6.8 — zumbido elétrico e Dagger visível na água

**Estado real:** testes simulados aprovados. Não testado no DST. As versões 0.6.5 a 0.6.7 foram confirmadas no jogo pelo usuário, inclusive nas cavernas.

- **Zumbido:** ao equipar, toca o mesmo zumbido elétrico da Estrela da Manhã (`dontstarve_DLC001/common/morningstar`). Ele continua enquanto a Dagger estiver equipada e para ao desequipar, quebrar ou guardar no manequim.
- **Na água:** a Dagger ficava invisível porque o item boiando usa uma animação nativa que desenha a peça `swap_spear`, e a Dagger não indicava qual peça usar no lugar. Agora ela usa uma peça própria para a água, centralizada na mesma posição da Lança. Ao sair da água, volta ao visual normal do chão.

# Versão 0.6.7 — dash gasta uso, choque 50

**Estado real:** testes simulados aprovados. Não testado no DST.

- **Dash gasta 1 uso:** sem a Pedra do Ímpeto, o uso sai da Dagger. Com a Pedra equipada, sai só da Pedra, e a Dagger não gasta. Dash recusado não gasta nada. Se for o último uso, o dash acontece e depois o item quebra.
- **Dano do choque:** 50 por padrão, em cada salto, mantendo os 5 saltos.
- **Força:** continua no personagem (`combat.damagemultiplier` do BLINK) e vale para qualquer arma: Dagger 35 → 70, Lança 34 → 68. As opções foram renomeadas para deixar isso claro: "Dano da Dagger (a força do BLINK multiplica)" e "Força do BLINK (dano físico)".

Mundos já criados podem guardar o choque antigo (75). Confira em Configurar mod.

# Versão 0.6.6 — desgaste da Dagger, dano 35 e 5 saltos

**Estado real:** testes simulados aprovados. Não testado no DST.

- **Desgaste:** a Dagger tem **150 usos**, como a Lança, e cada ataque comum gasta 1. O dash e os saltos do choque não gastam. A porcentagem aparece no ícone. Ao quebrar, BLINK diz "A Dagger se partiu. Hora de forjar outra." e, se houver outra Dagger no inventário, ela é equipada automaticamente, como acontece com tochas e com a Estrela da Manhã. É configurável: 100, 150, 200 ou sem desgaste.
- **Dano base:** 35 por padrão, o que dá 70 com a força 2x.
- **Saltos do quinto choque:** 5 por padrão. Continuam atingindo criaturas neutras, como o dash.
- **Daggers antigas:** as que já existiam no mundo passam a ter 150 usos ao carregar.

**Atenção:** um mundo já criado pode guardar os valores antigos das opções (dano 50, 3 saltos). Confira em Hospedar → mundo → Mods → BLINK → Configurar mod.

# Versão 0.6.5 — choque em cadeia, luz e Dagger menor

**Estado real:** testes simulados aprovados. Não testado no DST.

- **Choque em cadeia (5º acerto):** o choque de 75 atinge o alvo e salta para o inimigo elegível mais próximo, a até 4 unidades, encadeando até **3 saltos** (configurável: 0, 2, 3 ou 5). Cada salto causa os mesmos 75 de dano elétrico, e cada criatura é atingida uma vez por choque. Os saltos acontecem com 0,2 s de intervalo, desenhando o arco elétrico original do jogo (`shock_arc_fx`). O choque se espalha mesmo se o 5º golpe já tiver matado o alvo.
- **Atordoamento:** os atingidos entram no estado "eletrocutado" do jogo (atordoamento curto e brilho), como na Estrela da Manhã. Chefes e criaturas imunes seguem as regras do jogo; alvos eletrocutados há pouco tempo levam o dano, mas não ficam atordoados de novo.
- **Proteções:** iguais às do dash. Jogadores, aliados, seguidores de jogadores e estruturas nunca são atingidos. Criaturas neutras próximas podem ser atingidas, como no dash.
- **Luz:** com a Dagger equipada, BLINK emite luz com os mesmos raio (4), intensidade e queda da Estrela da Manhã, em tom ciano. Não gasta nada e pode ser desligada nas configurações do mod ("Luz da Dagger equipada").
- **Dagger na mão:** cerca de 17% menor.

Novas opções em Configurar mod: "Saltos do quinto choque" e "Luz da Dagger equipada".

# Versão 0.6.4 — Dagger com a lâmina para baixo

A Dagger na mão foi girada 180° em torno da empunhadura. Agora o cabo fica na mão, com o pomo para cima, e a lâmina pende para baixo com o fio curvo voltado para frente, como na pegada de faca da referência. O tamanho é o mesmo da 0.6.3. O chão, o ícone e a Pedra não mudaram.

Instalação: feche o jogo, apague `mods\blink` e copie a pasta `blink` nova. Não testado no DST.

# Versão 0.6.3 — Dagger maior, Pedra com arte própria e fim do halo branco

**Estado real:** testes simulados aprovados e arquivos de animação conferidos, renderizando de volta cada quadro. Não testado no DST.

## Mudanças

- **Halo branco nos ícones:** a causa era técnica. O jogo espera texturas com alfa pré-multiplicado, confirmado nas texturas originais, e as do mod não estavam assim. Todas as texturas de interface foram refeitas: ícones, retratos, ícone do mapa e nomes. O brilho ciano dos ícones também saiu; agora eles têm contorno escuro, no estilo do jogo.
- **Dagger na mão:** 1,4× maior, com mais contraste e cor e contorno escuro mais grosso. O ângulo e a empunhadura continuam iguais. No chão, recebeu o mesmo reforço.
- **Pedra do Ímpeto no corpo:** pingente próprio (pedra lunar, faixa de ouro, três gemas, rachadura elétrica) num cordão de couro. Segue os mesmos quadros do amuleto original: de frente, de lado e só o cordão quando o personagem está de costas.
- **Pedra no chão:** pedra deitada com o cordão em laço. Usa só o movimento nativo do amuleto e a arte é própria.
- **Compilação própria:** as animações agora são geradas por `art/klei_anim.py`, no formato conferido byte a byte com arquivos do jogo. As Mod Tools não são mais necessárias.

## Instalação

1. Feche o jogo.
2. **Apague** a pasta `mods\blink` antiga.
3. Copie a pasta `blink` deste pacote para `mods`.

## O que conferir

- Ícones no inventário e na fabricação, sem contorno branco.
- Dagger na mão de frente, de lado e atacando: tamanho e legibilidade.
- Pedra equipada: pingente no peito de frente, de lado, e sumindo de costas.
- Pedra no chão.
- Retratos na seleção de personagem: as bordas devem estar sem clarão.

# Versão 0.6.2 — Dagger na mão (segunda correção)

**Causa encontrada:** as animações do jogador pedem quadros específicos da peça da mão. Ficar parado, andar e trabalhar pedem o quadro 1, e os ataques pedem 0, 1, 2, 5 e 6. A lança original tem os quadros 0–2 e 5–8, mas a Dagger compilada tinha só o quadro 0, então a mão ficava vazia. Isso foi confirmado lendo os arquivos `player_idles`, `player_basic`, `player_attacks`, `player_actions` e `swap_spear` da instalação do jogo.

**Correção:** a peça da mão agora cobre os quadros 0–2 e 5–8, com a mesma imagem da adaga. O quadro 5 está em escala 0,8 e o 7 em 1,1, para acompanhar a perspectiva dos ataques, como na lança.

**Importante na instalação:** apague a pasta `mods\blink` antiga antes de copiar a nova. A pasta `exported` saiu do mod (a fonte Spriter está em `art/spriter`). Se ela ficar, as Mod Tools podem recompilar e desfazer a correção.

Não testado no DST.

# Versão 0.6.1 — correção da Dagger na mão

A Dagger aparecia no chão, mas não na mão. O arquivo compilado pelas Mod Tools estava correto. O problema era a escolha automática entre arte própria e lança provisória: servidor e cliente podiam decidir de formas diferentes (por exemplo, com cavernas, o servidor roda em outro processo), e a mão ficava vazia. Agora a Dagger usa sempre a arte própria, e o `anim/blink_dagger.zip` compilado já vem no pacote. As Mod Tools não são mais obrigatórias para essa peça.

Não testado no DST após a correção.

# Versão 0.6 — arte própria da Dagger e ícones

**Estado real:** testes simulados aprovados. Esta versão AINDA NÃO foi executada no DST, e a compilação da arte pelas Mod Tools não pôde ser executada aqui.

## O que mudou

- **Dagger:** ícone de inventário e de receita feito a partir da arte de referência (`art/referencias/dagger_referencia.png`). A adaga foi recortada do fundo e recebeu contorno escuro e um brilho ciano leve.
- **Dagger na mão e no chão:** imagens próprias em `blink/exported/blink_dagger/` (projeto Spriter). Viram animação do jogo só depois de compiladas pelas **Don't Starve Mod Tools**. Sem a compilação, a Dagger continua com o visual provisório de lança na mão e no chão, sem erro.
- **Pedra do Ímpeto:** ícone próprio, desenhado por código (pedra lunar, faixa de ouro, gemas azul/vermelha/roxa e rachadura elétrica). No chão e no corpo ela ainda usa o amuleto azul provisório.
- Mecânicas, números e controles: sem mudanças.

## Como atualizar

1. Na Steam, abra a **Biblioteca**, inclua **Ferramentas** no filtro e instale **Don't Starve Mod Tools** (gratuito). É preciso fazer isso só uma vez.
2. Feche o jogo e substitua `mods/blink` pela pasta `blink` deste pacote.
3. Abra o DST. Com as Mod Tools instaladas, o compilador automático cria `mods/blink/anim/blink_dagger.zip` na abertura. Pode aparecer uma janela de terminal; espere ela terminar.
4. Confira se esse arquivo existe. Se não existir, o ícone novo aparece mesmo assim, mas a Dagger na mão continua como lança. Nesse caso, envie o final do `client_log.txt`.
5. Para jogar com outra pessoa, envie a pasta `blink` já com `anim/blink_dagger.zip`, para os dois verem a mesma arte.

## O que conferir no jogo

- Ícone da Dagger e da Pedra no inventário e no menu de fabricação.
- Dagger na mão: o cabo deve ficar na mão e a lâmina, voltada para cima e para frente. Tamanho e encaixe são uma primeira estimativa. Se ficar grande, pequena ou deslocada, envie uma captura de tela: o ajuste é só no pivô ou na escala.
- Dagger no chão: deve aparecer inteira, apoiada no solo.
- Ataque, dash e choque continuam iguais.

## Próxima etapa: corpo do BLINK

A ficha `art/referencias/blink_ficha_frente_perfil_costas.png` é a referência do corpo. O DST precisa das peças separadas e com as proporções do jogo (cabeça grande em relação ao corpo). Por isso a ficha não pode ser só recortada; veja o planejamento na conversa.

--- Histórico ---

# Versão 0.5 — Pedra do Ímpeto

**Estado real:** código implementado e aprovado nos testes simulados. Esta versão AINDA NÃO foi executada no Don't Starve Together.

## Pedra do Ímpeto

- Receita exclusiva do BLINK, sem estação de ciência: **1 gema azul + 1 gema vermelha + 1 gema roxa + 1 pedra da lua + 1 pepita de ouro** (`bluegem`, `redgem`, `purplegem`, `moonrocknugget`, `goldnugget`). Aba de personagem/magia.
- Equipada no **espaço do corpo**, como um amuleto. Ocupa o lugar de armadura e mochila.
- Com a pedra equipada e a Dagger na mão, o dash não espera a recarga.
- **50 usos por pedra.** Cada dash realizado com sucesso consome 1 uso, mesmo se a recarga já estivesse pronta.
- Tentativas recusadas (sem Dagger, fantasma, montado, ocupado, terreno inválido, direção nula, pedidos repetidos em menos de 0,15 s) não consomem uso.
- No último uso o dash acontece e a pedra se quebra, com faísca e a fala "A Pedra do Ímpeto se partiu."
- Todo dash, com ou sem pedra, inicia a recarga normal. Ao retirar ou quebrar a pedra, vale o tempo restante desde o último dash: equipar/retirar não gera dash grátis nem usos extras.
- Dano, alcance (8), direção e proteção de aliados não mudam.
- Os usos restantes ficam salvos em cada pedra (componente nativo de usos do jogo) e aparecem em porcentagem no ícone do inventário.
- HUD: com a pedra ativa, aparece uma segunda linha: `Pedra do Ímpeto ativa: sem recarga | 37/50 usos`.
- **Visual provisório:** ícone e peça no corpo do Amuleto Gelado (azul) nativo; no chão, tingida de ciano. Identifique pelo nome "Pedra do Ímpeto" ao passar o mouse.

## Teste sugerido no jogo

1. Junte os ingredientes (no modo de teste, use o console: `c_give("bluegem")` etc.) e fabrique a pedra como BLINK.
2. Equipe a pedra e a Dagger. Dê vários dashes seguidos: cada um deve consumir 1 uso (a porcentagem cai 2%).
3. Tente dash diante do oceano ou sem a Dagger: a porcentagem não deve cair.
4. Dê um dash e retire a pedra logo em seguida: a recarga de 5 s deve aparecer.
5. Saia e volte ao mundo com uma pedra parcialmente gasta: os usos devem ser mantidos.
6. Gaste uma pedra até o fim (50 dashes) e confira a quebra e a volta da recarga normal.

Atualização: feche o jogo e substitua `mods/blink` pela pasta `blink` deste pacote. Se houver erro, envie o final de `client_log.txt`.

--- Histórico ---

# Versão 0.4 — receita e controles do mouse

Receita da Dagger: 2 salitres (nitre) + 1 sílex/pederneira (flint), exclusiva do BLINK, sem estação de ciência. Armas já existentes continuam válidas e sem desgaste.

No jogo, F6 abre o menu pessoal. Pressione uma tecla, clique no scroll, role para cima/baixo ou pressione um botão extra; depois clique em Salvar. Esquerdo e direito são reservados ao jogo/menu. Botões extras dependem de o jogo/driver entregar esses eventos: se o nome não aparecer, mapeie o botão para uma tecla no software do mouse e selecione essa tecla. A rolagem pode continuar acionando o zoom original; não removemos controles do jogo. Preferências antigas de teclado são preservadas. A escolha é local, não compartilhada com outros jogadores. Não há dash ao rolar sobre elementos de interface.

Dano padrão: base 50; com a força 2x do BLINK, 100 por golpe. Quinto acerto: +75 elétrico no alvo se ainda vivo. Dash: 100 elétrico por criatura no percurso. Defesas podem reduzir esses valores, e configurações antigas do mundo podem ter outros valores. Confira Dano do dash = 100 na configuração do mod. Recarga 5 s, configurável. Efeitos especiais não aplicam força 2x novamente.

Atualização: feche o jogo e substitua mods/blink pela pasta blink deste pacote. Testes simulados passaram; botões físicos e scroll ainda precisam ser testados no DST.

--- Histórico ---

# Versão 0.3 — tecla individual do dash

1. Feche o jogo e substitua mods/blink pela pasta blink deste pacote.
2. Entre com BLINK e pressione F6.
3. Pressione a tecla desejada. O menu mostra a seleção.
4. Clique em Salvar com o mouse. Cancelar/Esc descarta a mudança; Padrao: G apenas seleciona G (clique em Salvar para confirmar).

A escolha fica salva localmente para as próximas sessões, individualmente em cada instalação do jogo. Não é uma opção global do servidor. Letras, números, F1–F12 (exceto F6) e algumas teclas especiais são aceitos. F6 é reservado ao menu e Esc cancela. Evite teclas usadas para movimento, chat ou inventário: o mod não remove as ações originais do jogo. O menu pode abrir enquanto o mundo continua rodando.

Corrigido o padrão incorreto 5 da versão 0.2; o padrão agora é G. A opção antiga de tecla do servidor foi removida. Também restaurado o padrão de dano do dash para 100 (o mundo pode manter o valor anterior nas configurações). Recarga padrão permanece 5 segundos. Menu e persistência passaram em simulações; ainda precisam ser validados no jogo.

--- Histórico e instruções gerais ---

# Atualização 0.2 — direção, recarga e força permanente

Feche o jogo. Substitua a pasta mods/blink pela pasta blink deste pacote.
Na configuração do mod do mundo, selecione explicitamente Recarga do dash = 5 segundos: mundos existentes podem conservar os 10 segundos antigos.

Mudanças: dash para frente usando a orientação local do personagem; posição e alcance validados no servidor. Atinge criaturas hostis e neutras no percurso, mantendo proteção de aliados e estruturas. Recarga padrão 5 s. Estado mighty permanente com suporte nativo a carregar peso sem penalidade de equipamento, animação de caminhada pesada rápida, eficiência de trabalho, isolamento térmico e navegação do estado forte. Não adiciona árvore de habilidades nem academia do Wolfgang. Mantém 300/200/200 e multiplicador de dano configurável.

Teste no jogo: andar em cada direção e apertar G; parar e usar G; atravessar duas criaturas alinhadas; testar aliado ao lado; carregar estátua; salvar e reabrir. A versão 0.2 passou nos testes simulados, mas ainda não foi executada no DST. A versão 0.1 teve entrada no mundo, dash e choque confirmados pelo usuário.

---

# BLINK — primeira versão de teste (0.2.0 alpha)

Personagem jogável independente para Don't Starve Together, com Dagger, força permanente e duas habilidades elétricas. Não depende de NPC Friends nem de DSTAdmin.

**Estado real da entrega:** código e arquivos preparados, testes locais aprovados com simulação de partes do motor. Esta versão NÃO foi executada em Don't Starve Together. A validação dentro do jogo ainda é necessária. Não é uma versão final pronta para publicação na Oficina.

## Aparência: o que você verá

- Nos retratos: conceito original do assassino encapuzado BLINK.
- No mundo: corpo e animações nativos do Wolfgang poderoso, provisoriamente.
- Na mão e no inventário: recurso visual nativo de lança para representar a Dagger, provisoriamente.
- A arte do assassino está em `art/BLINK_conceito.png`. Ela ainda NÃO é uma animação jogável: faltam separar peças do corpo, produzir as vistas e compilar o build de animação do personagem e da adaga.

O personagem final ainda precisará dessa etapa artística. O mod não contém assets extraídos de Dota 2 nem de NPC Friends; os visuais provisórios são referenciados da instalação do próprio DST.

## Instalação no Windows (Steam)

1. Feche o jogo.
2. Extraia o ZIP.
3. Na Steam, abra a Biblioteca, clique com o botão direito em Don't Starve Together e escolha **Gerenciar → Explorar arquivos locais** (a tradução pode variar).
4. Abra a pasta `mods` dentro da instalação. Se ela não existir, crie-a.
5. Copie a pasta **blink** inteira para dentro de `mods`.
6. Confira que o caminho termina em `Don't Starve Together\mods\blink\modinfo.lua`. Não deixe duas pastas `blink` encaixadas.
7. Abra o jogo. Em **Hospedar → mundo de teste → Mods do servidor**, habilite **BLINK - Assassino Eletrico (ALPHA)**.
8. Crie um mundo de teste e selecione **BLINK** na escolha de personagem. Ativar o mod não transforma automaticamente um personagem já existente em BLINK.
9. Para o primeiro teste, use apenas este mod. NPC Friends não é necessário.

Todos os participantes precisam instalar a mesma versão manualmente. Ainda não há publicação na Oficina para baixar automaticamente. Para servidor dedicado, caves e migração entre servidores, ainda é preciso validar a instalação e os testes específicos. A cópia de um mundo deve ser feita antes de testar nele; remover um mod de personagem usado em um save pode impedir a entrada desse personagem.

## Como jogar

- Equipar a **Dagger**, recebida ao nascer.
- Pressionar **G** para avançar na direção do movimento; parado, avança para onde está olhando. O cursor não define mais o destino.
- O dash possui alcance máximo de 8 unidades do mundo e largura aproximada de 1,6 unidades (mais o raio do alvo).
- Movimento instantâneo com trilha elétrica; o dano é calculado ao longo do percurso, não só no destino. Ainda não há animação própria de corrida/deslizamento.
- Recarga: **5 segundos**. O indicador no alto da tela informa o tempo restante.
- Dano do dash: **100**, uma vez por inimigo elegível no trajeto.
- A cada **5 acertos que causem dano com a Dagger**, o alvo recebe **75 de dano elétrico adicional**. Se o quinto golpe já o matou, não há alvo vivo para receber o dano adicional.
- O contador é mostrado como `Choque: 0/5`, `1/5` etc. O dash e o próprio choque não alimentam esse contador.
- Perdeu a Dagger? BLINK tem uma receita exclusiva de reposição: **2 salitres + 1 silex**, sem estação de ciência.

Teclado e mouse são o controle implementado nesta alpha. Não há suporte específico a controle/gamepad.

## Atributos e limites

| Item | Padrão |
|---|---:|
| Vida máxima | 300 |
| Fome máxima | 200 |
| Sanidade máxima | 200 |
| Multiplicador de dano físico | 2x |
| Dano base da Dagger | 50 |
| Dano físico da Dagger com BLINK | 100 antes de defesas/modificadores |
| Dano elétrico do dash | 100 antes de defesas do alvo |
| Dano elétrico do quinto acerto | 75 antes de defesas do alvo |
| Recarga do dash | 5 s |
| Desgaste da Dagger | Nenhum |

Os ataques elétricos especiais não recebem novamente o multiplicador de força e não ganham multiplicação extra por chuva nesta implementação. A defesa do alvo continua sendo processada pelo sistema de combate do jogo. Não há invulnerabilidade, fome infinita, imunidade ao frio, supervelocidade permanente nem atordoamento garantido de chefes. Fora dessas habilidades, BLINK usa as regras comuns de sobrevivência.

Força, dano da arma, dano do dash, dano do choque, tempo de recarga podem ser alterados na configuração do mod antes de iniciar o servidor. A tecla é pessoal e configurada com F6 dentro do jogo.

## Proteção de aliados e segurança do dash

As habilidades elétricas excluem jogadores, estruturas, paredes, companheiros marcados, aliados reconhecidos pelo sistema de combate e seguidores vinculados a jogadores. O dash atinge também animais neutros no caminho, uma vez por criatura; aliados continuam protegidos. A compatibilidade com qualquer outro mod de NPCs não é garantida.

Essas proteções são das habilidades especiais. Um ataque comum obedece às regras normais de PvP e ataque forçado do servidor.

O servidor confere a arma equipada, estado vivo, recarga, alcance e terreno. Não permite dash durante estados ocupados nem montado. O trajeto para antes de terrenos inválidos, oceano, paredes e estruturas sólidas detectadas. Barcos, obstáculos especiais e mods de mapas exigem validação no jogo. Não foi prometido atravessar paredes.

A recarga e o contador pertencem ao personagem; trocar ou fabricar outra Dagger não deve reiniciá-los. Eles são salvos pelo componente do personagem.

## Roteiro do primeiro teste no jogo

1. Verifique se o mod aparece, se BLINK é selecionável e se nasce com 300/200/200 e uma Dagger.
2. Equipe a Dagger. Confira o indicador de recarga e pressione G apontando para chão livre.
3. Pressione G de novo imediatamente: não deve haver um segundo dash antes da recarga.
4. Ataque um alvo resistente cinco vezes: o contador deve reiniciar no quinto acerto. Defesas do alvo podem reduzir o dano.
5. Atravesse dois inimigos alinhados: cada um deve ser atingido uma vez. Um alvo longe da faixa não deve receber dano.
6. Teste perto de um aliado e de um baú: as habilidades não devem causar dano a eles.
7. Teste diante de um litoral e de uma parede: o personagem deve parar antes da barreira.
8. Saia com contador em 3/5 e volte. Confira a persistência.
9. Teste morte e ressurreição. O fantasma deve aparecer; reviver não deve apagar as habilidades.
10. Só depois valide com outro jogador, cavernas e outros mods.

Se houver erro, envie a tela e o trecho final de `client_log.txt` ou `server_log.txt` da pasta `Documentos\Klei\DoNotStarveTogether` (os logs do servidor podem estar em subpastas do mundo). Se o personagem ficar invisível, informe se foi ao selecionar, nascer ou reviver.

## Testes feitos aqui

- Sintaxe de todos os arquivos Lua, usando liblua 5.4. O código evita recursos exclusivos de Lua 5.2+; o motor Lua 5.1 do DST não foi executado aqui.
- Verificações com objetos simulados: geometria, entradas inválidas, limites de alcance, aliados, recarga, cinco golpes, ausência de recursão, salvamento e terreno.
- Estrutura dos 10 pares de atlas/XML e textura KTEX, dimensões e tamanho dos dados.
- NÃO testados aqui: renderização real, seleção do personagem, interação com saves, efeitos visuais, rede real e motor do DST.

Resultados em `VALIDACAO.txt`. Para reproduzir em Linux com Python e liblua5.4: `python3 tests/run_tests.py`.

## Conteúdo do pacote

- `blink/`: pasta instalável do mod.
- `art/`: conceito e script de preparação dos retratos (Python/Pillow).
- `tests/`: testes locais com motor simulado.
- `FONTES.md`: referências consultadas.

Não redistribua como versão final com visual completo: os retratos já mostram a proposta final, mas o modelo em jogo ainda é provisório.

---

# Versão 0.1 — primeira versão jogável

Primeira versão de teste: força permanente, Dagger com aparência provisória (lança nativa), dash e choque. Entrada no mundo, dash e choque confirmados no jogo, depois de uma dificuldade inicial para ativar o dash.
