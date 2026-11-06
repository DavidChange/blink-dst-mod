-- Pure geometry; independently testable without the DST engine.
local M = {}
function M.finite(n)
    return type(n) == "number" and n == n and n > -math.huge and n < math.huge
end
function M.destination(x,z,tx,tz,maxrange)
    if not (M.finite(tx) and M.finite(tz)) then return nil end
    local dx,dz = tx-x,tz-z
    local length = math.sqrt(dx*dx+dz*dz)
    if length < 0.25 then return nil end
    local distance = math.min(length,maxrange)
    return x+dx/length*distance,z+dz/length*distance,distance
end
function M.segment_distance_sq(px,pz,ax,az,bx,bz)
    local dx,dz = bx-ax,bz-az
    local length = dx*dx+dz*dz
    local t = length > 0 and ((px-ax)*dx+(pz-az)*dz)/length or 0
    t = math.max(0,math.min(1,t))
    return (px-ax-t*dx)^2+(pz-az-t*dz)^2
end
return M
