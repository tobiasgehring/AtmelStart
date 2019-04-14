
# Atmel Start

This projects consists in a command-line tool to streamline work with the [Atmel Start](http://start.atmel.com/) code generator, as well as a CMake toolchain generator which allows to integrate code generated using Atmel Start in a CMake project (for use in the [JetBrains CLion](https://www.jetbrains.com/clion/) IDE for example)

## Quick Start

**Initialize the Atmel Start configuration**
```
$ atstart init
```
This initializes the current directory as project directory. It creates a `src/` subdirectory for
your own code and a `CMakeLists.txt` for `cmake`. It then opens a webbrower with Atmel start. Please
save the configuration file in the project root directory as `atmel_start_config.atstart`.

**Generate the Atmel Start code and download it**
```
$ atstart reconfigure
``` 
This will generate the code, download it and extract it in a `atstart` directory. The code is the
same as the one you would get using *Export Project* in Atmel Start. This will also generate
`toolchain.cmake` for building your project with `cmake`. Call this command after you updated the
configuration file `atmel_start_config.atstart` in the root directory.


**Create your project files**

Create a main code file `main.c` for your project in the `src/` directory. You can copy `atstart/main.c`  as a starter if you wish.

**Build your project**

```
$ atstart build
```

**CLion**

CLion has `openocd` integration. Start CLion and create a new project from existing source.
To correctly build the project you need to edit the settings:

`File | Settings | Build, Execution, Deployment | CMake`

Add `-DCMAKE_SYSTEM_NAME=Generic` to `CMake options`.

To use `openocd` edit the `Run / Debug Configuration`.

**Credits**

This tool is heavily inspired by
[AtmelStart by Jacques Michiels](https://github.com/jmichiels/AtmelStart).