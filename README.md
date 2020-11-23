# SlicerAblationPlanner

Ablation Planner

This is an extension for 3D Slicer that is used to plan and evaluate ablation zones. 

This module was developed to address research and clinical work at the Rhode Island Hospital, Providence, Rhode Island. This module was primarily developed by Nathaniel Rex (Brown University), with the support of Scott Collins (Rhode Island Hospital) and Krishna Keshava. 

This module was designed to assist in the planning, and intra-procedural decision making, of ablation type procedures in the liver, kidney, and lung. 

An appropriate workflow associated with an ablation procedure would resemble the following.

1. A pre-procedure CT of the thorax/abdomen is obtained, in which a lesion to be ablated is identified. 
2. The lesion is manually segmented in it's native coordinate system using the SegmentEditor tool. 
3. The operator imports the appropriate ablation profile for hardware available at the institution.
4. The operator simulates the position of the ablation profile and evaluates the assocaited "margin", or minimum distance from lesion to the ablation profile. 
5. On the day of the procedure a preliminary CT is taken. The operator uses landmark fiducials to translate the lesion to "patient table space" from "pre-procedure space."
6. The ablation probes are placed by an interventional radiologist, or similar and a final CT scan is taken before the ablation proceeds. 
7. The ablation probe margins and approximate lesion position are evaluated and ablation probe position is adjusted to maximize margin. 
8. The ablation proceeds. 

A library of ablation profiles for common manufacturers is included.
