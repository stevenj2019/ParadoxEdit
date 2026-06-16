from gui.warning_messages import GFX_file_copying_warn, GFX_is_focus_upload
from gui.file_dialogue import gfx_files_folder_selector, gfx_save_folder_selector
from gui.util import get_app_instance, get_main_window
from ParadoxParser.ParadoxNodes import GenericBlock
from Backend.PDXScriptBlocks import generate_GFX_block, generate_GFX_shine_block
import os
from pathlib import Path
import shutil

def image_collection_loop(images, path):
    for root, dirs, files in os.walk(path):
        for name in dirs:
            image_collection_loop(images, os.path.join(root, name))
        for name in files:
            if name.endswith("dds") or name.endswith("png"):
                images.append(Path(os.path.join(root, name)))
    return images

def copy_files_to_new_directory(save_to, image_list:list):
    image_paths = list()
    for img in image_list: #image is source Path
        if img.name.startswith("GFX_"):
            new_filename = f"GFX_{img.name}" #GFX_file.ext
        else:
            new_filename = img.name
        new_img = Path(os.path.join(save_to, new_filename))
        shutil.copyfile(img, new_img)
        image_paths.append(new_img)
    return image_paths

def add_new_GFX(file):
    app = get_app_instance()
    main_window = get_main_window()
    if not GFX_file_copying_warn(main_window):
        return 

    path = gfx_files_folder_selector(main_window)
    image_list = image_collection_loop(list(), path)
    save_path = gfx_save_folder_selector(main_window)
    sprites = copy_files_to_new_directory(save_path, image_list)

    generate_shines = GFX_is_focus_upload(main_window)
    sprite_blocks = list()
    for sprite in sprites:
        icon = generate_GFX_block(sprite.stem, sprite.relative_to(main_window.mod.mod_base_dir))
        sprite_blocks.append(icon)
        if generate_shines:
            shine_icon = generate_GFX_shine_block(sprite.stem, sprite.relative_to(main_window.mod.mod_base_dir))
            sprite_blocks.append(shine_icon)

    sprite_block = next(node for node in file.obj.nodes
                        if isinstance(node, GenericBlock) and node.key == "spriteTypes")
    sprite_block.children.extend(sprite_blocks)

def add_missing_shines():
    #Step 1: check all icons, make list of icons and _shine icons
    #Step 2: if icon and not _shine icon, insert _shine icon after regular icon
    pass