'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at
    http://aws.amazon.com/apache2.0/
or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import sys
import os
import irc.bot
import requests
import subprocess
import zipfile
import re

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print ('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)
        

    def on_welcome(self, c, e):
        print ('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        message = "/me bot connected"
        c.privmsg(self.channel, message)

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        print (e)
        print (e.arguments[0])
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            try:
                arg1 = e.arguments[0].split(' ')[1][0:]
            except IndexError:
                arg1 = None
            try:
                sender = e.source.split('!')[0]
            except IndexError:
                sender = None
            try:
                mod = e.tags[8]['value']
            except IndexError:
                mod = None
            print ('Received command: ' + cmd)
            self.do_command(e, cmd, arg1, sender, mod)
        return

    def do_command(self, e, cmd, arg1, sender, mod):
        try:
            c = self.connection
            howto = "To request a map find the key of it on http://ohshapes.com and put it behind this command"   
            notfound = "A map with that key was not found, recheck key on http://ohshapes.com"
            
#            # Poll the API to get current game.
#            if cmd == "game":
#                url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
#                headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
#                r = requests.get(url, headers=headers).json()
#                c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])
#
#            # Poll the API the get the current status of the stream
#            elif cmd == "title":
#                url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
#                headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
#                r = requests.get(url, headers=headers).json()
#                c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])
#
            # Responds with most recently uploaded map
            if cmd == "oslatest":
                url = 'http://ohshapes.com/api/maps/latest/0?'
                r = requests.get(url).json()
                c.privmsg(self.channel, 'Most recently uploaded was ' + r['docs'][0]['metadata']['songName'] + ' by ' + r['docs'][0]['metadata']['songAuthorName'] + ' uploaded by ' + r['docs'][0]['uploader']['username'] + " (" + r['docs'][0]['key'] + ")" )
            
            # Request a map from http://OhShapes.com and put it in current directory
            elif cmd == "osr":  
                if arg1 == None:   
                    c.privmsg(self.channel, howto)
                elif arg1 == "?":
                    c.privmsg(self.channel, howto)
                elif arg1 == "help":
                    c.privmsg(self.channel, howto)
                elif arg1 == "howto":
                    c.privmsg(self.channel, howto)
                else:
                    url = 'http://ohshapes.com/api/maps/detail/'
                    try:
                        with open('blocklist.txt') as f:
                            blocked = [line.rstrip() for line in f]
                        if arg1 in blocked :
                            c.privmsg(self.channel, arg1 + ' was blocked')
                        else:
                            r = requests.get(url + arg1).json()

                            if len(str(r['stats']['rating'])[2:4]) == 1:
                                rating = str(r['stats']['rating'])[2:4] + "0"
                            else:
                                rating = str(r['stats']['rating'])[2:4]
                            c.privmsg(self.channel, r['metadata']['songName'] + ' ' + str(rating) + '% (' + r['key'] + ') was added to requests.')
                            
                            # Downloading map
                            url2 = 'http://ohshapes.com'
                            r2 = requests.get(url2 + r['directDownload'])
                            open(r['key'] + ' (' + re.sub('[^A-z0-9 ]+', '', r['metadata']['songName']) + ' - ' + re.sub('[^A-z0-9 ]+', '', r['metadata']['levelAuthorName']) + ')' + '.zip' , 'xb').write(r2.content)
                            os.mkdir(os.getcwd() + '\\' + r['key'] + ' (' + re.sub('[^A-z0-9 ]+', '', r['metadata']['songName']) + ' - ' + re.sub('[^A-z0-9 ]+', '', r['metadata']['levelAuthorName']) + ')' + '\\')
                            
                            # Unzipping
                            zip = zipfile.ZipFile(r['key'] + ' (' + re.sub('[^A-z0-9 ]+', '', r['metadata']['songName']) + ' - ' + re.sub('[^A-z0-9 ]+', '', r['metadata']['levelAuthorName']) + ')' + '.zip')
                            zip.extractall(os.getcwd() + '\\' + r['key'] + ' (' + re.sub('[^A-z0-9 ]+', '', r['metadata']['songName']) + ' - ' + re.sub('[^A-z0-9 ]+', '', r['metadata']['levelAuthorName']) + ')' + '\\')
                    except FileExistsError:
                        print("File already exists")
                    except ValueError:
                        c.privmsg(self.channel, notfound)
            
            # Block a map from being requested
            elif cmd == "block":
                if self.channel[1:] == sender or mod == "1" :
                    if arg1 == None:
                        c.privmsg(self.channel, 'Specify a key to block')
                    else:
                        # Open the file in append & read mode ('a+')
                        with open('blocklist.txt') as f:
                            blocked = [line.rstrip() for line in f]
                        if arg1 in blocked :
                            c.privmsg(self.channel, arg1 + ' is already blocked')
                        else:
                            with open("blocklist.txt", "a+") as file_object:
                                # Move read cursor to the start of file.
                                file_object.seek(0)
                                data = file_object.read(100)
                                # Append text at the end of file
                                file_object.write(arg1)
                                file_object.write("\n")
                            c.privmsg(self.channel, arg1 + ' has been blocked')
                else:
                    c.privmsg(self.channel, 'Only mods can block')
                
            # Unblock a map so it can be requested again
            elif cmd == "unblock":
                if self.channel[1:] == sender or mod == 1 :
                    with open('blocklist.txt') as f:
                        blocked = [line.rstrip() for line in f]
                    if arg1 == None:
                        c.privmsg(self.channel, 'Specify a key to block')
                    elif arg1 in blocked :
                        #read input file
                        fin = open("blocklist.txt", "rt")
                        #read file contents to string
                        data = fin.read()
                        #replace all occurrences of the required string
                        data = data.replace(arg1 + "\n" , '')
                        #close the input file
                        fin.close()
                        #open the input file in write mode
                        fin = open("blocklist.txt", "wt")
                        #overrite the input file with the resulting data
                        fin.write(data)
                        #close the file
                        fin.close()
                        c.privmsg(self.channel, arg1 + ' in now unblocked')
                    else:
                        c.privmsg(self.channel, arg1 + ' was not blocked')
                else:
                    c.privmsg(self.channel, 'Only mods can unblock')
            # The command was not recognized
            else:
                print("Did not understand command: " + cmd + " " + arg1 )
        except:
            c.privmsg(self.channel, 'Something went wrong, please contact joerkig#1337 on Discord')

def main():
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)
    if os.path.exists('blocklist.txt') == False :
        open('blocklist.txt', 'a').close()

    username  = sys.argv[1]
    client_id = sys.argv[2]
    token     = sys.argv[3]
    channel   = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()