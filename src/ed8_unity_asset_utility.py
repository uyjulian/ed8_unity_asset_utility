# SPDX-License-Identifier: MIT

# Utility for preparing and inserting variables and keywords using the ED8Shader shader.

# Run the script with "--help" as the argument for descriptions of these options.

def parse_uvb(filepath):
	import struct

	with open(filepath, "rb") as f:
		shouldbeUVab = struct.unpack("I", f.read(4))
		if shouldbeUVab[0] != 1650546261:
			return []
		length, = struct.unpack("I", f.read(4))
		if length == 0:
			return []
		data = f.read(length * 4)
		pos = 0
		data_decoded = []
		while pos < (length - 3):
			int1, = struct.unpack("I", data[pos * 4:(pos + 1) * 4])
			float1, = struct.unpack("f", data[pos * 4:(pos + 1) * 4])
			if int1 == 1:
				data_decoded.append([int1, list(struct.unpack("I", data[(pos + 1) * 4:(pos + 2) * 4]))])
				pos += 1
			elif int1 == 2 or int1 == 14 or int1 == 17 or int1 == 19:
				data_decoded.append([int1, list(struct.unpack("I", data[(pos + 1) * 4:(pos + 2) * 4]))])
				pos += 1
			elif int1 == 3:
				data_decoded.append([int1, list(struct.unpack("ffff", data[(pos + 1) * 4:(pos + 5) * 4]))])
				pos += 4
			elif int1 == 4 or int1 == 5 or int1 == 6 or int1 == 7 or int1 == 8 or int1 == 9 or int1 == 10:
				data_decoded.append([int1, list(struct.unpack("ff", data[(pos + 1) * 4:(pos + 3) * 4]))])
				pos += 2
			elif int1 == 11 or int1 == 12:
				data_decoded.append([int1, list(struct.unpack("Iffff", data[(pos + 1) * 4:(pos + 6) * 4]))])
				pos += 5
			elif int1 == 13:
				data_decoded.append([int1, list(struct.unpack("I", data[(pos + 1) * 4:(pos + 2) * 4]))])
				pos += 1
			elif int1 == 15:
				data_decoded.append([int1, list(struct.unpack("III", data[(pos + 1) * 4:(pos + 4) * 4]))])
				pos += 3
			elif int1 == 16 or int1 == 20:
				data_decoded.append([int1, []])
				pos += 0
			elif int1 == 18:
				data_decoded.append([int1, list(struct.unpack("Iffff", data[(pos + 1) * 4:(pos + 6) * 4]))])
				pos += 5
			else:
				data_decoded.append([int1])
			pos += 1
		return data_decoded

# Utility functions for manipulating UnityYAML
def split_indentation_level(instr):
	str_lines = instr.split("\n")
	filtered_lines = []
	filtered_last_line = [None]
	filtered_indented_lines = []
	filtered_indented_arr = [None]
	def deposit_indented_lines(is_last=False):
		if is_last:
			if filtered_indented_arr[0] == None:
				ret = None
				if len(filtered_indented_lines) != 0:
					ret = "\n".join(filtered_indented_lines)
					del filtered_indented_lines[:]
				return ret
		if filtered_indented_arr[0] == None:
			filtered_indented_arr[0] = []
		if len(filtered_indented_lines) > 0:
			filtered_indented_arr[0].append("\n".join(filtered_indented_lines))
			del filtered_indented_lines[:]
		return filtered_indented_arr[0]

	def deposit_lines(new_line):
		if filtered_last_line[0] != None:
			filtered_lines.append([filtered_last_line[0], deposit_indented_lines(True)])
		filtered_last_line[0] = new_line
		filtered_indented_arr[0] = None

	for line in str_lines:
		if line[0:2] == "  ":
			filtered_indented_lines.append(line[2:])
		elif line[0:2] == "- ":
			deposit_indented_lines()
			filtered_indented_lines.append(line[2:])
		else:
			deposit_lines(line)
	deposit_lines(line)
	return filtered_lines

def join_indentation_level(inarr):
	lines = []
	for x in inarr:
		lines.append(x[0])
		contents = x[1]
		if contents != None:
			if type(contents) == str:
				contents_lines = contents.split("\n")
				for line in contents_lines:
					lines.append("  " + line)
			elif type(contents) == list:
				for xx in contents:
					contents_lines = xx.split("\n")
					lines.append("- " + contents_lines[0])
					for line in contents_lines[1:]:
						lines.append("  " + line)
			
	return "\n".join(lines)

def find_indentation_level(inarr, key):
	for i in range(len(inarr)):
		if type(inarr[i][0]) == str and inarr[i][0].startswith(key + ":"):
			return i
	return -1

def mutate_indentation_level(inarr, dic):
	for key in sorted(dic.keys()):
		i = find_indentation_level(inarr, key)
		if i == -1:
			raise Exception("Key " + key + " not found")
		if inarr[i][1] == None:
			inarr[i][0] = key + ": " + dic[key]
		elif type(inarr[i][1]) == str:
			e_split = split_indentation_level(inarr[i][1])
			mutate_indentation_level(e_split, dic[key])
			inarr[i][1] = join_indentation_level(e_split)
		elif type(inarr[i][1]) == list:
			raise Exception("List mutation NYI")

def float_as_shortest_str(flt):
	return ("%g" % flt) if (type(flt) == float) else str(flt)

shader_name_to_basename = {
	"ED8/Cold Steel Shader/Cutout (Grabpass)" : "ED8_Cutout (Grabpass).shader",
	"ED8/Cold Steel Shader/Cutout (Outline)" : "ED8_Cutout (Outline).shader",
	"ED8/Cold Steel Shader/Cutout" : "ED8_Cutout.shader",
	"ED8/Cold Steel Shader/Opaque (Grabpass)" : "ED8_Default (Grabpass).shader",
	"ED8/Cold Steel Shader/Opaque (Outline)" : "ED8_Default (Outline).shader",
	"ED8/Cold Steel Shader/Opaque" : "ED8_Default.shader",
	"ED8/Cold Steel Shader/Transparent (Grabpass)" : "ED8_Transparent (Grabpass).shader",
	"ED8/Cold Steel Shader/Transparent (Outline)" : "ED8_Transparent (Outline).shader",
	"ED8/Cold Steel Shader/Transparent" : "ED8_Transparent.shader",
}

def save_unity_mat(config_struct):
	import os
	import re
	import json

	# Is sen3 and above?
	isCS3Up = True
	isXanadu = False
	debug_list = None
	if config_struct["save_material_configuration_to_unity_metadata_debug"]:
		debug_list = []
	def debug_log(ln):
		if debug_list is not None:
			debug_list.append(ln)

	shader_parameter_filter = config_struct["save_material_configuration_to_unity_metadata_filter_shader_parameter"].split(",")
	if "" in shader_parameter_filter:
		shader_parameter_filter.remove("")

	in_filename = config_struct["input_file"]

	in_structure = None
	if "input_structure" in config_struct:
		in_structure = config_struct["input_structure"]
	else:
		with open(in_filename, "r") as f:
			in_structure = json.load(f)

	input_filename = in_structure["input_filename"]
	material_objs = in_structure["materials"]
	parameter_buffer_objs = in_structure["parameter_buffers"]
	asset_reference_import_objs = in_structure["asset_reference_imports"]
	sampler_state_objs = in_structure["sampler_states"]

	def readdir_to_basename_fullpath_dict(in_path, out_fullpath_dict, file_ext=None):
		import pathlib
		if in_path != "":
			in_path = pathlib.Path(in_path)
			for file in sorted(in_path.glob('**/*')):
				file_name = file.name.lower()
				if (file_ext == None or file_name.endswith(file_ext)) and (not file_name.startswith("._")):
					file_name_modified = file_name
					if file_ext != None:
						file_name_modified = file_name[:-(len(file_ext))]
					out_fullpath_dict[file_name_modified] = str(file)

	def readdir_meta_to_guid_and_fullpath(in_path, out_guid_dict, out_fullpath_dict):
		import pathlib
		if in_path != "":
			in_path_pathobj = pathlib.Path(in_path)
			for file in sorted(in_path_pathobj.glob('**/*')):
				if (file.name.endswith(".meta")) and (not file.name.startswith("._")):
					meta_contents = []
					with open(file, "r", encoding="utf-8") as f:
						meta_contents = f.read().split("\n")
					guid = ""
					for line in meta_contents:
						if line.startswith("guid: "):
							guid = line[6:]
							break
					if guid != "":
						out_guid_dict[os.path.basename(file).lower()[:-5]] = guid
						out_fullpath_dict[os.path.basename(file).lower()[:-5]] = str(file)[:-5]
					debug_log("GUID for " + str(file) + ": " + guid)

	basename_to_guid_mat = {}
	basename_to_projectpath_mat = {}
	
	readdir_meta_to_guid_and_fullpath(config_struct["save_material_configuration_to_unity_metadata_path"], basename_to_guid_mat, basename_to_projectpath_mat)


	basename_to_guid_texture = {}
	basename_to_projectpath_texture = {}

	project_texture_path = config_struct["save_material_configuration_to_unity_metadata_texture_path"]
	if project_texture_path == "":
		project_texture_path = config_struct["save_material_configuration_to_unity_metadata_path"]

	readdir_meta_to_guid_and_fullpath(project_texture_path, basename_to_guid_texture, basename_to_projectpath_texture)

	basename_to_guid_model = basename_to_guid_texture
	basename_to_projectpath_model = basename_to_projectpath_texture

	project_model_path = config_struct["save_material_configuration_to_unity_metadata_model_path"]
	if project_model_path != "":
		basename_to_guid_model = {}
		basename_to_projectpath_model = {}
		readdir_meta_to_guid_and_fullpath(project_model_path, basename_to_guid_model, basename_to_projectpath_model)

	basename_to_guid_shader = basename_to_guid_texture
	basename_to_projectpath_shader = basename_to_projectpath_texture

	project_shader_path = config_struct["save_material_configuration_to_unity_metadata_shader_path"]
	if project_shader_path != "":
		basename_to_guid_shader = {}
		basename_to_projectpath_shader = {}
		readdir_meta_to_guid_and_fullpath(project_shader_path, basename_to_guid_shader, basename_to_projectpath_shader)

	basename_to_path_inf = {}
	readdir_to_basename_fullpath_dict(config_struct["save_material_configuration_to_unity_metadata_inf_path"], basename_to_path_inf, ".inf")

	basename_to_path_uvb = {}
	readdir_to_basename_fullpath_dict(config_struct["save_material_configuration_to_unity_metadata_uvb_path"], basename_to_path_uvb, ".uvb")

	basename_to_path_effect_json = {}
	readdir_to_basename_fullpath_dict(config_struct["save_material_configuration_to_unity_metadata_effect_json_path"], basename_to_path_effect_json, ".effect.json")

	basename_to_path_texture_json = {}
	readdir_to_basename_fullpath_dict(config_struct["save_material_configuration_to_unity_metadata_texture_json_path"], basename_to_path_texture_json, ".texture.json")

	backup_path = config_struct["backup_path"]

	def do_backup_path(in_path):
		if os.path.isfile(in_path):
			base_backup_in_path = in_path + ".bak"
			if backup_path != "":
				base_backup_in_path = backup_path + "/" + os.path.basename(in_path) + ".bak"
			backup_count = 0
			while os.path.isfile(base_backup_in_path + str(backup_count)):
				backup_count += 1
			os.rename(in_path, base_backup_in_path + str(backup_count))

	def write_if_unchanged(in_path, in_contents):
		if os.path.isfile(in_path):
			old_contents = ""
			with open(in_path, "r", encoding="utf-8") as f:
				old_contents = f.read()
			if old_contents == in_contents:
				return
		tmp_in_path = in_path + ".tmp"
		with open(tmp_in_path, "w", encoding="utf-8") as f:
			f.write(in_contents)
		do_backup_path(in_path)
		os.replace(tmp_in_path, in_path)

	def get_guid_for_path(in_filename, in_path, in_guid_dict, in_fullpath_dict):
		import uuid
		in_filename_basename = os.path.basename(in_filename).lower()
		in_filename_basename_normalized = in_filename_basename.lower()
		if in_filename_basename_normalized in in_guid_dict:
			return in_guid_dict[in_filename_basename_normalized]
		new_uuid = str(uuid.uuid4().hex)

		lns = []
		lns.append("fileFormatVersion: 2")
		lns.append("guid: " + new_uuid)
		lns.append("NativeFormatImporter:")
		lns.append("  externalObjects: {}")
		lns.append("  mainObjectFileID: 2100000")
		lns.append("  userData: ")
		lns.append("  assetBundleName: ")
		lns.append("  assetBundleVariant: ")

		full_path = in_path + "/" + in_filename_basename
		meta_path = full_path + ".meta"
		if not config_struct["dry_run"]:
			write_if_unchanged(meta_path, "".join([x + "\n" for x in lns if x != ""]))
		in_fullpath_dict[in_filename_basename_normalized] = full_path
		in_guid_dict[in_filename_basename_normalized] = new_uuid
		return new_uuid

	uvb_info = {}
	gameid_to_parameters = {}
	clsuter_basename_noext = input_filename.split(".", 1)[0].lower()
	if clsuter_basename_noext in basename_to_path_inf:
		material_anim_set_arg_match = re.compile(r'([^ =]*?)="([^"]*?)"')
		inf_content = []
		with open(basename_to_path_inf[clsuter_basename_noext], "r", encoding="utf-8") as f:
			inf_content = f.read().split("\n")
		anim_objs = []
		for line in inf_content:
			if "material_anim_set" in line:
				animobj = {}
				for x in material_anim_set_arg_match.finditer(line):
					animobj[x.group(1)] = x.group(2)
				if len(animobj) > 0:
					anim_objs.append(animobj)
		if len(anim_objs) > 0:
			for x in anim_objs:
				parameter_for_shader_uvb = None
				if "gameMateiralIDs" in x:
					if not (int(x["gameMateiralIDs"]) in gameid_to_parameters):
						gameid_to_parameters[int(x["gameMateiralIDs"])] = {}
					parameter_for_shader_uvb = gameid_to_parameters[int(x["gameMateiralIDs"])]
				if parameter_for_shader_uvb is not None and "source" in x:
					source_noext = x["source"][:-4]
					if source_noext in basename_to_path_uvb and not (source_noext in uvb_info):
						uvb_parsed = parse_uvb(basename_to_path_uvb[source_noext])
						uvb_type = None
						u_flip = 100
						v_flip = 100
						for xx in uvb_parsed:
							if xx[0] == 17: # uv_target
								if xx[1][0] == 0: # tex1
									uvb_type = "_TexCoordOffset" # TODO: verify
									u_flip = 100
									v_flip = -100
								elif xx[1][0] == 1: # tex
									uvb_type = "_TexCoordOffset"
									u_flip = 100
									v_flip = -100
								elif xx[1][0] == 2: # proj
									uvb_type = "_ProjectionScroll"
									u_flip = -100
									v_flip = 100
								elif xx[1][0] == 4: # muv
									uvb_type = "_TexCoordOffset2"
									u_flip = 100
									v_flip = -100
								elif xx[1][0] == 8: # muv2
									uvb_type = "_TexCoordOffset3"
									u_flip = 100
									v_flip = -100
								elif xx[1][0] == 16: # dudv
									uvb_type = "_DuDvScroll"
									u_flip = 100
									v_flip = -100
								else:
									u_flip = 100
									v_flip = 100
								break
						if uvb_type is None:
							# Fallback type
							uvb_type = "_TexCoordOffset"
							u_flip = 100
							v_flip = -100
						if uvb_type is not None:
							for xx in uvb_parsed:
								if xx[0] == 7: # uv_ofs_dt
									parameter_for_shader_uvb[uvb_type] = [xx[1][0] * u_flip, xx[1][1] * v_flip, 0, 0]
									break

	texture_fullpath_to_sampler = {}
	for v in material_objs:
		parameters_samplerstate = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_tweakableShaderParameterDefinitions_object_references_sampler_state_indexes"]
		parameters_imports = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_tweakableShaderParameterDefinitions_object_references_asset_reference_import_indexes"]
		for key in sorted(parameters_imports.keys()):
			if (key + "S") in parameters_samplerstate:
				texture_fullpath_to_sampler[asset_reference_import_objs[parameters_imports[key]]["m_id"]["m_buffer"]] = sampler_state_objs[parameters_samplerstate[key + "S"]]
			elif (key + "Sampler") in parameters_samplerstate:
				texture_fullpath_to_sampler[asset_reference_import_objs[parameters_imports[key]]["m_id"]["m_buffer"]] = sampler_state_objs[parameters_samplerstate[key + "Sampler"]]

	wrap_map = {
		0 : 1, # CLAMP_TO_EDGE
		1 : 0, # REPEAT
		2 : 1, # CLAMP_TO_EDGE
		3 : 1, # CLAMP_TO_EDGE
		4 : 2, # MIRROR
	}
	texture_fullpath_to_guid = {}
	effectvariant_fullpath_to_switches = {}
	for v in asset_reference_import_objs:
		if v["m_targetAssetType"] == "PTexture2D":
			texture2d_name = v["m_id"]["m_buffer"]
			texture2d_basename = os.path.basename(texture2d_name).lower()
			is_transparency_enabled = True
			if texture2d_basename in basename_to_path_texture_json:
				import json
				texture_structure = None
				with open(basename_to_path_texture_json[texture2d_basename], "r") as f:
					texture_structure = json.load(f)
				effect_switches_list = []
				texture2d_objs = texture_structure["texture2d_list"]
				if len(texture2d_objs) > 0:
					texture2d_obj = texture2d_objs[0]
					if "m_format" in texture2d_obj:
						texture2d_obj_format = texture2d_obj["m_format"]
						# Known formats: LA8, L8, ARGB8, ARGB8_SRGB, RGBA8, RGB565, ARGB4444, BC5, BC7, DXT1, DXT3, DXT5
						no_transparency_formats = ["L8", "RGB565", "BC5", "DXT1"]
						debug_log("Texture format for " + texture2d_name + " is " + texture2d_obj_format)
						if texture2d_obj_format in no_transparency_formats:
							is_transparency_enabled = False
			else:
				debug_log("Texture file not found for " + texture2d_name)
			basename_noext = os.path.basename(texture2d_name).split(".", 1)[0].lower()
			found_texture_path = None
			if basename_noext + ".png" in basename_to_guid_texture:
				found_texture_path = basename_noext + ".png"
			elif basename_noext + ".dds" in basename_to_guid_texture:
				found_texture_path = basename_noext + ".dds"
			if found_texture_path is not None:
				texture_fullpath_to_guid[texture2d_name] = basename_to_guid_texture[found_texture_path]
				meta_path = basename_to_projectpath_texture[found_texture_path] + ".meta"
				debug_log("Handling texture " + str(texture2d_name))
				if texture2d_name in texture_fullpath_to_sampler:
					samplerstate = texture_fullpath_to_sampler[texture2d_name]
					wrapS = 0
					wrapT = 0
					filterMode = 2
					aniso = 8
					alphaIsTransparency = 1
					textureFormat_Default = -1
					textureFormat_Windows = 29 # RGBA Crunched DXT5
					textureFormat_Android = 52 # ASTC 10x10
					maxTextureSize = 1024
					textureCompression = 0
					compressionQuality = 100
					crunchedCompression = 0
					if not is_transparency_enabled:
						textureFormat_Windows = 28 # RGB Crunched DXT1
					if config_struct["save_material_configuration_to_unity_metadata_compress_textures"]:
						textureCompression = 1
						crunchedCompression = 1
					if samplerstate["m_wrapS"] in wrap_map:
						wrapS = wrap_map[samplerstate["m_wrapS"]]
					if samplerstate["m_wrapT"] in wrap_map:
						wrapT = wrap_map[samplerstate["m_wrapT"]]
					texture_changed = False
					meta_png_content = ""
					with open(meta_path, "r", encoding="utf-8") as f:
						meta_png_content = f.read()
					meta_png_split_root = split_indentation_level(meta_png_content)
					meta_png_find_TextureImporter = find_indentation_level(meta_png_split_root, "TextureImporter")
					if meta_png_find_TextureImporter != -1:
						meta_png_split_TextureImporter = split_indentation_level(meta_png_split_root[meta_png_find_TextureImporter][1])
						meta_png_mutate_TextureImporter = {
							"textureSettings" : {
								"filterMode" : str(filterMode),
								"aniso" : str(aniso),
								"wrapU" : str(wrapS),
								"wrapV" : str(wrapT),
							},
							"alphaIsTransparency" : str(alphaIsTransparency),
							"compressionQuality" : str(compressionQuality),
						}
						mutate_indentation_level(meta_png_split_TextureImporter, meta_png_mutate_TextureImporter)
						meta_png_find_platformSettings = find_indentation_level(meta_png_split_TextureImporter, "platformSettings")
						if meta_png_find_platformSettings != -1:
							meta_png_val_platformSettings = meta_png_split_TextureImporter[meta_png_find_platformSettings][1]
							if type(meta_png_val_platformSettings) == list:
								for ii in range(len(meta_png_val_platformSettings)):
									meta_png_mutate_platformSettings_element = {
										"textureCompression" : str(textureCompression),
										"compressionQuality" : str(compressionQuality),
										"crunchedCompression" : str(crunchedCompression),
										"maxTextureSize" : str(maxTextureSize),
									}
									platformSettings_element_split = split_indentation_level(meta_png_val_platformSettings[ii])
									meta_png_find_buildTarget = find_indentation_level(platformSettings_element_split, "buildTarget")
									if meta_png_find_buildTarget != -1:
										if platformSettings_element_split[meta_png_find_buildTarget][0] in ["buildTarget: DefaultTexturePlatform"]:
											meta_png_mutate_platformSettings_element["textureFormat"] = str(textureFormat_Default)
										elif platformSettings_element_split[meta_png_find_buildTarget][0] in ["buildTarget: Standalone"]:
											meta_png_mutate_platformSettings_element["textureFormat"] = str(textureFormat_Windows)
										elif platformSettings_element_split[meta_png_find_buildTarget][0] in ["buildTarget: Android"]:
											meta_png_mutate_platformSettings_element["textureFormat"] = str(textureFormat_Android)
									mutate_indentation_level(platformSettings_element_split, meta_png_mutate_platformSettings_element)
									meta_png_val_platformSettings[ii] = join_indentation_level(platformSettings_element_split)

						meta_png_split_root[meta_png_find_TextureImporter][1] = join_indentation_level(meta_png_split_TextureImporter)
					else:
						debug_log("TextureImporter element not found")
					meta_png_content_new = join_indentation_level(meta_png_split_root)
					texture_changed = meta_png_content_new != meta_png_content
					if texture_changed:
						if not config_struct["dry_run"]:
							write_if_unchanged(meta_path, meta_png_content_new)
					else:
						debug_log("Texture unchanged")
				else:
					debug_log("Sampler state not found")
			else:
				debug_log("Texture for " + str(texture2d_name) + " not found")
		elif v["m_targetAssetType"] == "PEffectVariant":
			effectvariant_name = v["m_id"]["m_buffer"]
			effectvariant_basename = os.path.basename(effectvariant_name).lower()
			if effectvariant_basename in basename_to_path_effect_json:
				import json
				effect_structure = None
				with open(basename_to_path_effect_json[effectvariant_basename], "r") as f:
					effect_structure = json.load(f)
				effect_switches_list = []
				effects_objs = effect_structure["effects"]
				if len(effects_objs) > 0:
					effect_variants_objs = effects_objs[0]["m_effectVariants"]
					if len(effect_variants_objs) > 0:
						effect_variants_obj = effect_variants_objs[0]
						switches_dict = effect_variants_obj["mu_switches_dict"]
						for vv in sorted(switches_dict.keys()):
							if switches_dict[vv] == "1":
								effect_switches_list.append(vv)
				effectvariant_fullpath_to_switches[effectvariant_name] = effect_switches_list
			else:
				debug_log("Effect variant file not found for " + effectvariant_name)

	material_name_to_guid = {}
	for v in material_objs:
		debug_log("Handling material " + v["mu_name"] + " (" + v["mu_materialname"] + ")")

		matname = (v["mu_materialname"] + ".mat").lower()
		if (config_struct["save_material_configuration_to_unity_metadata_create_materials"]) or (matname in basename_to_projectpath_mat):
			shader_keywords_list = []
			if v["m_effectVariantIndex"] != None:
				effect_variant_path = asset_reference_import_objs[v["m_effectVariantIndex"]]["m_id"]["m_buffer"]
				if effect_variant_path in effectvariant_fullpath_to_switches:
					shader_keywords_list = effectvariant_fullpath_to_switches[effect_variant_path][:]

			def shader_keyword_has(s):
				return (s in shader_keywords_list)
			def shader_keyword_add(s):
				if s != "":
					if not shader_keyword_has(s):
						shader_keywords_list.append(s)
			def shader_keyword_remove(s):
				if shader_keyword_has(s):
					shader_keywords_list.remove(s)

			material_name_to_guid[v["mu_materialname"]] = get_guid_for_path(matname, config_struct["save_material_configuration_to_unity_metadata_path"], basename_to_guid_mat, basename_to_projectpath_mat)
			material_fullpath = basename_to_projectpath_mat[matname]
			material_content_rewrite = []

			parameters = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_shaderParameters"]
			gamematid = None
			possible_material_root_attributes = {}
			possible_material_root_attributes_keyorder = []
			possible_material_texenvs = {}
			possible_material_ints = {}
			possible_material_floats = {}
			possible_material_colors = {}

			def add_material_root_attribute(k, v):
				possible_material_root_attributes[k] = v
				possible_material_root_attributes_keyorder.append(k)
			def remove_material_root_attribute(k):
				if k in possible_material_root_attributes_keyorder:
					del possible_material_root_attributes[k]
					possible_material_root_attributes_keyorder.remove(k)
			material_version = config_struct["save_material_configuration_to_unity_metadata_material_version"]
			add_material_root_attribute("serializedVersion", "") # This will be set later
			add_material_root_attribute("m_ObjectHideFlags", "0")
			add_material_root_attribute("m_CorrespondingSourceObject", "{fileID: 0}")
			add_material_root_attribute("m_PrefabInstance", "{fileID: 0}")
			add_material_root_attribute("m_PrefabAsset", "{fileID: 0}")
			add_material_root_attribute("m_Name", v["mu_materialname"])
			add_material_root_attribute("m_Shader", "{fileID: 0}")
			add_material_root_attribute("m_Parent", "{fileID: 0}")
			add_material_root_attribute("m_ModifiedSerializedProperties", "0")
			add_material_root_attribute("m_ValidKeywords", "") # This will be set later
			add_material_root_attribute("m_InvalidKeywords", "[]")
			add_material_root_attribute("m_ShaderKeywords", "") # This will be set later
			add_material_root_attribute("m_LightmapFlags", "4")
			add_material_root_attribute("m_EnableInstancingVariants", "0")
			add_material_root_attribute("m_DoubleSidedGI", "0")
			add_material_root_attribute("m_CustomRenderQueue", "-1")
			add_material_root_attribute("stringTagMap", "{}")
			add_material_root_attribute("disabledShaderPasses", "[]")
			add_material_root_attribute("m_LockedProperties", "")
			add_material_root_attribute("m_SavedProperties", "") # This will be set later
			add_material_root_attribute("m_BuildTextureStacks", "[]")
			if config_struct["save_material_configuration_to_unity_metadata_apply_previous_configuration"] and os.path.isfile(material_fullpath):
				material_existing_content = []
				with open(material_fullpath, "r", encoding="utf-8") as f:
					material_existing_content = f.read().split("\n")
				material_content_texenv_last_name = ""
				paramtype = ""
				for line in material_existing_content:
					if line == "    m_TexEnvs:":
						paramtype = "TexEnvs"
						continue
					elif line == "    m_Ints:":
						raise Exception("Non-empty ints not yet supported")
					elif line == "    m_Ints: []":
						paramtype = ""
						continue
					elif line == "    m_Floats:":
						paramtype = "Floats"
						continue
					elif line == "    m_Colors:":
						paramtype = "Colors"
						continue
					elif line[0:2] == "  " and line[2:3] != " " and (":" in line):
						colon_pos = line.find(": ")
						check_key = line[2:colon_pos]
						if check_key == "m_SavedProperties":
							pass
						elif check_key == "m_ShaderKeywords":
							paramtype = ""
							shader_keywords_list_tmp = [x.strip() for x in line[colon_pos + 2:].split(" ")]
							for keyword in shader_keywords_list_tmp:
								shader_keyword_add(keyword)
						elif check_key == "m_ValidKeywords" or check_key == "m_InvalidKeywords":
							paramtype = "KeywordList"
						else:
							paramtype = ""
							if check_key in possible_material_root_attributes:
								possible_material_root_attributes[check_key] = line[colon_pos + 2:]
							else:
								debug_log("Unknown material root key " + check_key + " (" + v["mu_materialname"] + ")")
					if paramtype == "":
						pass
					elif paramtype == "KeywordList":
						if line.startswith("  - "):
							shader_keyword_add(line[4:].strip())
					elif paramtype == "TexEnvs":
						colon_pos = line.find(":")
						if line.startswith("    - "):
							material_content_texenv_last_name = line[6:colon_pos]
						elif line.startswith("        m_Texture: "):
							possible_material_texenvs[material_content_texenv_last_name] = line[19:]
					elif paramtype == "Ints":
						colon_pos = line.find(":")
						if line.startswith("    - ") and colon_pos != 0:
							possible_material_ints[line[6:colon_pos]] = line[colon_pos + 2:]
					elif paramtype == "Floats":
						colon_pos = line.find(":")
						if line.startswith("    - ") and colon_pos != 0:
							possible_material_floats[line[6:colon_pos]] = line[colon_pos + 2:]
					elif paramtype == "Colors":
						colon_pos = line.find(":")
						if line.startswith("    - ") and colon_pos != 0:
							possible_material_colors[line[6:colon_pos]] = [component[2:] for component in line[colon_pos + 2:][1:-1].replace(" ", "").split(",")]

			if config_struct["save_material_configuration_to_unity_metadata_apply_shader_parameter_configuration"]:
				parameters_for_textures = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_tweakableShaderParameterDefinitions_object_references_asset_reference_import_indexes"]
				for key in sorted(parameters_for_textures.keys()):
					transformed_parameter_name = "_" + key
					if key == "DiffuseMapSampler":
						transformed_parameter_name = "_MainTex"
					if key == "NormalMapSampler":
						transformed_parameter_name = "_BumpMap"
					if key == "PerMaterialMainLightClampFactor":
						transformed_parameter_name = "_GlobalMainLightClampFactor"
					debug_log("Handling shader parameter  " + key + "; transformed " + transformed_parameter_name)
					parameter_value = asset_reference_import_objs[parameters_for_textures[key]]["m_id"]["m_buffer"]
					if (len(shader_parameter_filter) == 0) or (transformed_parameter_name in shader_parameter_filter):
						if type(parameter_value) is str:
							if parameter_value in texture_fullpath_to_guid:
								possible_material_texenvs[transformed_parameter_name] = R"{fileID: 2800000, guid: " + texture_fullpath_to_guid[parameter_value] + ", type: 3}"
							else:
								possible_material_texenvs[transformed_parameter_name] = R"{fileID: 0}"
								if len(texture_fullpath_to_guid) > 0:
									debug_log("Texture is not found (" + parameter_value + ")")
								else:
									debug_log("Texture is not mapped due to no texture .meta files found")
						else:
							debug_log("Did not map texture: Invalid type (" + str(type(parameter_value)) + ")")
					else:
						debug_log("Did not map texture: Shader parameter not in allowlist (" + str(transformed_parameter_name) + ")")
				for key in sorted(parameters.keys()):
					transformed_parameter_name = "_" + key
					parameter_value = parameters[key]
					if key == "DiffuseMapSampler":
						transformed_parameter_name = "_MainTex"
					if key == "NormalMapSampler":
						transformed_parameter_name = "_BumpMap"
					if key == "PerMaterialMainLightClampFactor":
						transformed_parameter_name = "_GlobalMainLightClampFactor"
					debug_log("Handling shader parameter  " + key + "; transformed " + transformed_parameter_name)
					if key == "GameMaterialID":
						gamematid = int(parameter_value[0])
					if (len(shader_parameter_filter) == 0) or (transformed_parameter_name in shader_parameter_filter):
						if not (type(parameter_value) is str):
							if len(parameter_value) == 1:
								param_float = parameter_value[0]
								possible_material_floats[transformed_parameter_name] = param_float
								debug_log("Mapped float " + key + " in shader parameters")
							else:
								debug_log("Did not map float: Parameter length is too long (" + str(len(parameter_value)) + ")")
						else:
							debug_log("Did not map float: Invalid type (" + str(type(parameter_value)) + ")")
					else:
						debug_log("Did not map float: Shader parameter not in allowlist (" + str(transformed_parameter_name) + ")")
					if (len(shader_parameter_filter) == 0) or (transformed_parameter_name in shader_parameter_filter):
						if (not (type(parameter_value) is str)) and (not (type(parameter_value) is dict)):
							arr_len = len(parameter_value)
							param_r = 0
							param_g = 0
							param_b = 0
							param_a = 0
							if arr_len >= 1:
								param_r = parameter_value[0]
							if arr_len >= 2:
								param_g = parameter_value[1]
							if arr_len >= 3:
								param_b = parameter_value[2]
							if arr_len >= 4:
								param_a = parameter_value[3]
							if key == "WindyGrassDirection":
								param_g *= -1
							if arr_len in [2, 3, 4]:
								possible_material_colors[transformed_parameter_name] = [param_r, param_g, param_b, param_a]
								debug_log("Mapped color " + key + " in shader parameters")
							else:
								debug_log("Did not map color: Array length is too long (" + str(arr_len) + ")")
						else:
							debug_log("Did not map color: Invalid type (" + str(type(parameter_value)) + ")")
					else:
						debug_log("Did not map color: Shader parameter not in allowlist (" + str(transformed_parameter_name) + ")")
				if gamematid is not None:
					if gamematid in gameid_to_parameters:
						gameid_to_parameters_item = gameid_to_parameters[gamematid]
						for key in sorted(gameid_to_parameters_item.keys()):
							if (len(shader_parameter_filter) == 0) or (transformed_parameter_name in shader_parameter_filter):
								possible_material_colors[key] = gameid_to_parameters_item[key]
								debug_log("Mapped color " + key + " in shader parameters (for GameMaterialID)")
							else:
								debug_log("Did not map color " + key + " in shader parameters (for GameMaterialID) due to not in allowlist")
					else:
						debug_log("Could not map GameMaterialID for this material")
				else:
					debug_log("Could not detect GameMaterialID for this material")

			if config_struct["save_material_configuration_to_unity_metadata_apply_shader_keyword_configuration"]:
				# TODO: DOUBLE_SIDED, CASTS_SHADOWS_ONLY, CASTS_SHADOWS, RECEIVE_SHADOWS, _FogRangeParameters, _HemiSphereAmbientAxis, _Instancing/material.enableInstancing, ints

				if (shader_keyword_has("NOTHING_ENABLED")):
					possible_material_floats["_NothingEnabled"] = 1.0

				if (shader_keyword_has("WATER_SURFACE_ENABLED")):
					possible_material_floats["m_start_WaterSurface"] = 1.0
					possible_material_floats["_WaterSurfaceEnabled"] = 1.0
					possible_material_floats["m_end_WaterSurface"] = 0.0

				if (shader_keyword_has("TRANSPARENT_DELAY_ENABLED")):
					possible_material_floats["_TransparentDelayEnabled"] = 1.0

				if (shader_keyword_has("VERTEX_COLOR_ENABLED")):
					possible_material_floats["_VertexColorEnabled"] = 1.0

				if (shader_keyword_has("BLEND_VERTEX_COLOR_BY_ALPHA_ENABLED")):
					possible_material_floats["_BlendVertexColorAlphaEnabled"] = 1.0

				if (shader_keyword_has("NO_ALL_LIGHTING_ENABLED")) or (shader_keyword_has("GLARE_EMISSION_ENABLED")):
					possible_material_floats["_NoAllLightingEnabled"] = 1.0

				if (shader_keyword_has("NO_MAIN_LIGHT_SHADING_ENABLED")):
					possible_material_floats["_NoMainLightShadingEnabled"] = 1.0

				if (shader_keyword_has("HALF_LAMBERT_LIGHTING_ENABLED")):
					possible_material_floats["_HalfLambertLightingEnabled"] = 1.0

				if (shader_keyword_has("LIGHT_DIRECTION_FOR_CHARACTER_ENABLED")):
					possible_material_floats["m_start_PortraitLight"] = 1.0
					possible_material_floats["_PortraitLightEnabled"] = 1.0
					possible_material_floats["m_end_PortraitLight"] = 0.0

				if (shader_keyword_has("UVA_SCRIPT_ENABLED")):
					possible_material_floats["m_start_UVA"] = 1.0
					possible_material_floats["_UVAEnabled"] = 1.0
					possible_material_floats["m_end_UVA"] = 0.0

				if (shader_keyword_has("FAR_CLIP_BY_DITHER_ENABLED")):
					possible_material_floats["_FarClipDitherEnabled"] = 1.0

				if (shader_keyword_has("FOG_ENABLED")):
					possible_material_floats["m_start_Fog"] = 1.0
					possible_material_floats["_FogEnabled"] = 1.0
					possible_material_floats["m_end_Fog"] = 0.0

				if (shader_keyword_has("FOG_RATIO_ENABLED")):
					possible_material_floats["_FogRatioEnabled"] = 1.0

				if (shader_keyword_has("SHADOW_COLOR_SHIFT_ENABLED")):
					possible_material_floats["m_start_ShadowColorShift"] = 1.0
					possible_material_floats["_ShadowColorShiftEnabled"] = 1.0
					possible_material_floats["m_end_ShadowColorShift"] = 0.0

				if (shader_keyword_has("SPECULAR_ENABLED")):
					possible_material_floats["m_start_Specular"] = 1.0
					possible_material_floats["_SpecularEnabled"] = 1.0
					possible_material_floats["m_end_Specular"] = 0.0

				if (shader_keyword_has("FAKE_CONSTANT_SPECULAR_ENABLED")):
					possible_material_floats["m_start_FakeConstantSpec"] = 1.0
					possible_material_floats["_FakeConstantSpecularEnabled"] = 1.0
					possible_material_floats["m_end_FakeConstantSpec"] = 0.0

				if (shader_keyword_has("SPECULAR_COLOR_ENABLED")):
					possible_material_floats["m_start_SpecColor"] = 1.0
					possible_material_floats["_SpecularColorEnabled"] = 1.0
					possible_material_floats["m_end_SpecColor"] = 0.0

				if (shader_keyword_has("RIM_LIGHTING_ENABLED")):
					possible_material_floats["m_start_RimLighting"] = 1.0
					possible_material_floats["_RimLightingEnabled"] = 1.0
					possible_material_floats["m_end_RimLighting"] = 0.0

				if (shader_keyword_has("RIM_TRANSPARENCY_ENABLED")):
					possible_material_floats["_RimTransparencyEnabled"] = 1.0

				if (shader_keyword_has("TEXCOORD_OFFSET_ENABLED")):
					possible_material_floats["_TexcoordOffsetEnabled"] = 1.0

				if (shader_keyword_has("NORMAL_MAPP_DXT5_NM_ENABLED")):
					possible_material_floats["_NormalMapDXT5NMEnabled"] = 1.0

				if (shader_keyword_has("NORMAL_MAPP_DXT5_LP_ENABLED")):
					possible_material_floats["_NormalMapDXT5LPEnabled"] = 1.0

				if (shader_keyword_has("NORMAL_MAPPING_ENABLED")):
					possible_material_floats["m_start_NormalMap"] = 1.0
					possible_material_floats["_NormalMappingEnabled"] = 1.0
					possible_material_floats["m_end_NormalMap"] = 0.0

				if (shader_keyword_has("SPECULAR_MAPPING_ENABLED")):
					possible_material_floats["m_start_SpecularMap"] = 1.0
					possible_material_floats["_SpecularMappingEnabled"] = 1.0
					possible_material_floats["m_end_SpecularMap"] = 0.0

				if (shader_keyword_has("OCCULUSION_MAPPING_ENABLED")):
					possible_material_floats["m_start_OcculusionMap"] = 1.0
					possible_material_floats["_OcculusionMappingEnabled"] = 1.0
					possible_material_floats["m_end_OcculusionMap"] = 0.0

				if (shader_keyword_has("EMISSION_MAPPING_ENABLED")):
					possible_material_floats["m_start_EmissionMap"] = 1.0
					possible_material_floats["_EmissionMappingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_ENANLED")):
					possible_material_floats["m_start_MultiUV"] = 1.0
					possible_material_floats["_MultiUVEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_ADDITIVE_BLENDING_ENANLED")):
					possible_material_floats["_MultiUVAdditiveBlendingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_MULTIPLICATIVE_BLENDING_ENANLED")):
					possible_material_floats["_MultiUVMultiplicativeBlendingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_MULTIPLICATIVE_BLENDING_LM_ENANLED")):
					possible_material_floats["_MultiUVMultiplicativeBlendingLMEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_MULTIPLICATIVE_BLENDING_EX_ENANLED")):
					possible_material_floats["_MultiUVMultiplicativeBlendingEXEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_SHADOW_ENANLED")):
					possible_material_floats["_MultiUVShadowEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_FACE_ENANLED")):
					possible_material_floats["_MultiUVFaceEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_TEXCOORD_OFFSET_ENABLED")):
					possible_material_floats["_MultiUVTexCoordOffsetEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_NO_DIFFUSE_MAPPING_ENANLED")):
					possible_material_floats["_MultiUVNoDiffuseEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_NORMAL_MAPPING_ENABLED")):
					possible_material_floats["m_start_MultiUVNormalMap"] = 1.0
					possible_material_floats["_MultiUVNormalMappingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_SPECULAR_MAPPING_ENABLED")):
					possible_material_floats["m_start_MultiUVSpecularMap"] = 1.0
					possible_material_floats["_MultiUVSpecularMappingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_OCCULUSION_MAPPING_ENABLED")):
					possible_material_floats["m_start_MultiUVOcculusionMap"] = 1.0
					possible_material_floats["_MultiUVOcculusionMappingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV_GLARE_MAP_ENABLED")):
					possible_material_floats["m_start_MultiUVGlareMap"] = 1.0
					possible_material_floats["_MultiUVGlareMappingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_ENANLED")):
					possible_material_floats["m_start_MultiUV2"] = 1.0
					possible_material_floats["_MultiUV2Enabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_ADDITIVE_BLENDING_ENANLED")):
					possible_material_floats["_MultiUV2AdditiveBlendingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_MULTIPLICATIVE_BLENDING_ENANLED")):
					possible_material_floats["_MultiUV2MultiplicativeBlendingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_MULTIPLICATIVE_BLENDING_LM_ENANLED")):
					possible_material_floats["_MultiUV2MultiplicativeBlendingLMEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_MULTIPLICATIVE_BLENDING_EX_ENANLED")):
					possible_material_floats["_MultiUV2MultiplicativeBlendingEXEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_SHADOW_ENANLED")):
					possible_material_floats["_MultiUV2ShadowEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_FACE_ENANLED")):
					possible_material_floats["_MultiUV2FaceEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_TEXCOORD_OFFSET_ENABLED")):
					possible_material_floats["_MultiUV2TexCoordOffsetEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_NO_DIFFUSE_MAPPING_ENANLED")):
					possible_material_floats["_MultiUV2NoDiffuseEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_NORMAL_MAPPING_ENABLED")):
					possible_material_floats["m_start_MultiUV2NormalMap"] = 1.0
					possible_material_floats["_MultiUV2NormalMappingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_SPECULAR_MAPPING_ENABLED")):
					possible_material_floats["m_start_MultiUV2SpecularMap"] = 1.0
					possible_material_floats["_MultiUV2SpecularMappingEnabled"] = 1.0

				if (shader_keyword_has("MULTI_UV2_OCCULUSION_MAPPING_ENABLED")):
					possible_material_floats["m_start_MultiUV2OcculusionMap"] = 1.0
					possible_material_floats["_MultiUV2OcculusionMappingEnabled"] = 1.0

				if (shader_keyword_has("CARTOON_SHADING_ENABLED")):
					possible_material_floats["m_start_CartoonShading"] = 1.0
					possible_material_floats["_CartoonShadingEnabled"] = 1.0

				if (shader_keyword_has("CARTOON_HILIGHT_ENABLED")):
					possible_material_floats["m_start_CartoonHilight"] = 1.0
					possible_material_floats["_CartoonHilightEnabled"] = 1.0

				if (shader_keyword_has("EMVMAP_AS_IBL_ENABLED")):
					possible_material_floats["_EMVMapAsIBLEnabled"] = 1.0

				if (shader_keyword_has("SPHERE_MAPPING_ENABLED")):
					possible_material_floats["m_start_SphereMap"] = 1.0
					possible_material_floats["_SphereMappingEnabled"] = 1.0

				if (shader_keyword_has("CUBE_MAPPING_ENABLED")):
					possible_material_floats["m_start_CubeMap"] = 1.0
					possible_material_floats["_CubeMappingEnabled"] = 1.0

				if (shader_keyword_has("PROJECTION_MAP_ENABLED")):
					possible_material_floats["m_start_ProjectionMap"] = 1.0
					possible_material_floats["_ProjectionMappingEnabled"] = 1.0

				if (shader_keyword_has("DUDV_MAPPING_ENABLED")):
					possible_material_floats["m_start_DuDvMap"] = 1.0
					possible_material_floats["_DuDvMappingEnabled"] = 1.0

				if (shader_keyword_has("WINDY_GRASS_ENABLED")):
					possible_material_floats["m_start_WindyGrass"] = 1.0
					possible_material_floats["_WindyGrassEnabled"] = 1.0

				if (shader_keyword_has("WINDY_GRASS_TEXV_WEIGHT_ENABLED")):
					possible_material_floats["_WindyGrassTexVEnabled"] = 1.0

				if (shader_keyword_has("USE_OUTLINE")):
					possible_material_floats["m_start_Outline"] = 1.0
					possible_material_floats["_OutlineEnabled"] = 1.0

				if (shader_keyword_has("USE_OUTLINE_COLOR")):
					possible_material_floats["m_start_OutlineColor"] = 1.0
					possible_material_floats["_OutlineColorEnabled"] = 1.0

				if (shader_keyword_has("USE_SCREEN_UV")):
					possible_material_floats["m_start_ScreenUV"] = 1.0
					possible_material_floats["_ScreenUVEnabled"] = 1.0

				if (shader_keyword_has("GLARE_MAP_ENABLED")):
					possible_material_floats["m_start_GlareMap"] = 1.0
					possible_material_floats["_GlareMappingEnabled"] = 1.0
					possible_material_floats["_GlareHilightPassEnabled"] = 1.0

				if (shader_keyword_has("GLARE_HIGHTPASS_ENABLED")):
					possible_material_floats["_GlareHilightPassEnabled"] = 1.0

				if (shader_keyword_has("ALPHA_BLENDING_ENABLED")):
					possible_material_floats["_SrcBlend"] = 5.0
					possible_material_floats["_DstBlend"] = 10.0
					possible_material_floats["_ZWrite"] = 0.0

				if (shader_keyword_has("ADDITIVE_BLENDING_ENABLED")):
					possible_material_floats["_SrcBlend"] = 5.0
					possible_material_floats["_DstBlend"] = 1.0
					possible_material_floats["_ZWrite"] = 0.0
					possible_material_floats["_AdditiveBlendEnabled"] = 1.0

				if (shader_keyword_has("SUBTRACT_BLENDING_ENABLED") or shader_keyword_has("MULTIPLICATIVE_BLENDING_ENABLED")):
					possible_material_floats["_SrcBlend"] = 0.0
					possible_material_floats["_DstBlend"] = 6.0
					possible_material_floats["_ZWrite"] = 0.0

					if (shader_keyword_has("SUBTRACT_BLENDING_ENABLED")):
						possible_material_floats["_SubtractiveBlendEnabled"] = 1.0

					if (shader_keyword_has("MULTIPLICATIVE_BLENDING_ENABLED")):
						possible_material_floats["_MultiplicativeBlendEnabled"] = 1.0

				if ("_GlareIntensity" in possible_material_floats) and (possible_material_floats["_GlareIntensity"] == 1.0):
					if ((not shader_keyword_has("GLARE_HIGHTPASS_ENABLED")) and (not shader_keyword_has("GLARE_MAP_ENABLED")) and (not shader_keyword_has("MULTI_UV_GLARE_MAP_ENABLED"))):
						possible_material_floats["_GlareIntensity"] = 0.0
				
				# Disable keywords that will be ignored.
				if (shader_keyword_has("NO_ALL_LIGHTING_ENABLED")):
					if (shader_keyword_has("NO_MAIN_LIGHT_SHADING_ENABLED")):
						shader_keyword_remove("NO_MAIN_LIGHT_SHADING_ENABLED")
						possible_material_floats["_NoMainLightShadingEnabled"] = 0.0

					if (shader_keyword_has("HALF_LAMBERT_LIGHTING_ENABLED")):
						shader_keyword_remove("HALF_LAMBERT_LIGHTING_ENABLED")
						possible_material_floats["_HalfLambertLightingEnabled"] = 0.0

					if (shader_keyword_has("CARTOON_SHADING_ENABLED")):
						shader_keyword_remove("CARTOON_SHADING_ENABLED")
						possible_material_floats["_CartoonShadingEnabled"] = 0.0

				if (shader_keyword_has("NO_MAIN_LIGHT_SHADING_ENABLED")):
					if (shader_keyword_has("HALF_LAMBERT_LIGHTING_ENABLED")):
						shader_keyword_remove("HALF_LAMBERT_LIGHTING_ENABLED")
						possible_material_floats["_HalfLambertLightingEnabled"] = 0.0
					
					if (shader_keyword_has("CARTOON_SHADING_ENABLED")):
						shader_keyword_remove("CARTOON_SHADING_ENABLED")
						possible_material_floats["_CartoonShadingEnabled"] = 0.0

				if (shader_keyword_has("CARTOON_SHADING_ENABLED")):
					if (shader_keyword_has("HALF_LAMBERT_LIGHTING_ENABLED")):
						shader_keyword_remove("HALF_LAMBERT_LIGHTING_ENABLED")
						possible_material_floats["_HalfLambertLightingEnabled"] = 0.0

				# Disable keywords that aren't needed.
				if ((shader_keyword_has("TEXCOORD_OFFSET_ENABLED")) or (shader_keyword_has("MULTI_UV_TEXCOORD_OFFSET_ENABLED")) or (shader_keyword_has("MULTI_UV2_TEXCOORD_OFFSET_ENABLED"))):
					if (shader_keyword_has("UVA_SCRIPT_ENABLED")):
						shader_keyword_remove("UVA_SCRIPT_ENABLED")
						possible_material_floats["m_start_UVA"] = 0.0
						possible_material_floats["_UVAEnabled"] = 0.0
						possible_material_floats["m_end_UVA"] = 0.0

				if ((shader_keyword_has("GLARE_MAP_ENABLED")) or (shader_keyword_has("MULTI_UV_GLARE_MAP_ENABLED"))):
					if (shader_keyword_has("GLARE_HIGHTPASS_ENABLED")):
						shader_keyword_remove("GLARE_HIGHTPASS_ENABLED")
						possible_material_floats["_GlareHilightPassEnabled"] = 0.0

				## Mode 2 related stuff
				if isCS3Up:
					if ((not (shader_keyword_has("NO_ALL_LIGHTING_ENABLED"))) and (not (shader_keyword_has("NO_MAIN_LIGHT_SHADING_ENABLED"))) and (not (shader_keyword_has("CARTOON_SHADING_ENABLED")))):
						shader_keyword_add("HALF_LAMBERT_LIGHTING_ENABLED")
						possible_material_floats["_HalfLambertLightingEnabled"] = 1.0
					if (shader_keyword_has("RIM_LIGHTING_ENABLED")):
						shader_keyword_add("RIM_CLAMP_ENABLED")
						possible_material_floats["m_start_RimClamp"] = 1.0
						possible_material_floats["_RimClampEnabled"] = 1.0
						possible_material_floats["m_end_RimClamp"] = 0.0
					shader_keyword_add("FLAT_AMBIENT_ENABLED")
					possible_material_floats["_FlatAmbientEnabled"] = 1.0
				
				if isXanadu:
					if ((not (shader_keyword_has("NO_ALL_LIGHTING_ENABLED"))) and (not (shader_keyword_has("CARTOON_SHADING_ENABLED")))):
						shader_keyword_add("NO_MAIN_LIGHT_SHADING_ENABLED")
						shader_keyword_remove("HALF_LAMBERT_LIGHTING_ENABLED")
						possible_material_floats["_NoMainLightShadingEnabled"] = 1.0
						possible_material_floats["_HalfLambertLightingEnabled"] = 0.0

					if (shader_keyword_has("RIM_LIGHTING_ENABLED")):
						shader_keyword_add("RIM_CLAMP_ENABLED")
						possible_material_floats["m_start_RimClamp"] = 1.0
						possible_material_floats["_RimClampEnabled"] = 1.0
						possible_material_floats["_RimLightClampFactor"] = 2.0
						possible_material_floats["m_end_RimClamp"] = 0.0

				if ("_GlareIntensity" in possible_material_floats) and (possible_material_floats["_GlareIntensity"] == 0.0):
					if ((not (shader_keyword_has("GLARE_HIGHTPASS_ENABLED"))) and (not (shader_keyword_has("GLARE_MAP_ENABLED"))) and (not (shader_keyword_has("ALPHA_BLENDING_ENABLED")))):
						shader_keyword_add("RECEIVE_SHADOWS")
						possible_material_floats["_ReceiveShadowsEnabled"] = 1.0

			shader_fn = ""
			if shader_keyword_has("USE_OUTLINE"):
				if shader_keyword_has("ALPHA_TESTING_ENABLED"):
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Cutout (Outline)"]
				elif shader_keyword_has("ALPHA_BLENDING_ENABLED"):
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent (Outline)"]
				else:
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Opaque (Outline)"]
			else:
				if (shader_keyword_has("ALPHA_TESTING_ENABLED")) and (shader_keyword_has("ALPHA_BLENDING_ENABLED")):
					if (shader_keyword_has("DUDV_MAPPING_ENABLED")) or (shader_keyword_has("WATER_SURFACE_ENABLED")):
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent (Grabpass)"]
					else:
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent"]
				elif shader_keyword_has("ALPHA_TESTING_ENABLED"):
					if (shader_keyword_has("DUDV_MAPPING_ENABLED")) or (shader_keyword_has("WATER_SURFACE_ENABLED")):
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Cutout (Grabpass)"]
					else:
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Cutout"]
				elif shader_keyword_has("ALPHA_BLENDING_ENABLED"):
					if (shader_keyword_has("DUDV_MAPPING_ENABLED")) or (shader_keyword_has("WATER_SURFACE_ENABLED")):
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent (Grabpass)"]
					else:
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent"]
				else:
					if (shader_keyword_has("DUDV_MAPPING_ENABLED")) or (shader_keyword_has("WATER_SURFACE_ENABLED")):
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Opaque (Grabpass)"]
					else:
						shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Opaque"]
			shader_fn_transformed = shader_fn.lower()
			if shader_fn_transformed != "":
				if shader_fn_transformed in basename_to_guid_shader:
					possible_material_root_attributes["m_Shader"] = "{fileID: 4800000, guid: " + basename_to_guid_shader[shader_fn_transformed] + ", type: 3}"
					debug_log("Setting shader " + shader_fn)
				else:
					debug_log("Shader has not been set because it was not found")
			else:
				debug_log("Shader has not been set due to unknown keyword configuration")

			if material_version >= 8:
				possible_material_root_attributes["serializedVersion"] = "8"
				possible_material_root_attributes["m_ValidKeywords"] = "[]" if (len(shader_keywords_list) == 0) else ""
				remove_material_root_attribute("m_ShaderKeywords")
			else:
				possible_material_root_attributes["serializedVersion"] = "6"
				possible_material_root_attributes["m_ShaderKeywords"] = (" ").join(sorted(shader_keywords_list))
				remove_material_root_attribute("m_Parent")
				remove_material_root_attribute("m_ModifiedSerializedProperties")
				remove_material_root_attribute("m_ValidKeywords")
				remove_material_root_attribute("m_InvalidKeywords")
				remove_material_root_attribute("m_LockedProperties")
				remove_material_root_attribute("m_BuildTextureStacks")
			if True:
				material_content_rewrite.append("%YAML 1.1")
				material_content_rewrite.append("%TAG !u! tag:unity3d.com,2011:")
				material_content_rewrite.append("--- !u!21 &2100000")
				material_content_rewrite.append("Material:")
				for k in possible_material_root_attributes_keyorder:
					target_value = possible_material_root_attributes[k]
					material_content_rewrite.append("  " + k + ": " + target_value)
					if k == "m_ValidKeywords":
						for keyword in sorted(shader_keywords_list):
							material_content_rewrite.append("  - " + keyword)
					if k == "m_SavedProperties":
						material_content_rewrite.append("    serializedVersion: 3")
						material_content_rewrite.append("    m_TexEnvs:")
						for item in sorted(possible_material_texenvs.keys()):
							material_content_rewrite.append("    - %s:" % (item))
							material_content_rewrite.append("        m_Texture: %s" % (possible_material_texenvs[item]))
							material_content_rewrite.append("        m_Scale: {x: 1, y: 1}")
							material_content_rewrite.append("        m_Offset: {x: 0, y: 0}")
						if material_version >= 8:
							material_content_rewrite.append("    m_Ints: []")
						material_content_rewrite.append("    m_Floats:")
						for item in sorted(possible_material_floats.keys()):
							material_content_rewrite.append("    - %s: %s" % (item, float_as_shortest_str(possible_material_floats[item])))
						material_content_rewrite.append("    m_Colors:")
						for item in sorted(possible_material_colors.keys()):
							indexed_item = possible_material_colors[item]
							material_content_rewrite.append("    - %s: {r: %s, g: %s, b: %s, a: %s}" % (item, float_as_shortest_str(indexed_item[0]), float_as_shortest_str(indexed_item[1]), float_as_shortest_str(indexed_item[2]), float_as_shortest_str(indexed_item[3])))

			if not config_struct["dry_run"]:
				write_if_unchanged(material_fullpath, "".join([x + "\n" for x in material_content_rewrite if x != ""]))
		else:
			debug_log("Material .mat not found")

	basename_noext = clsuter_basename_noext
	found_model_path = None
	if basename_noext + ".dae" in basename_to_guid_model:
		found_model_path = basename_noext + ".dae"
	if basename_noext + ".fbx" in basename_to_guid_model:
		found_model_path = basename_noext + ".fbx"
	if basename_noext + ".glb.fbx" in basename_to_guid_model:
		found_model_path = basename_noext + ".glb.fbx"
	if found_model_path is not None:
		meta_path = basename_to_projectpath_model[found_model_path] + ".meta"
		debug_log("Handling model " + str(found_model_path))
		meta_dae_content = []
		with open(meta_path, "r", encoding="utf-8") as f:
			meta_dae_content = f.read().split("\n")
		meta_dae_content_rewrite = []
		in_external_objects = False
		for x in meta_dae_content:
			if in_external_objects:
				if (not x.startswith("  - ")) and (not x.startswith("    ")):
					in_external_objects = False
					meta_dae_content_rewrite.append(x)
					continue
			else:
				if x == "  externalObjects:":
					in_external_objects = True
				meta_dae_content_rewrite.append(x)
				if in_external_objects:
					for x in sorted(material_name_to_guid.keys()):
						debug_log("Adding external material for " + str(found_model_path) + " with GUID " + material_name_to_guid[x])
						meta_dae_content_rewrite.append("  - first:")
						meta_dae_content_rewrite.append("      type: UnityEngine:Material")
						meta_dae_content_rewrite.append("      assembly: UnityEngine.CoreModule")
						meta_dae_content_rewrite.append("      name: " + x)
						meta_dae_content_rewrite.append("    second: {fileID: 2100000, guid: " + material_name_to_guid[x] + ", type: 2}")
		if not config_struct["dry_run"]:
			write_if_unchanged(meta_path, "".join([x + "\n" for x in meta_dae_content_rewrite if x != ""]))
	else:
		debug_log("Model for " + str(found_model_path) + " not found")

	if debug_list is not None and len(debug_list) > 0:
		with open(in_filename + ".matsetdebug.txt", "w", encoding="utf-8") as f:
			for line in debug_list:
				f.write(line + "\n")

def get_parser():
	import argparse

	parser = argparse.ArgumentParser(
		description='Utility to insert materials from ED8 into Unity prefabs automatically.',
		usage='Use "%(prog)s --help" for more information.',
		fromfile_prefix_chars='@',
		formatter_class=argparse.RawTextHelpFormatter)
	return parser

def add_common_arguments(parser):
	import textwrap

	parser.add_argument("--dry-run",
		type=str,
		default=str(False),
		help=textwrap.dedent('''\
			Do not output or modify any files.
		''')
		)
	parser.add_argument("--backup-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path of a directory to save the backup of the modified files.
			If this is not specified, it will default to the same path of the directory of the original file.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path to save material configuration to unity .mat files.
			The old .mat files will be backed up before saving.
			The path specified by this argument needs to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-texture-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path containing .png.meta, .dds.meta, .fbx.meta, and .shader.meta files.
			If the string is empty, the above option will be used for the path instead.
			The path specified by this argument needs to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-model-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path containing .fbx.meta files.
			If the string is empty, the texture path option will be used for the path instead.
			The path specified by this argument needs to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-shader-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path containing .shader.meta files.
			If the string is empty, the texture path option will be used for the path instead.
			The path specified by this argument needs to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-inf-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path containing .inf files.
			If the string is empty, the information contained in the file will not be inserted.
			The path specified by this argument does not need to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-uvb-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path containing .uvb files.
			If the string is empty, the information contained in the file will not be inserted.
			The path specified by this argument does not need to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-effect-json-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path containing .effect.json files.
			If the string is empty, the information contained in the file will not be inserted.
			The path specified by this argument does not need to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-texture-json-path",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Set this to a path containing .texture.json files.
			If the string is empty, the information contained in the file will not be inserted.
			The path specified by this argument does not need to be in the Assets directory of the Unity project.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-debug",
		type=str,
		default=str(False),
		help=textwrap.dedent('''\
			Debug saving material configuration.
			This option can be used to determine when files are not found or variables are not set correctly.
			This will create a .matsetdebug.txt file
			Not affected by the --dry-run command line argument.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-create-materials",
		type=str,
		default=str(True),
		help=textwrap.dedent('''\
			Create .mat files if they do not already exist.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-compress-textures",
		type=str,
		default=str(True),
		help=textwrap.dedent('''\
			Set the Unity metadata to compress textures using Unity Crunch format.
			If this option is disabled, it will not use Unity Crunch format.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-apply-previous-configuration",
		type=str,
		default=str(True),
		help=textwrap.dedent('''\
			If previous material configuration exists already, apply it.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-apply-shader-keyword-configuration",
		type=str,
		default=str(True),
		help=textwrap.dedent('''\
			Applies the new material configuration on top of the current one based on shader keywords.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-apply-shader-parameter-configuration",
		type=str,
		default=str(True),
		help=textwrap.dedent('''\
			Applies the new material configuration on top of the current one based on shader parameters.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-filter-shader-parameter",
		type=str,
		default="",
		help=textwrap.dedent('''\
			Applies the new material configuration on top of the current one only based on shader parameters passed in as comma delimited list.
		''')
		)
	parser.add_argument("--save-material-configuration-to-unity-metadata-material-version",
		type=str,
		default="6",
		help=textwrap.dedent('''\
			The target version to generate material data.
		''')
		)

def handle_common_arguments(args_namespace, config_struct):
	def set_path(dic, in_key, in_path):
		import os
		new_path = ""

		if in_path != "":
			new_path = os.path.realpath(in_path)
			if not os.path.isdir(new_path):
				raise Exception("Path passed in for " + in_key + " is not existent")
		dic[in_key] = new_path
	config_struct["dry_run"] = args_namespace.dry_run.lower() == "true"
	set_path(config_struct, "backup_path", args_namespace.backup_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_path", args_namespace.save_material_configuration_to_unity_metadata_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_texture_path", args_namespace.save_material_configuration_to_unity_metadata_texture_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_model_path", args_namespace.save_material_configuration_to_unity_metadata_model_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_shader_path", args_namespace.save_material_configuration_to_unity_metadata_shader_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_inf_path", args_namespace.save_material_configuration_to_unity_metadata_inf_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_uvb_path", args_namespace.save_material_configuration_to_unity_metadata_uvb_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_effect_json_path", args_namespace.save_material_configuration_to_unity_metadata_effect_json_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_texture_json_path", args_namespace.save_material_configuration_to_unity_metadata_texture_json_path)
	config_struct["save_material_configuration_to_unity_metadata_debug"] = args_namespace.save_material_configuration_to_unity_metadata_debug.lower() == "true"
	config_struct["save_material_configuration_to_unity_metadata_create_materials"] = args_namespace.save_material_configuration_to_unity_metadata_create_materials.lower() == "true"
	config_struct["save_material_configuration_to_unity_metadata_compress_textures"] = args_namespace.save_material_configuration_to_unity_metadata_compress_textures.lower() == "true"
	config_struct["save_material_configuration_to_unity_metadata_apply_previous_configuration"] = args_namespace.save_material_configuration_to_unity_metadata_apply_previous_configuration.lower() == "true"
	config_struct["save_material_configuration_to_unity_metadata_apply_shader_keyword_configuration"] = args_namespace.save_material_configuration_to_unity_metadata_apply_shader_keyword_configuration.lower() == "true"
	config_struct["save_material_configuration_to_unity_metadata_apply_shader_parameter_configuration"] = args_namespace.save_material_configuration_to_unity_metadata_apply_shader_parameter_configuration.lower() == "true"
	config_struct["save_material_configuration_to_unity_metadata_filter_shader_parameter"] = args_namespace.save_material_configuration_to_unity_metadata_filter_shader_parameter
	config_struct["save_material_configuration_to_unity_metadata_material_version"] = int(args_namespace.save_material_configuration_to_unity_metadata_material_version)

class UnityMatPostProcessHandler:
	def __init__(self):
		pass

	def parse_start(self, module, args=[]):
		parser = get_parser()
		add_common_arguments(parser)

		args_namespace, remaining_args = parser.parse_known_args(args=args)
		config_struct = {}
		handle_common_arguments(args_namespace, config_struct)
		self.config_struct = config_struct
		self.module = module
		return remaining_args

	def parse_cluster(self, cluster_mesh_info=None):
		import os
		config_struct = self.config_struct
		config_struct["input_file"] = os.path.splitext(cluster_mesh_info.filename)[0] + ".material.json"
		config_struct["input_structure"] = self.module.DUMP_convert_material_to_structure(cluster_mesh_info)
		save_unity_mat(config_struct)

	def parse_finish(self):
		pass

def get_postprocess_handler():
	return UnityMatPostProcessHandler()

def standalone_main():
	parser = get_parser()
	parser.add_argument("input_file",
		type=str, 
		help="The input .material.json file.")
	add_common_arguments(parser)

	args_namespace = parser.parse_args()

	config_struct = {}
	config_struct["input_file"] = args_namespace.input_file
	handle_common_arguments(args_namespace, config_struct)

	save_unity_mat(config_struct)

if __name__ == "__main__":
	standalone_main()
