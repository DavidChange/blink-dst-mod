local Geometry = require("blink/math")
local Targets = require("blink/targets")
local BlinkPower = Class(function(self,inst)
    self.inst = inst
    self.ready_at = 0
    self.hits = 0
    self.last_request = -math.huge
    self.wet_steps = 0
    self.might = -1
    inst:DoPeriodicTask(0.1,function() self:Sync() end)
    inst:DoPeriodicTask(1,function() self:WetTick() end)
    inst:ListenForEvent("hungerdelta",function() self:UpdateStrength() end)
    inst:DoTaskInTime(0,function() self:UpdateStrength() end)
    inst:ListenForEvent("onhitother",function(_,data)
        if data and data.weapon and data.weapon.prefab == "blink_dagger"
            and data.stimuli ~= "electric" and (data.damageresolved or data.damage or 0) > 0 then
            self:OnDaggerHit(data.target,data.weapon)
        end
    end)
end)
-- 0.13.0: forca em 3 faixas conforme a fome. Acima de 75%: maxima (e fome 25% mais rapida);
-- de 30% a 75%: media; abaixo de 30%: base. Vale para todas as armas (damagemultiplier).
function BlinkPower:UpdateStrength()
    local hunger = self.inst.components.hunger
    if hunger == nil or self.inst.components.combat == nil then return end
    local pct = hunger:GetPercent()
    local tier = (pct > 0.75 and 2) or (pct >= 0.30 and 1) or 0
    if tier == self.might then return end
    self.might = tier
    local mult = TUNING.BLINK.strength_tiers[tier+1]
    self.inst.components.combat.damagemultiplier = mult
    if tier == 2 then hunger.burnratemodifiers:SetModifier(self.inst,TUNING.BLINK.full_hunger_rate,"blink_strength")
    else hunger.burnratemodifiers:RemoveModifier(self.inst,"blink_strength") end
    if self.inst._blink_might ~= nil then self.inst._blink_might:set(tier) end
end
-- 0.13.0: agua. Acima de 15% de umidade: faiscas e dano leve (metade do WX-78); a partir de 50%
-- o dash e o choque em cadeia ficam desligados (curto-circuito).
function BlinkPower:WetPercent()
    local m = self.inst.components.moisture
    if m == nil or (m.IsForceDry ~= nil and m:IsForceDry()) then return 0 end
    return m:GetMoisturePercent() or 0
end
function BlinkPower:IsShorted()
    return TUNING.BLINK.wet_weakness and self:WetPercent() >= 0.5
end
function BlinkPower:WetTick()
    local inst = self.inst
    if not TUNING.BLINK.wet_weakness or inst:HasTag("playerghost") or inst.components.health == nil
        or inst.components.health:IsDead() then self.wet_steps = 0 return end
    local pct = self:WetPercent()
    if pct <= 0.15 then self.wet_steps = 0 return end
    self.wet_steps = self.wet_steps + 1
    local x,y,z = inst.Transform:GetWorldPosition()
    local fx = SpawnPrefab("sparks")
    if fx ~= nil then fx.Transform:SetPosition(x,y+1+math.random()*1.5,z) end
    if self.wet_steps >= 5 then
        local t = (pct-0.15)/0.85
        local dps = TUNING.BLINK.wet_dps_min + (TUNING.BLINK.wet_dps_max-TUNING.BLINK.wet_dps_min)*t
        inst.components.health:DoDelta(-dps*self.wet_steps,false,"water")
        self.wet_steps = 0
        local big = SpawnPrefab("wx78_big_spark")
        if big ~= nil and big.AlignToTarget ~= nil and inst.entity:IsVisible() then big:AlignToTarget(inst) end
        inst:PushEvent("wx78_spark")
    end
end
-- Pedra do Impeto equipada no corpo e com usos restantes; nil caso contrario.
function BlinkPower:GetImpetusStone()
    local inventory = self.inst.components.inventory
    local stone = inventory ~= nil and EQUIPSLOTS.BODY ~= nil and inventory:GetEquippedItem(EQUIPSLOTS.BODY) or nil
    if stone ~= nil and stone.prefab == "blink_impeto" and stone:IsValid()
        and stone.components.finiteuses ~= nil and stone.components.finiteuses:GetUses() > 0 then
        return stone
    end
    return nil
end
function BlinkPower:Sync()
    self.inst._blink_cooldown:set(math.ceil(math.max(0,self.ready_at-GetTime())))
    self.inst._blink_hits:set(self.hits)
    if self.inst._blink_wet ~= nil then self.inst._blink_wet:set(self:IsShorted()) end
    if self.inst._blink_stone ~= nil then
        local stone = self:GetImpetusStone()
        self.inst._blink_stone:set(stone ~= nil and math.min(255,math.ceil(stone.components.finiteuses:GetUses())) or 0)
    end
end
function BlinkPower:OnSave()
    return {remaining=math.max(0,self.ready_at-GetTime()),hits=self.hits}
end
function BlinkPower:OnLoad(data)
    if data then
        self.ready_at = GetTime()+math.min(TUNING.BLINK.cooldown,math.max(0,tonumber(data.remaining) or 0))
        self.hits = math.floor(math.max(0,tonumber(data.hits) or 0))%5
    end
    self:Sync()
end
function BlinkPower:OnDaggerHit(target,weapon)
    if target == nil or target.components.combat == nil or target:HasTag("player")
        or target:HasTag("structure") or target:HasTag("wall") then return end
    if self:IsShorted() then return end      -- molhado: o choque nao carrega
    self.hits = self.hits+1
    if self.hits >= 5 then
        self.hits = 0
        Targets.chain(self.inst,target,TUNING.BLINK.shock_damage,weapon,TUNING.BLINK.chain_jumps or 0)
    end
    self:Sync()
end
local function ClearPoint(inst,x,z)
    if not TheWorld.Map:IsPassableAtPoint(x,0,z) or TheWorld.Map:IsOceanAtPoint(x,0,z) then return false end
    -- Allow creatures along the path; stop for walls and solid structures.
    for _,obj in ipairs(TheSim:FindEntities(x,0,z,3,nil,{"INLIMBO","FX"})) do
        if obj ~= inst and obj.Physics ~= nil and (obj:HasTag("wall") or obj:HasTag("structure")) then
            local ox,_,oz = obj.Transform:GetWorldPosition()
            local radius = (obj.GetPhysicsRadius and obj:GetPhysicsRadius(0) or 0)+0.45
            if (ox-x)^2+(oz-z)^2 < radius*radius then return false end
        end
    end
    return true
end
-- Direction is read from the predicted local facing, position from the server.
function BlinkPower:DashForward(dx,dz)
    if not Geometry.finite(dx) or not Geometry.finite(dz) then return false end
    local length = math.sqrt(dx*dx+dz*dz)
    if not Geometry.finite(length) or length < 0.001 then return false end
    local x,_,z = self.inst.Transform:GetWorldPosition()
    return self:Dash(x+8*dx/length,z+8*dz/length)
end
function BlinkPower:Dash(tx,tz)
    local inst = self.inst
    local now = GetTime()
    if now-self.last_request < 0.15 then return false end
    self.last_request = now
    if not Geometry.finite(tx) or not Geometry.finite(tz) then return false end
    -- 0.13.0: a Runa sozinha tambem da o dash (com recarga normal); Runa + Dagger = sem recarga.
    local stone = self:GetImpetusStone()
    local weapon = inst.components.inventory:GetEquippedItem(EQUIPSLOTS.HANDS)
    local dagger = weapon ~= nil and weapon.prefab == "blink_dagger" and weapon or nil
    if dagger == nil and stone == nil then return false end
    if self:IsShorted() then return false end
    local free = stone ~= nil and dagger ~= nil
    if self.ready_at > now and not free then return false end
    if inst:HasTag("playerghost") or inst.components.health:IsDead()
        or inst.sg:HasStateTag("busy") or inst.sg:HasStateTag("dead")
        or (inst.components.rider and inst.components.rider:IsRiding()) then return false end
    local x,_,z = inst.Transform:GetWorldPosition()
    local ex,ez,distance = Geometry.destination(x,z,tx,tz,8)
    if ex == nil then return false end
    local sx,sz = x,z
    local steps = math.ceil(distance/0.25)
    for i=1,steps do
        local px,pz = x+(ex-x)*i/steps,z+(ez-z)*i/steps
        if not ClearPoint(inst,px,pz) then break end
        sx,sz = px,pz
    end
    if (sx-x)^2+(sz-z)^2 < 0.25 then return false end
    if not free then self.ready_at = now+TUNING.BLINK.cooldown end
    self:Sync()
    inst.components.locomotor:Stop()
    inst:ClearBufferedAction()
    inst:ForceFacePoint(sx,0,sz)
    -- Fast blink movement; damage is calculated along the complete validated segment.
    inst.Physics:Teleport(sx,0,sz)
    local length = math.sqrt((sx-x)^2+(sz-z)^2)
    for _,target in ipairs(TheSim:FindEntities((x+sx)/2,0,(z+sz)/2,length/2+3,{"_combat","_health"},{"INLIMBO","FX"})) do
        if Targets.is_enemy(inst,target) then
            local px,_,pz = target.Transform:GetWorldPosition()
            local radius = 0.8+(target.GetPhysicsRadius and target:GetPhysicsRadius(0) or 0)
            if Geometry.segment_distance_sq(px,pz,x,z,sx,sz) <= radius*radius then
                Targets.shock(inst,target,TUNING.BLINK.dash_damage,dagger)
            end
        end
    end
    for i=0,math.ceil(length) do
        local t = i/math.max(1,math.ceil(length))
        local fx = SpawnPrefab("electrichitsparks")
        if fx then fx.Transform:SetPosition(x+(sx-x)*t,0.2,z+(sz-z)*t) end
    end
    -- Dash concluido: consome 1 uso. Com a Pedra do Impeto equipada, o uso sai da Pedra
    -- (a Dagger nao gasta); sem ela, sai da Dagger. No ultimo uso o item se quebra apos o dash.
    -- A recarga normal ja foi iniciada acima, entao retirar a pedra nao libera dash gratuito.
    if stone ~= nil and stone:IsValid() and stone.components.finiteuses ~= nil then
        stone.components.finiteuses:Use(1)
    elseif dagger ~= nil and dagger:IsValid() and dagger.components ~= nil and dagger.components.finiteuses ~= nil then
        dagger.components.finiteuses:Use(1)
    end
    self:Sync()
    return true
end
return BlinkPower
