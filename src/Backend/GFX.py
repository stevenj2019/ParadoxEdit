from gui.warning_messages import GFX_file_copying_warn, GFX_is_focus_upload
from gui.file_dialogue import gfx_files_folder_selector, gfx_save_folder_selector
from gui.util import get_app_instance, get_main_window
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericComment
from Backend.PDXScriptBlocks import generate_GFX_block, generate_GFX_shine_block, generate_focus_icon_comment_block
import os
from pathlib import Path
import shutil

def focus_icon_build(sprite_name, sprite_path):
    return [
		GenericComment(f"Focus Icon for: {sprite_name}"),
		generate_GFX_block(sprite_name, sprite_path),
		generate_GFX_shine_block(sprite_name, sprite_path)
	]

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
	if GFX_file_copying_warn(get_main_window()):
		path, cont = gfx_files_folder_selector(get_main_window())
		if not cont:
			return
		save_path, cont = gfx_save_folder_selector(get_main_window())
		if not cont:
			return
		image_list = image_collection_loop(list(), path)
		sprites = copy_files_to_new_directory(save_path, image_list)

		generate_shines = GFX_is_focus_upload(get_main_window())
		sprite_blocks = list()
		for sprite in sprites:
			if generate_shines:
				sprite_blocks.extend(focus_icon_build(sprite.stem), sprite.relative_to(get_main_window().mod.mod_base_dir))
			else:
				sprite_block.append(generate_GFX_block(sprite.stem, sprite.relative_to(get_main_window().mod.mod_base_dir)))

		sprite_block = next(node for node in file.obj.nodes
						if isinstance(node, GenericBlock) and node.key == "spriteTypes")
		sprite_block.children.extend(sprite_blocks)

def add_missing_shines(file):
	focus_sprites = list()
	for node in file.obj.nodes:
		if node.key.lower() == "spritetypes":
			for child in node.children:
				if isinstance(child, GenericBlock):
					icon_keys = [c.key for c in child.children]
					if child.key.lower() == "spritetype" and not "animation" in icon_keys:
						icon_dict = dict()
						for kv in child.children:
							k, v = kv._get_key_val()
							icon_dict[k]=v._get_value()
						focus_sprites.append(icon_dict)
			focus_icon_blocks = list()
			for sprite in focus_sprites:
				focus_icon_blocks.extend(focus_icon_build(sprite["name"], sprite["texturefile"]))
			file.obj.nodes = [GenericBlock("spriteTypes", focus_icon_blocks)]
			breakpoint()
		else:
			pass

      