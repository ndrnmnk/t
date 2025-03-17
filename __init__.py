from backend.BaseAddon import BaseAddon
from PyQt5.QtWidgets import QLabel
import json
import os
import re


def parse_string(template, snap_list, content_list):
	def replace_snap(match):
		index = int(match.group(1))
		return snap_list[index] if index < len(snap_list) else ''

	def replace_content(match):
		index = int(match.group(1))
		return content_list[index] if index < len(content_list) else ''

	template = re.sub(r'\$snap(\d+)\$', replace_snap, template)
	template = re.sub(r'\$content(\d+)\$', replace_content, template)

	return template


def generate_includes(dependencies):
	res = ""
	for d in dependencies:
		res = res + f"#include <{d}>\n"
	return res


def convert_blocks_to_code(blocks, block_definitions):
	dependencies = []

	def process_block(block):
		internal_name = block['internal_name']

		content_list = [c[0] for c in block.get('content', [])]  # Update this to use variables later

		# recursively processes all the blocks
		snaps = [process_block(snap) if snap else '' for snap in block.get('snaps', [])]

		if internal_name in block_definitions:
			# if block definition is available, format its template and use it
			block_template = block_definitions[internal_name]['code']
			dependencies.extend(block_definitions[internal_name]['dependencies'])
			return parse_string(block_template, snaps, content_list)
		else:
			# if block definition is missing, don't add anything
			return ''
	# add new lines between blocks
	res = '\n'.join(process_block(block) for block in blocks)
	return generate_includes(set(dependencies)) + res


class ExampleAddonClassName(BaseAddon):
	def init(self):
		print("example addon init")
		self.ui.add_compiler("C++", self)
		with open(os.path.join("addons", "useless_addon", "code.json")) as f:
			self.code_json = json.load(f)

	def on_options(self):
		return QLabel("label")

	def on_compile(self):
		data = self.ui.code_tab.get_data(False)
		code = convert_blocks_to_code(data, self.code_json)
		with open(os.path.join(self.ui.opened_project_path, 'main.cpp'), 'w') as output:
			output.write(code)
		self.ui.backend.run_command(f'cd {os.path.join(self.ui.opened_project_path, "build")}; cmake ..; make')

	def on_run(self):
		self.ui.backend.run_command(os.path.join(self.ui.opened_project_path, "build", "main"))



def run(ui):
	return ExampleAddonClassName(ui)
