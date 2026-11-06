local G = GLOBAL
PrefabFiles = {"blink","blink_none","blink_dagger","blink_impeto"}
Assets = {}
for _,path in ipairs({
 "images/saveslot_portraits/blink", "images/selectscreen_portraits/blink",
 "images/selectscreen_portraits/blink_silho", "bigportraits/blink",
 "images/map_icons/blink", "images/avatars/avatar_blink",
 "images/avatars/avatar_ghost_blink", "images/avatars/self_inspect_blink",
 "images/names_blink", "images/names_gold_blink",
}) do
    table.insert(Assets,Asset("ATLAS",path..".xml"))
    table.insert(Assets,Asset("IMAGE",path..".tex"))
end
for _,name in ipairs({"blink_dagger","blink_impeto"}) do
    table.insert(Assets,Asset("ATLAS","images/inventoryimages/"..name..".xml"))
    table.insert(Assets,Asset("IMAGE","images/inventoryimages/"..name..".tex"))
end
AddMinimapAtlas("images/map_icons/blink.xml")
-- Icones proprios de inventario (tambem usados nas receitas e no menu de fabricacao).
if G.RegisterInventoryItemAtlas ~= nil then
    for _,name in ipairs({"blink_dagger","blink_impeto"}) do
        local atlas = "images/inventoryimages/"..name..".xml"
        G.RegisterInventoryItemAtlas(G.softresolvefilepath(atlas) or atlas,name..".tex")
    end
end
-- 0.13.1: equilibrio fixo (nao configuravel no menu do mod).
G.TUNING.BLINK = {
    cooldown=8,
    dash_damage=50,
    shock_damage=50,
    dagger_damage=38,
    dagger_uses=150,
    strength=2,
    stone_uses=30,
    full_hunger_rate=1.25,
    wet_weakness=true,
    wet_dps_min=0.3,
    wet_dps_max=0.9,
    stone_speed=1.1,
    chain_jumps=5,
    dagger_light=true,
}
-- Tela de selecao: vida/fome/sanidade e itens iniciais (lidos pelo jogo como nos personagens oficiais).
G.TUNING.BLINK_HEALTH = 125
G.TUNING.BLINK_HUNGER = 200
G.TUNING.BLINK_SANITY = 250
G.TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.BLINK = {"blink_dagger"}
-- Forca por faixa de fome: base / media / maxima = 62,5% / 75% / 100% da forca maxima configurada.
do local mx = G.TUNING.BLINK.strength; G.TUNING.BLINK.strength_tiers = {mx*0.625, mx*0.75, mx} end
local S = G.STRINGS
-- Idioma: ingles ou portugues (configuracao "language"; "auto" segue o idioma do jogo).
local Lang = G.require("blink/lang")
local LANG = Lang.pick(G, GetModConfigData("language"))
local T = Lang[LANG]
S.BLINK_UI = T
S.CHARACTER_TITLES.blink = T.title
S.CHARACTER_NAMES.blink = "BLINK"
S.CHARACTER_DESCRIPTIONS.blink = T.description
S.CHARACTER_QUOTES.blink = T.quote
S.CHARACTER_SURVIVABILITY.blink = T.survivability
S.NAMES.BLINK = "BLINK"
S.NAMES.BLINK_DAGGER = T.dagger
S.NAMES.BLINK_IMPETO = T.rune
S.SKIN_NAMES.blink_none = "BLINK"
-- Falas proprias (sarcasticas); o que faltar cai nas falas genericas ja traduzidas pelo jogo.
S.CHARACTERS.BLINK = G.require(LANG == "pt" and "speech_blink_pt" or "speech_blink_en")
S.CHARACTERS.GENERIC.DESCRIBE.BLINK_DAGGER = T.dagger_desc
S.CHARACTERS.GENERIC.DESCRIBE.BLINK_IMPETO = T.rune_desc
S.CHARACTERS.GENERIC.DESCRIBE.BLINK = T.blink_seen
S.CHARACTERS.GENERIC.ANNOUNCE_BLINK_DAGGER_BROKE = T.dagger_broke
S.RECIPE_DESC.BLINK_DAGGER = T.dagger_recipe
S.RECIPE_DESC.BLINK_IMPETO = T.rune_recipe
S.BLINK_IMPETO_BROKEN = T.rune_broke
AddModCharacter("blink","MALE",{{type="ghost_skin",anim_bank="ghost",idle_anim="idle",scale=0.75,offset={0,-25}}})
-- Uses only base-game visuals; no assets from NPC Friends or Dota are included.
AddRecipe2("blink_dagger",{G.Ingredient("flint",2),G.Ingredient("nitre",1),G.Ingredient("goldnugget",1)},G.TECH.SCIENCE_TWO, -- Motor de Alquimia
    {builder_tag="blink_assassin",atlas="images/inventoryimages/blink_dagger.xml",image="blink_dagger.tex"},{"CHARACTER","WEAPONS"})
-- Runa Eletrica (antes "Pedra do Impeto"; id interno blink_impeto mantido para nao perder itens salvos).
AddRecipe2("blink_impeto",{G.Ingredient("purplegem",1),G.Ingredient("moonrocknugget",3),
    G.Ingredient("goldnugget",4),G.Ingredient("nightmarefuel",2)},G.TECH.MAGIC_THREE, -- Manipulador das Sombras (prototipar 1x, depois em qualquer lugar)
    {builder_tag="blink_assassin",atlas="images/inventoryimages/blink_impeto.xml",image="blink_impeto.tex"},{"CHARACTER","MAGIC"})
AddModRPCHandler("BLINK","dash",function(player,dx,dz)
    if player ~= nil and player:IsValid() and player.components.blinkpower ~= nil then
        player.components.blinkpower:DashForward(dx,dz)
    end
end)
if not G.TheNet:IsDedicated() then
    local keymenu = G.require("blink/keymenu")(G, function()
        local player = G.ThePlayer
        if player == nil or player.prefab ~= "blink" or player.HUD == nil
            or player:HasTag("playerghost") or not player.HUD:IsVisible() then return end
        local screen = G.TheFrontEnd:GetActiveScreen()
        if screen ~= player.HUD or player.HUD:HasInputFocus() then return end
        local angle = player.Transform:GetRotation() * G.DEGREES
        G.SendModRPCToServer(G.MOD_RPC.BLINK.dash,math.cos(angle),-math.sin(angle))
    end)
    AddClassPostConstruct("widgets/controls",function(self)
        local Text = G.require("widgets/text")
        local label = self.top_root:AddChild(Text(G.UIFONT,23,""))
        label:SetPosition(0,-85,0)
        label:SetColour(0.3,0.9,1,1)
        label:SetClickable(false)
        self.inst:DoPeriodicTask(0.1,function()
            local p = G.ThePlayer
            if p == nil or p.prefab ~= "blink" or p._blink_cooldown == nil or p:HasTag("playerghost") then
                label:Hide()
                return
            end
            label:Show()
            local cd = p._blink_cooldown:value()
            local weapon = p.replica.inventory and p.replica.inventory:GetEquippedItem(G.EQUIPSLOTS.HANDS)
            local stone = p._blink_stone ~= nil and p._blink_stone:value() or 0
            local state
            local U = G.STRINGS.BLINK_UI
            local dagger = weapon ~= nil and weapon.prefab == "blink_dagger"
            if p._blink_wet ~= nil and p._blink_wet:value() then state = U.hud_wet
            elseif not dagger and stone <= 0 then state = U.hud_equip
            elseif (dagger and stone > 0) or cd <= 0 then state = string.format(U.hud_ready, keymenu:GetLabel())
            else state = string.format(U.hud_cd, cd) end
            local tier = p._blink_might ~= nil and p._blink_might:value() or 1
            local mult = G.TUNING.BLINK.strength_tiers[tier+1] or G.TUNING.BLINK.strength
            local text = string.format(U.hud_line, state, p._blink_hits:value(), string.format("%g", mult))
            if stone > 0 then
                text = text.."\n"..string.format(U.hud_rune, stone, G.TUNING.BLINK.stone_uses)
            end
            label:SetString(text)
        end)
    end)
end
