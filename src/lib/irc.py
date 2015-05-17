import socket
import re
import sys
import thread

from functions_general import *
import cron
from src.lib.refresh_moderators import refresh_moderators


class irc:
    def __init__(self, config, credentials):
        self.config = config
        self.credentials = credentials
        self.lastMsg = ""
        self.lastMsgTime = 1

    def check_for_message(self, data):
        if re.match(
                r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$',
                data):
            return True

    def check_is_command(self, message, valid_commands):
        for command in valid_commands:
            if command == message:
                return True

    def check_for_connected(self, data):
        if re.match(r'^:.+ 001 .+ :connected to TMI$', data):
            return True

    def check_for_ping(self, data):
        if data[:4] == "PING":
            self.sock.send('PONG')

    def get_message(self, data):
        return {
            'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
            'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
        }

    def check_login_status(self, data):
        if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return False
        else:
            return True

    def send_message(self, channel, message):
        if message == self.lastMsg:
            self.lastMsgTime += 1
        else:
            self.lastMsgTime = 1

        if self.lastMsgTime > 1:
            self.sock.send('PRIVMSG %s :%s\n' % (channel, (message + " (" + str(self.lastMsgTime) + ")").encode('utf-8')))
        else:
            self.sock.send('PRIVMSG %s :%s\n' % (channel, message.encode('utf-8')))

        self.lastMsg = message

    def get_irc_socket_object(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        self.sock = sock

        try:
            sock.connect((self.config['server'], self.config['port']))
        except:
            pp('Cannot connect to server (%s:%s).' % (self.config['server'], self.config['port']), 'error')
            sys.exit()

        sock.settimeout(None)

        sock.send('USER %s\r\n' % self.credentials['username'])
        sock.send('PASS %s\r\n' % self.credentials['oauth_password'])
        sock.send('NICK %s\r\n' % self.credentials['username'])

        if self.check_login_status(sock.recv(1024)):
            pp('Login successful.')
        else:
            pp('Login unsuccessful. (hint: make sure your oauth token is set in self.config/self.config.py).', 'error')
            sys.exit()

        # start threads for channels that have cron messages to run
        for channel in self.config['channels']:
            if channel in self.config['cron']:
                if self.config['cron'][channel]['run_cron']:
                    thread.start_new_thread(cron.cron(self, channel).run, ())
                if self.config['cron'][channel]['refresh_moderators']:
                    thread.start_new_thread(refresh_moderators(channel).run, ())

        self.join_channels(self.channels_to_string(self.config['channels']))

        return sock

    def channels_to_string(self, channel_list):
        return ','.join(channel_list)

    def join_channels(self, channels):
        pp('Joining channels %s.' % channels)
        self.sock.send('JOIN %s\r\n' % channels)
        pp('Joined channels.')

    def leave_channels(self, channels):
        pp('Leaving chanels %s,' % channels)
        self.sock.send('PART %s\r\n' % channels)
        pp('Left channels.')