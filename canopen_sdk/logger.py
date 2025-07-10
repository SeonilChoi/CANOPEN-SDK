import os
import sys
import datetime

class Logger:
    def __init__(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        self.file = open(filename, 'w+t')
        self.keys = []
        self.separator = ','

    def write_key_values(self, key_values):
        extra_keys = key_values.keys() - self.keys
        if extra_keys:
            self.keys.extend(extra_keys)
            self.file.seek(0)
            lines = self.file.readlines()
            self.file.seek(0)
            for i, key in enumerate(self.keys):
                if i > 0:
                    self.file.write(self.separator)
                self.file.write(key)
            self.file.write('\n')
            for line in lines[1:]:
                self.file.write(line[:-1])
                self.file.write(self.separator * len(extra_keys))
                self.file.write('\n')
        for i, key in enumerate(self.keys):
            if i > 0:
                self.file.write(self.separator)
            value = key_values.get(key)
            if value is not None:
                self.file.write(str(value))
        self.file.write('\n')
        self.file.flush()

    def close(self):
        self.file.close()
