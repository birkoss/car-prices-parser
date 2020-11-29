class Logs:
    logs = {
        "debug": "",
        "error": "",
        "warning": "",
    }

    def __str__(self):
        content = ""

        if self.logs['debug']:
            content += "# Debug #\n\n"
            content += self.logs['debug']

        if self.logs['warning']:
            content += "# Warning #\n\n"
            content += self.logs['warning']

        if self.logs['error']:
            content += "# Error #\n\n"
            content += self.logs['error']

        return content

    def debug(self, content):
        self.logs['debug'] += content + "\n"

    def error(self, content):
        self.logs['error'] += content + "\n"

    def warning(self, content):
        self.logs['warning'] += content + "\n"
