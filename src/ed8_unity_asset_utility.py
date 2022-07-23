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
	debug_list = None
	if config_struct["save_material_configuration_to_unity_metadata_debug"]:
		debug_list = []
	def debug_log(ln):
		if debug_list is not None:
			debug_list.append(ln)

	in_filename = config_struct["input_file"]

	in_structure = None
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
				file_name = os.path.basename(file).lower()
				if file_ext == None or file_name.endswith(file_ext):
					file_name_modified = file_name
					if file_ext != None:
						file_name_modified = file_name[:-(len(file_ext))]
					out_fullpath_dict[file_name_modified] = str(file)

	def readdir_meta_to_guid_and_fullpath(in_path, out_guid_dict, out_fullpath_dict):
		import pathlib
		if in_path != "":
			in_path_pathobj = pathlib.Path(in_path)
			for file in sorted(in_path_pathobj.glob('**/*')):
				if str(file).endswith(".meta"):
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

	# Just copy variables for now
	basename_to_guid_model = basename_to_guid_texture
	basename_to_projectpath_model = basename_to_projectpath_texture
	basename_to_guid_shader = basename_to_guid_texture
	basename_to_projectpath_shader = basename_to_projectpath_texture

	basename_to_path_inf = {}
	readdir_to_basename_fullpath_dict(config_struct["save_material_configuration_to_unity_metadata_inf_path"], basename_to_path_inf, ".inf")

	basename_to_path_uvb = {}
	readdir_to_basename_fullpath_dict(config_struct["save_material_configuration_to_unity_metadata_uvb_path"], basename_to_path_uvb, ".uvb")

	basename_to_path_effect_json = {}
	readdir_to_basename_fullpath_dict(config_struct["save_material_configuration_to_unity_metadata_effect_json_path"], basename_to_path_effect_json, ".effect.json")

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
			if os.path.isfile(meta_path):
				backup_count = 0
				while os.path.isfile(meta_path + ".bak" + str(backup_count)):
					backup_count += 1
				os.rename(meta_path, meta_path + ".bak" + str(backup_count))

			with open(meta_path, "w", encoding="utf-8") as f:
				for line in lns:
					if line != "":
						f.write(line + "\n")
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
		parameters_samplerstate = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_tweakableShaderParameterDefinitionsObjectReferencesSamplerStateIndexes"]
		parameters_imports = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_tweakableShaderParameterDefinitionsObjectReferencesAssetReferenceImportIndexes"]
		for key in sorted(parameters_imports.keys()):
			if (key + "S") in parameters_samplerstate:
				texture_fullpath_to_sampler[asset_reference_import_objs[parameters_imports[key]]["m_id"]] = sampler_state_objs[parameters_samplerstate[key + "S"]]
			elif (key + "Sampler") in parameters_samplerstate:
				texture_fullpath_to_sampler[asset_reference_import_objs[parameters_imports[key]]["m_id"]] = sampler_state_objs[parameters_samplerstate[key + "Sampler"]]

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
			basename_noext = os.path.basename(v["m_id"]).split(".", 1)[0].lower()
			found_texture_path = None
			if basename_noext + ".png" in basename_to_guid_texture:
				found_texture_path = basename_noext + ".png"
			elif basename_noext + ".dds" in basename_to_guid_texture:
				found_texture_path = basename_noext + ".dds"
			if found_texture_path is not None:
				texture_fullpath_to_guid[v["m_id"]] = basename_to_guid_texture[found_texture_path]
				meta_path = basename_to_projectpath_texture[found_texture_path] + ".meta"
				debug_log("Handling texture " + str(v["m_id"]))
				if v["m_id"] in texture_fullpath_to_sampler:
					samplerstate = texture_fullpath_to_sampler[v["m_id"]]
					wrapS = 0
					wrapT = 0
					filterMode = 2
					aniso = 8
					alphaIsTransparency = 1
					textureCompression = 0
					compressionQuality = 100
					crunchedCompression = 0
					if config_struct["save_material_configuration_to_unity_metadata_compress_textures"]:
						textureCompression = 1
						crunchedCompression = 1
					if samplerstate["m_wrapS"] in wrap_map:
						wrapS = wrap_map[samplerstate["m_wrapS"]]
					if samplerstate["m_wrapT"] in wrap_map:
						wrapT = wrap_map[samplerstate["m_wrapT"]]
					texture_changed = False
					meta_png_content = []
					with open(meta_path, "r", encoding="utf-8") as f:
						meta_png_content = f.read().split("\n")
					for i in range(len(meta_png_content)):
						if meta_png_content[i].startswith("    wrapU: "):
							new_wrap_argument = "    wrapU: " + str(wrapS)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("    wrapV: "):
							new_wrap_argument = "    wrapV: " + str(wrapT)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("    filterMode: "):
							new_wrap_argument = "    filterMode: " + str(filterMode)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("    aniso: "):
							new_wrap_argument = "    aniso: " + str(aniso)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("  alphaIsTransparency: "):
							new_wrap_argument = "  alphaIsTransparency: " + str(alphaIsTransparency)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("    textureCompression: "):
							new_wrap_argument = "    textureCompression: " + str(textureCompression)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("  compressionQuality: "):
							new_wrap_argument = "  compressionQuality: " + str(compressionQuality)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("    compressionQuality: "):
							new_wrap_argument = "    compressionQuality: " + str(compressionQuality)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
						if meta_png_content[i].startswith("    crunchedCompression: "):
							new_wrap_argument = "    crunchedCompression: " + str(crunchedCompression)
							if new_wrap_argument != meta_png_content[i]:
								meta_png_content[i] = new_wrap_argument
								texture_changed = True
							continue
					if texture_changed:
						if not config_struct["dry_run"]:
							backup_count = 0
							while os.path.isfile(meta_path + ".bak" + str(backup_count)):
								backup_count += 1
							os.rename(meta_path, meta_path + ".bak" + str(backup_count))

							with open(meta_path, "w", encoding="utf-8") as f:
								for line in meta_png_content:
									if line != "":
										f.write(line + "\n")
					else:
						debug_log("Texture unchanged")
				else:
					debug_log("Sampler state not found")
			else:
				debug_log("Texture for " + str(v["m_id"]) + " not found")
		elif v["m_targetAssetType"] == "PEffectVariant":
			effectvariant_basename = os.path.basename(v["m_id"]).lower()
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
				effectvariant_fullpath_to_switches[v["m_id"]] = effect_switches_list
			else:
				debug_log("Effect variant file not found for " + v["m_id"])

	material_name_to_guid = {}
	for v in material_objs:
		effectvariant_dict = None
		shader_keywords_list = []
		shader_keywords_str = ""
		if v["m_effectVariantIndex"] != None:
			effect_variant_path = asset_reference_import_objs[v["m_effectVariantIndex"]]["m_id"]
			if effect_variant_path in effectvariant_fullpath_to_switches:
				shader_keywords_list = effectvariant_fullpath_to_switches[effect_variant_path]
				shader_keywords_str = (" ").join(shader_keywords_list)
		shader_fn = ""
		if "USE_OUTLINE" in shader_keywords_list:
			if "ALPHA_TESTING_ENABLED" in shader_keywords_list:
				shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Cutout (Outline)"]
			elif "ALPHA_BLENDING_ENABLED" in shader_keywords_list:
				shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent (Outline)"]
			else:
				shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Opaque (Outline)"]
		else:
			if "ALPHA_TESTING_ENABLED" in shader_keywords_list:
				if ("DUDV_MAPPING_ENABLED" in shader_keywords_list) or ("WATER_SURFACE_ENABLED" in shader_keywords_list):
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Cutout (Grabpass)"]
				else:
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Cutout"]
			elif "ALPHA_BLENDING_ENABLED" in shader_keywords_list:
				if ("DUDV_MAPPING_ENABLED" in shader_keywords_list) or ("WATER_SURFACE_ENABLED" in shader_keywords_list):
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent (Grabpass)"]
				else:
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Transparent"]
			else:
				if ("DUDV_MAPPING_ENABLED" in shader_keywords_list) or ("WATER_SURFACE_ENABLED" in shader_keywords_list):
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Opaque (Grabpass)"]
				else:
					shader_fn = shader_name_to_basename["ED8/Cold Steel Shader/Opaque"]
		shader_str = "{fileID: 0}"
		shader_fn_transformed = shader_fn.lower()
		if (shader_fn_transformed != "") and (shader_fn_transformed in basename_to_guid_shader):
			shader_str = "{fileID: 4800000, guid: " + basename_to_guid_shader[shader_fn_transformed] + ", type: 3}"
			debug_log("Setting shader " + shader_fn)

		debug_log("Handling material " + v["mu_name"] + " (" + v["mu_materialname"] + ")")
		matname = (v["mu_materialname"] + ".mat").lower()
		if True:
			material_name_to_guid[v["mu_materialname"]] = get_guid_for_path(matname, config_struct["save_material_configuration_to_unity_metadata_path"], basename_to_guid_mat, basename_to_projectpath_mat)
			fullpath = basename_to_projectpath_mat[matname]
			material_content_rewrite = []

			parameters = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_shaderParameters"]
			gamematid = None
			possible_material_texenvs = {}
			possible_material_floats = {}
			possible_material_colors = {}
			parameters_for_textures = parameter_buffer_objs[v["m_parameterBufferIndex"]]["mu_tweakableShaderParameterDefinitionsObjectReferencesAssetReferenceImportIndexes"]
			for key in parameters_for_textures.keys():
				transformed_parameter_name = "_" + key
				if key == "DiffuseMapSampler":
					transformed_parameter_name = "_MainTex"
				debug_log("Handling shader parameter  " + key + "; transformed " + transformed_parameter_name)
				parameter_value = asset_reference_import_objs[parameters_for_textures[key]]["m_id"]
				if True:
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
			for key in parameters.keys():
				transformed_parameter_name = "_" + key
				parameter_value = parameters[key]
				if key == "DiffuseMapSampler":
					transformed_parameter_name = "_MainTex"
				debug_log("Handling shader parameter  " + key + "; transformed " + transformed_parameter_name)
				if key == "GameMaterialID":
					gamematid = int(parameter_value[0])
				if True:
					if not (type(parameter_value) is str):
						if len(parameter_value) == 1:
							param_float = parameter_value[0]
							if key == "WindyGrassSpeed":
								param_float *= 2
							possible_material_floats[transformed_parameter_name] = param_float
							debug_log("Mapped float " + key + " in shader parameters")
						else:
							debug_log("Did not map float: Parameter length is too long (" + str(len(parameter_value)) + ")")
					else:
						debug_log("Did not map float: Invalid type (" + str(type(parameter_value)) + ")")
				if True:
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
			if gamematid is not None:
				if gamematid in gameid_to_parameters:
					gameid_to_parameters_item = gameid_to_parameters[gamematid]
					for key in gameid_to_parameters_item.keys():
						possible_material_colors[key] = gameid_to_parameters_item[key]
						debug_log("Mapped color " + key + " in shader parameters (for GameMaterialID)")
				else:
					debug_log("Could not map GameMaterialID for this material")
			else:
				debug_log("Could not detect GameMaterialID for this material")

			if True:
				# TODO: DOUBLE_SIDED, CASTS_SHADOWS_ONLY, CASTS_SHADOWS, RECEIVE_SHADOWS, _FogRangeParameters, _HemiSphereAmbientAxis

				if ("NOTHING_ENABLED" in shader_keywords_list):
					possible_material_floats["_NothingEnabled"] = 1.0

				if ("WATER_SURFACE_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_WaterSurface"] = 1.0
					possible_material_floats["_WaterSurfaceEnabled"] = 1.0
					possible_material_floats["m_end_WaterSurface"] = 0.0

				if ("TRANSPARENT_DELAY_ENABLED" in shader_keywords_list):
					possible_material_floats["_TransparentDelayEnabled"] = 1.0

				if ("VERTEX_COLOR_ENABLED" in shader_keywords_list):
					possible_material_floats["_VertexColorEnabled"] = 1.0

				if ("BLEND_VERTEX_COLOR_BY_ALPHA_ENABLED" in shader_keywords_list):
					possible_material_floats["_BlendVertexColorAlphaEnabled"] = 1.0

				if ("NO_ALL_LIGHTING_ENABLED" in shader_keywords_list):
					possible_material_floats["_NoAllLightingEnabled"] = 1.0

				if ("NO_MAIN_LIGHT_SHADING_ENABLED" in shader_keywords_list):
					possible_material_floats["_NoMainLightShadingEnabled"] = 1.0

				if ("HALF_LAMBERT_LIGHTING_ENABLED" in shader_keywords_list):
					possible_material_floats["_HalfLambertLightingEnabled"] = 1.0

				if ("LIGHT_DIRECTION_FOR_CHARACTER_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_PortraitLight"] = 1.0
					possible_material_floats["_PortraitLightEnabled"] = 1.0
					possible_material_floats["m_end_PortraitLight"] = 0.0

				if ("UVA_SCRIPT_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_UVA"] = 1.0
					possible_material_floats["_UVAEnabled"] = 1.0
					possible_material_floats["m_end_UVA"] = 0.0

				if ("FAR_CLIP_BY_DITHER_ENABLED" in shader_keywords_list):
					possible_material_floats["_FarClipDitherEnabled"] = 1.0

				if ("FOG_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_Fog"] = 1.0
					possible_material_floats["_FogEnabled"] = 1.0
					possible_material_floats["m_end_Fog"] = 0.0

				if ("FOG_RATIO_ENABLED" in shader_keywords_list):
					possible_material_floats["_FogRatioEnabled"] = 1.0

				if ("SHADOW_COLOR_SHIFT_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_ShadowColorShift"] = 1.0
					possible_material_floats["_ShadowColorShiftEnabled"] = 1.0
					possible_material_floats["m_end_ShadowColorShift"] = 0.0

				if ("SPECULAR_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_Specular"] = 1.0
					possible_material_floats["_SpecularEnabled"] = 1.0
					possible_material_floats["m_end_Specular"] = 0.0

				if ("FAKE_CONSTANT_SPECULAR_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_FakeConstantSpec"] = 1.0
					possible_material_floats["_FakeConstantSpecularEnabled"] = 1.0
					possible_material_floats["m_end_FakeConstantSpec"] = 0.0

				if ("SPECULAR_COLOR_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_SpecColor"] = 1.0
					possible_material_floats["_SpecularColorEnabled"] = 1.0
					possible_material_floats["m_end_SpecColor"] = 0.0

				if ("RIM_LIGHTING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_RimLighting"] = 1.0
					possible_material_floats["_RimLightingEnabled"] = 1.0
					possible_material_floats["m_end_RimLighting"] = 0.0

				if ("RIM_TRANSPARENCY_ENABLED" in shader_keywords_list):
					possible_material_floats["_RimTransparencyEnabled"] = 1.0

				if ("RIM_CLAMP_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_RimClamp"] = 1.0
					possible_material_floats["_RimClampEnabled"] = 1.0
					possible_material_floats["m_end_RimClamp"] = 0.0

				if ("TEXCOORD_OFFSET_ENABLED" in shader_keywords_list):
					possible_material_floats["_TexcoordOffsetEnabled"] = 1.0

				if ("NORMAL_MAPP_DXT5_NM_ENABLED" in shader_keywords_list):
					possible_material_floats["_NormalMapDXT5NMEnabled"] = 1.0

				if ("NORMAL_MAPP_DXT5_LP_ENABLED" in shader_keywords_list):
					possible_material_floats["_NormalMapDXT5LPEnabled"] = 1.0

				if ("NORMAL_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_NormalMap"] = 1.0
					possible_material_floats["_NormalMappingEnabled"] = 1.0
					possible_material_floats["m_end_NormalMap"] = 0.0

				if ("SPECULAR_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_SpecularMap"] = 1.0
					possible_material_floats["_SpecularMappingEnabled"] = 1.0
					possible_material_floats["m_end_SpecularMap"] = 0.0

				if ("OCCULUSION_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_OcculusionMap"] = 1.0
					possible_material_floats["_OcculusionMappingEnabled"] = 1.0
					possible_material_floats["m_end_OcculusionMap"] = 0.0

				if ("EMISSION_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_EmissionMap"] = 1.0
					possible_material_floats["_EmissionMappingEnabled"] = 1.0

				if ("MULTI_UV_ENANLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUV"] = 1.0
					possible_material_floats["_MultiUVEnabled"] = 1.0

				if ("MULTI_UV_ADDITIVE_BLENDING_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUVAdditiveBlendingEnabled"] = 1.0

				if ("MULTI_UV_MULTIPLICATIVE_BLENDING_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUVMultiplicativeBlendingEnabled"] = 1.0

				if ("MULTI_UV_MULTIPLICATIVE_BLENDING_LM_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUVMultiplicativeBlendingLMEnabled"] = 1.0

				if ("MULTI_UV_MULTIPLICATIVE_BLENDING_EX_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUVMultiplicativeBlendingEXEnabled"] = 1.0

				if ("MULTI_UV_SHADOW_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUVShadowEnabled"] = 1.0

				if ("MULTI_UV_FACE_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUVFaceEnabled"] = 1.0

				if ("MULTI_UV_TEXCOORD_OFFSET_ENABLED" in shader_keywords_list):
					possible_material_floats["_MultiUVTexCoordOffsetEnabled"] = 1.0

				if ("MULTI_UV_NO_DIFFUSE_MAPPING_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUVNoDiffuseEnabled"] = 1.0

				if ("MULTI_UV_NORMAL_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUVNormalMap"] = 1.0
					possible_material_floats["_MultiUVNormalMappingEnabled"] = 1.0

				if ("MULTI_UV_SPECULAR_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUVSpecularMap"] = 1.0
					possible_material_floats["_MultiUVSpecularMappingEnabled"] = 1.0

				if ("MULTI_UV_OCCULUSION_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUVOcculusionMap"] = 1.0
					possible_material_floats["_MultiUVOcculusionMappingEnabled"] = 1.0

				if ("MULTI_UV_GLARE_MAP_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUVGlareMap"] = 1.0
					possible_material_floats["_MultiUVGlareMappingEnabled"] = 1.0

				if ("MULTI_UV2_ENANLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUV2"] = 1.0
					possible_material_floats["_MultiUV2Enabled"] = 1.0

				if ("MULTI_UV2_ADDITIVE_BLENDING_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2AdditiveBlendingEnabled"] = 1.0

				if ("MULTI_UV2_MULTIPLICATIVE_BLENDING_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2MultiplicativeBlendingEnabled"] = 1.0

				if ("MULTI_UV2_MULTIPLICATIVE_BLENDING_LM_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2MultiplicativeBlendingLMEnabled"] = 1.0

				if ("MULTI_UV2_MULTIPLICATIVE_BLENDING_EX_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2MultiplicativeBlendingEXEnabled"] = 1.0

				if ("MULTI_UV2_SHADOW_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2ShadowEnabled"] = 1.0

				if ("MULTI_UV2_FACE_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2FaceEnabled"] = 1.0

				if ("MULTI_UV2_TEXCOORD_OFFSET_ENABLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2TexCoordOffsetEnabled"] = 1.0

				if ("MULTI_UV2_NO_DIFFUSE_MAPPING_ENANLED" in shader_keywords_list):
					possible_material_floats["_MultiUV2NoDiffuseEnabled"] = 1.0

				if ("MULTI_UV2_NORMAL_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUV2NormalMap"] = 1.0
					possible_material_floats["_MultiUV2NormalMappingEnabled"] = 1.0

				if ("MULTI_UV2_SPECULAR_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUV2SpecularMap"] = 1.0
					possible_material_floats["_MultiUV2SpecularMappingEnabled"] = 1.0

				if ("MULTI_UV2_OCCULUSION_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_MultiUV2OcculusionMap"] = 1.0
					possible_material_floats["_MultiUV2OcculusionMappingEnabled"] = 1.0

				if ("CARTOON_SHADING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_CartoonShading"] = 1.0
					possible_material_floats["_CartoonShadingEnabled"] = 1.0

				if ("CARTOON_HILIGHT_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_CartoonHilight"] = 1.0
					possible_material_floats["_CartoonHilightEnabled"] = 1.0

				if ("EMVMAP_AS_IBL_ENABLED" in shader_keywords_list):
					possible_material_floats["_EMVMapAsIBLEnabled"] = 1.0

				if ("SPHERE_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_SphereMap"] = 1.0
					possible_material_floats["_SphereMappingEnabled"] = 1.0

				if ("CUBE_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_CubeMap"] = 1.0
					possible_material_floats["_CubeMappingEnabled"] = 1.0

				if ("PROJECTION_MAP_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_ProjectionMap"] = 1.0
					possible_material_floats["_ProjectionMappingEnabled"] = 1.0

				if ("DUDV_MAPPING_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_DuDvMap"] = 1.0
					possible_material_floats["_DuDvMappingEnabled"] = 1.0

				if ("WINDY_GRASS_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_WindyGrass"] = 1.0
					possible_material_floats["_WindyGrassEnabled"] = 1.0

				if ("WINDY_GRASS_TEXV_WEIGHT_ENABLED" in shader_keywords_list):
					possible_material_floats["_WindyGrassTexVEnabled"] = 1.0

				if ("USE_OUTLINE" in shader_keywords_list):
					possible_material_floats["m_start_Outline"] = 1.0
					possible_material_floats["_OutlineEnabled"] = 1.0

				if ("USE_OUTLINE_COLOR" in shader_keywords_list):
					possible_material_floats["m_start_OutlineColor"] = 1.0
					possible_material_floats["_OutlineColorEnabled"] = 1.0

				if ("USE_SCREEN_UV" in shader_keywords_list):
					possible_material_floats["m_start_ScreenUV"] = 1.0
					possible_material_floats["_ScreenUVEnabled"] = 1.0

				if ("GLARE_MAP_ENABLED" in shader_keywords_list):
					possible_material_floats["m_start_GlareMap"] = 1.0
					possible_material_floats["_GlareMappingEnabled"] = 1.0

				if ("GLARE_HIGHTPASS_ENABLED" in shader_keywords_list):
					possible_material_floats["_GlareHilightPassEnabled"] = 1.0

				if ("ALPHA_BLENDING_ENABLED" in shader_keywords_list):
					possible_material_floats["_SrcBlend"] = 5.0
					possible_material_floats["_DstBlend"] = 10.0
					possible_material_floats["_ZWrite"] = 0.0

				if ("ADDITIVE_BLENDING_ENABLED" in shader_keywords_list):
					possible_material_floats["_SrcBlend"] = 5.0
					possible_material_floats["_DstBlend"] = 1.0
					possible_material_floats["_ZWrite"] = 0.0
					possible_material_floats["_AdditiveBlendEnabled"] = 1.0

				if ("SUBTRACT_BLENDING_ENABLED" in shader_keywords_list or "MULTIPLICATIVE_BLENDING_ENABLED" in shader_keywords_list):
					possible_material_floats["_SrcBlend"] = 0.0
					possible_material_floats["_DstBlend"] = 6.0
					possible_material_floats["_ZWrite"] = 0.0

					if ("SUBTRACT_BLENDING_ENABLED" in shader_keywords_list):
						possible_material_floats["_SubtractiveBlendEnabled"] = 1.0

					if ("MULTIPLICATIVE_BLENDING_ENABLED" in shader_keywords_list):
						possible_material_floats["_MultiplicativeBlendEnabled"] = 1.0

				if ("_GlareIntensity" in possible_material_floats) and (possible_material_floats["_GlareIntensity"] == 1.0):
					if ((not "GLARE_HIGHTPASS_ENABLED" in shader_keywords_list) and (not "GLARE_MAP_ENABLED" in shader_keywords_list)):
						possible_material_floats["_GlareIntensity"] = 0.0

				possible_material_floats["_Instancing"] = 1.0

				# Lighting
				possible_material_colors["_GlobalAmbientColor"] = [0.50, 0.50, 0.50, 1]
				possible_material_colors["_HemiSphereAmbientSkyColor"] = [0.55, 0.55, 0.55, 1]
				possible_material_colors["_HemiSphereAmbientGndColor"] = [0.55, 0.55, 0.55, 1]
				possible_material_colors["_FogColor"] = [0.44, 0.62, 0.60, 0]
				possible_material_floats["_FogRateClamp"] = 1
				possible_material_colors["_GameMaterialDiffuse"] = [1.00, 1.00, 1.00, 1.00]
				possible_material_colors["_GameMaterialEmission"] = [0.0, 0.0, 0.0, 0.0]

			if True:
				material_content_rewrite.append("%YAML 1.1")
				material_content_rewrite.append("%TAG !u! tag:unity3d.com,2011:")
				material_content_rewrite.append("--- !u!21 &2100000")
				material_content_rewrite.append("Material:")
				material_content_rewrite.append("  serializedVersion: 6")
				material_content_rewrite.append("  m_ObjectHideFlags: 0")
				material_content_rewrite.append("  m_CorrespondingSourceObject: {fileID: 0}")
				material_content_rewrite.append("  m_PrefabInstance: {fileID: 0}")
				material_content_rewrite.append("  m_PrefabAsset: {fileID: 0}")
				material_content_rewrite.append("  m_Name: " + v["mu_materialname"])
				material_content_rewrite.append("  m_Shader: " + shader_str)
				material_content_rewrite.append("  m_ShaderKeywords: " + shader_keywords_str)
				material_content_rewrite.append("  m_LightmapFlags: 4")
				material_content_rewrite.append("  m_EnableInstancingVariants: 0")
				material_content_rewrite.append("  m_DoubleSidedGI: 0")
				material_content_rewrite.append("  m_CustomRenderQueue: -1")
				material_content_rewrite.append("  stringTagMap: {}")
				material_content_rewrite.append("  disabledShaderPasses: []")
				material_content_rewrite.append("  m_SavedProperties:")
				material_content_rewrite.append("    serializedVersion: 3")
				material_content_rewrite.append("    m_TexEnvs:")
				for item in sorted(possible_material_texenvs.keys()):
					material_content_rewrite.append("    - " + item + ":")
					material_content_rewrite.append("        m_Texture: " + possible_material_texenvs[item])
					material_content_rewrite.append("        m_Scale: {x: 1, y: 1}")
					material_content_rewrite.append("        m_Offset: {x: 0, y: 0}")
				material_content_rewrite.append("    m_Floats:")
				for item in sorted(possible_material_floats.keys()):
					material_content_rewrite.append("    - " + item + ": " + str(possible_material_floats[item]))
				material_content_rewrite.append("    m_Colors:")
				for item in sorted(possible_material_colors.keys()):
					indexed_item = possible_material_colors[item]
					material_content_rewrite.append("    - " + item + ": " + "{r: " + str(indexed_item[0]) + ", g: " + str(indexed_item[1]) + ", b: " + str(indexed_item[2]) + ", a: " + str(indexed_item[3]) + "}")

			if not config_struct["dry_run"]:
				if os.path.isfile(fullpath):
					backup_count = 0
					while os.path.isfile(fullpath + ".bak" + str(backup_count)):
						backup_count += 1
					os.rename(fullpath, fullpath + ".bak" + str(backup_count))

				with open(fullpath, "w", encoding="utf-8") as f:
					for line in material_content_rewrite:
						if line != "":
							f.write(line + "\n")
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
			backup_count = 0
			while os.path.isfile(meta_path + ".bak" + str(backup_count)):
				backup_count += 1
			os.rename(meta_path, meta_path + ".bak" + str(backup_count))

			with open(meta_path, "w", encoding="utf-8") as f:
				for line in meta_dae_content_rewrite:
					if line != "":
						f.write(line + "\n")
	else:
		debug_log("Model for " + str(found_model_path) + " not found")

	if debug_list is not None and len(debug_list) > 0:
		with open(in_filename + ".matsetdebug.txt", "w", encoding="utf-8") as f:
			for line in debug_list:
				f.write(line + "\n")

def standalone_main():
	import argparse
	import textwrap

	parser = argparse.ArgumentParser(
		description='Utility to insert materials from ED8 into Unity prefabs automatically.',
		usage='Use "%(prog)s --help" for more information.',
		formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument("input_file",
		type=str, 
		help="The input .material.json file.")
	parser.add_argument("--dry-run",
		type=str,
		default=str(False),
		help=textwrap.dedent('''\
			Do not output or modify any files.
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
	parser.add_argument("--save-material-configuration-to-unity-metadata-compress-textures",
		type=str,
		default=str(True),
		help=textwrap.dedent('''\
			Set the Unity metadata to compress textures using Unity Crunch format.
			If this option is disabled, it will not use Unity Crunch format.
		''')
		)

	args = parser.parse_args()

	def set_path(dic, in_key, in_path):
		import os
		new_path = ""

		if in_path != "":
			new_path = os.path.realpath(in_path)
			if not os.path.isdir(new_path):
				raise Exception("Path passed in for " + in_key + " is not existent")
		dic[in_key] = new_path

	config_struct = {}
	config_struct["input_file"] = args.input_file
	config_struct["dry_run"] = args.dry_run.lower() == "true"
	set_path(config_struct, "save_material_configuration_to_unity_metadata_path", args.save_material_configuration_to_unity_metadata_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_texture_path", args.save_material_configuration_to_unity_metadata_texture_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_inf_path", args.save_material_configuration_to_unity_metadata_inf_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_uvb_path", args.save_material_configuration_to_unity_metadata_uvb_path)
	set_path(config_struct, "save_material_configuration_to_unity_metadata_effect_json_path", args.save_material_configuration_to_unity_metadata_effect_json_path)
	config_struct["save_material_configuration_to_unity_metadata_debug"] = args.save_material_configuration_to_unity_metadata_debug.lower() == "true"
	config_struct["save_material_configuration_to_unity_metadata_compress_textures"] = args.save_material_configuration_to_unity_metadata_compress_textures.lower() == "true"

	save_unity_mat(config_struct)

if __name__ == "__main__":
	standalone_main()
