from openwiden.services import exceptions


class RemoteException(exceptions.ServiceException):
    pass


class RemoteSyncException(RemoteException):
    pass
