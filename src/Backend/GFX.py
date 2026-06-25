# from gui.dialogues.warning_messages import GFX_file_copying_warn, GFX_is_focus_upload, invalid_GFX_file_warning, GFX_load_and_store_are_same
# from gui.dialogues.file_dialogue import gfx_files_folder_selector, gfx_save_folder_selector
# from gui.util import get_main_window
# from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment
# from PDXFactory.blocks.sprites import GFX_icon, GFX_shine_icon
# import os
# from pathlib import Path
# import shutil

# def image_collection_loop(images, path):
#     for root, dirs, files in os.walk(path):
#         for name in dirs:
#             image_collection_loop(images, os.path.join(root, name))
#         for name in files:
#             if name.endswith("dds") or name.endswith("png"):
#                 images.append(Path(os.path.join(root, name)))
#     return images

# def copy_files_to_new_directory(save_to, image_list:list):
#     image_paths = list()
#     for img in image_list: #image is source Path
#         if img.name.startswith("GFX_"):
#             new_filename = f"GFX_{img.name}" #GFX_file.ext
#         else:
#             new_filename = img.name
#         new_img = Path(os.path.join(save_to, new_filename))

#         try:
#             shutil.copyfile(img, new_img)
#             image_paths.append(new_img)
#         except shutil.SameFileError:
#             GFX_load_and_store_are_same()
#             return
#     return image_paths

# def add_new_GFX(file):
# 	try:
# 		sprite_block = next(node for node in file.obj.nodes
# 						if isinstance(node, GenericBlock) and node.key.lower() == "spritetypes")
# 	except StopIteration:
# 		invalid_GFX_file_warning()
# 		return
	
# 	if GFX_file_copying_warn(get_main_window()):
# 		path, cont = gfx_files_folder_selector(get_main_window())
# 		if not cont:
# 			return
# 		save_path, cont = gfx_save_folder_selector(get_main_window())
# 		if not cont:
# 			return
# 		image_list = image_collection_loop(list(), path)
# 		sprites = copy_files_to_new_directory(save_path, image_list)
# 		if not sprites:
# 			return
# 		generate_shines = GFX_is_focus_upload(get_main_window())
# 		sprite_blocks = list()
# 		base_dir = get_main_window().mod.mod_base_dir
# 		for sprite in sprites:
# 			if generate_shines:
# 				sprite_blocks.extend([ 	GenericComment(f"Focus Icon for: {sprite.stem}"),
# 									 	GFX_icon(sprite.stem, sprite.relative_to(base_dir)),
# 										GFX_shine_icon(sprite.stem, sprite.relative_to(base_dir))])
# 			else:
# 				sprite_blocks.extend([GFX_icon(sprite.stem, sprite.relative_to(base_dir))])
# 		sprite_block.children.extend(sprite_blocks)

# def add_missing_shines(file):
# 	focus_sprites = list()
# 	for node in file.obj.nodes:
# 		if node.key.lower() == "spritetypes":
# 			for child in node.children:
# 				if isinstance(child, GenericBlock):
# 					icon_keys = [c.key for c in child.children]
# 					if (child.key.lower() == "spritetype" and 
# 		 				not any(k.startswith("animation") for k in icon_keys)):
# 						icon_dict = dict()
# 						for kv in child.children:
# 							k, v = kv._get_key_val()
# 							icon_dict[k]=v._get_value()
# 						focus_sprites.append(icon_dict)
# 			focus_icon_blocks = list()
# 			for sprite in focus_sprites:
# 				focus_icon_blocks.extend([ 	GenericComment(f"Focus Icon for: {sprite["name"]}"),
# 									 		GFX_icon(sprite["name"], sprite["texturefile"]),
# 											GFX_shine_icon(sprite["name"], sprite["texturefile"])])
# 			file.obj.nodes = [GenericBlock("spriteTypes", focus_icon_blocks)]
# 		else:
# 			pass
      