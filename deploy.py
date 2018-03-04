from tornado import wsgi, ioloop, httpserver, log
from cprj.wsgi import application

if __name__ == '__main__':
    
    container = wsgi.WSGIContainer(application)

    server = httpserver.HTTPServer(container)
    server.listen(8080, address='0.0.0.0')
    log.enable_pretty_logging()

    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        ioloop.IOLoop.current().stop()