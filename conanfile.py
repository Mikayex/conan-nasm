from conans import ConanFile, CMake, tools
import os
import shutil


class NasmConan(ConanFile):
    name = "nasm"
    description = "The Netwide Assembler (NASM) is an assembler for x86 architecture (16, 32, or 64 bits)"
    version = "2.12.02"
    license = "https://opensource.org/licenses/BSD-2-Clause"
    url = "https://github.com/Mikayex/conan-nasm"
    settings = "os", "compiler", "arch"
    exports = "CMakeLists.txt", "config.h.cmake", "cmake/LargeFiles.cmake", "cmake/LargeFiles.c", "cmake/LargeFiles64.c", \
              "cmake/LargeFilesWindows.c"
    generators = "cmake"
    build_policy = "missing"

    def configure(self):
        del self.settings.compiler.libcxx  # Pure C project

    def conan_info(self):
        del self.info.settings._dict["compiler"]  # The compiled binaries don't depend on compiler

    def source(self):
        tools.download("http://www.nasm.us/pub/nasm/releasebuilds/%s/nasm-%s.zip" % (self.version, self.version),
                       "nasm.zip")
        tools.unzip("nasm.zip", "nasm-src")
        os.unlink("nasm.zip")
        shutil.copy("CMakeLists.txt", "nasm-src")
        shutil.copy("config.h.cmake", "nasm-src")

        os.makedirs("nasm-src/cmake")
        shutil.copy("cmake/LargeFiles.cmake", "nasm-src/cmake")
        shutil.copy("cmake/LargeFiles.c", "nasm-src/cmake")
        shutil.copy("cmake/LargeFiles64.c", "nasm-src/cmake")
        shutil.copy("cmake/LargeFilesWindows.c", "nasm-src/cmake")

    def build(self):
        cmake = CMake(self.settings)

        self.run('cmake nasm-src -DCMAKE_BUILD_TYPE=Release %s' % cmake.command_line)
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        ext = ".exe" if self.settings.os == "Windows" else ""
        self.copy("nasm%s" % ext, "bin", "bin", keep_path=False)
        self.copy("ndisasm%s" % ext, "bin", "bin", keep_path=False)
        self.copy("rdfdump%s" % ext, "bin/rdoff", "bin", keep_path=False)
        self.copy("ldrdf%s" % ext, "bin/rdoff", "bin", keep_path=False)
        self.copy("rdx%s" % ext, "bin/rdoff", "bin", keep_path=False)
        self.copy("rdflib%s" % ext, "bin/rdoff", "bin", keep_path=False)

        if self.settings.os == "Windows":
            shutil.copy("bin/rdf2bin%s" % ext, "bin/rdf2com%s" % ext)
            shutil.copy("bin/rdf2bin%s" % ext, "bin/rdf2ith%s" % ext)
            shutil.copy("bin/rdf2bin%s" % ext, "bin/rdf2ihx%s" % ext)
            shutil.copy("bin/rdf2bin%s" % ext, "bin/rdf2srec%s" % ext)
        else:
            os.symlink("rdf2bin%s" % ext, "bin/rdf2com%s" % ext)
            os.symlink("rdf2bin%s" % ext, "bin/rdf2ith%s" % ext)
            os.symlink("rdf2bin%s" % ext, "bin/rdf2ihx%s" % ext)
            os.symlink("rdf2bin%s" % ext, "bin/rdf2srec%s" % ext)

        self.copy("rdf2*%s" % ext, "bin/rdoff", "bin", keep_path=False, links=True)

    def package_info(self):
        self.cpp_info.bindirs = ["bin", "bin/rdoff"]
