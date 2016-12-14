from conans import ConanFile, errors
import os

channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "Mikayex")


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "arch", "build_type"
    requires = "nasm/2.12.02@%s/%s" % (username, channel)
    generators = "txt"

    @property
    def nasm_command(self):
        for dir in self.deps_cpp_info["nasm"].bin_paths:
            nasm = os.path.join(dir, "nasm.exe" if self.settings.os == "Windows" else "nasm")
            if os.path.exists(nasm):
                return nasm
        raise errors.ConanException("nasm not found!")

    @property
    def ndisasm_command(self):
        for dir in self.deps_cpp_info["nasm"].bin_paths:
            ndisasm = os.path.join(dir, "ndisasm.exe" if self.settings.os == "Windows" else "ndisasm")
            if os.path.exists(ndisasm):
                return ndisasm
        raise errors.ConanException("ndisasm not found!")

    @property
    def output_test(self):
        return "testPackage.exe" if self.settings.os == "Windows" else "testPackage"

    def build(self):
        command = '%s -fbin "%s%sbinexe.asm" -o %s -i%s' % (self.nasm_command, self.conanfile_directory, os.sep,
                                                            self.output_test, self.conanfile_directory + os.sep)
        self.run(command)

    def test(self):
        # Due to the non portability of asm, it is impossible to test the produced exe everywhere...
        # We test the disassembly instead.
        command = '%s -p intel "%s" > binexe.disasm' % (self.ndisasm_command, self.output_test)
        self.run(command)

        with open("binexe.disasm", 'r') as disasm_file:
            disasm = disasm_file.read()
        instr1 = disasm.count("int 0x21")
        instr2 = disasm.count("mov ax,0x4c00")
        if instr1 != 2 or instr2 != 1:
            raise errors.ConanException("Test failed")
