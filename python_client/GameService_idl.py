# Python stubs generated by omniidl from GameService.idl
# DO NOT EDIT THIS FILE!

import omniORB, _omnipy
from omniORB import CORBA, PortableServer
_0_CORBA = CORBA


_omnipy.checkVersion(4,2, __file__, 1)

try:
    property
except NameError:
    def property(*args):
        return None


#
# Start of module "GameModule"
#
__name__ = "GameModule"
_0_GameModule = omniORB.openModule("GameModule", r"GameService.idl")
_0_GameModule__POA = omniORB.openModule("GameModule__POA", r"GameService.idl")


# exception AlreadyLoggedInException
_0_GameModule.AlreadyLoggedInException = omniORB.newEmptyClass()
class AlreadyLoggedInException (CORBA.UserException):
    _NP_RepositoryId = "IDL:GameModule/AlreadyLoggedInException:1.0"

    def __init__(self, message):
        CORBA.UserException.__init__(self, message)
        self.message = message

_0_GameModule.AlreadyLoggedInException = AlreadyLoggedInException
_0_GameModule._d_AlreadyLoggedInException  = (omniORB.tcInternal.tv_except, AlreadyLoggedInException, AlreadyLoggedInException._NP_RepositoryId, "AlreadyLoggedInException", "message", (omniORB.tcInternal.tv_string,0))
_0_GameModule._tc_AlreadyLoggedInException = omniORB.tcInternal.createTypeCode(_0_GameModule._d_AlreadyLoggedInException)
omniORB.registerType(AlreadyLoggedInException._NP_RepositoryId, _0_GameModule._d_AlreadyLoggedInException, _0_GameModule._tc_AlreadyLoggedInException)
del AlreadyLoggedInException

# typedef ... StringSeq
class StringSeq:
    _NP_RepositoryId = "IDL:GameModule/StringSeq:1.0"
    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")
_0_GameModule.StringSeq = StringSeq
_0_GameModule._d_StringSeq  = (omniORB.tcInternal.tv_sequence, (omniORB.tcInternal.tv_string,0), 0)
_0_GameModule._ad_StringSeq = (omniORB.tcInternal.tv_alias, StringSeq._NP_RepositoryId, "StringSeq", (omniORB.tcInternal.tv_sequence, (omniORB.tcInternal.tv_string,0), 0))
_0_GameModule._tc_StringSeq = omniORB.tcInternal.createTypeCode(_0_GameModule._ad_StringSeq)
omniORB.registerType(StringSeq._NP_RepositoryId, _0_GameModule._ad_StringSeq, _0_GameModule._tc_StringSeq)
del StringSeq

# struct GameStateDTO
_0_GameModule.GameStateDTO = omniORB.newEmptyClass()
class GameStateDTO (omniORB.StructBase):
    _NP_RepositoryId = "IDL:GameModule/GameStateDTO:1.0"

    def __init__(self, maskedWord, incorrectGuesses, currentRound, totalRounds, playerWins, roundOver, gameOver, sessionResult, remainingTime, roundWinner, finishedTime):
        self.maskedWord = maskedWord
        self.incorrectGuesses = incorrectGuesses
        self.currentRound = currentRound
        self.totalRounds = totalRounds
        self.playerWins = playerWins
        self.roundOver = roundOver
        self.gameOver = gameOver
        self.sessionResult = sessionResult
        self.remainingTime = remainingTime
        self.roundWinner = roundWinner
        self.finishedTime = finishedTime

_0_GameModule.GameStateDTO = GameStateDTO
_0_GameModule._d_GameStateDTO  = (omniORB.tcInternal.tv_struct, GameStateDTO, GameStateDTO._NP_RepositoryId, "GameStateDTO", "maskedWord", (omniORB.tcInternal.tv_string,0), "incorrectGuesses", omniORB.tcInternal.tv_long, "currentRound", omniORB.tcInternal.tv_long, "totalRounds", omniORB.tcInternal.tv_long, "playerWins", omniORB.tcInternal.tv_long, "roundOver", omniORB.tcInternal.tv_boolean, "gameOver", omniORB.tcInternal.tv_boolean, "sessionResult", (omniORB.tcInternal.tv_string,0), "remainingTime", omniORB.tcInternal.tv_long, "roundWinner", (omniORB.tcInternal.tv_string,0), "finishedTime", omniORB.tcInternal.tv_long)
_0_GameModule._tc_GameStateDTO = omniORB.tcInternal.createTypeCode(_0_GameModule._d_GameStateDTO)
omniORB.registerType(GameStateDTO._NP_RepositoryId, _0_GameModule._d_GameStateDTO, _0_GameModule._tc_GameStateDTO)
del GameStateDTO

# struct SystemStatisticsDTO
_0_GameModule.SystemStatisticsDTO = omniORB.newEmptyClass()
class SystemStatisticsDTO (omniORB.StructBase):
    _NP_RepositoryId = "IDL:GameModule/SystemStatisticsDTO:1.0"

    def __init__(self, totalGames, wins, losses, winRate, waitingTime, roundTime):
        self.totalGames = totalGames
        self.wins = wins
        self.losses = losses
        self.winRate = winRate
        self.waitingTime = waitingTime
        self.roundTime = roundTime

_0_GameModule.SystemStatisticsDTO = SystemStatisticsDTO
_0_GameModule._d_SystemStatisticsDTO  = (omniORB.tcInternal.tv_struct, SystemStatisticsDTO, SystemStatisticsDTO._NP_RepositoryId, "SystemStatisticsDTO", "totalGames", omniORB.tcInternal.tv_long, "wins", omniORB.tcInternal.tv_long, "losses", omniORB.tcInternal.tv_long, "winRate", omniORB.tcInternal.tv_double, "waitingTime", omniORB.tcInternal.tv_long, "roundTime", omniORB.tcInternal.tv_long)
_0_GameModule._tc_SystemStatisticsDTO = omniORB.tcInternal.createTypeCode(_0_GameModule._d_SystemStatisticsDTO)
omniORB.registerType(SystemStatisticsDTO._NP_RepositoryId, _0_GameModule._d_SystemStatisticsDTO, _0_GameModule._tc_SystemStatisticsDTO)
del SystemStatisticsDTO

# struct LeaderboardEntryDTO
_0_GameModule.LeaderboardEntryDTO = omniORB.newEmptyClass()
class LeaderboardEntryDTO (omniORB.StructBase):
    _NP_RepositoryId = "IDL:GameModule/LeaderboardEntryDTO:1.0"

    def __init__(self, username, wins):
        self.username = username
        self.wins = wins

_0_GameModule.LeaderboardEntryDTO = LeaderboardEntryDTO
_0_GameModule._d_LeaderboardEntryDTO  = (omniORB.tcInternal.tv_struct, LeaderboardEntryDTO, LeaderboardEntryDTO._NP_RepositoryId, "LeaderboardEntryDTO", "username", (omniORB.tcInternal.tv_string,0), "wins", omniORB.tcInternal.tv_long)
_0_GameModule._tc_LeaderboardEntryDTO = omniORB.tcInternal.createTypeCode(_0_GameModule._d_LeaderboardEntryDTO)
omniORB.registerType(LeaderboardEntryDTO._NP_RepositoryId, _0_GameModule._d_LeaderboardEntryDTO, _0_GameModule._tc_LeaderboardEntryDTO)
del LeaderboardEntryDTO

# typedef ... LeaderboardEntrySeq
class LeaderboardEntrySeq:
    _NP_RepositoryId = "IDL:GameModule/LeaderboardEntrySeq:1.0"
    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")
_0_GameModule.LeaderboardEntrySeq = LeaderboardEntrySeq
_0_GameModule._d_LeaderboardEntrySeq  = (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:GameModule/LeaderboardEntryDTO:1.0"], 0)
_0_GameModule._ad_LeaderboardEntrySeq = (omniORB.tcInternal.tv_alias, LeaderboardEntrySeq._NP_RepositoryId, "LeaderboardEntrySeq", (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:GameModule/LeaderboardEntryDTO:1.0"], 0))
_0_GameModule._tc_LeaderboardEntrySeq = omniORB.tcInternal.createTypeCode(_0_GameModule._ad_LeaderboardEntrySeq)
omniORB.registerType(LeaderboardEntrySeq._NP_RepositoryId, _0_GameModule._ad_LeaderboardEntrySeq, _0_GameModule._tc_LeaderboardEntrySeq)
del LeaderboardEntrySeq

# interface GameService
_0_GameModule._d_GameService = (omniORB.tcInternal.tv_objref, "IDL:GameModule/GameService:1.0", "GameService")
omniORB.typeMapping["IDL:GameModule/GameService:1.0"] = _0_GameModule._d_GameService
_0_GameModule.GameService = omniORB.newEmptyClass()
class GameService :
    _NP_RepositoryId = _0_GameModule._d_GameService[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_GameModule.GameService = GameService
_0_GameModule._tc_GameService = omniORB.tcInternal.createTypeCode(_0_GameModule._d_GameService)
omniORB.registerType(GameService._NP_RepositoryId, _0_GameModule._d_GameService, _0_GameModule._tc_GameService)

# GameService operations and attributes
GameService._d_login = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.tcInternal.tv_boolean, ), {_0_GameModule.AlreadyLoggedInException._NP_RepositoryId: _0_GameModule._d_AlreadyLoggedInException})
GameService._d_logout = (((omniORB.tcInternal.tv_string,0), ), (), None)
GameService._d_startGame = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_sendGuess = (((omniORB.tcInternal.tv_string,0), omniORB.tcInternal.tv_char), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_finishRound = (((omniORB.tcInternal.tv_string,0), omniORB.tcInternal.tv_long, omniORB.tcInternal.tv_boolean), (), None)
GameService._d_viewLeaderboard = ((), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_getMaskedWord = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_createPlayer = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_deletePlayer = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_updatePlayerPassword = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_updateSettings = ((omniORB.tcInternal.tv_long, omniORB.tcInternal.tv_long), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_updatePlayerUsername = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_updatePlayerWins = (((omniORB.tcInternal.tv_string,0), omniORB.tcInternal.tv_long), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_viewPlayers = ((), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_getRoundTime = ((), (omniORB.tcInternal.tv_long, ), None)
GameService._d_getWaitingTime = ((), (omniORB.tcInternal.tv_long, ), None)
GameService._d_getRemainingTime = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_long, ), None)
GameService._d_getIncorrectGuesses = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_long, ), None)
GameService._d_endGameSession = (((omniORB.tcInternal.tv_string,0), ), (), None)
GameService._d_getCurrentRound = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_long, ), None)
GameService._d_getPlayerWins = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_long, ), None)
GameService._d_startNewRound = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_isRoundOver = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_isGameSessionOver = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_getGameState = (((omniORB.tcInternal.tv_string,0), ), (omniORB.typeMapping["IDL:GameModule/GameStateDTO:1.0"], ), None)
GameService._d_cleanupPlayerSession = (((omniORB.tcInternal.tv_string,0), ), (), None)
GameService._d_addWord = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_updateWord = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_deleteWord = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_getAllWords = ((), (omniORB.typeMapping["IDL:GameModule/StringSeq:1.0"], ), None)
GameService._d_getSystemStatistics = ((), (omniORB.typeMapping["IDL:GameModule/SystemStatisticsDTO:1.0"], ), None)
GameService._d_getLeaderboardEntries = ((), (omniORB.typeMapping["IDL:GameModule/LeaderboardEntrySeq:1.0"], ), None)
GameService._d_startMultiplayerGame = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_getMultiplayerLobbyState = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_sendMultiplayerGuess = (((omniORB.tcInternal.tv_string,0), omniORB.tcInternal.tv_char), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_startMultiplayerNextRound = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_boolean, ), None)
GameService._d_getMatchHistory = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_getMatchDetails = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)

# GameService object reference
class _objref_GameService (CORBA.Object):
    _NP_RepositoryId = GameService._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def login(self, *args):
        return self._obj.invoke("login", _0_GameModule.GameService._d_login, args)

    def logout(self, *args):
        return self._obj.invoke("logout", _0_GameModule.GameService._d_logout, args)

    def startGame(self, *args):
        return self._obj.invoke("startGame", _0_GameModule.GameService._d_startGame, args)

    def sendGuess(self, *args):
        return self._obj.invoke("sendGuess", _0_GameModule.GameService._d_sendGuess, args)

    def finishRound(self, *args):
        return self._obj.invoke("finishRound", _0_GameModule.GameService._d_finishRound, args)

    def viewLeaderboard(self, *args):
        return self._obj.invoke("viewLeaderboard", _0_GameModule.GameService._d_viewLeaderboard, args)

    def getMaskedWord(self, *args):
        return self._obj.invoke("getMaskedWord", _0_GameModule.GameService._d_getMaskedWord, args)

    def createPlayer(self, *args):
        return self._obj.invoke("createPlayer", _0_GameModule.GameService._d_createPlayer, args)

    def deletePlayer(self, *args):
        return self._obj.invoke("deletePlayer", _0_GameModule.GameService._d_deletePlayer, args)

    def updatePlayerPassword(self, *args):
        return self._obj.invoke("updatePlayerPassword", _0_GameModule.GameService._d_updatePlayerPassword, args)

    def updateSettings(self, *args):
        return self._obj.invoke("updateSettings", _0_GameModule.GameService._d_updateSettings, args)

    def updatePlayerUsername(self, *args):
        return self._obj.invoke("updatePlayerUsername", _0_GameModule.GameService._d_updatePlayerUsername, args)

    def updatePlayerWins(self, *args):
        return self._obj.invoke("updatePlayerWins", _0_GameModule.GameService._d_updatePlayerWins, args)

    def viewPlayers(self, *args):
        return self._obj.invoke("viewPlayers", _0_GameModule.GameService._d_viewPlayers, args)

    def getRoundTime(self, *args):
        return self._obj.invoke("getRoundTime", _0_GameModule.GameService._d_getRoundTime, args)

    def getWaitingTime(self, *args):
        return self._obj.invoke("getWaitingTime", _0_GameModule.GameService._d_getWaitingTime, args)

    def getRemainingTime(self, *args):
        return self._obj.invoke("getRemainingTime", _0_GameModule.GameService._d_getRemainingTime, args)

    def getIncorrectGuesses(self, *args):
        return self._obj.invoke("getIncorrectGuesses", _0_GameModule.GameService._d_getIncorrectGuesses, args)

    def endGameSession(self, *args):
        return self._obj.invoke("endGameSession", _0_GameModule.GameService._d_endGameSession, args)

    def getCurrentRound(self, *args):
        return self._obj.invoke("getCurrentRound", _0_GameModule.GameService._d_getCurrentRound, args)

    def getPlayerWins(self, *args):
        return self._obj.invoke("getPlayerWins", _0_GameModule.GameService._d_getPlayerWins, args)

    def startNewRound(self, *args):
        return self._obj.invoke("startNewRound", _0_GameModule.GameService._d_startNewRound, args)

    def isRoundOver(self, *args):
        return self._obj.invoke("isRoundOver", _0_GameModule.GameService._d_isRoundOver, args)

    def isGameSessionOver(self, *args):
        return self._obj.invoke("isGameSessionOver", _0_GameModule.GameService._d_isGameSessionOver, args)

    def getGameState(self, *args):
        return self._obj.invoke("getGameState", _0_GameModule.GameService._d_getGameState, args)

    def cleanupPlayerSession(self, *args):
        return self._obj.invoke("cleanupPlayerSession", _0_GameModule.GameService._d_cleanupPlayerSession, args)

    def addWord(self, *args):
        return self._obj.invoke("addWord", _0_GameModule.GameService._d_addWord, args)

    def updateWord(self, *args):
        return self._obj.invoke("updateWord", _0_GameModule.GameService._d_updateWord, args)

    def deleteWord(self, *args):
        return self._obj.invoke("deleteWord", _0_GameModule.GameService._d_deleteWord, args)

    def getAllWords(self, *args):
        return self._obj.invoke("getAllWords", _0_GameModule.GameService._d_getAllWords, args)

    def getSystemStatistics(self, *args):
        return self._obj.invoke("getSystemStatistics", _0_GameModule.GameService._d_getSystemStatistics, args)

    def getLeaderboardEntries(self, *args):
        return self._obj.invoke("getLeaderboardEntries", _0_GameModule.GameService._d_getLeaderboardEntries, args)

    def startMultiplayerGame(self, *args):
        return self._obj.invoke("startMultiplayerGame", _0_GameModule.GameService._d_startMultiplayerGame, args)

    def getMultiplayerLobbyState(self, *args):
        return self._obj.invoke("getMultiplayerLobbyState", _0_GameModule.GameService._d_getMultiplayerLobbyState, args)

    def sendMultiplayerGuess(self, *args):
        return self._obj.invoke("sendMultiplayerGuess", _0_GameModule.GameService._d_sendMultiplayerGuess, args)

    def startMultiplayerNextRound(self, *args):
        return self._obj.invoke("startMultiplayerNextRound", _0_GameModule.GameService._d_startMultiplayerNextRound, args)

    def getMatchHistory(self, *args):
        return self._obj.invoke("getMatchHistory", _0_GameModule.GameService._d_getMatchHistory, args)

    def getMatchDetails(self, *args):
        return self._obj.invoke("getMatchDetails", _0_GameModule.GameService._d_getMatchDetails, args)

omniORB.registerObjref(GameService._NP_RepositoryId, _objref_GameService)
_0_GameModule._objref_GameService = _objref_GameService
del GameService, _objref_GameService

# GameService skeleton
__name__ = "GameModule__POA"
class GameService (PortableServer.Servant):
    _NP_RepositoryId = _0_GameModule.GameService._NP_RepositoryId


    _omni_op_d = {"login": _0_GameModule.GameService._d_login, "logout": _0_GameModule.GameService._d_logout, "startGame": _0_GameModule.GameService._d_startGame, "sendGuess": _0_GameModule.GameService._d_sendGuess, "finishRound": _0_GameModule.GameService._d_finishRound, "viewLeaderboard": _0_GameModule.GameService._d_viewLeaderboard, "getMaskedWord": _0_GameModule.GameService._d_getMaskedWord, "createPlayer": _0_GameModule.GameService._d_createPlayer, "deletePlayer": _0_GameModule.GameService._d_deletePlayer, "updatePlayerPassword": _0_GameModule.GameService._d_updatePlayerPassword, "updateSettings": _0_GameModule.GameService._d_updateSettings, "updatePlayerUsername": _0_GameModule.GameService._d_updatePlayerUsername, "updatePlayerWins": _0_GameModule.GameService._d_updatePlayerWins, "viewPlayers": _0_GameModule.GameService._d_viewPlayers, "getRoundTime": _0_GameModule.GameService._d_getRoundTime, "getWaitingTime": _0_GameModule.GameService._d_getWaitingTime, "getRemainingTime": _0_GameModule.GameService._d_getRemainingTime, "getIncorrectGuesses": _0_GameModule.GameService._d_getIncorrectGuesses, "endGameSession": _0_GameModule.GameService._d_endGameSession, "getCurrentRound": _0_GameModule.GameService._d_getCurrentRound, "getPlayerWins": _0_GameModule.GameService._d_getPlayerWins, "startNewRound": _0_GameModule.GameService._d_startNewRound, "isRoundOver": _0_GameModule.GameService._d_isRoundOver, "isGameSessionOver": _0_GameModule.GameService._d_isGameSessionOver, "getGameState": _0_GameModule.GameService._d_getGameState, "cleanupPlayerSession": _0_GameModule.GameService._d_cleanupPlayerSession, "addWord": _0_GameModule.GameService._d_addWord, "updateWord": _0_GameModule.GameService._d_updateWord, "deleteWord": _0_GameModule.GameService._d_deleteWord, "getAllWords": _0_GameModule.GameService._d_getAllWords, "getSystemStatistics": _0_GameModule.GameService._d_getSystemStatistics, "getLeaderboardEntries": _0_GameModule.GameService._d_getLeaderboardEntries, "startMultiplayerGame": _0_GameModule.GameService._d_startMultiplayerGame, "getMultiplayerLobbyState": _0_GameModule.GameService._d_getMultiplayerLobbyState, "sendMultiplayerGuess": _0_GameModule.GameService._d_sendMultiplayerGuess, "startMultiplayerNextRound": _0_GameModule.GameService._d_startMultiplayerNextRound, "getMatchHistory": _0_GameModule.GameService._d_getMatchHistory, "getMatchDetails": _0_GameModule.GameService._d_getMatchDetails}

GameService._omni_skeleton = GameService
_0_GameModule__POA.GameService = GameService
omniORB.registerSkeleton(GameService._NP_RepositoryId, GameService)
del GameService
__name__ = "GameModule"

#
# End of module "GameModule"
#
__name__ = "GameService_idl"

_exported_modules = ( "GameModule", )

# The end.
