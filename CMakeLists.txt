cmake_minimum_required(VERSION 3.13.4)

project(AblationPlanner)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/AblationPlanner")
set(EXTENSION_CATEGORY "Surgical Planning")
set(EXTENSION_CONTRIBUTORS "Nathaniel Rex (Brown University), Scott Collins (Rhode Island Hospital)")
set(EXTENSION_DESCRIPTION "This is a first attempt at the creation of an extension. ")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/AblationPlanner.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/AblationPlanner/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(probe_placer)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
