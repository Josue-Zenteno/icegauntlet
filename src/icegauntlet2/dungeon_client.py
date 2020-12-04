#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W1203

'''
    ICE Gauntlet ONLINE GAME
'''

import sys
import atexit
import logging
import argparse
import json

import Ice
Ice.loadSlice('IceGauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

import game
import game.common
import game.screens
import game.pyxeltools
import game.orchestration


EXIT_OK = 0
BAD_COMMAND_LINE = 1

DEFAULT_ROOM = 'tutorial.json'
DEFAULT_HERO = game.common.HEROES[0]

class RemoteDungeonMap(Ice.Application):
    def run(self, gameProxy):
        try:
            #gameProxy = input("Introduce el Proxy del servicio de juego: ")
            cantidadDeMapas = input("Cuantos mapas quieres jugar:")
            proxy = self.communicator().stringToProxy(gameProxy[0])
            gameServer = IceGauntlet.GamePrx.checkedCast(proxy)
            #print("\nTe has conectado al Proxy: " + gameProxy)
            
            if not gameServer:
                raise RuntimeError('Invalid proxy')
            
            new_levels = self.getRooms(gameServer, int(cantidadDeMapas))
            self._levels_ = new_levels
            #print(self._levels_)

        except IceGauntlet.RoomNotExists:
            print("No hay mapas disponibles en el servidor")
    
    def getRooms(self, gameServer, cantidadDeMapas):
        rooms = list()
        for i in range(cantidadDeMapas):
            roomData = gameServer.getRoom()
            rooms.append(self.saveRoom(roomData))
        return rooms

    def saveRoom(self, roomData):
        roomDict = json.loads(roomData)
        roomName=""
        for x in roomDict["room"].split(' '):
            roomName+=x
        roomFile = roomName+'.json'
        roomFilePath = './src/icegauntlet2/assets/'+roomName+'.json'
        
        with open(roomFilePath, 'w') as roomfile:
            json.dump(roomDict, roomfile, indent=4)
        
        return roomFile
    
    def generateDungeonMap(self):
        return game.DungeonMap(self._levels_)

@atexit.register
# pylint: disable=W0613
def bye(*args, **kwargs):
    '''Exit callback, use for shoutdown'''
    print('Thanks for playing!')
# pylint: enable=W0613

def parse_commandline():
    '''Parse and check commandline'''
    parser = argparse.ArgumentParser('IceDungeon Local Game')
    #parser.add_argument('LEVEL', nargs='+', default=[DEFAULT_ROOM], help='List of levels')
    parser.add_argument("PROXY", help="Proxy del servicio de juego")
    parser.add_argument(
        '-p', '--player', default=DEFAULT_HERO, choices=game.common.HEROES,
        dest='hero', help='Hero to play with'
    )
    options = parser.parse_args()

    #for level_file in options.LEVEL:
        #if not game.assets.search(level_file):
            #logging.error(f'Level "{level_file}" not found!')
            #return None
    return options


def main():
    '''Start game according to commandline'''
    user_options = parse_commandline()
    if not user_options:
        return BAD_COMMAND_LINE

    game.pyxeltools.initialize()
    remoteDungeon = RemoteDungeonMap()
    arg = list()
    arg.append(user_options.PROXY)
    remoteDungeon.main(arg)
    dungeon = remoteDungeon.generateDungeonMap()
    gauntlet = game.Game(user_options.hero, dungeon)
    gauntlet.add_state(game.screens.TileScreen, game.common.INITIAL_SCREEN)
    gauntlet.add_state(game.screens.StatsScreen, game.common.STATUS_SCREEN)
    gauntlet.add_state(game.screens.GameScreen, game.common.GAME_SCREEN)
    gauntlet.add_state(game.screens.GameOverScreen, game.common.GAME_OVER_SCREEN)
    gauntlet.add_state(game.screens.GoodEndScreen, game.common.GOOD_END_SCREEN)
    gauntlet.start()

    return EXIT_OK

if __name__ == '__main__':
    sys.exit(main())