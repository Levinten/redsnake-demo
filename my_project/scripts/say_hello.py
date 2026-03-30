# python hello_world_simple.py --name=""

import time

from redsnake import ScriptBase, CliScriptRunner
from redsnake.params import StringParam

class SayHello(ScriptBase):
    def static(self):
        self.static_settings.set_basics(
            script_id="ab807d21-2de0-4302-91a4-15de61378b1a",
            script_name="say_hello",
            timeout_seconds=3600
        )

    def dynamic(self):
        self.dynamic_settings.add_parameter(StringParam("name", description="A parameter", default="Steve", min_length=0, max_length=100, regex=r"^[A-Za-z ]*$", regex_description="only letters and spaces"))

        self.dynamic_settings.add_step(name="show_arg", description="Show the provided argument")
        self.dynamic_settings.add_step(name="simulate_work", description="Simulate some work")
        self.dynamic_settings.add_step(name="say_hello", description="Say hello to the user")

    def execute(self):
        self.logger.info("Starting script execution...")
        self.logger.info(f"Provided argument: {self.args.get("name")}")
        self.outputs.progress.next_step()
        time.sleep(3)  # Simulate work
        self.outputs.progress.next_step()
        name = self.args.get("name", "World")
        self.logger.info(f"Hello {name}!")

if __name__ == "__main__":
    CliScriptRunner(SayHello).run()