"""Example RedSnake script — Hello World."""

import time

from redsnake import ScriptBase
from redsnake.params import Value


class HelloWorld(ScriptBase):

    def setup(self):
        self.settings.set_basics(
            ui_name="Hello World",
            description="A simple example script that greets the given target.",
        )
        self.settings.set_tags(["example"])

    def dynamic(self):
        self.dynamic_settings.add_param(Value("target", str, ui_name="Target Name",
            desc="Who or what to greet",
            required=True,
            default="World",
        ))
        self.dynamic_settings.add_param(Value(
            "count",
            int,
            ui_name="Repeat Count",
            desc="How many times to greet",
            default=1,
            min=1,
            max=10,
        ))

    def execute(self):
        target = self.args["target"]
        count = self.args["count"]

        self.logger.info(f"Greeting {target} {count} time(s)")
        self.artifacts.status.set("Running", progress=0)

        lines = []
        for i in range(count):
            line = f"Hello, {target}! (#{i + 1})"
            time.sleep(0.2)  # Simulate work
            self.logger.debug(f"Generated line: {line}")
            lines.append(line)
            progress = int((i + 1) / count * 100)
            self.artifacts.status.set(f"Greeting {i + 1}/{count}", progress=progress)

        output = "\n".join(lines)

        self.artifacts.ui_result.add_text("greeting", output)
        self.artifacts.api_result.add({"greeting": output, "count": count})

        self.logger.info("Done!")
        self.logger.info("asdf", extra=self.meta)
