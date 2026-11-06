-- Visual proprio da Dagger: anim/blink_dagger.zip ja vem incluido no mod (fonte Spriter em
-- art/; compilado por art/compilar_anim.py; simbolo da mao cobre os quadros 0-2 e 5-8 como a lanca). Sempre usado: servidor e cliente precisam
-- concordar no visual, e uma verificacao de arquivo pode dar resultados diferentes em cada processo
-- (por exemplo, com cavernas o servidor roda separado), deixando a mao vazia.
local ICON_ATLAS = "images/inventoryimages/blink_dagger.xml"
local assets = {Asset("ANIM","anim/blink_dagger.zip"),Asset("ANIM","anim/blink_dagger_float.zip"),
    Asset("ATLAS",ICON_ATLAS),Asset("IMAGE","images/inventoryimages/blink_dagger.tex")}
-- Luz enquanto equipada, como a Estrela da Manha (mesmos raio/intensidade/queda; tom ciano).
local function removelight(inst)
    if inst._light ~= nil then
        inst._light:Remove()
        inst._light = nil
    end
end
local function addlight(inst,owner)
    if not TUNING.BLINK.dagger_light then return end
    if inst._light == nil then
        inst._light = SpawnPrefab("blink_dagger_light")
    end
    inst._light.entity:SetParent(owner.entity)
end
local function equip(inst,owner)
    addlight(inst,owner)
    owner.AnimState:OverrideSymbol("swap_object","blink_dagger","swap_blink_dagger")
    owner.AnimState:Show("ARM_carry")
    owner.AnimState:Hide("ARM_normal")
end
local function unequip(inst,owner)
    removelight(inst)
    owner.AnimState:Hide("ARM_carry")
    owner.AnimState:Show("ARM_normal")
end
-- Ao quebrar: igual a Estrela da Manha/tocha. O personagem comenta e o jogo equipa
-- automaticamente outra Dagger do inventario, se houver ("itemranout").
local function onfinished(inst)
    local equippable = inst.components.equippable
    local owner = inst.components.inventoryitem ~= nil and inst.components.inventoryitem.owner or nil
    if owner ~= nil and equippable ~= nil and equippable:IsEquipped() then
        local data = {prefab=inst.prefab,equipslot=equippable.equipslot,announce="ANNOUNCE_BLINK_DAGGER_BROKE"}
        inst:Remove()
        owner:PushEvent("itemranout",data)
        return
    end
    inst:Remove()
end
local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("blink_dagger")
    inst.AnimState:SetBuild("blink_dagger")
    inst.AnimState:PlayAnimation("idle")
    inst:AddTag("sharp")
    inst:AddTag("pointy")
    inst:AddTag("weapon")
    -- Na agua o jogo troca para o banco nativo "floating_item", que desenha o simbolo
    -- "swap_spear" (quadro 2). Como na Clava de Presunto, a peca vem de um build separado
    -- (anim/blink_dagger_float.zip), centralizada como a Lanca (quadro 0, sem deslocamento).
    MakeInventoryFloatable(inst,"med",0.05,{1.1,0.5,1.1},true,0,
        {sym_build="blink_dagger_float",bank="blink_dagger",anim="idle"})
    inst.entity:SetPristine()
    if not TheWorld.ismastersim then return inst end
    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(TUNING.BLINK.dagger_damage)
    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "blink_dagger"
    inst.components.inventoryitem.atlasname = ICON_ATLAS
    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(equip)
    inst.components.equippable:SetOnUnequip(unequip)
    if inst.components.equippable.SetOnEquipToModel ~= nil then
        inst.components.equippable:SetOnEquipToModel(removelight) -- manequim: sem luz
    end
    inst.OnRemoveEntity = removelight
    -- Desgaste: 1 uso por ataque comum (o componente de arma do jogo desconta sozinho).
    -- Dash e choque em cadeia nao gastam usos. Configuravel; 0 = sem desgaste.
    if (TUNING.BLINK.dagger_uses or 0) > 0 then
        inst:AddComponent("finiteuses")
        inst.components.finiteuses:SetMaxUses(TUNING.BLINK.dagger_uses)
        inst.components.finiteuses:SetUses(TUNING.BLINK.dagger_uses)
        inst.components.finiteuses:SetOnFinished(onfinished)
    end
    MakeHauntableLaunch(inst)
    return inst
end
local function lightfn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddLight()
    inst.entity:AddNetwork()
    inst:AddTag("FX")
    inst.Light:SetIntensity(.75)
    inst.Light:SetColour(170/255,235/255,1)
    inst.Light:SetFalloff(.6)
    inst.Light:SetRadius(4)
    inst.Light:Enable(true)
    inst.entity:SetPristine()
    if not TheWorld.ismastersim then return inst end
    inst.persists = false
    return inst
end
return Prefab("blink_dagger",fn,assets,{"electrichitsparks","shock_arc_fx","electrocute_fx","blink_dagger_light"}),
    Prefab("blink_dagger_light",lightfn)
