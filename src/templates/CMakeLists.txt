cmake_minimum_required(VERSION 3.3)
set(CMAKE_SYSTEM_NAME Generic)

project({{ project_name }})

include("${CMAKE_CURRENT_LIST_DIR}/atstart/toolchain.cmake")

# Target built with atmel start configuration
atstart_add_executable({{ project_name}} src/main.c)

# Target to upload binary using openocd.
add_custom_target(
    upload
    COMMAND openocd -f "${CMAKE_CURRENT_LIST_DIR}/scripts/openocd-atmel_same70q21.cfg" -c "init; halt; program ${CMAKE_BINARY_DIR}/ITLALaserController.elf verify reset exit" 
    DEPENDS ${CMAKE_BINARY_DIR}/ITLALaserController.elf
)

