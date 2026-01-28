from State import State
from FetchState import FetchState
from NormalizeState import NormalizeOnlyState

class InitState(State):
	def __init__(self, context):
		self.context = context

	def execute(self):
		if self.context.normalize_only:
			self.context.changeState(NormalizeOnlyState(self.context))
		else:
			self.context.changeState(FetchState(self.context))
		
		self.context.execute()