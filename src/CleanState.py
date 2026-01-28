from State import State
from FinalState import FinalState

class CleanState(State):
    def __init__(self, context):
        self.context = context

    def execute(self):
        for file in self.context.downloaded_files:
            target = self.context.target_dir / file.name
            if target.exists():
                print(f"📣 {target} already exists! Not replacing it...")
                file.unlink()
            else:
                file.rename(target)

        try:
            self.context.temp_dir.rmdir()
            print("Temporary directory removed successfully.")
        except Exception as e:
            print(f"Failed to remove temporary directory: {e}")

        self.context.changeState(FinalState(self.context))
        self.context.execute()