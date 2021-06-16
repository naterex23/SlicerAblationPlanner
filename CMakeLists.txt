cmake_minimum_required(VERSION 3.13.4)

project(AblationPlanner)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/AblationPlanner")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Nathaniel Rex (Brown University), Scott Collins (Rhode Island Hospital)")
set(EXTENSION_DESCRIPTION "This extension enables the user to place virtual ablation profiles and evaluate a theoretical margin associated with these profiles.  ")
set(EXTENSION_ICONURL "https://github.com/naterex23/SlicerAblationPlanner/raw/main/AblationPlanner/Resources/Icons/AblationPlanner.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/naterex23/SlicerAblationPlanner/raw/main/Screenshots/minimum_required_inputs.png, https://github.com/naterex23/SlicerAblationPlanner/raw/main/Screenshots/minimum_required_placement.png, https://github.com/naterex23/SlicerAblationPlanner/raw/main/Screenshots/ablation_steps.png, https://github.com/naterex23/SlicerAblationPlanner/raw/main/Screenshots/ablation_outputs.png, https://github.com/naterex23/SlicerAblationPlanner/raw/main/Screenshots/margin_colors.png")
set(EXTENSION_DEPENDS "ModelToModelDistance") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(AblationPlanner)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
