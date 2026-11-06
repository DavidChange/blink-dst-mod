-- Runa Eletrica (antes Pedra do Impeto): amuleto de corpo que permite ao BLINK ignorar a recarga do dash.
-- Arte propria (anim/blink_impeto.zip): runa em cordao no corpo e runa deitada no chao.
-- O chao reaproveita apenas o BANCO nativo "amulets" (movimento), com o build proprio:
-- por isso o simbolo do chao se chama "blueamulet", nome que essa animacao nativa procura.
-- A logica do dash fica em components/blinkpower.lua; aqui ficam apenas item, usos e quebra.
local ICON_ATLAS = "images/inventoryimages/blink_impeto.xml"
local assets = {Asset("ANIM","anim/amulets.zip"),Asset("ANIM","anim/blink_impeto.zip"),
    Asset("ATLAS",ICON_ATLAS),Asset("IMAGE","images/inventoryimages/blink_impeto.tex")}
local function onequip(inst,owner)
    owner.AnimState:OverrideSymbol("swap_body","blink_impeto","swap_blink_impeto")
end
local function onunequip(inst,owner)
    owner.AnimState:ClearOverrideSymbol("swap_body")
end
local function onfinished(inst)
    local owner = inst.components.inventoryitem ~= nil and inst.components.inventoryitem.owner or nil
    if owner ~= nil and owner.Transform ~= nil then
        local fx = SpawnPrefab("electrichitsparks")
        if fx ~= nil then fx.Transform:SetPosition(owner.Transform:GetWorldPosition()) end
        if owner.components.talker ~= nil then owner.components.talker:Say(STRINGS.BLINK_IMPETO_BROKEN) end
    end
    inst:Remove()
end
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("amulets")
    inst.AnimState:SetBuild("blink_impeto")
    inst.AnimState:PlayAnimation("blueamulet")
    inst:AddTag("blink_impeto")
    MakeInventoryFloatable(inst,"med",nil,0.6)
    inst.entity:SetPristine()
    if not TheWorld.ismastersim then return inst end
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "blink_impeto"
    inst.components.inventoryitem.atlasname = ICON_ATLAS
    inst:AddComponent("equippable")
    inst.components.equippable.equipslot = EQUIPSLOTS.BODY
    inst.components.equippable:SetOnEquip(onequip)
    inst.components.equippable:SetOnUnequip(onunequip)
    -- +10% de velocidade enquanto equipada (mesmo mecanismo da Bengala; a forca do BLINK
    -- so anula penalidades < 1, entao o bonus vale normalmente).
    inst.components.equippable.walkspeedmult = TUNING.BLINK.stone_speed
    -- finiteuses (componente nativo) salva e carrega os usos restantes de cada pedra.
    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(TUNING.BLINK.stone_uses)
    inst.components.finiteuses:SetUses(TUNING.BLINK.stone_uses)
    inst.components.finiteuses:SetOnFinished(onfinished)
    MakeHauntableLaunch(inst)
    return inst
end
return Prefab("blink_impeto",fn,assets,{"electrichitsparks"})
