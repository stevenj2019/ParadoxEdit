from ParadoxParser.ParadoxNodes import (GenericBlock, GenericKeyValue, GenericString,
                                        GenericInt, GenericFloat, GenericBool)
def GFX_icon(name=None, path=None):
    name = name if name else "GFX_icon_here"
    path = path if path else "/path/to/file.dds"
    return GenericBlock(
        "SpriteType",
        [
            GenericKeyValue("name", GenericString(name)),
            GenericKeyValue("texturefile", GenericString(str(path))),
        ]
    )

def GFX_shine_icon(name=None, path=None):
    name = name if name else "GFX_icon_here"
    path = path if path else "/path/to/file.dds"
    def _animation_block(path, rotation):
        return GenericBlock(
            "animation",
            [
                GenericKeyValue("animationmaskfile", GenericString(str(path))),
                GenericKeyValue("animationtextutefile", GenericString("gfx/interface/goals/shine_overlay.dds")),
                GenericKeyValue("animationrotation", GenericInt(rotation)),
                GenericKeyValue("animationlooping", GenericBool(False)),
                GenericKeyValue("animationtime", GenericFloat(0.75)),
                GenericKeyValue("animationdelay", GenericInt(0)),
                GenericKeyValue("animationblendmode",GenericString("add")),
                GenericKeyValue("animationtype", GenericString("scrolling")),
                _shine_rotation_block(),
                _shine_texture_block()
            ]
        )
    
    def _shine_rotation_block():
        return GenericBlock(
            "animationrotationoffset", 
            [
                GenericKeyValue("x", GenericFloat(0.0)),
                GenericKeyValue("y", GenericFloat(0.0))
            ]
        )
    
    def _shine_texture_block():
        return GenericBlock(
            "animationtexturescale",
            [
                GenericKeyValue("x", GenericFloat(1.0)),
                GenericKeyValue("y", GenericFloat(1.0))
            ]
        )
    
    return GenericBlock(
        "SpriteType", 
        [
            GenericKeyValue("name", GenericString(f"{name}_shine")),
            GenericKeyValue("texturefile", GenericString(str(path))),
            GenericKeyValue("effectFile", GenericString("gfx/FX/buttonstate.lua")),
            GenericKeyValue("legacy_lazy_load", GenericBool(False)),
            _animation_block(path, 90),
            _animation_block(path, -90)
        ]
    )
