from ParadoxParser.ParadoxNodes import GenericBlock
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

###NEW (unfinished) code
# def get_node_name(block):
#     try:
#         name = next(
#             node.value for node in block if node.key.lower() == "name"
#         )
#     except StopIteration:
#         return
#     return name

# def collect_icons(block):
#     icon_nodes = list()
#     shine_nodes = list()
#     for node in block.nodes:
#         if isinstance(node, GenericBlock) and node.key.lower() == "spritetype":
#             if any(isinstance(block, GenericBlock) for block in node.nodes):
#                 shine_nodes.append(block)
#             else:
#                 icon_nodes.append(node)

# def add_missing_shines(file, app_controller):
#     try:
#         spritetypes_block = next(
#             node for node in file.nodes
#             if node.key.lower() == "spritetypes"
#         )
#     except StopIteration:
#         return
#     normal_icons, shine_icons = collect_icons(spritetypes_block)
#     if len(normal_icons) > len(shine_icons):
#         shine_icon_names = [get_node_name(n) for n in shine_icons]
#         for icon in normal_icons:
#             icon_name = get_node_name(icon)
#             if f"{icon_name}_shine" not in shine_icon_names:
                