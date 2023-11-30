# SlicerAblationPlanner

This is an extension for 3D Slicer that is used to plan and evaluate ablation procedures. 

This module was developed to support research and clinical decision support involving kidney, liver, and lung ablations at the Rhode Island Hospital, Providence, Rhode Island. This module was primarily developed by Nathaniel Rex (Brown University) with the support of Scott Collins, Ben Hsieh (Rhode Island Hospital), and Krishna Nand Keshava Murthy (Memorial Sloan Kettering Cancer Center). 

Procedure planning required inputs: 
1. A pre-procedure "planning" CT/CTA that shows the tumor location. 
2. A segmented tumor/lesion to be ablated. 
3. An "ablation profile" as specified by a vendor, generally an ellipsoid that be imported into Slicer as a segmentation. 

Ablation Planning Workflow:

1. A pre-procedure CT of the thorax/abdomen is obtained, in which a lesion to be ablated is identified. 
2. The lesion is manually segmented in it's native coordinate system using the SegmentEditor tool. 

![minimum_required_inputs](/Screenshots/minimum_required_inputs.PNG)

3. The operator imports the appropriate ablation profile for hardware available at the institution. A library of common ablation profiles can be found at: https://github.com/naterex23/SlicerAblationPlannerProfiles
4. The operator places fiducials to plant probes in an appropriate orientation to cover the lesion. Note that "odd" fiducials (1,3,5..) correspond to the tip of the probe and that "even" fiducials (2,4,6...) correspond to the approximate position at which the probe enters the body and therefore should be placed on the "patients skin" (see image below). After placing all desired fiducials the "Place Probes" button should be pushed. 

![minimum_required_placement](/Screenshots/minimum_required_placement.PNG)

5. After the "Place Probes" button is hit, the placement of the probes should be evaluated. The probe segments have not yet been fused and therefore can be independently adjusted using the transform module. Alternatively one could start the process over again if the probe placement is not optimal. Next the "Translate Probe" button can be pressed. This step merges the segments and creates a unified ablation profile. 

![ablation_steps](/Screenshots/ablation_steps.PNG)

6. After the unified ablation profile has been evaluated and is satisfactory the "Evaluate Tumor Margins" button can be clicked. This operation generates numerous output files and should take approximately 2-5 minutes to run based on computer speed and number of probes used. The output should look something like the screenshot below. 

![ablation_outputs](/Screenshots/ablation_outputs.PNG)

7. A variety of useful information including the minimum margin is available in the python interactor. If desired the "Apply Margin Color" can be pressed to create an output as below. The "Revert Color" button can be pressed to return to the original model colors. 

![margin_colors](/Screenshots/margin_colors.png)

8. The output margins are evaluated and probe selection/addition are considered. The surgical planner relays relevant instructional information to the proceduralist.

Intra-procedural inputs: 
1. A pre-procedure "planning" CT/CTA that shows the tumor location. 
2. A segmented tumor/lesion for ablation. 
3. An "ablation profile" as specified by a vendor, generally an ellipsoid that be imported into Slicer as a segmentation. 
4. A computer, preferably in the procedure room or just outside, that has 3D slicer with a DICOM listener to receive intra-operative CT images.  

Intra-Operative Support Workflow

-Note that this necessitates intra-op CT scans be available to a workstation with 3DSlicer. At our institution we have programmed the CT scanners in the IR suites to send their outputs to a DICOM listener in 3DSlicer such that when a patient is scanned, their most recent result is instantaneously available to the technician operating this software and they can subsequently begin work on adjusting the lesion to the patient's anatomy. (See https://www.slicer.org/wiki/Documentation/4.10/Modules/DICOM for details)

Steps 1-8 of the ablation planning workflow are completed before the day of the procedure. 

9. On the day of the procedure a preliminary CT is taken. The operator imports both the the "native" ("pre-procedure"/prior) and "new" ("intra-procedure") patient scans, along with the segmented lesion. 
10. The operator places at minimum 2 sets of corresponding fiducials, at least 3 in "native" space and 3 in "intra-procedure" space. Fiducials should be as close to the lesion as possible while maintaining their relative relationship. An example of 3 points for a RCC ablation might include the apex and the nadir of the kidney, as well as a solid bony landmark like a spinus process. After the 2 sets of 3 fiducials are placed, the "Translate Tumor" button can be pressed. 
11. The extension uses fiducial registration to translate the tumor from "native" space to "new" space. Fiducial registration is optomized to minimize the distance between the fiducial sets, but is not perfect; any additional adjustments to lesion location can be made using the transform module. The transform is hardened with the "Harden Transform" button or in the transform module. 
12. While the technologist is performing steps 9-11, the ablation can proceed and the probes are eventually placed in the patient. The most recent CT (with probe placement) is uploaded and the ablation planning workflow is repeated with the observed probe locations. 
13. Projected ablation margins surrounding the lesion are evaluated, and the technician and operator make adjustments to probe placement to maximise any margin. Ablation margin information is provided via the a 3D voronoi model (which displays a heatmap based on distance between the tumor and the ablation profile), a printed minimum margin (via the python command line interface), and an output table called "surface_distances" (that contains a variety of data extracted from the 3D voronoi model). The "Signed" column contains information about the signed distance between the two models should these be of interest for research purposes. 

AblationPlanner in Action
![mid_procedure](/Screenshots/mid_procedure.png)

Disclaimer

SlicerAblationPlanner, same as 3D Slicer, is a research software. SlicerAblationPlanner is NOT an FDA-approved medical device. It is not intended for clinical use. The user assumes full responsibility to comply with the appropriate regulations.

Support

Please feel free to contact me for questions, feedback, suggestions or bugs. 
nathaniel (underscore) rex@ brown.edu

Acknowledgments

Development of SlicerAblationPlanner was supported in part by the following NIH grants:

T35 HL094308 NIH National Heart, Lung, Blood Institute (NHLBI) Training Grant


