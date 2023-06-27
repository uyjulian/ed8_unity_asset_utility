# SPDX-License-Identifier: MIT

import sys
import json
from ed8_unity_asset_utility import parse_uvb

if __name__ == "__main__":
	if sys.argv[1] == "--uvb":
		dat_type_dic = {
			1 : "jmp",
			2 : "wait",
			3 : "uv_minmax",
			5 : "uv_ofs_set",
			6 : "uv_ofs_add",
			7 : "uv_ofs_dt",
			8 : "uv_scl_set",
			11 : "col_dif",
			12 : "col_emi",
			13 : "cntr_clr",
			14 : "cntr_inc",
			15 : "jmp_neq",
			17 : "uv_target",
			18 : "col_muv",
			19 : "uv_ofs_interp",
			20 : "time_stop",
		}

		uv_target_dic = {
			0 : "tex1",
			1 : "tex",
			2 : "proj",
			4 : "muv",
			8 : "muv2",
			16 : "dudv",
		}

		data_decoded = parse_uvb(sys.argv[2])
		for dat in data_decoded:
			int1 = dat[0]
			if int1 == 17:
				uv_target = "unknown"
				if dat[1][0] in uv_target_dic:
					uv_target = uv_target_dic[dat[1][0]]
				dat.append(uv_target)
			dat_type = "???"
			if dat[0] in dat_type_dic:
				dat_type = dat_type_dic[dat[0]]
			print(dat_type, dat)
