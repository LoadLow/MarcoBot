# coding: utf8

"""
Simple IRC Bot for Twitch.tv

Developed by Aidan Thomson <aidraj0@gmail.com>
"""

import lib.irc as irc_
from lib.functions_general import *
import lib.functions_commands as commands
from src.lib import channel_runtime


class MarcoBot:
    def __init__(self, config, credentials):
        self.config = config
        self.irc = irc_.irc(config, credentials)
        self.socket = self.irc.get_irc_socket_object()


    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config

        while True:
            data = sock.recv(config['socket_buffer_size']).rstrip()

            if len(data) == 0:
                pp('Connection was lost, reconnecting.')
                sock = self.irc.get_irc_socket_object()

            if config['debug']:
                print data

            # check for ping, reply with pong
            irc.check_for_ping(data)

            for channel in config['channels'] :
                channel_runtime.of(channel)

            if irc.check_for_message(data):
                message_dict = irc.get_message(data)

                channel = message_dict['channel']
                message = message_dict['message']
                username = message_dict['username']

                ppi(channel, message, username)

                if username.lower() == "Alexbip15_bot".lower():
                    continue

                lowerMsg = message.lower()
                if "eu ta nouvelle manette" in lowerMsg \
                        or "ta nouvelle manette" in lowerMsg\
                        or "ta manette" in lowerMsg\
                        or "eu ta manette" in lowerMsg\
                        or "alors ta nouvelle manette" in lowerMsg:
                    result = "Oui j'ai recu ma nouvelle manette et oui elle va bien ! - marco8641, 5/16/2015"
                    resp = '%s' % result
                    pbot(resp, channel)
                    irc.send_message(channel, resp)
                    continue

                # check if message is a command with no arguments
                if commands.is_valid_command(message) or commands.is_valid_command(message.split(' ')[0]):
                    command = message

                    if commands.is_protected(message.split(' ')[0]) \
                                    and not username in channel_runtime.of(channel).moderators:
                                continue

                    if commands.check_returns_function(command.split(' ')[0]):
                        if commands.check_has_correct_args(command, command.split(' ')[0]):
                            args = command.split(' ')
                            del args[0]

                            command = command.split(' ')[0]

                            """if commands.is_on_cooldown(command, channel):
                                pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                    command, username, commands.get_cooldown_remaining(command, channel)),
                                    channel
                                )
                            else:
                                pbot('Command is valid an not on cooldown. (%s) (%s)' % (
                                    command, username),
                                    channel
                                )"""

                            #args.append(username)
                            result = commands.pass_to_function(command, args, username, channel_runtime.of(channel))
                            commands.update_last_used(command, channel)

                            if result:
                                resp = '%s' % result
                                pbot(resp, channel)
                                irc.send_message(channel, resp)

                    else:
                        """if commands.is_on_cooldown(command, channel):
                            pbot('Command is on cooldown. (%s) (%s) (%ss remaining)' % (
                                    command, username, commands.get_cooldown_remaining(command, channel)),
                                    channel
                            )
                        elif commands.check_has_return(command):
                            pbot('Command is valid and not on cooldown. (%s) (%s)' % (
                                command, username),
                                channel
                            )"""
                        commands.update_last_used(command, channel)

                        resp = '%s' % commands.get_return(command)
                        commands.update_last_used(command, channel)
                        if resp != "nothing":
                            pbot(resp, channel)
                            irc.send_message(channel, resp)
