# Twitch Simple OhShapes Requests
Here you will find a simple Python chatbot using IRC adapted to make requests from Twitch chat possible.

## Installation
After you have cloned this repository, use pip or easy_install to install the IRC library.

```sh
$ pip install -r requirements.txt
```

## Usage
To run the chatbot, you will need to provide an OAuth access token with the chat_login scope.  You can reference an authentication sample to accomplish this, or simply use the [Twitch Chat OAuth Password Generator](http://twitchapps.com/tmi/).

```sh
$ python chatbot.py <username> <client id> <token> <channel>
```
* Username - The username of the chatbot
* Client ID - Your registered application's Client ID to allow API calls by the bot
* Token - Your OAuth Token
* Channel - The channel your bot will connect to

## Wishlist
List of things I want to add at some point.
~~* Ability to block maps~~
* An actual queue of some kind
* Store previously downloaded maps and use them when available
