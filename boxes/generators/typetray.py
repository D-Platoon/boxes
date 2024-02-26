# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *
from boxes import edges, Color
from boxes.lids import _TopEdge, LidSettings


class FingerHoleEdgeSettings(edges.Settings):
    """Settings for FingerHoleEdge"""
    absolute_params = {
        "wallheight": 0,
        "fingerholedepth": 0}

class FingerHoleEdge(edges.BaseEdge):
    """An edge with room to get your fingers around cards"""
    def __call__(self, length, **kw):
        depth = self.settings.fingerholedepth-10
        self.edge(length/2-10, tabs=2)
        self.corner(90)
        self.edge(depth, tabs=2)
        self.corner(-180, 10)
        self.edge(depth, tabs=2)
        self.corner(90)
        self.edge(length/2-10, tabs=2)

class TypeTray(_TopEdge):
    """Type tray - allows only continuous walls"""

    ui_group = "Tray"

    def __init__(self) -> None:
        Boxes.__init__(self)
        self.addTopEdgeSettings(fingerjoint={"surroundingspaces": 0.5},
                                roundedtriangle={"outset" : 1})
        self.addSettingsArgs(LidSettings)
        self.buildArgParser("sx", "sy", "h", "hi", "outside", "bottom_edge",
                            "top_edge")
        self.argparser.add_argument(
            "--back_height",  action="store", type=float, default=0.0,
            help="additional height of the back wall - e top edge only")
        self.argparser.add_argument(
            "--radius",  action="store", type=float, default=0.0,
            help="radius for strengthening side walls with back_height")
        self.argparser.add_argument(
            "--gripheight", action="store", type=float, default=30,
            dest="gh", help="height of the grip hole in mm")
        self.argparser.add_argument(
            "--gripwidth", action="store", type=float, default=70,
            dest="gw", help="width of th grip hole in mm (zero for no hole)")
        self.argparser.add_argument(
            "--handle", type=boolarg, default=False, help="add handle to the bottom (changes bottom edge in the front)")
        self.argparser.add_argument(
            "--fingerhole", action="store", type=str, default="regular",
            choices=['regular', 'deep', 'custom', 'none'],
            help="Depth of cutout to grab the cards")
        self.argparser.add_argument(
            "--fingerhole_depth", action="store", type=float, default=20,
            help="Depth in mm of cutout if fingerhole is set to 'custom'. Disabled otherwise.")
        self.argparser.add_argument(
            "--text_size", action="store", type=int, default=12,
            help="Textsize in mm for the traycontent")
        self.argparser.add_argument(
            "--text_alignment", action="store", type=str, default="left",
            choices=['left', 'center', 'right'],
            help="Text Alignment")
        self.argparser.add_argument(
            "--text_distance_x", action="store", type=float, default=2.0,
            help="Distance in X from edge of tray in mm. Has no effect when text is centered.")
        self.argparser.add_argument(
            "--text_distance_y", action="store", type=float, default=2.0,
            help="Distance in Y from edge of tray in mm.")
        if self.UI == "web":
            self.argparser.add_argument(
                "--layout", action="store", type=str, default="1\r\n2\r\n3\r\n4\r\n5\r\n6\r\n7\r\n8\r\n",
                help="Every line is the text of one tray. Beginning with front left")
        else:
            self.argparser.add_argument(
                "--input", action="store", type=argparse.FileType('r'),
                default="traylayout.txt",
                help="layout file")
            self.layout = None

    @property
    def fingerholedepth(self):
        if self.fingerhole == 'custom':
            return self.fingerhole_depth
        elif self.fingerhole == 'regular':
            a = self.h/4
            if a < 35:
                return a
            else:
                return 35
        elif self.fingerhole == 'deep':
            return self.h-self.thickness-10
        elif self.fingerhole == 'none':
            return 0

    def xSlots(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def ySlots(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            posx = 0
            for x in reversed(self.sx):
                self.fingerHolesAt(posy, posx, x)
                posx += x + self.thickness

    def xHoles(self):
        posx = -0.5 * self.thickness
        for x in self.sx[:-1]:
            posx += x + self.thickness
            self.fingerHolesAt(posx, 0, self.hi)

    def yHoles(self):
        posy = -0.5 * self.thickness
        for y in self.sy[:-1]:
            posy += y + self.thickness
            self.fingerHolesAt(posy, 0, self.hi)

    def gripHole(self):
        if not self.gw:
            return

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        r = min(self.gw, self.gh) / 2.0
        self.rectangularHole(x / 2.0, self.gh * 1.5, self.gw, self.gh, r)

    def textCB(self):
        ## declare text-variables
        textsize = self.text_size
        texty = self.hi - textsize - self.text_distance_y
        if self.text_alignment == 'center':
            texty -= self.fingerholedepth
        textdistance = self.sx[0] + self.thickness

        ## Generate text-fields for each tray
        for n in range(len(self.sx)):
            # Break for-loop if further list is empty
            if self.textnumber >= len(self.textcontent):
                break

            textx = n * (self.sx[0] + self.thickness)
            # Calculate textposition
            if self.text_alignment == 'left':
                textx += self.text_distance_x
            elif  self.text_alignment == 'center':
                textx += self.sx[0] / 2
            elif self.text_alignment == 'right':
                textx += self.sx[0] - self.text_distance_x

            # Generate text
            self.text(
                "%s" % self.textcontent[self.textnumber],
                textx,
                texty,
                0,
                align=self.text_alignment,
                fontsize=textsize,
                color=Color.ETCHING)
            self.textnumber +=1

    def render(self):
        if self.outside:
            self.sx = self.adjustSize(self.sx)
            self.sy = self.adjustSize(self.sy)
            self.h = self.adjustSize(self.h, e2=False)
            if self.hi:
                self.hi = self.adjustSize(self.hi, e2=False)

        x = sum(self.sx) + self.thickness * (len(self.sx) - 1)
        y = sum(self.sy) + self.thickness * (len(self.sy) - 1)
        h = self.h
        sameh = not self.hi
        hi = self.hi = self.hi or h
        t = self.thickness

        # outer walls
        b = self.bottom_edge
        tl, tb, tr, tf = self.topEdges(self.top_edge)
        self.closedtop = self.top_edge in "fFhŠ"

        bh = self.back_height if self.top_edge == "e" else 0.0

        self.textcontent = "".join(self.layout).split("\r\n")
        self.textnumber = 0

        # x sides

        self.ctx.save()

        # outer walls - front/back
        if bh:
            self.rectangularWall(x, h+bh, [b, "f", tb, "f"],
                                 callback=[self.xHoles],
                                 ignore_widths=[],
                                 move="up", label="back")
            self.rectangularWall(x, h, ["f" if self.handle else b, "f", tf, "f"],
                                 callback=[self.mirrorX(self.xHoles, x),
                                           None, self.gripHole],
                                 move="up", label="front")
        else:
            self.rectangularWall(x, h, [b, "F", tb, "F"],
                                 callback=[self.xHoles],
                                 ignore_widths=[1, 6],
                                 move="up", label="back")
            self.rectangularWall(x, h, ["f" if self.handle else b, "F", tf, "F"],
                                 callback=[self.mirrorX(self.xHoles, x),
                                           None, self.gripHole],
                                 ignore_widths=[] if self.handle else [1, 6],
                                 move="up", label="front")

        # floor
        if b != "e":
            if self.handle:
                self.rectangularWall(x, y, "ffYf", callback=[self.xSlots, self.ySlots], move="up", label="bottom")
            else:
                self.rectangularWall(x, y, "ffff", callback=[self.xSlots, self.ySlots], move="up", label="bottom")

        # Inner walls

        be = "f" if b != "e" else "e"

        # set finger holes
        s = FingerHoleEdgeSettings(thickness=t, wallheight=h, fingerholedepth=self.fingerholedepth)
        p = FingerHoleEdge(self, s)
        p.char = "A"
        self.addPart(p)

        ######
        for i in range(len(self.sy) - 1):

            ## set horizontal divider
            ### if fingerholedepth is set to 0 create a straight edge, otherwise a fingerhole
            if self.fingerholedepth == 0:
                e = [edges.SlottedEdge(self, self.sx, be), "f",
                     edges.SlottedEdge(self, self.sx[::-1], "e", slots=0.5 * hi), "f"]
            else:
                e = [edges.SlottedEdge(self, self.sx, be), "f",
                    edges.SlottedEdge(self, self.sx[::-1], "A", slots=0.5 * hi), "f"]

            if self.closedtop and sameh:
                e = [edges.SlottedEdge(self, self.sx, be), "f",
                     edges.SlottedEdge(self, self.sx[::-1], "f", slots=0.5 * hi), "f"]

            self.rectangularWall(x, hi, e, move="up", callback=[self.textCB],
                                 label=f"inner x {i+1}")

        # top / lid
        if self.closedtop and sameh:
            e = "FFFF" if self.top_edge == "f" else "ffff"
            self.rectangularWall(x, y, e, callback=[
                self.xSlots, self.ySlots], move="up", label="top")
        else:
            self.drawLid(x, y, self.top_edge)
        self.lid(x, y, self.top_edge)

        self.ctx.restore()
        self.rectangularWall(x, hi, "ffff", move="right only")

        # y walls

        # outer walls - left/right

        if bh:
            self.trapezoidSideWall(
                y, h, h+bh, [b, "h", "e", "h"],
                radius=self.radius, callback=[self.yHoles, ],
                move="up", label="left side")
            self.trapezoidSideWall(
                y, h+bh, h, [b, "h", "e", "h"], radius=self.radius,
                callback=[self.mirrorX(self.yHoles, y), ],
                move="up", label="right side")
        else:
            self.rectangularWall(
                y, h, [b, "f", tl, "f"], callback=[self.yHoles, ],
                ignore_widths=[6] if self.handle else [1, 6],
                move="up", label="left side")
            self.rectangularWall(
                y, h, [b, "f", tr, "f"],
                callback=[self.mirrorX(self.yHoles, y), ],
                ignore_widths=[1] if self.handle else [1, 6],
                move="up", label="right side")

        # inner walls
        for i in range(len(self.sx) - 1):
            e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * hi),
                 "f", "e", "f"]
            if self.closedtop and sameh:
                e = [edges.SlottedEdge(self, self.sy, be, slots=0.5 * hi),"f",
                     edges.SlottedEdge(self, self.sy[::-1], "f"), "f"]
            self.rectangularWall(y, hi, e, move="up", label=f"inner y {i+1}")
