import gnomekeyring as gkey


class Keyring(object):
    def __init__(self, name, server):
        self._name = name
        self._server = server
        self._protocol = 'imap'
        #self._keyring = gkey.get_default_keyring_sync()

    def hasPassword(self, user):
        try:
            attrs = {"server": self._server, 'protocol': self._protocol}
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            for item in items:
                if item.attributes['user'] == user : return True
            return False
        except gkey.DeniedError:
            return False
        except gkey.NoMatchError:
            return False

    def getPassword(self, user):
        attrs = {"server": self._server, 'protocol': self._protocol}
        items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
        for item in items:
            if item.attributes['user'] == str(user): return item.secret
        return False

    def setPassword(self, user, pw):
        attrs = {
                "user": str(user),
                "server": self._server,
                "protocol": self._protocol
            }
        gkey.item_create_sync(gkey.get_default_keyring_sync(),
                gkey.ITEM_NETWORK_PASSWORD, self._name, attrs, str(pw), True)

