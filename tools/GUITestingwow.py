from direct.showbase.MessengerGlobal import *
from toontown.toonbase.ToonBase import ToonBase
from panda3d.core import *
from panda3d.core import loadPrcFile
from direct.gui import DirectGuiGlobals
from direct.interval.IntervalGlobal import *

from imgui_bundle import imgui

import p3dimgui

loadPrcFile('config/dev.prc')

'''Prepare VFS'''
from panda3d.core import VirtualFileSystem, ConfigVariableList, Filename
vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

class MyApp(ToonBase):

    def __init__(self):
        ToonBase.__init__(self)
        self.disableMouse()
        self.addCullBins()
        self.initNametagGlobals()

        """
        #TTR AUDITOR BEAR CAMERA
        .setPosHprScale((0.00, -9.80, 7.45), (0.00, -10.80, 0.00), (1.00, 1.00, 1.00))
        """

        # Install Dear ImGui
        p3dimgui.init()

        from toontown.suit import DistributedSuitBase
        from toontown.suit import SuitDNA

        self.demotedCeo = DistributedSuitBase.DistributedSuitBase(None)
        self.demotedCeo.dna = SuitDNA.SuitDNA()
        self.demotedCeo.dna.newSuit('aud')
        self.demotedCeo.setDNA(self.demotedCeo.dna)
        self.demotedCeo.reparentTo(render)
        self.demotedCeo.loop('neutral')
        self.demotedCeo.setPos(2, 5.3, 0)
        self.demotedCeo.setH(170)
        self.demotedCeo.corpMedallion.hide()
        self.demotedCeo.healthBar.show()
        self.demotedCeo.setBlend(frameBlend=True)
        self.demotedCeo.doId = 1
        #self.demotedCeo.stash()

        self.demotedCeo2 = DistributedSuitBase.DistributedSuitBase(None)
        self.demotedCeo2.dna = SuitDNA.SuitDNA()
        self.demotedCeo2.dna.newSuit('tw')
        self.demotedCeo2.setDNA(self.demotedCeo2.dna)
        self.demotedCeo2.reparentTo(render)
        self.demotedCeo2.loop('neutral')
        self.demotedCeo2.setPos(-2, 5.3, 0)
        self.demotedCeo2.setH(180)
        self.demotedCeo2.setLevelDist(2)
        self.demotedCeo2.healthBar.show()
        self.demotedCeo2.corpMedallion.hide()
        self.demotedCeo2.setHP(40)
        self.demotedCeo2.doId = 2
        self.demotedCeo2.setBlend(frameBlend=True)
        #self.demotedCeo.stash()

        self.auditorSfx = self.loader.loadSfx('phase_4/audio/sfx/ttr_s_ene_cgc_cashbotAuditor_marketFlip.ogg')
        #self.auditorCoins = self.loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_payRaise.bam')
        #self.auditorCoins.setPos(self.demotedCeo2.getPos())
        #self.auditorCoins.reparentTo(render)
        #self.auditorCoins.setZ(-4)
        base.camLens.setMinFov(80.0/(4./3.))
        camera.setPosHprScale((0.00, -9.80, 7.45), (0.00, -10.80, 0.00), (1.00, 1.00, 1.00))
        """
        self.auditorOtherSuitTrack = Sequence(
            Wait(3.0),
            ActorInterval(self.demotedCeo2, 'pie-small-react', duration=0.2), Func(self.demotedCeo2.setLevel, self.demotedCeo2.getLevel() + 1), Func(self.demotedCeo2.showHpText, self.demotedCeo2.getMaxHP() - self.demotedCeo2.getHP()), Func(self.demotedCeo2.setHP, self.demotedCeo2.getMaxHP() + 1),
            Parallel(Func(self.demotedCeo2.setZ, 3), self.auditorCoins.posInterval(0.2, Point3(self.demotedCeo2.getX(), self.demotedCeo2.getY(), 0), blendType='easeInOut'), ActorInterval(self.demotedCeo2, 'slip-forward', startTime=2.43)))

        self.auditorCoinsLowerTrack = Parallel(
            self.demotedCeo2.posInterval(0.2, Point3(self.demotedCeo2.getX(), self.demotedCeo2.getY(), 0), blendType='easeInOut'),
            Sequence(self.auditorCoins.posInterval(0.2, Point3(self.demotedCeo2.getX(), self.demotedCeo2.getY(), -4), blendType='easeInOut'),
            Func(self.auditorCoins.hide))
        )

        self.auditorPromoteTrack = Sequence(
            Parallel(self.auditorOtherSuitTrack,
            Sequence(Wait(0.3), ActorInterval(self.demotedCeo, 'promoting')),
            SoundInterval(self.auditorSfx, node=self.demotedCeo)),
            self.auditorCoinsLowerTrack
        )
        """

        self.auditorPromoteTrack = Sequence(
            Parallel(Sequence(Wait(0.3), ActorInterval(self.demotedCeo, 'double-hand-whistle')),
            SoundInterval(self.auditorSfx, node=self.demotedCeo)), Func(self.demotedCeo.loop, 'neutral')
        )
        

        #OTHER SUIT TIME: 3 secs

        


        # This assumes that the ExplorerManager has replaced the .explore() method.
        self.render.explore()
        
        self.auditorPromoteTrack.popupControls()

        self.accept('imgui-new-frame', self.draw)

    def draw(self):
        # Show the demo window.
        imgui.show_demo_window()

base = MyApp()

'''Prepare GUI Globals'''
DirectGuiGlobals.setDefaultDialogGeom(base.loader.loadModel('phase_3/models/gui/dialog_box_gui'))
DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
DirectGuiGlobals.setDefaultFont(base.loader.loadFont('phase_3/fonts/ImpressBT.ttf'))

base.run()