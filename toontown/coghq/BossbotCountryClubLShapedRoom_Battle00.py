from panda3d.core import *

GlobalEntities = {0: {'type': 'zone', 'name': 'UberZone', 'comment': '', 'parentEntId': 0, 'scale': LVecBase3f(1, 1, 1), 'description': '', 'visibility': []}, 1000: {'type': 'levelMgr', 'name': 'LevelMgr', 'comment': '', 'parentEntId': 0, 'cogLevel': 0, 'farPlaneDistance': 1500, 'modelFilename': 'phase_12/models/bossbotHQ/ttr_m_ara_bhq_cgcZone12a', 'wantDoors': 1}, 1001: {'type': 'editMgr', 'name': 'EditMgr', 'parentEntId': 0, 'insertEntity': None, 'removeEntity': None, 'requestNewEntity': None, 'requestSave': None}, 1002: {'type': 'model', 'name': '<unnamed>', 'comment': '', 'parentEntId': 0, 'pos': LPoint3f(-57.7353, -1.77506, 0), 'hpr': LVecBase3f(0, 0, 0), 'scale': LVecBase3f(1, 1, 1), 'modelPath': 'phase_12/models/bossbotHQ/ttr_m_ara_bhq_cgcCentersectionSpearhead'}, 1003: {'type': 'battleBlocker', 'name': '<unnamed>', 'comment': '', 'parentEntId': 0, 'pos': LPoint3f(-4.29697, 0.176697, 0), 'hpr': LVecBase3f(-90, 0, 0), 'scale': LVecBase3f(1, 1, 1), 'cellId': 0, 'radius': 15.0}, 1004: {'type': 'battleBlocker', 'name': '<unnamed>', 'comment': '', 'parentEntId': 0, 'pos': LPoint3f(-51.8713, 52.5093, 0), 'hpr': LVecBase3f(180, 0, 0), 'scale': LVecBase3f(1, 1, 1), 'cellId': 1, 'radius': 15.0}}

Scenario0 = {}
levelSpec = {
    'globalEntities': GlobalEntities,
    'scenarios': [Scenario0]
}
