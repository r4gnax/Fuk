nick = "fukrc"
part_message = "DDOS'd while fuking protocols"
timeout = 10
vhost = None
proxy = None # SOCKS5 proxy here (eg: 10.10.10.10:4444)

exploit = False
mass_hilite = False
join_throttle = 3
message_throttle = 0.5
max_channels = 3
max_threads = 10
minimum_users = 10


servers = {
        "127.0.0.1": {"ipv6": False, "ssl": False, "port": 6667, "password": None, "channels":['#yo']},
}



bad_msgs = {
    'Color is not permitted',
    'No external channel messages',
    'You need voice',
    'You must have a registered nick'
}


bad_numerics = {
    '471': 'ERR_CHANNELISFULL',
    '473' : 'ERR_INVITEONLYCHAN',
    '474' : 'ERR_BANNEDFROMCHAN',
    '475' : 'ERR_BADCHANNELKEY',
    '477' : 'ERR_NEEDREGGEDNICK',
    '489' : 'ERR_SECUREONLYCHAN',
    '519' : 'ERR_TOOMANYUSERS',
    '520' : 'ERR_OPERONLY'
}
