#
# Client code for Update Agent
# Copyright (c) 1999-2002 Red Hat, Inc.  Distributed under GPL.
#
# Author: Preston Brown <pbrown@redhat.com>
#         Adrian Likins <alikins@redhat.com
#         Cristian Gafton <gafton@redhat.com>
#

import up2dateLog
import gettext
t = gettext.translation('rhn-client-tools', fallback=True)
_ = t.ugettext
import OpenSSL
import config
from platform import getPlatform

class Error:
    """base class for errors"""
    premsg = ''
    def __init__(self, errmsg):
        self.errmsg = self.premsg + errmsg
        self.log = up2dateLog.initLog()

    def __repr__(self):
        self.log.log_me(self.errmsg)
        return self.errmsg
    
class RpmError(Error):
    """rpm itself raised an error condition"""
    premsg = _("RPM error.  The message was:\n")

class RhnServerException(Error):
    pass

class PasswordError(RhnServerException):
    """Raise when the server responds with that a password is incorrect"""
    premsg = _("Password error. The message was:\n")

class DependencyError(Error):
    """Raise when a rpm transaction set has a dependency error"""
    premsg = _("RPM dependency error. The message was:\n")
    def __init__(self, msg, deps=None):
        Error.__init__(self, msg)
        # just tag on the whole deps tuple, so we have plenty of info
        # to play with
        self.deps = deps


class CommunicationError(RhnServerException):
    """Indicates a problem doing xml-rpc http communication with the server"""
    premsg = _("Error communicating with server. "\
                 "The message was:\n")

class FileNotFoundError(Error):
    """
    Raise when a package or header that is requested returns
    a 404 error code"""
    premsg =  _("File Not Found: \n")


class DelayError(RhnServerException):
    """
    Raise when the expected response from a xml-rpc call
    exceeds a timeout"""
    premsg =  _("Delay error from server.  The message was:\n")

class RpmRemoveError(Error):
    """
    Raise when we can't remove a package for some reason
    (failed deps, etc)"""
    def __init__(self, args):
        self.args = args
        self.errmsg = ""
        for key in self.args.keys():
            self.errmsg = self.errmsg + "%s failed because of %s\n" % (
                key, self.args[key])
        self.data = self.args
    def __repr__(self):
        return self.errmsg

class NoLogError(Error):
    def __init__(self, msg):
        self.errmsg = self.premsg + msg

    def __repr__(self):
        return self.errmsg

class AbuseError(Error):
    pass

class AuthenticationTicketError(NoLogError, RhnServerException):
    pass

class AuthenticationError(NoLogError):
    pass

class ValidationError(NoLogError, RhnServerException):
    """indicates an error during server input validation"""
    premsg = _("Error validating data at server:\n")

class InvalidRegistrationNumberError(ValidationError):
    pass

class InvalidProductRegistrationError(NoLogError):
    """indicates an error during server input validation"""
    premsg = _("The installation number is invalid")
    
class OemInfoFileError(NoLogError):
    premsg = _("Error parsing the oemInfo file at field:\n")

class NoBaseChannelError(NoLogError, RhnServerException):
    """No valid base channel was found for this system"""
    pass

class UnknownMethodException(NoLogError, RhnServerException):
    pass

class RhnUuidUniquenessError(NoLogError, RhnServerException):
    pass

class ServerCapabilityError(Error):
    def __init__(self, msg, errorlist=None):
        self.errmsg = msg
        self.errorlist = []
        if errorlist:
            self.errorlist=errorlist

    def __repr__(self):
        return self.errmsg

class NoChannelsError(NoLogError):
    pass

if getPlatform() == 'deb':
    RepoError = Error
else:
    from yum.Errors import RepoError

class SSLCertificateVerifyFailedError(RepoError):
    def __init__(self):
        # Need to override __init__ because the base class requires a message arg
        # and this exception shouldn't.
        up2dateConfig = config.initUp2dateConfig()
        certFile = up2dateConfig['sslCACert']
        f = open(certFile, "r")
        buf = f.read()
        f.close()
        tempCert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, buf)
        if tempCert.has_expired():
            RepoError.__init__(self ,"The certificate %s is expired. Please ensure you have the correct"
                           " certificate and your system time is correct." % certFile)
        else:
            RepoError.__init__(self, "The SSL certificate %s failed verification." % certFile)

class SSLCertificateFileNotFound(Error):
    pass


class AuthenticationOrAccountCreationError(ValidationError):
    """Class that can represent different things depending on context:
    While logging in with an existing user it represents a username or password 
    being incorrect.
    While creating a new account, it represents the username already being 
    taken or the user not being allowed to create an account.
    Optimally these different things would be different exceptions, but there
    are single fault codes the server can return to the client that can mean
    more than one of them so we have no way of knowing which is actually 
    intended.
    
    """
    pass

class NotEntitlingError(Error):
    pass

class InvalidProtocolError(Error):
    pass

class UnableToCreateUser(NoLogError):
     pass

class ActivationKeyUsageLimitError(NoLogError):
    pass

class LoginMinLengthError(NoLogError):
    pass

class PasswordMinLengthError(NoLogError):
    pass

class PasswordMaxLengthError(NoLogError):
    pass


class InsuffMgmntEntsError(RhnServerException):
    def __init__(self, msg ):
        self.errmsg = self.changeExplanation(msg)

    def __repr__(self):
        return self.errmsg

    def changeExplanation(self, msg):
        newExpln = _("""
    Your organization does not have enough Management entitlements to register this
    system to Red Hat Network. Please notify your organization administrator of this error. 
    You should be able to register this system after your organization frees existing 
    or purchases additional entitlements. Additional entitlements may be purchased by your
    organization administrator by logging into Red Hat Network and visiting
    the 'Subscription Management' page in the 'Your RHN' section of RHN.
    
    A common cause of this error code is due to having mistakenly setup an
    Activation Key which is set as the universal default.  If an activation key is set
    on the account as a universal default, you can disable this key and retry to avoid
    requiring a Management entitlement.""")
        term = "Explanation:"
        loc = msg.rindex(term) + len(term)
        return msg[:loc] + newExpln 

class NoSystemIdError(NoLogError):
    pass

class InvalidRedirectionError(NoLogError):
    """ Raise when redirect requests could'nt return a package"""
    pass
