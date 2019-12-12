prog_name="easy-setup-env.sh"

echo "NOTE: remember that this is inteded for a test purpose."

if [ -f $prog_name ] ; then
    echo "ERROR: You have to change directory into each application directory e.g. cd tcp_client_server"
fi
if [ -z "$LINES" ] ; then
    # not sure whehter it's good way to find that this
    # script has been run by the "source" shell build-in command.
    echo "ERROR: You have to run with source. i.e. source ../${prog_name}"
fi

export OPENSCHCDIR=../..
export PYTHONPATH=
export PYTHONPATH=$OPENSCHCDIR/src
