local pt = (locale == "pt" or locale == "br")
local function L(en, ptbr) return pt and ptbr or en end
name = "BLINK"
description = L(
    "BLINK, the sarcastic electric assassin. Fragile (125 health), hits hard, hates rain.\n\n- Strength by hunger: 1.25x / 1.5x / 2x (well-fed = strongest, but burns food faster)\n- Dagger: electric dash (G by default; F6 changes the key)\n- Every 5th hit, a chain shock jumps between enemies\n- Electric Rune: grants the dash; with the Dagger, no cooldown (30 uses)\n- Wet: sparks and small damage; soaked = no dash or shock\n- English and Portuguese (BR)\n\nMod by Projeto BLINK",
    "BLINK, o assassino elétrico sarcástico. Frágil (125 de vida), bate forte, odeia chuva.\n\n- Força pela fome: 1,25x / 1,5x / 2x (bem alimentado = mais forte, mas gasta comida mais rápido)\n- Dagger: dash elétrico (G por padrão; F6 troca a tecla)\n- A cada 5 golpes, um choque em cadeia salta entre inimigos\n- Runa Elétrica: dá o dash; com a Dagger, sem recarga (30 usos)\n- Molhado: faíscas e dano leve; encharcado = sem dash nem choque\n- Inglês e português (BR)\n\nMod por Projeto BLINK")
author = "Projeto BLINK"
version = "1.0.0"
api_version = 10
dst_compatible = true
dont_starve_compatible = false
reign_of_giants_compatible = false
all_clients_require_mod = true
client_only_mod = false
icon_atlas = "modicon.xml"
icon = "modicon.tex"
server_filter_tags = {"BLINK", "character"}
configuration_options = {
 {name="language",label=L("Language","Idioma"),options={{description=L("Auto (game language)","Automático (idioma do jogo)"),data="auto"},{description="English",data="en"},{description="Português (BR)",data="pt"}},default="auto"},
}
