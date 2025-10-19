from .RegenTreasurePlannerAI import RegenTreasurePlannerAI
from toontown.quest import Quests
from direct.directnotify import DirectNotifyGlobal

class SZTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SZTreasurePlannerAI')

    def __init__(self, zoneId, treasureType, healAmount, spawnPoints, spawnRate, maxTreasures):
        self.zoneId = zoneId
        self.spawnPoints = spawnPoints
        self.healAmount = healAmount
        self.treasureType = treasureType
        RegenTreasurePlannerAI.__init__(self, zoneId, treasureType, 'SZTreasurePlanner-%d' % zoneId, spawnRate, maxTreasures)

    def initSpawnPoints(self):
        pass

    def validAvatar(self, treasure, av):
        # Avatars can only heal if they are missing some health, but aren't sad.
        if self.treasureType == 10:
            av.addMoney(self.healAmount)
            return True
        if self.treasureType == 11:
            avQuests = av.quests
            for questDesc in avQuests:
                questClass = Quests.getQuestClass(questDesc[0])
                if (questClass == Quests.FindPackageQuest):
                    quest = Quests.getQuest(questDesc[0])
                    if quest.getPackageZoneId() == self.zoneId:
                        completed = quest.getCompletionStatus(av, questDesc) == Quests.COMPLETE
                        if not completed:
                            questDesc[4] += 1
                            av.updateQuests()
                            return True
            
        else:
            if av.getHp() < av.getMaxHp() and av.getHp() > 0:
                av.toonUp(self.healAmount)
                return True
            else:
                return False
