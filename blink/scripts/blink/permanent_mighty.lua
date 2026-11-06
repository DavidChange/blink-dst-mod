-- Native locomotor and stategraphs query mightiness on server and its tag on client.
-- Keep the native component permanently mighty without morphing BLINK's custom skin.
return function(inst)
    inst:AddComponent("mightiness")
    local might = inst.components.mightiness
    local function lock(self)
        self.state = "mighty"
        self.current = self.max
        self:Pause()
        inst:RemoveTag("mightiness_normal")
        inst:RemoveTag("mightiness_wimpy")
        inst:AddTag("mightiness_mighty")
    end
    might.DoDelta = lock
    might.OnLoad = lock
    might.BecomeState = lock
    lock(might)
    inst.components.temperature.inherentinsulation = TUNING.INSULATION_TINY
    inst.components.temperature.inherentsummerinsulation = -TUNING.INSULATION_TINY
    if inst.components.efficientuser == nil then inst:AddComponent("efficientuser") end
    for _,action in ipairs({ACTIONS.CHOP,ACTIONS.MINE,ACTIONS.HAMMER}) do
        inst.components.workmultiplier:AddMultiplier(action,TUNING.MIGHTY_WORK_EFFECTIVENESS,inst)
        inst.components.efficientuser:AddMultiplier(action,TUNING.MIGHTY_WORK_EFFECTIVENESS,inst)
    end
    if inst.components.expertsailor == nil then inst:AddComponent("expertsailor") end
    local sailor = inst.components.expertsailor
    sailor:SetRowForceMultiplier(TUNING.MIGHTY_ROWER_MULT)
    sailor:SetRowExtraMaxVelocity(TUNING.MIGHTY_ROWER_EXTRA_MAX_VELOCITY)
    sailor:SetAnchorRaisingSpeed(TUNING.MIGHTY_ANCHOR_SPEED)
    sailor:SetLowerSailStrength(TUNING.MIGHTY_SAIL_BOOST_STRENGTH)
end
