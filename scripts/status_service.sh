#!/bin/sh -e
### BEGIN INIT INFO
# Provides:          status
# Required-Start:    $local_fs
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: status
### END INIT INFO

DAEMON="/home/pi/scripts/status.py"
DAEMON_USER="root"
DEAMON_NAME="status"
PID_FILE="/var/run/$DEAMON_NAME.pid"

PATH="/sbin:/bin:/usr/sbin:/usr/bin"

test -x $DAEMON || exit 0

. /lib/lsb/init-functions

d_start () {
  log_daemon_msg "Starting system $DEAMON_NAME Daemon"
  start-stop-daemon --start --background --name $DEAMON_NAME --make-pidfile --pidfile $PID_FILE --user $DAEMON_USER --exec $DAEMON
  log_end_msg $?
}

d_stop () {
  log_daemon_msg "Stopping system $DEAMON_NAME Daemon"
  start-stop-daemon --stop --retry 5 --quiet --oknodo --pidfile $PID_FILE --user $DAEMON_USER
  rm -f $PIDFILE
  log_end_msg $?
}

case "$1" in

  start|stop)
    d_${1}
    ;;

  restart|reload|force-reload)
    d_stop
    d_start
    ;;

  force-stop)
    d_stop
    killall -q $DEAMON_NAME || true
    sleep 2
    killall -q -9 $DEAMON_NAME || true
    ;;

  status)
    status_of_proc "$DEAMON_NAME" "$DAEMON" "system-wide $DEAMON_NAME" && exit 0 || exit $?
    ;;

  *)
    echo "Usage: /etc/init.d/$DEAMON_NAME {start|stop|force-stop|restart|reload|force-reload|status}"
    exit 1
    ;;

esac

exit 0

