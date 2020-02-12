import critiqapp
import sys, os

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    
    app = critiqapp.create_app()
    app.debug = True
    app.run('0.0.0.0',port)