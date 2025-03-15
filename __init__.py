from backend.BaseAddon import BaseAddon
from PyQt5.QtWidgets import QLabel


class ExampleAddonClassName(BaseAddon):
	def __init__(self, ui):
		super().__init__(ui)
		print("example addon init")

	def on_options(self):
		return QLabel("label")
	
	def on_delete(self):
		print("why do you deleet me(")
		return True


def run(ui):
	return ExampleAddonClassName(ui)
