local checks=0
local function ok(value,message) assert(value,message);checks=checks+1 end
local mathlib=require('blink/math')
local x,z,d=mathlib.destination(0,0,100,0,8)
ok(x==8 and z==0 and d==8,'range clamp')
ok(mathlib.destination(0,0,0,0,8)==nil,'zero-length request')
ok(mathlib.destination(0,0,0/0,0,8)==nil,'NaN rejected')
ok(mathlib.destination(0,0,math.huge,0,8)==nil,'infinity rejected')
ok(mathlib.destination(0,0,'bad',0,8)==nil,'non-number rejected')
ok(mathlib.segment_distance_sq(4,1,0,0,8,0)==1,'segment perpendicular distance')
ok(mathlib.segment_distance_sq(10,0,0,0,8,0)==4,'segment endpoint distance')
local now=100
GetTime=function()return now end
Class=function(constructor)
 local cls={};cls.__index=cls
 return setmetatable(cls,{__call=function(_,...)local o=setmetatable({},cls);constructor(o,...);return o end})
end
local function entity(tags,x,z)
 local e={components={},tags=tags or {},x=x or 0,z=z or 0,events={}}
 function e:IsValid()return true end
 function e:HasTag(t)return self.tags[t] or false end
 function e:PushEvent(name,data)self.pushed=self.pushed or {};table.insert(self.pushed,{name,data})end
 e.Transform={GetWorldPosition=function()return e.x,0,e.z end}
 e.GetPhysicsRadius=function()return 0 end
 e.components.health={IsDead=function()return false end}
 e.components.combat={GetAttacked=function(_,p,damage,weapon,stimuli)
  e.total=(e.total or 0)+damage;e.hits=(e.hits or 0)+1
  if p.events.onhitother then p.events.onhitother(p,{target=e,weapon=weapon,damage=damage,stimuli=stimuli})end
 end}
 return e
end
local p=entity({player=true})
p.sg={HasStateTag=function()return false end}
p.Physics={Teleport=function(_,x,y,z)p.x=x;p.z=z end}
p.ClearBufferedAction=function()end;p.ForceFacePoint=function()end
p.components.locomotor={Stop=function()end}
p.components.combat.IsAlly=function(_,t)return t.tags.ally end
p.components.combat.CanTarget=function()return true end
local dagger={prefab='blink_dagger',IsValid=function()return true end}
EQUIPSLOTS={HANDS='hands'}
p.components.inventory={GetEquippedItem=function()return dagger end}
p.DoPeriodicTask=function()end
p.DoTaskInTime=function(_,t,fn)fn()end
TheSim={FindEntities=function()return {} end}
p.ListenForEvent=function(_,name,fn)p.events[name]=fn end
local function net()return {set=function(self,n)self.current=n end}end
p._blink_cooldown=net();p._blink_hits=net()
TUNING={BLINK={cooldown=10,dash_damage=100,shock_damage=75,chain_jumps=3}}
SpawnPrefab=function()return {Transform={SetPosition=function()end}}end
local Targets=require('blink/targets')
local enemy=entity({hostile=true},4,0)
local neutral=entity({},3,0)
local ally=entity({hostile=true,ally=true},3,0)
local pet=entity({hostile=true},3,0);pet.components.follower={leader=p}
ok(Targets.is_enemy(p,enemy),'hostile target')
ok(Targets.is_enemy(p,neutral),'neutral creatures eligible')
ok(not Targets.is_enemy(p,p),'player protected')
ok(not Targets.is_enemy(p,ally),'ally protected')
ok(not Targets.is_enemy(p,pet),'player follower protected')
local cyclic=entity({hostile=true});cyclic.components.follower={leader=cyclic}
ok(Targets.is_enemy(p,cyclic),'cyclic leader graph terminates')
local structure=entity({hostile=true,structure=true})
ok(not Targets.is_enemy(p,structure),'structures protected')
local Power=require('components/blinkpower');local power=Power(p)
for i=1,4 do p.events.onhitother(p,{target=enemy,weapon=dagger,damage=100})end
ok(power.hits==4 and enemy.total==nil,'no shock on first four hits')
p.events.onhitother(p,{target=enemy,weapon=dagger,damage=100})
ok(power.hits==0 and enemy.total==75,'fifth hit shock, no recursive count or doubled damage')
ok(enemy.pushed and enemy.pushed[1][1]=='electrocute' and enemy.pushed[1][2].numforks==0 and enemy.pushed[1][2].stimuli=='electric','fifth hit uses native electrocute without native forks')
p.events.onhitother(p,{target=enemy,weapon=dagger,damage=0})
ok(power.hits==0,'zero-damage hits do not count')
p.events.onhitother(p,{target=enemy,weapon={prefab='spear'},damage=100})
ok(power.hits==0,'other weapon does not count')
TheWorld={Map={IsPassableAtPoint=function()return true end,IsOceanAtPoint=function()return false end}}
local offpath=entity({hostile=true},4,4)
TheSim={FindEntities=function(_,x,y,z,r,must)
 if must then return {enemy,pet,ally,neutral,p,structure,offpath} end
 return {}
end}
ok(power:Dash(100,0),'valid dash accepted')
ok(p.x==8 and p.z==0,'dash stops at range')
ok(enemy.total==175 and enemy.hits==2,'dash deals 100 exactly once')
ok(pet.total==nil and ally.total==nil and neutral.total==100 and offpath.total==nil,'dash hits neutral creatures and protects allies and out-of-path entities')
ok(power.hits==0,'dash does not count as dagger hit')
ok(not power:Dash(16,0),'immediate repeated RPC rejected')
now=101
ok(not power:Dash(16,0),'cooldown enforced')
power.hits=3
local saved=power:OnSave();ok(saved.remaining==9 and saved.hits==3,'remaining cooldown saved')
now=200;local restored=Power(p);restored:OnLoad(saved)
ok(restored.ready_at==209 and restored.hits==3,'cooldown and counter restored')
now=220
TheWorld.Map.IsOceanAtPoint=function()return true end
ok(not restored:Dash(16,0) and p.x==8,'ocean refused without moving')
ok(restored.ready_at==209,'invalid destination does not consume cooldown')
TheWorld.Map.IsOceanAtPoint=function()return false end
TheWorld.Map.IsPassableAtPoint=function(_,x)return x<10 end
now=221
ok(restored:Dash(16,0) and p.x<10,'cliff stops trajectory')
now=240;dagger=nil
ok(not restored:Dash(17,0),'requires equipped dagger')
now=241;dagger={prefab='blink_dagger',IsValid=function()return true end};p.tags.playerghost=true
ok(not restored:Dash(17,0),'ghost cannot dash')
print('PASS: '..checks..' geometry, targeting, cooldown, hit-counter and persistence checks (mocked engine).')

p.tags.playerghost=false;p.x=0;p.z=0;now=300
TheWorld.Map.IsPassableAtPoint=function()return true end
ok(power:DashForward(0,-1) and p.x==0 and p.z==-8,'forward direction uses server position')
now=310
ok(not power:DashForward(0,0),'zero direction rejected')
ok(not power:DashForward(0/0,1),'NaN direction rejected')
TUNING.BLINK.cooldown=5
ok(power:DashForward(1,0),'five second dash starts')
now=314.9;ok(not power:DashForward(1,0),'five second cooldown not expired')
now=315.2;ok(power:DashForward(1,0),'five second cooldown expires')
print('PASS: direction validation and five-second cooldown regression checks.')

-- Permanent mighty state survives load/drain without altering damage again.
local hero={components={temperature={},combat={damagemultiplier=2}},tags={}}
function hero:AddTag(t)self.tags[t]=true end
function hero:RemoveTag(t)self.tags[t]=nil end
local function sink()return setmetatable({},{__index=function()return function()end end})end
hero.components.workmultiplier=sink()
function hero:AddComponent(name)
 if name=='mightiness' then self.components[name]={max=100,state='normal',current=50,Pause=function(self)self.draining=false end}
 else self.components[name]=sink() end
end
ACTIONS={CHOP='chop',MINE='mine',HAMMER='hammer'}
TUNING.INSULATION_TINY=30
require('blink/permanent_mighty')(hero)
local mighty=hero.components.mightiness
ok(mighty.state=='mighty' and mighty.current==100 and not mighty.draining,'permanent mighty state')
mighty:DoDelta(-100);ok(mighty.current==100,'drain cannot remove permanent strength')
mighty:OnLoad({mightiness=0});ok(mighty.state=='mighty' and mighty.current==100,'load cannot weaken character')
ok(hero.tags.mightiness_mighty and not hero.tags.mightiness_normal,'client mighty tag matches server state')
ok(hero.components.combat.damagemultiplier==2,'mighty support does not multiply damage twice')
print('PASS: permanent strength load/drain/tag and damage regression checks.')

-- Exercise actual local key menu callbacks, asynchronous load/save and HUD gating.
local handler,mousehandler,loadcb,savecb,savedvalue
local calls=0
local hud={HasInputFocus=function()return false end}
local frontend={active=hud}
function frontend:GetActiveScreen()return self.active end
function frontend:PushScreen(screen)self.active=screen end
function frontend:PopScreen(screen)assert(self.active==screen);self.active=hud end
local sim={}
function sim:GetPersistentString(_,cb)loadcb=cb end
function sim:SetPersistentString(_,value,encode,cb)savedvalue=value;savecb=cb end
local input={AddKeyHandler=function(_,fn)handler=fn end, AddMouseButtonHandler=function(_,fn)mousehandler=fn end, GetHUDEntityUnderMouse=function()return nil end}
local env={MOUSEBUTTON_LEFT=1000,MOUSEBUTTON_RIGHT=1001,MOUSEBUTTON_MIDDLE=1002,MOUSEBUTTON_SCROLLUP=1003,MOUSEBUTTON_SCROLLDOWN=1004,KEY_G=103,KEY_F6=287,KEY_ESCAPE=27,CONTROL_CANCEL=99,TheSim=sim,TheInput=input,TheFrontEnd=frontend,ThePlayer={prefab='blink',HUD=hud}}
env.require=function(name)
 assert(name=='screens/redux/popupdialog')
 return function(title,body,buttons)
  return {buttons=buttons,dialog={body={SetString=function()end}},OnControl=function()return true end}
 end
end
local keys=require('blink/keymenu')(env,function()if frontend.active==hud then calls=calls+1 end end)
ok(keys:GetLabel()=='G','fresh install defaults to G')
handler(53,true);ok(calls==0,'old accidental 5 does not trigger dash')
handler(103,true);ok(calls==1,'G triggers dash')
handler(287,true);local screen=frontend.active
handler(118,true);ok(calls==1,'choosing key never dashes')
screen.buttons[1].cb();ok(savedvalue=='118','save writes local selected key')
loadcb(true,'98');savecb(true)
ok(keys:GetLabel()=='V','late load cannot replace user choice')
handler(103,true);ok(calls==1,'old key disabled immediately')
handler(118,true);ok(calls==2,'new key triggers dash')
handler(287,true);handler(98,true);frontend.active.buttons[3].cb()
ok(keys:GetLabel()=='V','cancel discards pending choice')
handler(287,true);handler(287,true);frontend.active.buttons[1].cb();savecb(false)
ok(frontend.active~=hud and keys:GetLabel()=='V','save failure leaves menu open and active binding unchanged')
frontend.active.buttons[3].cb()
local second=require('blink/keymenu')(env,function()end)
loadcb(true,'118');ok(second:GetLabel()=='V','saved preference restored next session')
local invalid=require('blink/keymenu')(env,function()end)
loadcb(true,'287');ok(invalid:GetLabel()=='G','menu hotkey cannot be assigned as dash')
print('PASS: personal key menu selection, cancel, persistence, failed save and old-key regression checks.')

local mousecalls=0
local mousekeys=require('blink/keymenu')(env,function()mousecalls=mousecalls+1 end)
loadcb(true,'118');ok(mousekeys:GetLabel()=='V','legacy keyboard preference survives update')
handler(287,true);mousehandler(1003,true)
mousehandler(1000,true);frontend.active.buttons[1].cb()
ok(savedvalue=='mouse:1003','save click does not overwrite scroll selection')
savecb(true)
ok(mousekeys:GetLabel()=='Scroll up','scroll label shown')
mousehandler(1003,false);ok(mousecalls==0,'release never triggers dash')
mousehandler(1004,true);ok(mousecalls==0,'opposite scroll direction ignored')
mousehandler(1003,true);ok(mousecalls==1,'selected scroll direction triggers dash')
input.GetHUDEntityUnderMouse=function()return {} end
mousehandler(1003,true);ok(mousecalls==1,'scroll over inventory does not dash')
input.GetHUDEntityUnderMouse=function()return nil end
handler(287,true);mousehandler(1005,true)
ok(mousecalls==1,'capturing mouse extra does not dash')
frontend.active.buttons[1].cb();savecb(true)
mousehandler(1003,true);ok(mousecalls==1,'previous scroll binding disabled')
mousehandler(1005,true);ok(mousecalls==2,'extra button triggers dash')
local restoredmouse=require('blink/keymenu')(env,function()end)
loadcb(true,'mouse:1005');ok(restoredmouse:GetLabel()=='Extra mouse button (1005)','extra mouse preference persists')
local bindings=require('blink/keybind')
ok(bindings.parse('mouse:1000',bindings.names(env),env)==nil,'left mouse cannot replace saved binding')
ok(bindings.parse('mouse:1001',bindings.names(env),env)==nil,'right mouse reserved')
ok(bindings.parse('mouse:garbage',bindings.names(env),env)==nil,'invalid mouse storage rejected')
ok(bindings.label('mouse:1002',bindings.names(env),env)=='Scroll click','middle button label')
print('PASS: mouse capture, scroll direction, UI protection, persistence and legacy binding checks.')

-- Pedra do Impeto: prefab real carregado com motor simulado + regras do dash.
local function sink()return setmetatable({},{__index=function()return function()end end})end
local said,removed=nil,0
EQUIPSLOTS.BODY='body'
TUNING.BLINK.stone_uses=30
TUNING.BLINK.stone_speed=1.1
STRINGS={BLINK_IMPETO_BROKEN='A Runa Eletrica se partiu.'}
Asset=function(...)return {...}end
Prefab=function(name,fn,assets,deps)return {name=name,fn=fn,assets=assets,deps=deps}end
MakeInventoryPhysics=function()end;MakeInventoryFloatable=function()end;MakeHauntableLaunch=function()end
TheWorld.ismastersim=true
CreateEntity=function()
 local e={components={},tags={},valid=true,entity=sink(),Transform=sink(),overrides={}}
 e.AnimState=setmetatable({},{__index=function(_,k)
  if k=='OverrideSymbol' then return function(_,sym,build,name)e.overrides[sym]=build..'/'..name end end
  return function()end end})
 function e:AddTag(t)self.tags[t]=true end
 function e:IsValid()return self.valid end
 function e:Remove()self.valid=false;removed=removed+1 end
 function e:AddComponent(name)
  local c
  if name=='finiteuses' then
   c={current=100,total=100}
   function c:SetMaxUses(n)self.total=n end
   function c:SetOnFinished(fn)self.onfinished=fn end
   function c:GetUses()return self.current end
   function c:SetUses(n)self.current=n;if self.current<=0 then self.current=0;if self.onfinished then self.onfinished(e)end end end
   function c:Use(n)self:SetUses(self.current-(n or 1))end
  elseif name=='equippable' then
   c={}
   function c:SetOnEquip(fn)self.onequip=fn end
   function c:SetOnUnequip(fn)self.onunequip=fn end
  else c={} end
  self.components[name]=c
 end
 return e
end
local def=dofile(package.path:match('^(.-)%?%.lua;')..'prefabs/blink_impeto.lua')
ok(def.name=='blink_impeto','stone prefab registered')
local function newstone()local s=def.fn();s.prefab='blink_impeto';return s end
local stone=newstone()
ok(stone.components.equippable.equipslot=='body','stone uses body slot')
ok(stone.components.equippable.walkspeedmult==1.1,'rune gives +10% walk speed while equipped')
ok(stone.components.finiteuses:GetUses()==30 and stone.components.finiteuses.total==30,'stone starts with 30 uses')
ok(stone.components.weapon==nil,'stone does not change weapon damage')
local owner=entity({player=true},0,0);owner.AnimState={OverrideSymbol=function()end,ClearOverrideSymbol=function()end}
stone.components.equippable.onequip(stone,owner)
ok(stone.overrides.swap_body==nil,'equip callback overrides owner, not item')

-- Jogador BLINK com inventario por slot.
local q=entity({player=true},0,0)
q.sg={HasStateTag=function()return false end}
q.Physics={Teleport=function(_,x,y,z)q.x=x;q.z=z end}
q.ClearBufferedAction=function()end;q.ForceFacePoint=function()end
q.components.locomotor={Stop=function()end}
q.components.combat.IsAlly=function(_,t)return t.tags.ally end
q.components.combat.CanTarget=function()return true end
q.components.talker={Say=function(_,s)said=s end}
local slots={hands={prefab='blink_dagger',IsValid=function()return true end},body=nil}
q.components.inventory={GetEquippedItem=function(_,slot)return slots[slot]end}
q.DoPeriodicTask=function()end
q.DoTaskInTime=function(_,t,fn)end
q.ListenForEvent=function(_,name,fn)q.events[name]=fn end
q._blink_cooldown=net();q._blink_hits=net();q._blink_stone=net()
TUNING.BLINK.cooldown=5
TheWorld.Map.IsPassableAtPoint=function()return true end
TheWorld.Map.IsOceanAtPoint=function()return false end
local foe=entity({hostile=true},4,0)
TheSim={FindEntities=function(_,x,y,z,r,must)if must then return {foe} end return {} end}
local qp=Power(q)
now=1000
local function reset()q.x=0;q.z=0;foe.x=4;foe.z=0 end
reset();ok(qp:DashForward(1,0),'normal dash without stone')
now=1001;reset();ok(not qp:DashForward(1,0),'cooldown blocks without stone')
stone.components.inventoryitem.owner=q
slots.body=stone;now=1001.2;reset()
ok(qp:DashForward(1,0),'rune + dagger skips cooldown')
ok(stone.components.finiteuses:GetUses()==29,'successful stone dash consumes one use')
ok(foe.total==200,'stone dash keeps damage at 100 per target')
ok(q.x==8 and q.z==0,'stone dash keeps range and direction')
ok(q._blink_stone.current==29,'HUD netvar shows remaining uses')
now=1001.25;reset()
ok(not qp:DashForward(1,0) and stone.components.finiteuses:GetUses()==29,'spam-protected request does not consume')
now=1001.5;reset()
TheWorld.Map.IsOceanAtPoint=function()return true end
ok(not qp:DashForward(1,0) and stone.components.finiteuses:GetUses()==29,'invalid terrain does not consume')
TheWorld.Map.IsOceanAtPoint=function()return false end
now=1002;reset();ok(not qp:DashForward(0,0) and stone.components.finiteuses:GetUses()==29,'zero direction does not consume')
now=1002.5;reset();slots.hands=nil
ok(not qp:DashForward(1,0) and stone.components.finiteuses:GetUses()==29,'rune alone respects the normal cooldown')
slots.hands={prefab='blink_dagger',IsValid=function()return true end}
now=1003;reset();q.tags.playerghost=true
ok(not qp:DashForward(1,0) and stone.components.finiteuses:GetUses()==29,'ghost cannot use stone')
q.tags.playerghost=false
now=1003.5;reset();q.sg.HasStateTag=function(_,t)return t=='busy'end
ok(not qp:DashForward(1,0) and stone.components.finiteuses:GetUses()==29,'busy state does not consume')
q.sg.HasStateTag=function()return false end
now=1004;reset();ok(qp:DashForward(1,0) and stone.components.finiteuses:GetUses()==28,'consecutive stone dashes without waiting')
ok(qp.ready_at==1005,'rune + dagger dash does not start a cooldown')
slots.body=nil;qp:Sync()
ok(q._blink_stone.current==0,'HUD clears stone when removed')
now=1004.3;reset();ok(not qp:DashForward(1,0),'removing stone restores cooldown (no bypass)')
slots.body=stone;now=1004.45;qp:Sync()
ok(stone.components.finiteuses:GetUses()==28,'re-equipping creates no free uses')
local other=newstone();other.components.finiteuses:SetUses(1)
other.components.inventoryitem.owner=q;slots.body=other
local beforeRemoved=removed
reset();ok(qp:DashForward(1,0),'last use still performs the dash')
ok(q.x==8,'last-use dash moved the player')
ok(other.components.finiteuses:GetUses()==0 and not other:IsValid() and removed==beforeRemoved+1,'stone breaks after last use')
ok(said=='A Runa Eletrica se partiu.','break message shown')
ok(q._blink_stone.current==0,'HUD shows no stone after breaking')
now=1004.7;reset();ok(not qp:DashForward(1,0),'broken stone no longer skips cooldown')
local fake={prefab='blueamulet',IsValid=function()return true end,components={finiteuses={GetUses=function()return 10 end}}}
slots.body=fake;now=1004.9;reset();ok(not qp:DashForward(1,0),'other amulets do not skip cooldown')
local saved=qp:OnSave();ok(saved.remaining>0 and saved.remaining<=5,'cooldown save unchanged by stone')

-- 0.13.0: Runa sozinha da o dash com recarga normal; molhado desliga dash/choque; forca pela fome.
local solo=newstone();solo.components.inventoryitem.owner=q;slots.body=solo;slots.hands=nil
now=1010;reset();ok(qp:DashForward(1,0) and solo.components.finiteuses:GetUses()==29,'rune alone grants a dash and spends a use')
ok(qp.ready_at==1010+TUNING.BLINK.cooldown,'rune-only dash starts the normal cooldown')
now=1011;reset();ok(not qp:DashForward(1,0),'rune-only dash waits for cooldown')
slots.hands={prefab='blink_dagger',IsValid=function()return true end}
TUNING.BLINK.wet_weakness=true;TUNING.BLINK.wet_dps_min=0.3;TUNING.BLINK.wet_dps_max=0.9
local wet=0.6;q.components.moisture={GetMoisturePercent=function()return wet end,IsForceDry=function()return false end}
now=1020;reset();ok(not qp:DashForward(1,0) and solo.components.finiteuses:GetUses()==29,'soaked: no dash, no use spent')
qp.hits=0;q.events.onhitother(q,{target=foe,weapon=slots.hands,damage=50});ok(qp.hits==0,'soaked: dagger hits do not charge the shock')
wet=0.3;now=1021;reset();ok(qp:DashForward(1,0),'damp (below 50%) still dashes')
local hp=125;q.components.health.DoDelta=function(_,d)hp=hp+d end
q.entity={IsVisible=function()return true end};q.PushEvent=function(self,n)self.lastevent=n end
for i=1,5 do qp:WetTick() end
ok(hp<125 and hp>122 and q.lastevent=='wx78_spark','wet: periodic sparks and light damage (half of WX-78)')
wet=0.1;hp=125;for i=1,6 do qp:WetTick() end;ok(hp==125,'dry enough: no damage')
TUNING.BLINK.strength_tiers={1.25,1.5,2};TUNING.BLINK.full_hunger_rate=1.25
local mods={};local hpct=0.9
q.components.hunger={GetPercent=function()return hpct end,burnratemodifiers={SetModifier=function(_,src,v,k)mods[k]=v end,RemoveModifier=function(_,src,k)mods[k]=nil end}}
q._blink_might=net();qp.might=-1
qp:UpdateStrength();ok(q.components.combat.damagemultiplier==2 and mods.blink_strength==1.25,'well fed: 2x and faster hunger')
hpct=0.5;qp:UpdateStrength();ok(q.components.combat.damagemultiplier==1.5 and mods.blink_strength==nil,'mid hunger: 1.5x')
hpct=0.2;qp:UpdateStrength();ok(q.components.combat.damagemultiplier==1.25 and q._blink_might.current==0,'low hunger: 1.25x')
print('PASS: Runa Eletrica: slot, 30 usos, dash sozinha com recarga, sem recarga com a Dagger, molhado, forca pela fome, consumo so em dash valido, quebra, recarga ao retirar, HUD e dano inalterado.')

-- Dagger: arte propria quando anim/blink_dagger.zip existe; lanca provisoria quando nao existe.
local function dagger_entity()
 local e={components={},tags={},anim={},sounds={},valid=true,entity=sink(),Transform=sink()}
 e.SoundEmitter={PlaySound=function(_,path,name)e.sounds[name]=path end,KillSound=function(_,name)e.sounds[name]=nil end}
 e.AnimState=setmetatable({},{__index=function(_,k)return function(_,...)e.anim[k]={...}end end})
 function e:AddTag(t)self.tags[t]=true end
 function e:AddComponent(name)
  local c=setmetatable({},{__index=function(t,k)return function(self,...)rawset(t,'_'..k,{...})end end})
  self.components[name]=c
 end
 return e
end
CreateEntity=dagger_entity
TUNING.BLINK.dagger_damage=50
TUNING.BLINK.dagger_uses=150
local daggerpath=package.path:match('^(.-)%?%.lua;')..'prefabs/blink_dagger.lua'
for _,mode in ipairs({{true,'blink_dagger','blink_dagger','swap_blink_dagger'},{false,'blink_dagger','blink_dagger','swap_blink_dagger'}}) do
 local resolved={}
 softresolvefilepath=function(p)resolved[#resolved+1]=p;return mode[1] and p or nil end
 local d=dofile(daggerpath)
 local item=d.fn()
 local label=mode[1] and 'custom art' or 'fallback'
 ok(#resolved==0,'dagger visual never depends on a runtime file check ('..label..')')
 ok(item.anim.SetBank[1]==mode[2] and item.anim.SetBuild[1]==mode[3] and item.anim.PlayAnimation[1]=='idle','dagger ground visual ('..label..')')
 ok(item.anim.SetMultColour==nil,'no placeholder tint ('..label..')')
 local inv=item.components.inventoryitem
 ok(inv.imagename=='blink_dagger' and inv.atlasname=='images/inventoryimages/blink_dagger.xml','own inventory icon ('..label..')')
 ok(item.components.weapon._SetDamage[1]==50 and item.components.finiteuses~=nil and item.components.finiteuses._SetMaxUses[1]==150,'configured damage and 150 uses ('..label..')')
 local owner={AnimState=setmetatable({},{__index=function(t,k)return function(_,...)rawset(t,'_'..k,{...})end end})}
 item.components.equippable._SetOnEquip[1](item,owner)
 ok(owner.AnimState._OverrideSymbol[1]=='swap_object' and owner.AnimState._OverrideSymbol[2]==mode[3] and owner.AnimState._OverrideSymbol[3]==mode[4],'held visual ('..label..')')
 local hasanim=false
 for _,a in ipairs(d.assets)do if a[2]=='anim/blink_dagger.zip' then hasanim=true end end
 ok(hasanim,'compiled anim always listed ('..label..')')
end
local stone2=def.fn()
ok(stone2.anim.SetBank[1]=='amulets' and stone2.anim.SetBuild[1]=='blink_impeto' and stone2.anim.PlayAnimation[1]=='blueamulet' and stone2.anim.SetMultColour==nil,'stone ground uses own build on native bank')
local sowner={AnimState=setmetatable({},{__index=function(t,k)return function(_,...)rawset(t,'_'..k,{...})end end})}
stone2.components.equippable._SetOnEquip[1](stone2,sowner)
ok(sowner.AnimState._OverrideSymbol[1]=='swap_body' and sowner.AnimState._OverrideSymbol[2]=='blink_impeto' and sowner.AnimState._OverrideSymbol[3]=='swap_blink_impeto','stone body visual uses own build')
ok(stone2.components.inventoryitem.imagename=='blink_impeto' and stone2.components.inventoryitem.atlasname=='images/inventoryimages/blink_impeto.xml','stone has own inventory icon')
print('PASS: Dagger sempre com arte propria (mesmo resultado em servidor e cliente), icones proprios.')

-- Choque em cadeia do quinto acerto (salto para o inimigo elegivel mais proximo).
local T=require('blink/targets')
local arcs=0
SpawnPrefab=function(name)if name=='shock_arc_fx' then arcs=arcs+1 end return {Transform={SetPosition=function()end}} end
local tasks={}
p.DoTaskInTime=function(_,t,fn)ok(t==T.CHAIN_DELAY,'hops are delayed like the native fork');table.insert(tasks,fn)end
local function run() while #tasks>0 do table.remove(tasks,1)() end end
local function at(tags,x,z)local e=entity(tags,x,z);return e end
p.x,p.z=0,0
local first=at({hostile=true},2,0)
local near=at({hostile=true},5,0)        -- 3 do primeiro
local nearer=at({},4,0)                  -- 2 do primeiro: neutro elegivel, vem antes
local far=at({hostile=true},30,0)        -- fora do alcance de qualquer salto
local friend=at({hostile=true,ally=true},3,0)
local follower=at({hostile=true},3,1);follower.components.follower={leader=p}
local other=at({player=true},3,-1)
local wall=at({structure=true},3,0.5)
local all={first,near,nearer,far,friend,follower,other,wall}
TheSim={FindEntities=function()return all end}
T.chain(p,first,75,dagger,3)
ok(first.total==75,'first target shocked synchronously')
ok(#tasks==1 and nearer.total==nil,'next hop waits for the delay')
run()
ok(nearer.total==75 and near.total==75,'chain hops to nearest eligible enemies with full damage')
ok(far.total==nil,'out-of-range creature not reached')
ok(friend.total==nil and follower.total==nil and other.total==nil and wall.total==nil,'chain respects allies, followers, players and structures')
ok(first.total==75 and nearer.hits==1 and near.hits==1,'each creature hit once per chain')
ok(arcs==2,'one native arc per hop')
ok(nearer.pushed[1][1]=='electrocute' and nearer.pushed[1][2].numforks==0,'hopped targets stunned by native electrocute')
-- limite de saltos
local line={}
for i=1,8 do line[i]=at({hostile=true},i*3,0) end
TheSim={FindEntities=function()return line end}
T.chain(p,line[1],75,dagger,3);run()
local n=0 for i=1,8 do if line[i].total then n=n+1 end end
ok(n==4,'first target plus exactly 3 hops')
T.chain(p,at({hostile=true},0,0),75,dagger,0);run()
ok(#tasks==0,'zero hops: only the struck target')
-- alvo morto pelo quinto golpe: o choque ainda se espalha a partir dele
local dead=at({hostile=true},50,0);dead.components.health={IsDead=function()return true end}
local nb=at({hostile=true},52,0)
TheSim={FindEntities=function()return {dead,nb} end}
T.chain(p,dead,75,dagger,3);run()
ok(dead.total==nil and nb.total==75,'chain spreads even when the fifth hit killed the target')
print('PASS: choque em cadeia: atraso, mais proximo primeiro, alcance, protecoes, 1x por criatura, limite de saltos, atordoamento nativo.')

-- Luz da Dagger equipada.
local spawned={}
SpawnPrefab=function(name)local fx={name=name,entity={SetParent=function(self,pe)self.parent=pe end},removed=false};function fx:Remove()self.removed=true end;table.insert(spawned,fx);return fx end
CreateEntity=dagger_entity
local L=dofile(daggerpath)
local lit=L.fn()
local holder={entity={},AnimState=setmetatable({},{__index=function()return function()end end})}
TUNING.BLINK.dagger_light=true
lit.components.equippable._SetOnEquip[1](lit,holder)
ok(#spawned==1 and spawned[1].name=='blink_dagger_light' and spawned[1].entity.parent==holder.entity,'light follows the owner while equipped')
lit.components.equippable._SetOnUnequip[1](lit,holder)
ok(spawned[1].removed and lit._light==nil,'light removed on unequip')
lit.components.equippable._SetOnEquip[1](lit,holder);lit.OnRemoveEntity(lit)
ok(spawned[2].removed,'light removed with the item')
TUNING.BLINK.dagger_light=false
lit.components.equippable._SetOnEquip[1](lit,holder)
ok(#spawned==2,'light can be disabled in mod settings')
print('PASS: luz da Dagger: acende ao equipar, apaga ao desequipar/remover, opcao desligar.')

-- Desgaste da Dagger.
local wd=L.fn();wd.prefab='blink_dagger'
local fu=wd.components.finiteuses
ok(fu._SetMaxUses[1]==150 and fu._SetUses[1]==150,'dagger starts with 150 uses')
local onfin=fu._SetOnFinished[1]
local ranout,removed2=nil,false
local wearer={PushEvent=function(_,name,data)if name=='itemranout' then ranout=data end end}
wd.components.inventoryitem.owner=wearer
wd.components.equippable.equipslot='hands';wd.components.equippable.IsEquipped=function()return true end
wd.Remove=function()removed2=true end
onfin(wd)
ok(removed2 and ranout and ranout.prefab=='blink_dagger' and ranout.equipslot=='hands' and ranout.announce=='ANNOUNCE_BLINK_DAGGER_BROKE','broken dagger removed, announced and auto-replaced like vanilla')
local wd2=L.fn();local r2=false;wd2.Remove=function()r2=true end
wd2.components.equippable.IsEquipped=function()return false end
wd2.components.finiteuses._SetOnFinished[1](wd2)
ok(r2,'unequipped dagger still breaks')
TUNING.BLINK.dagger_uses=0
ok(L.fn().components.finiteuses==nil,'no-wear option keeps old behaviour')
TUNING.BLINK.dagger_uses=150
-- Arma removida antes de um salto atrasado nao e repassada ao combate.
local gone={prefab='blink_dagger',IsValid=function()return false end}
local victim=entity({hostile=true},0,0);local got='unset'
victim.components.combat.GetAttacked=function(_,a,dmg,w)got=w end
SpawnPrefab=function()return {Transform={SetPosition=function()end}} end
T.shock(p,victim,75,gone)
ok(got==nil,'removed weapon not passed to delayed shock')
print('PASS: desgaste da Dagger: 150 usos, quebra com aviso e troca automatica, opcao sem desgaste, arma quebrada segura no choque.')

-- Dash gasta 1 uso: da Dagger sem a Pedra; da Pedra (e nao da Dagger) com ela equipada.
local function usesmock(n)local f={current=n};function f:GetUses()return self.current end;function f:Use(k)self.current=self.current-(k or 1);if self.current<=0 then self.current=0;if self.onfinished then self.onfinished() end end end;return f end
local wdag={prefab='blink_dagger',valid=true,components={finiteuses=usesmock(10)}};function wdag:IsValid()return self.valid end
slots.hands=wdag;slots.body=nil
TheWorld.Map.IsOceanAtPoint=function()return false end
TheWorld.Map.IsPassableAtPoint=function()return true end
TheSim={FindEntities=function()return {} end}
now=2000;q.x,q.z=0,0;qp.ready_at=0
ok(qp:DashForward(1,0) and wdag.components.finiteuses.current==9,'dash without stone spends 1 dagger use')
now=2010;q.x,q.z=0,0
TheWorld.Map.IsOceanAtPoint=function()return true end
ok(not qp:DashForward(1,0) and wdag.components.finiteuses.current==9,'refused dash spends no dagger use')
TheWorld.Map.IsOceanAtPoint=function()return false end
local st3={prefab='blink_impeto',IsValid=function()return true end,components={finiteuses=usesmock(50)}};slots.body=st3
now=2011;q.x,q.z=0,0
ok(qp:DashForward(1,0) and st3.components.finiteuses:GetUses()==49 and wdag.components.finiteuses.current==9,'with stone: stone pays the use, dagger does not')
slots.body=nil
wdag.components.finiteuses.current=1;wdag.components.finiteuses.onfinished=function()wdag.valid=false end
now=2030;q.x,q.z=0,0
ok(qp:DashForward(1,0) and q.x==8 and not wdag.valid,'last dagger use: dash happens, then dagger breaks')
print('PASS: dash gasta 1 uso da Dagger, ou da Pedra quando equipada; recusado nao gasta; ultimo uso quebra apos o dash.')

-- Zumbido ao equipar e Dagger visivel ao boiar.
local floatargs
MakeInventoryFloatable=function(inst,...)floatargs={...}end
local hum=L.fn()
local ownerh={entity={},AnimState=setmetatable({},{__index=function()return function()end end})}
TUNING.BLINK.dagger_light=false
hum.components.equippable._SetOnEquip[1](hum,ownerh)
ok(next(hum.sounds)==nil,'0.6.11: no sound while holding the dagger')
hum.components.equippable._SetOnUnequip[1](hum,ownerh)
local sd=floatargs[5]
ok(floatargs[4]==true and floatargs[5]==0,'floats with bank swap, no extra offset')
ok(floatargs[6].sym_build=='blink_dagger_float' and floatargs[6].sym_name==nil and floatargs[6].bank=='blink_dagger' and floatargs[6].anim=='idle','floating uses our hand art and returns to our ground anim')

-- 0.11.0: idiomas
local lang=require('blink/lang')
for k,v in pairs(lang.en) do ok(lang.pt[k]~=nil and type(lang.pt[k])==type(v),'pt has key '..k) end
for k,v in pairs(lang.pt) do ok(lang.en[k]~=nil,'en has key '..k) end
ok(lang.pick({},'pt')=='pt' and lang.pick({},'en')=='en','language option forces')
ok(lang.pick({LOC={GetLocaleCode=function() return 'pt' end}},'auto')=='pt','auto follows Portuguese game')
ok(lang.pick({LOC={GetLocaleCode=function() return 'en' end}},'auto')=='en','auto defaults to English')
local en=require('speech_blink_en'); local pt=require('speech_blink_pt')
local function same(a,b,path) for k,v in pairs(a) do ok(b[k]~=nil and type(b[k])==type(v),'speech key '..path..k); if type(v)=='table' then same(v,b[k],path..k..'.') end end end
same(en,pt,''); same(pt,en,'')
ok(type(en.DESCRIBE.BLINK_DAGGER)=='string' and type(en.ANNOUNCE_EAT)=='table','speech shape')
for fmt,args in pairs({hud_ready={'G'},hud_cd={3},hud_line={'x',2,'2'},hud_rune={10,50},menu_body={'G'},mouse_extra={1005}}) do
  ok(pcall(string.format,lang.en[fmt],table.unpack(args)) and pcall(string.format,lang.pt[fmt],table.unpack(args)),'format ok '..fmt) end
print('PASS: Dagger silenciosa ao segurar; visivel na agua (peca propria em build separado).')
