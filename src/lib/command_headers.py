from src.config.config import *

commands = {
    '!test': {
        'limit': 30,
        'protected': True,
        'return': 'This is a test!'
    },

    '!startbets': {
        'limit': 0,
        'argc': 0,
        'protected': True,
        'return': 'command'
    },

    '!bet': {
        'limit': 0,
        'argc': 1,
        'return': 'command'
    },

    '!endbets': {
        'limit': 0,
        'argc': 0,
        'protected': True,
        'return': 'command'
    },

    '!winner': {
        'limit': 0,
        'argc': 1,
        'protected': True,
        'return': 'command'
    },

    '!wr': {
        'limit': 0,
        'argc': 0,
        'protected': False,
        'return': 'MM Any% WR is 1:27:09 (by Ennopp112)'
    },

    '!pb': {
        'limit': 0,
        'argc': 0,
        'protected': False,
        'return': 'MM Any% Marco8641\'s PB is 1:29:13 (sub 1:30 :o)'
    }
}

for channel in config['channels']:
    for command in commands:
        commands[command][channel] = {}
        commands[command][channel]['last_used'] = 0
