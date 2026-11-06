local M = {}
function M.names(G)
    local names = {}
    for code=97,122 do names[code]=string.upper(string.char(code)) end
    for code=48,57 do names[code]=string.char(code) end
    for n=1,12 do
        local code=G["KEY_F"..n]
        if code ~= nil and n ~= 6 then names[code]="F"..n end
    end
    for _,name in ipairs({"SPACE","TAB","LSHIFT","RSHIFT","LCTRL","RCTRL","LALT","RALT","UP","DOWN","LEFT","RIGHT","INSERT","DELETE","HOME","END","PAGEUP","PAGEDOWN"}) do
        if G["KEY_"..name] ~= nil then names[G["KEY_"..name]]=name end
    end
    names[G.KEY_F6]=nil
    return names
end
function M.mouse_id(button,G)
    if type(button) ~= "number" or button ~= math.floor(button) or button < 1000 or button > 65535 then return nil end
    if button == G.MOUSEBUTTON_LEFT or button == G.MOUSEBUTTON_RIGHT then return nil end
    return "mouse:"..button
end
function M.label(binding,names,G)
    if names[binding] ~= nil then return names[binding] end
    local button = type(binding)=="string" and tonumber(binding:match("^mouse:(%d+)$")) or nil
    if button == nil then return "G" end
    local U = (G.STRINGS and G.STRINGS.BLINK_UI) or {mouse_middle="Scroll click",mouse_up="Scroll up",mouse_down="Scroll down",mouse_extra="Extra mouse button (%d)"}
    if button == G.MOUSEBUTTON_MIDDLE then return U.mouse_middle end
    if button == G.MOUSEBUTTON_SCROLLUP then return U.mouse_up end
    if button == G.MOUSEBUTTON_SCROLLDOWN then return U.mouse_down end
    return string.format(U.mouse_extra, button)
end
function M.parse(value,names,G)
    if G ~= nil and type(value)=="string" then
        local button=tonumber(value:match("^mouse:(%d+)$"))
        local binding=M.mouse_id(button,G)
        if binding ~= nil then return binding end
    end
    local key=tonumber(value)
    return key ~= nil and names[key] ~= nil and key or nil
end
return M
