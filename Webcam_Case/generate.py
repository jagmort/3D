"""Webcam enclosure v0.6. Parametric CadQuery source; millimeters."""
import cadquery as cq
from cadquery import exporters
from pathlib import Path
O=Path(__file__).resolve().parent
L,W,D=59.,23.,34.
wall=1.5
pcb_l,pcb_w,pcb_t=55.,19.3,1.6
# Front outer face z=0, rear mounting face z=30.
# PCB front surface z=21.5, PCB rear surface z=23.1.
pcb_z=21.5
pcb_holes=[(-22.95,-7.4),(-22.95,7.4),(23.95,0)]
front_depth=26.1
# Shell has a thin flat front wall and rounded outer corners.
front=cq.Workplane('XY').box(L,W,front_depth,centered=(True,True,False)).edges('|Z').fillet(1.8)
front=front.cut(cq.Workplane('XY').box(L-2*wall,W-2*wall,front_depth+1,centered=(True,True,False)).translate((0,0,wall)))
for x,y,d in [(0.35,0,14.6),(-12.5,-6.65,1.5),(12.5,-6.65,1.5),(23.5,-5.65,2.)]:
    front=front.cut(cq.Workplane('XY').center(x,y).circle(d/2).extrude(2))
# Three pillars from front shell with short pegs. PCB rests at z=21.5.
for x,y in pcb_holes:
    front=front.union(cq.Workplane('XY').center(x,y).circle(2.05).extrude(pcb_z-wall).translate((0,0,wall)))
    front=front.union(cq.Workplane('XY').center(x,y).circle(1.1).extrude(1.5).translate((0,0,pcb_z)))
# Four THROUGH windows in the long walls, aligned to rear cap snap nubs.
# Cut crosses the entire 1.5 mm side wall; the extra outward reach
# guarantees the openings are visible and accessible from outside.
for x in (-16.,16.):
    for s in (-1,1):
        front=front.cut(cq.Workplane('XY').box(3.6,4.0,1.7).translate((x,s*10.75,24.8)))
# Back cap; back wall remains unperforated for double-sided tape.
rear=cq.Workplane('XY').box(L,W,D-front_depth,centered=(True,True,False)).translate((0,0,front_depth)).edges('|Z').fillet(1.8)
rear=rear.cut(cq.Workplane('XY').box(L-2*wall,W-2*wall,D-front_depth-wall+0.1,centered=(True,True,False)).translate((0,0,front_depth-.1)))
# Press pads from rear inner face z=32.5 down to PCB rear face z=23.2.
# Small compliant clearance 0.1mm; no interference with the 1.6mm PCB.
for x,y in pcb_holes:
    rear=rear.union(cq.Workplane('XY').center(x,y).circle(1.85).extrude(9.3).translate((0,0,23.2)))
# Four spring tabs in 1.85mm nominal clearance beside board; start at z=23.9.
# Retention nubs catch front-shell windows at z=24.8.
for x in (-16.,16.):
    for s in (-1,1):
        yy=s*9.5
        rear=rear.union(cq.Workplane('XY').box(2.6,0.9,9.0).translate((x,yy,28.4)))
        rear=rear.union(cq.Workplane('XY').box(2.0,0.55,0.8).translate((x,yy+s*0.57,24.8)))
# One cable bore centered on the seam z=26.1. Each half has exactly
# a semicircular notch. The connector stays attached during assembly.
# Side-wall thickness is 1.5 mm; cut extends through the short end.
cable_center_z=front_depth
bore=cq.Workplane('YZ').center(0,cable_center_z).circle(2.1).extrude(4,both=True).translate((-L/2,0,0))
front=front.cut(bore)
rear=rear.cut(bore)
# Reference PCB for collision checking, with its actual through-holes.
board=cq.Workplane('XY').box(pcb_l,pcb_w,pcb_t,centered=(True,True,False)).translate((0,0,pcb_z))
for x,y in pcb_holes:
    board=board.cut(cq.Workplane('XY').center(x,y).circle(1.25).extrude(pcb_t+0.2).translate((0,0,pcb_z-.1)))
for name,solid in [('front',front),('rear',rear),('pcb_reference',board)]:
    assert solid.val().isValid(),name
    exporters.export(solid,str(O/(name+'.step')))
    if name!='pcb_reference': exporters.export(solid,str(O/(name+'.stl')))
    print(name,round(solid.val().Volume(),1))
# Collision check: CAD nominal PCB and shell/press pads must not overlap.
for name,solid in [('front',front),('rear',rear)]:
    overlap=solid.val().intersect(board.val()).Volume()
    print('PCB overlap',name,round(overlap,5),'mm^3')
    assert overlap<0.01, (name,overlap)
