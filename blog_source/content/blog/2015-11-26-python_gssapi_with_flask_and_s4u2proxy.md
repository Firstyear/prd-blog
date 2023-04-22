+++
title = "python gssapi with flask and s4u2proxy"
date = 2015-11-26
slug = "2015-11-26-python_gssapi_with_flask_and_s4u2proxy"
# This is relative to the root!
aliases = [ "2015/11/26/python_gssapi_with_flask_and_s4u2proxy.html", "blog/html/2015/11/26/python_gssapi_with_flask_and_s4u2proxy.html" ]
+++
# python gssapi with flask and s4u2proxy

[UPDATE: 2019 I don\'t recommend using kerberos - read more
here.](/blog/html/2017/05/23/kerberos_why_the_world_moved_on.html)

I have recently been implementing gssapi negotiate support in a flask
application at work. In almost every case I advise that you use
mod-auth-gssapi: It\'s just better.

But if you have a use case where you cannot avoid implementing you own,
there are some really gotchas in using python-gssapi.

Python-gssapi is the updated, newer, better gssapi module for python,
essentially obsoleting python-kerberos. It will have python 3 support
and is more full featured.

However, like everything to do with gssapi, it\'s fiendishly annoying to
use, and lacks a lot in terms of documentation and examples.

The hardest parts:

-   Knowing how to complete the negotiation with the data set in headers
    by the client
-   Finding that python-gssapi expects you to base64 decode the request
-   Finding how to destroy credentials
-   Getting the delegated credentials into a ccache

Now, a thing to remember is that here, if your kdc support it, you will
be using s4u2proxy automatically. If you want to know more, and you are
using freeipa, you can look into [constrained
delegation](http://www.freeipa.org/page/V4/Service_Constraint_Delegation).

Here is how I implemented the negotiate handler in flask.

:

    def _negotiate_start(req):
        # This assumes a realm. You can leave this unset to use the default ream from krb5.conf iirc.
        svc_princ = gssnames.Name('HTTP/%s@EXAMPLE.COM'% (socket.gethostname()))
        server_creds = gsscreds.Credentials(usage='accept', name=svc_princ)
        context = gssctx.SecurityContext(creds=server_creds)
        # Yay! Undocumented gssapi magic. No indication that you need to b64 decode.
        context.step(base64.b64decode(req))
        deleg_creds = context.delegated_creds
        CCACHE = 'MEMORY:ccache_rest389_%s' % deleg_creds.name
        store = {'ccache': CCACHE}
        deleg_creds.store(store, overwrite=True)
        os.environ['KRB5CCNAME'] = CCACHE
        # Return the context, so we can free it later.
        return context


    def _negotiate_end(context):

        # tell python-gssapi to free gss_cred_id_t
        deleg_creds = context.delegated_creds
        del(deleg_creds)


    def _connection(f, *args, **kwargs):
        retval = None
        negotiate = False
        headers = Headers()  # Allows a multivalue header response.
        # Request comes from **kwargs
        authorization = request.headers.get("Authorization", None)
        try:
            if authorization is not None:
                values = authorization.split()
                if values[0] == 'Negotiate':
                    # If this is valid, it sets KRB5CCNAME
                    negotiate = _negotiate_start(values[1])
            # This is set by mod_auth_gssapi if you are using that instead.
            if request.headers.get("Krb5Ccname", '(null)') != '(null)':
                os.environ['KRB5CCNAME'] = request.headers.get("Krb5Ccname", None)
            if os.environ.get('KRB5CCNAME', '') != '':
                pass
                # Do something with the krb creds here, db connection etc.
                retval = f(dir_srv_conn, *args, **kwargs)
            else:
                headers.add('WWW-Authenticate', 'Negotiate')
                retval = Response("Unauthorized", 401, headers)
        finally:
            if negotiate is not False:
                _negotiate_end(negotiate)
            if os.environ.get('KRB5CCNAME', None) is not None:
                os.environ['KRB5CCNAME'] = ''
        return retval


    def authenticateConnection(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            return _connection(f, *args, **kwargs)
        return decorator


    @app.route('/', methods['GET'])
    @authenticateConnection
    def index():
        pass
