return CreatePrefabSkin("blink_none", {
    base_prefab = "blink",
    type = "base",
    assets = {Asset("ANIM","anim/blink.zip"),Asset("ANIM","anim/ghost_blink_build.zip")},
    skins = {normal_skin="blink",ghost_skin="ghost_blink_build"},
    skin_tags = {"BLINK","CHARACTER","BASE"},
    build_name_override = "blink",
    rarity = "Character",
})
