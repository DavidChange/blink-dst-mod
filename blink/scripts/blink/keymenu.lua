-- Local preference: never sent to the server or shared with other players.
local Binding = require("blink/keybind")
local GG = nil
local function U()
    local S = GG ~= nil and GG.STRINGS or nil
    return (S ~= nil and S.BLINK_UI) or require("blink/lang").en
end
return function(G, dash)
    GG = G
    local names = Binding.names(G)
    local current = G.KEY_G
    local storage = "blink_personal_dash_key_v1"
    local changed = false
    local menu = nil
    local candidate = current
    local saving = false
    local api = {}
    function api:GetLabel() return Binding.label(current,names,G) end
    G.TheSim:GetPersistentString(storage,function(success,value)
        local key = success and Binding.parse(value,names,G) or nil
        if key ~= nil and not changed then current=key end
    end)
    local function close()
        if menu ~= nil then
            local old=menu
            menu=nil
            G.TheFrontEnd:PopScreen(old)
        end
    end
    local function body(message)
        if menu ~= nil then
            menu.dialog.body:SetString(string.format(U().menu_body, Binding.label(candidate,names,G))..(message or ""))
        end
    end
    local function open()
        local p=G.ThePlayer
        if p == nil or p.prefab ~= "blink" or p.HUD == nil
            or G.TheFrontEnd:GetActiveScreen() ~= p.HUD or p.HUD:HasInputFocus() then return end
        candidate=current
        saving=false
        local Popup=G.require("screens/redux/popupdialog")
        menu=Popup(U().menu_title,"",{
            {text=U().menu_save,cb=function()
                if saving then return end
                saving=true
                changed=true
                local selected=candidate
                body(U().menu_saving)
                G.TheSim:SetPersistentString(storage,tostring(selected),false,function(success)
                    saving=false
                    if success then current=selected;close()
                    else body(U().menu_fail) end
                end)
            end},
            {text=U().menu_default,cb=function() if not saving then candidate=G.KEY_G;body() end end},
            {text=U().menu_cancel,cb=function() if not saving then close() end end},
        },200,"bigger")
        -- Do not let Space/Enter/arrow bindings activate dialog actions while choosing a key.
        local original_control=menu.OnControl
        menu.OnControl=function(self,control,down)
            if G.TheFrontEnd.isprimary then return original_control(self,control,down) end
            if control == G.CONTROL_CANCEL and not down and not saving then close() end
            return true
        end
        G.TheFrontEnd:PushScreen(menu)
        body()
    end
    G.TheInput:AddKeyHandler(function(key,down)
        if not down then return end
        if menu ~= nil and G.TheFrontEnd:GetActiveScreen() == menu then
            if key == G.KEY_ESCAPE then if not saving then close() end
            elseif key == G.KEY_F6 then return
            elseif not saving and names[key] ~= nil then candidate=key;body()
            elseif not saving then body(U().menu_badkey) end
            return
        end
        if key == G.KEY_F6 then open()
        elseif key == current then dash() end
    end)
    G.TheInput:AddMouseButtonHandler(function(button,down)
        if not down then return end
        local binding=Binding.mouse_id(button,G)
        if binding == nil then return end
        if menu ~= nil and G.TheFrontEnd:GetActiveScreen() == menu then
            if not saving then candidate=binding;body() end
            return
        end
        -- UI interaction must not activate the dash (inventory, menus, map).
        local p=G.ThePlayer
        if binding == current and p ~= nil and p.HUD ~= nil
            and G.TheFrontEnd:GetActiveScreen() == p.HUD
            and G.TheInput:GetHUDEntityUnderMouse() == nil then dash() end
    end)
    return api
end
