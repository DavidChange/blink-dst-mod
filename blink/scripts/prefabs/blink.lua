local MakePlayerCharacter = require("prefabs/player_common")
-- Visual proprio (0.9.0): anim/blink.zip = arte do BLINK (folhas em art/corpo_v2) encaixada nos quadros
-- molde do jogo; anim/ghost_blink_build.zip = fantasma do jogo com o cabelo do BLINK.
local assets = {Asset("ANIM","anim/blink.zip"),Asset("ANIM","anim/player_wolfgang.zip"),Asset("ANIM","anim/player_mount_wolfgang.zip"),Asset("ANIM","anim/ghost_blink_build.zip")}
local prefabs = {"blink_dagger","blink_dagger_light","blink_impeto","electrichitsparks","shock_arc_fx","electrocute_fx","sparks","wx78_big_spark"}
local function common(inst)
    inst:AddTag("blink_assassin")
    inst:AddTag("mightiness_mighty")
    inst.MiniMapEntity:SetIcon("blink.tex")
    inst.AnimState:SetBuild("blink")
    inst._blink_cooldown = net_ushortint(inst.GUID,"blink.cooldown","blinkstatusdirty")
    inst._blink_hits = net_tinybyte(inst.GUID,"blink.hits","blinkstatusdirty")
    inst._blink_stone = net_byte(inst.GUID,"blink.stone","blinkstatusdirty")
    inst._blink_might = net_tinybyte(inst.GUID,"blink.might","blinkstatusdirty")
    inst._blink_wet = net_bool(inst.GUID,"blink.wet","blinkstatusdirty")
end
local function master(inst)
    inst.soundsname = "wolfgang"
    inst.ghostbuild = "ghost_blink_build"
    inst.components.health:SetMaxHealth(TUNING.BLINK_HEALTH)
    inst.components.hunger:SetMax(TUNING.BLINK_HUNGER)
    inst.components.sanity:SetMax(TUNING.BLINK_SANITY)
    inst.starting_inventory = (TUNING.GAMEMODE_STARTING_ITEMS[TheNet:GetServerGameMode()] or TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT).BLINK or {"blink_dagger"}
    inst.components.combat.damagemultiplier = TUNING.BLINK.strength_tiers[2]   -- ajustado pela fome em blinkpower
    require("blink/permanent_mighty")(inst)
    inst:AddComponent("blinkpower")
end
return MakePlayerCharacter("blink",prefabs,assets,common,master,{"blink_dagger"})
