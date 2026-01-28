from State import State

class FinalState(State):
	def __init__(self, context):
		self.context = context

	def execute(self):
		print("\033[92m✅ All done! Your music files are ready.\033[0m")