from . import TownLoader
from . import DLStreet
from toontown.suit import Suit
from toontown.toontowngui import TTDialog
from toontown.toonbase import TTLocalizer

class DLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.musicFile = 'phase_8/audio/bgm/DL_SZ.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DL_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.xml'
        self.snoozeSquareText = TTDialog.TTDialog(
            style=TTDialog.Acknowledge,
            text=TTLocalizer.SnoozeSquareDialogInfo,
            text_wordwrap=15,
            command=self.snoozeSquareBoxClose)

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        Suit.loadSuits(3)
        dnaFile = 'phase_8/dna/donalds_dreamland_' + str(self.canonicalBranchZone) + '.xml'
        self.createHood(dnaFile)

    def snoozeSquareBoxClose(self, buttonValue=None):
        self.snoozeSquareText.hide()

    def unload(self):
        Suit.unloadSuits(3)
        TownLoader.TownLoader.unload(self)
