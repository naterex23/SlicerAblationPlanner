# SlicerAblationPlanner

Ablation Planner

This is an extension for 3D Slicer that is used to plan and evaluate ablation zones. 

This module was developed to address research and clinical decision support at the Rhode Island Hospital, Providence, Rhode Island. This module was primarily developed by Nathaniel Rex (Brown University), with the support of -----

This module was designed to assist in both planning and intra-procedural decision making of ablations in the liver, kidney, and lung. 

Ablation Planning Workflow:

1. A pre-procedure CT of the thorax/abdomen is obtained, in which a lesion to be ablated is identified. 
2. The lesion is manually segmented in it's native coordinate system ("pre-procedure space") using the SegmentEditor tool. 
3. The operator imports the appropriate ablation profile for hardware available at the institution.
4. The operator places fiducials at locations appropriate to cover the lesion. Note that "odd" fiducials (1,3,5..) correspond to the tip of the probe and that "even" fiducials (2,4,6...) correspond to the approximate position at which the probe enters the body (and therefore should be placed on "patients skin" as represented by the CT)

![fiducial_placement](/Screenshots/fiducial_placement.png)

5. The operator simulates the position of the ablation profile and evaluates the assocaited "margin", or minimum distance from lesion to the ablation profile. 

![combined_probes](/Screenshots/combined_probes.png)

6. The output margins are evaluated and probe selection/addition are considered. 

![margin_colors](/Screenshots/margin_colors.png)

7. The surgical planner relays relevant information to the proceduralist.

Intra-Operative Support Workflow
-Note that this necessitates intra-op CT scans be available to a workstation with 3DSlicer. At our institution we have programmed the CT scanners in the IR suites to send their outputs to a DICOM listener in 3DSlicer such that when a patient is scanned, their most recent result is immediately available to the technician operating this software can immediately begin work on tailoring the procedure to the patient's anatomy.  (A more detailed description of this process can be found @github.com//////) 

All of the steps of the ablation planning workflow are completed before the day of the procedure. 

8. On the day of the procedure a preliminary CT is taken. The operator uses imports both the the "native" and "new" patient scans, along with the segmented lesion. 
9. The operator places at minimum 3 sets of corresponding fiducials, 3 in "native" space and 3 in "new" space. Fiducials should be as relevant to the tumor as possible. An example of 3 points for a RCC ablation might include the apex and the nadir of the kidney, as well as a solid bony landmark like a spinus process. 
10. The extension uses fiducial registration to translate the tumor from "native" space to "new" space. Any additional anatomical adjustments should be made.
11. Simulatenously to these steps, the ablation has proceeded and the probes are placed in the patient. The most recent CT (with probe placement is uploaded and the ablation planning workflow is repeated with the observed probe locations. 
12. Projected ablation margins surrounding the lesion are evaluated, and the technician and operator make adjustments to probe placement to maximise any margin. 

A library of ablation profiles for common manufacturers can be found in the "probe_profiles" folder. 
