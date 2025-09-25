import string


def fix_illegal_chars(var_name):
	res = ""
	allowed_chars = string.ascii_letters + string.digits + "_"
	for char in var_name:
		if char in allowed_chars: res = res + char
		else: res = res + hex(ord(char))
	return res


def get_safe_var_names(var_dict):
	res = {}
	used_names = []
	for var in var_dict:
		temp = "v_" + fix_illegal_chars(var.replace(" ", "_"))
		if temp in used_names:
			i = 0
			while f"{temp}_{i}" in used_names: i += 1
			temp = f"{temp}_{i}"
		res[var] = [temp, var_dict[var]]
		used_names.append(temp)
	return res


def generate_safe_names_dict(data):
	safe_variables = {" global": get_safe_var_names(data["vars"])}
	for sprite in data:
		if sprite == "vars": continue
		safe_variables[sprite] = get_safe_var_names(data[sprite]["vars"])

	return safe_variables