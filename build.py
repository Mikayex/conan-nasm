from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager()

    # It always use the default compiler version on each platform
    if platform.system() == "Windows":
        for arch in builder.archs:
            builder.add(settings={"arch": arch, "compiler": "Visual Studio", "compiler.runtime": "MT"})
    elif platform.system() == "Linux" or builder.use_docker == True:
        for arch in builder.archs:
            builder.add(settings={"arch": arch, "compiler": "gcc"})
    elif platform.system() == "Darwin":
        for arch in builder.archs:
            builder.add(settings={"arch": arch, "compiler": "apple-clang"})

    builder.run()
