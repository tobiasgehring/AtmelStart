import re
from jinja2 import Template
import os


class Makefile:
    """
    Parses an atmel start makefile and generates a cmake toolchain file for compilation.

    Usage:
    Makefile.write_cmake_toolchain('atstart/gcc/Makefile', 'atstart/toolchain.cmake')
    """
    def __init__(self, filename):
        super().__init__()
        self._filename = filename
        with open(filename, 'r') as content_file:
            self._content = content_file.read()

    def get_include_dirs(self):
        """
        Returns include directories
        """
        result = re.findall('-I"\\.\\./(\\S*?)"', self._content)
        # remove empty strings and duplicates
        return list(dict.fromkeys(filter(None, result)))

    def get_source_files(self):
        """
        Returns source files except main.c
        """
        result = re.findall('"(\\S+?)\\.d"', self._content)
        # remove empty strings, duplicates
        result = dict.fromkeys(filter(None, result))
        # remove main
        result.pop('main', None)
        # sort
        result = sorted(result)
        # add .c
        return [value + '.c' for value in result]

    def get_linker_script(self):
        """
        Returns the linker script
        """
        results = re.findall('"\\.\\./(\\S+\\.ld)"', self._content)
        if len(results) == 0:
            raise Exception('Could not find linker script.')
        return results[0]

    def get_cpu(self):
        """
        Returns the CPU (-mcpu)
        """
        results = re.findall('-mcpu=(\\S*)', self._content)
        if len(results) == 0:
            raise Exception('Could not find CPU.')
        return results[0]

    def get_device(self):
        """
        Returns the device name
        """
        results = re.findall('-D__(\\S+)__', self._content)
        if len(results) == 0:
            raise Exception('Could not find device.')
        return results[0]

    def generate_cmake_toolchain(self):
        """
        Generates a cmake toolchain script

        :return: str the cmake toolchain script
        """
        # Read Template
        with open(os.path.join(os.path.dirname(__file__), 'templates/toolchain.cmake'), 'r') as file:
            content = file.read()
        template = Template(content)
        return template.render(
            include_dirs=self.get_include_dirs(),
            source_files=self.get_source_files(),
            linker_script=self.get_linker_script(),
            cpu=self.get_cpu(),
            device=self.get_device()
        )

    @classmethod
    def write_cmake_toolchain(cls, makefile, toolchain_cmake_file):
        """
        Opens an atmel start makefile, generates the cmake toolchain script and writes it to file.

        :param makefile: str, filename to makefile
        :param toolchain_cmake_file: str, filename where the cmake toolchain file is written to
        :return:
        """
        m = cls(makefile)
        with open(toolchain_cmake_file, 'w') as file:
            file.write(m.generate_cmake_toolchain())