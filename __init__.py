from backend import BaseAddon
from .name_fixer import generate_safe_names_dict
from .compiler import compile_sprite
import json
import os


class BasicCppCompiler(BaseAddon):
	def init(self):
		print("example addon init")
		self.ui.add_compiler("C++", self)
		with open(os.path.join(self.folder_name, "code.json")) as f:
			self.code_json = json.load(f)

	def on_compile(self):
		data = self.ui.code_tab.get_project_data()
		code = self.compile(data)
		with open(os.path.join(self.ui.opened_project_path, 'main.cpp'), 'w') as output:
			output.write(code)
		self.ui.backend.run_command(f'cd {os.path.join(self.ui.opened_project_path)}; g++ -o res main.cpp')

	def on_run(self):
		self.ui.backend.run_command(os.path.join(self.ui.opened_project_path, "res"))

	def compile(self, data):
		print(data)
		safe_variables = generate_safe_names_dict(data)
		start_id = self.get_start_id(data["Main"])
		if not start_id: return None

		res = compile_sprite(data, "Main", self.code_json, safe_variables)
		print(res)
		return res

	@staticmethod
	def get_start_id(sprite_data):
		for block_id in sprite_data["roots"]:
			if sprite_data["code"][block_id]["internal_name"] == "on_launch":
				return block_id
		return None


def run(ui, fn):
	return BasicCppCompiler(ui, fn)
