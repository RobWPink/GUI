res=$(ps aux | grep /home/pi/C200/C200Data.py | grep -v "grep" | wc -l)

if [ $res -lt 1 ] ; then
    echo -n "Display not detected. Restarting..."
    # This command will be run as root
    su pi -c "export DISPLAY=:0; /usr/bin/python3 /home/pi/C200/C200Data.py" > /dev/null 2>&1 &
    echo "Done."
else
    echo "Displayed detected. Exiting."
fi