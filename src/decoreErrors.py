# -*- coding: utf-8 -*-
"""DeCore için özel exceptionlar. Açıklama gelecek."""
class UndefinedDeviceException(Exception):
    """Config dosyası olmayan cihazlarda raise edilecek exception."""
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)
class DecoreServerConnectionException(Exception):
    """Sunucu bağlantısı patlarsa raise edilecek exception."""
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)