import gnomekeyring as gkey


class Keyring(object):
    def __init__(self, name='Daaq Mail', server='daaq.mail'):
        self._name = name
        self._server = server
        self._protocol = 'imap'
        #self._keyring = gkey.get_default_keyring_sync()

    def hasPassword(self, user):
        try:
            attrs = {"server": self._server, 'protocol': self._protocol, 'user': str(user)}
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            if items != [] : return True
            return False
            #print items[0].attributes['user']
        except gkey.DeniedError:
            return False
        except gkey.NoMatchError:
            return False

    def getPassword(self, user):
        attrs = {"server": self._server, 'protocol': self._protocol, 'user': str(user)}
        try:
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            if items != [] : return items[0].secret
            return False
        except:
            return False

    def setPassword(self, user, pw):
        attrs = {
                "user": str(user),
                "server": self._server,
                "protocol": self._protocol
            }
        gkey.item_create_sync(gkey.get_default_keyring_sync(),
                gkey.ITEM_NETWORK_PASSWORD, self._name, attrs, str(pw), True)

    def deletePassword(self, user):
        attrs = {"server": self._server, 'protocol': self._protocol, 'user': str(user)}
        try:
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
        except:
            return
        for item in items:
            gkey.item_delete_sync(item.keyring, item.item_id)

