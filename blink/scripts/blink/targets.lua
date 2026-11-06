local M = {}
function M.is_enemy(player,target)
    if target == nil or target == player or not target:IsValid() then return false end
    for _,tag in ipairs({"player","playerghost","companion","structure","wall","INLIMBO","notarget"}) do
        if target:HasTag(tag) then return false end
    end
    local c = target.components
    if c == nil or c.health == nil or c.health:IsDead() or c.combat == nil then return false end
    -- Protect followers of ANY player, including chained follower relationships.
    local leader = c.follower and c.follower.leader
    local seen = {}
    while leader ~= nil and not seen[leader] do
        seen[leader] = true
        if leader:HasTag("player") then return false end
        leader = leader.components and leader.components.follower and leader.components.follower.leader
    end
    if player.components.combat:IsAlly(target) then return false end
    -- Hit every eligible creature, including neutral wildlife along the path.
    return player.components.combat:CanTarget(target)
end
function M.shock(player,target,damage,weapon)
    if not M.is_enemy(player,target) then return false end
    -- A Dagger pode ter quebrado neste golpe (ou antes de um salto atrasado): nao repassar arma removida.
    if weapon ~= nil and weapon.IsValid ~= nil and not weapon:IsValid() then weapon = nil end
    -- Direct combat damage bypasses the attacker's strength multiplier, NOT armor.
    -- No world lightning entity: it would ignite objects and harm neutral entities.
    target.components.combat:GetAttacked(player,damage,weapon,"electric")
    local fx = SpawnPrefab("electrichitsparks")
    if fx ~= nil then fx.Transform:SetPosition(target.Transform:GetWorldPosition()) end
    return true
end
-- Atordoamento + piscar eletrico nativos (sistema "electrocute" do jogo). numforks=0: sem os
-- saltos nativos, que so atordoam; os saltos com dano sao feitos por M.chain, com as protecoes acima.
local function electrocute(player,target,weapon)
    if target:IsValid() and target.components.health ~= nil and not target.components.health:IsDead() then
        target:PushEvent("electrocute",{attacker=player,stimuli="electric",weapon=weapon,numforks=0})
    end
end
M.electrocute = electrocute
function M.arc(x,z,tx,tz)
    local fx = SpawnPrefab("shock_arc_fx")
    if fx ~= nil then
        fx.Transform:SetPosition((x+tx)/2,0,(z+tz)/2)
        if fx.ForceFacePoint ~= nil then fx:ForceFacePoint(tx,0,tz) end
    end
end
M.CHAIN_RANGE = 4
M.CHAIN_DELAY = 0.2
-- Choque do quinto acerto: atinge o alvo e salta para o inimigo elegivel mais proximo,
-- ate `jumps` vezes. Cada criatura uma vez por choque; mesmo dano em cada salto.
function M.chain(player,first,damage,weapon,jumps)
    local hit = {[first]=true}
    if M.shock(player,first,damage,weapon) then electrocute(player,first,weapon) end
    if (jumps or 0) <= 0 or not first:IsValid() then return end
    local function hop(fromx,fromz,remaining)
        if remaining <= 0 or not player:IsValid() then return end
        local best,bestd
        for _,v in ipairs(TheSim:FindEntities(fromx,0,fromz,M.CHAIN_RANGE+3,{"_combat","_health"},
            {"INLIMBO","FX","electricdamageimmune","player","playerghost"})) do
            if not hit[v] and M.is_enemy(player,v) then
                local vx,_,vz = v.Transform:GetWorldPosition()
                local r = M.CHAIN_RANGE+(v.GetPhysicsRadius ~= nil and v:GetPhysicsRadius(0) or 0)
                local d = (vx-fromx)^2+(vz-fromz)^2
                if d <= r*r and (bestd == nil or d < bestd) then best,bestd = v,d end
            end
        end
        if best == nil then return end
        hit[best] = true
        local bx,_,bz = best.Transform:GetWorldPosition()
        M.arc(fromx,fromz,bx,bz)
        if M.shock(player,best,damage,weapon) then electrocute(player,best,weapon) end
        player:DoTaskInTime(M.CHAIN_DELAY,function() hop(bx,bz,remaining-1) end)
    end
    local x,_,z = first.Transform:GetWorldPosition()
    player:DoTaskInTime(M.CHAIN_DELAY,function() hop(x,z,jumps) end)
end
return M
