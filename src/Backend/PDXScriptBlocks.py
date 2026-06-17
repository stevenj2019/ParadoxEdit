from ParadoxParser.ParadoxNodes import (GenericBlock, GenericKeyValue, GenericString, GenericBool,
                                        GenericInt, GenericFloat, GenericComment)
#comment for focus icons
def generate_focus_icon_comment_block(name):
    return GenericComment(f"Focus Icon for:{name}")
#generic icon
def generate_GFX_block(name, path):
    return GenericBlock(
        "SpriteType",
        [
            GenericKeyValue("name", GenericString(name)),
            GenericKeyValue("texturefile", GenericString(str(path))),
        ]
    )

### Shines
def generate_shine_rotation_block():
    return GenericBlock(
        "animationrotationoffset", 
        [
            GenericKeyValue("x", GenericFloat(0.0)),
            GenericKeyValue("y", GenericFloat(0.0))
        ]
    )

def generate_shine_texture_block():
    return GenericBlock(
        "animationtexturescale",
        [
            GenericKeyValue("x", GenericFloat(1.0)),
            GenericKeyValue("y", GenericFloat(1.0))
        ]
    )
def generate_positive_animation_block(path):
    return GenericBlock(
        "animation",
        [
            GenericKeyValue("animationmaskfile", GenericString(str(path))),
            GenericKeyValue("animationtextutefile", GenericString("gfx/interface/goals/shine_overlay.dds")),
            GenericKeyValue("animationrotation", GenericInt(90)),
            GenericKeyValue("animationlooping", GenericBool(False)),
            GenericKeyValue("animationtime", GenericFloat(0.75)),
            GenericKeyValue("animationdelay", GenericInt(0)),
            GenericKeyValue("animationblendmode",GenericString("add")),
            GenericKeyValue("animationtype", GenericString("scrolling")),
            generate_shine_rotation_block(),
            generate_shine_texture_block()
        ]
    )

def generate_negative_animation_block(path):
    return GenericBlock(
        "animation",
        [
            GenericKeyValue("animationmaskfile", GenericString(str(path))),
            GenericKeyValue("animationtextutefile", GenericString("gfx/interface/goals/shine_overlay.dds")),
            GenericKeyValue("animationrotation", GenericInt(-90)),
            GenericKeyValue("animationlooping", GenericBool(False)),
            GenericKeyValue("animationtime", GenericFloat(0.75)),
            GenericKeyValue("animationdelay", GenericInt(0)),
            GenericKeyValue("animationblendmode",GenericString("add")),
            GenericKeyValue("animationtype", GenericString("scrolling")),
            generate_shine_rotation_block(),
            generate_shine_texture_block()
        ]
    )

def generate_GFX_shine_block(name, path):
    return GenericBlock(
        "SpriteType", 
        [
            GenericKeyValue("name", GenericString(f"{name}_shine")),
            GenericKeyValue("texturefile", GenericString(str(path))),
            GenericKeyValue("effectFile", GenericString("gfx/FX/buttonstate.lua")),
            GenericKeyValue("legacy_lazy_load", GenericBool(False)),
            generate_negative_animation_block(path),
            generate_positive_animation_block(path)
        ]
    )


