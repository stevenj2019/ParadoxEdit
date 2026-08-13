from pathlib import Path

from ParadoxParser.ParadoxNodes import (
    GenericBlock,
    GenericBool,
    GenericFloat,
    GenericInt,
    GenericKeyValue,
    GenericString,
)


def GFX_icon(name: str = None, path: Path = None) -> GenericBlock:
    name = name if name else "GFX_icon_here"
    path = path if path else "/path/to/file.dds"
    return GenericBlock(
        "SpriteType",
        [
            GenericKeyValue("name", GenericString(name)),
            GenericKeyValue("texturefile", GenericString(str(path))),
        ],
    )


def GFX_shine_icon(name: str = None, path: Path = None) -> GenericBlock:
    name = name if name else "GFX_icon_here"
    path = path if path else Path("/path/to/file.dds")

    def _animation_block(path: Path, rotation: str) -> GenericBlock:
        return GenericBlock(
            "animation",
            [
                GenericKeyValue("animationmaskfile", GenericString(str(path))),
                GenericKeyValue(
                    "animationtextutefile", GenericString("gfx/interface/goals/shine_overlay.dds")
                ),
                GenericKeyValue("animationrotation", GenericInt(rotation)),
                GenericKeyValue("animationlooping", GenericBool(False)),
                GenericKeyValue("animationtime", GenericFloat(0.75)),
                GenericKeyValue("animationdelay", GenericInt(0)),
                GenericKeyValue("animationblendmode", GenericString("add")),
                GenericKeyValue("animationtype", GenericString("scrolling")),
                _shine_rotation_block(),
                _shine_texture_block(),
            ],
        )

    def _shine_rotation_block() -> GenericBlock:
        return GenericBlock(
            "animationrotationoffset",
            [GenericKeyValue("x", GenericFloat(0.0)), GenericKeyValue("y", GenericFloat(0.0))],
        )

    def _shine_texture_block() -> GenericBlock:
        return GenericBlock(
            "animationtexturescale",
            [GenericKeyValue("x", GenericFloat(1.0)), GenericKeyValue("y", GenericFloat(1.0))],
        )

    return GenericBlock(
        "SpriteType",
        [
            GenericKeyValue("name", GenericString(f"{name}_shine")),
            GenericKeyValue("texturefile", GenericString(str(path))),
            GenericKeyValue("effectFile", GenericString("gfx/FX/buttonstate.lua")),
            GenericKeyValue("legacy_lazy_load", GenericBool(False)),
            _animation_block(path, 90),
            _animation_block(path, -90),
        ],
    )
