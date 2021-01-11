#! /bin/sh

BASE_PATH=.venv/bin

PATH=$BASE_PATH/python
PROJCET_PATH=./
CONFIGURE=$PROJCET_PATH/uwsgi.ini
PID_FILE=$PROJCET_PATH/uwsgi.pid
UWSGI_CMD=$BASE_PATH/uwsgi

case   "$@"   in
    start)
        $UWSGI_CMD --ini $CONFIGURE
        echo "start uwsgi ok.."
        ;;
    stop)
        $UWSGI_CMD --stop $PID_FILE
        echo "stop uwsgi ok.."
        ;;
    reload)
        $UWSGI_CMD --reload $PID_FILE
        echo "reload uwsgi ok.."
        ;;
    restart)
        $UWSGI_CMD --stop $PID_FILE
        sleep 1
        $UWSGI_CMD --ini $CONFIGURE
        ;;
    *)
        echo 'unknown arguments (start|stop|reload|restart)'
        exit 1
        ;;
esac


