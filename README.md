# SlicerAblationPlanner

This is an extension for 3D Slicer that is used to plan and evaluate ablation zones. 

This module was developed to address research and clinical decision support involving kidney, liver, and lung ablations at the Rhode Island Hospital, Providence, Rhode Island. This module was primarily developed by Nathaniel Rex (Brown University) with the support of Scott Collins (Rhode Island Hospital). 

Ablation Planning Workflow:

1. A pre-procedure CT of the thorax/abdomen is obtained, in which a lesion to be ablated is identified. 
2. The lesion is manually segmented in it's native coordinate system ("pre-procedure" or "native" space) using the SegmentEditor tool. 
3. The operator imports the appropriate ablation profile for hardware available at the institution. A library of common ablation profiles can be found at: https://github.com/naterex23/SlicerAblationPlannerProfiles
4. The operator places fiducials to plant probes in an appropriate orientation to cover the lesion. Note that "odd" fiducials (1,3,5..) correspond to the tip of the probe and that "even" fiducials (2,4,6...) correspond to the approximate position at which the probe enters the body and therefore should be placed on the "patients skin" (see below). After placing all desired fiducials the "Place Probes" button should be pushed. 

![fiducial_placement](/Screenshots/fiducial_placement.png)

5. If a unified segment was created for multiple placed probes, the appropriate segment should be selected in the "Probe Segment:" selector. The operator simulates the position of the ablation profile and evaluates the assocaited "margin", or minimum distance from lesion to the ablation profile by clicking on the "Evaluate Tumor Margins" button. This operation generates numerous output files and should take approximately 1-3 minutes to run. 

![combined_probes](/Screenshots/combined_probes.png)

6. The output margins are evaluated and probe selection/addition are considered. 

![margin_colors](/Screenshots/margin_colors.png)

7. The surgical planner relays relevant instructional information to the proceduralist.

Intra-Operative Support Workflow

-Note that this necessitates intra-op CT scans be available to a workstation with 3DSlicer. At our institution we have programmed the CT scanners in the IR suites to send their outputs to a DICOM listener in 3DSlicer such that when a patient is scanned, their most recent result is instantaneously available to the technician operating this software and they can subsequently begin work on adjusting the lesion to the patient's anatomy. (See https://www.slicer.org/wiki/Documentation/4.10/Modules/DICOM for details)

Steps 1-7 of the ablation planning workflow are completed before the day of the procedure. 

8. On the day of the procedure a preliminary CT is taken. The operator imports both the the "native" ("pre-procedure"/prior) and "new" ("intra-procedure") patient scans, along with the segmented lesion. 
9. The operator places at minimum 2 sets of corresponding fiducials, at least 3 in "native" space and 3 in "new" space. Fiducials should be as close to the lesion as possible while maintaining their relative relationship. An example of 3 points for a RCC ablation might include the apex and the nadir of the kidney, as well as a solid bony landmark like a spinus process. 
10. The extension uses fiducial registration to translate the tumor from "native" space to "new" space. Fiducial registration is optomized to minimize the distance between the fiducial sets, but is not perfect; any additional adjustments to lesion location can be made using the transform tool.
11. Simulatenously to these steps, the ablation has proceeded and the probes are placed in the patient. The most recent CT (with probe placement is uploaded and the ablation planning workflow is repeated with the observed probe locations. 
12. Projected ablation margins surrounding the lesion are evaluated, and the technician and operator make adjustments to probe placement to maximise any margin. Ablation margin information is provided via the a 3D voronoi model (which displays a heatmap based on distance between the tumor and the ablation profile), a printed minimum margin (via the python command line interface), and an output table called "surface_distances" (that contains a variety of data extracted from the 3D voronoi model). The "Absolute" column contains information about the absolute distance between the two models should these be of interest. 

Disclaimer
SlicerAblationPlanner, same as 3D Slicer, is a research software. SlicerAblationPlanner is NOT an FDA-approved medical device. It is not intended for clinical use. The user assumes full responsibility to comply with the appropriate regulations.

Support
Please feel free to contact me for questions, feedback, suggestions or bugs. 
nathaniel rex@brown.edu

Acknowledgments
Development of SlicerAblationPlanner was supported in part by the following NIH grants:

T35 HL094308 NIH National Heart, Lung, Blood Institute (NHLBI) Training Grant


