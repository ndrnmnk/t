def compile_block(project_json, sprite_name, block_uuid, templates, safe_variables):
	"""
	Recursively compiles a block starting at block_uuid into C++ code.
	"""
	code_blocks = project_json[sprite_name]["code"]
	block = code_blocks[block_uuid]

	# Special handling
	if block["internal_name"].startswith(" var_") or block["internal_name"].startswith(" VAR_"):
		vname = block["internal_name"][5:]
		return safe_variables[sprite_name].get(vname, [vname])[0], set()

	template = templates.get(block["internal_name"], {"deps": [], "code": ""})

	code = template["code"]
	deps = set(template.get("deps", []))

	# Special handling
	if block["internal_name"] == "define_variable":
		var_uuid = block["content"][0][1]
		vname = code_blocks[var_uuid]["internal_name"][5:]
		vtype = safe_variables[sprite_name][vname][1]
		code = code.replace("~", vtype)
	if block["internal_name"] == "if":
		print(block["nonstatic"])
		if block["nonstatic"][1] == 1:
			code = code.replace("\n$snap1$", " else {\n$snap1$}\n$snap2$")

	# Replace $contentN$
	for idx, (static_val, child_uuid) in enumerate(block.get("content", [])):
		if child_uuid:  # recursive compile
			child_code, child_deps = compile_block(project_json, sprite_name, child_uuid, templates, safe_variables)
			replacement = child_code.strip()
			deps |= child_deps
		else:  # use static value
			replacement = static_val

		code = code.replace(f"$content{idx}$", replacement)

	# Replace $snapN$
	for idx, snap_uuid in enumerate(block.get("snaps", [])):
		if snap_uuid:
			snap_code, snap_deps = compile_block(project_json, sprite_name, snap_uuid, templates, safe_variables)
			deps |= snap_deps
			replacement = snap_code
		else:
			replacement = ""
		code = code.replace(f"$snap{idx}$", replacement)

	return code, deps


def compile_sprite(project_json, sprite_name, templates, safe_variables):
	"""
	Compiles all root blocks in a sprite into final C++ code.
	"""
	roots = project_json[sprite_name]["roots"]
	all_code = []
	all_deps = set()

	for root_uuid in roots:
		root_code, root_deps = compile_block(project_json, sprite_name, root_uuid, templates, safe_variables)
		all_code.append(root_code)
		all_deps |= root_deps

	# Add includes
	includes = "\n".join([f"#include <{d}>" for d in all_deps])

	return includes + "\n\n" + "\n".join(all_code)

if __name__ == "__main__":
	# Example usage:
	project_json = { ... }   # your JSON from above
	safe_variables = { ' global': {}, 'Main': {'test variable': ['v_test_variable', 'str']}}
	templates = { ... }  # your block template json

	cpp_code = compile_sprite(project_json, "Main", templates, safe_variables)
	print(cpp_code)
