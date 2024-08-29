# You need to exclude the grep command itself, otherwise this can AWLAYS retrun true Or a 1 
# since you would be running a grep command of /home/pi/R050gui/R050Data.py and looking for results 
# containing  /home/pi/R050gui/R050Data.py
res=$(ps aux | grep /home/pi/R050gui/R050Data.py | grep -v "grep" | wc -l)
#echo $res
if [ $res -lt 1 ] ; then
    echo -n "Display no detected. Restarting..."
    # This command will be run as root
    su pi -c "export DISPLAY=:0; /usr/bin/python3 /home/pi/R050gui/R050Data.py" > /dev/null 2>&1 &
    echo "Done."
else
    echo "Displayed detected. Exiting."
#    ps aux | grep /home/pi/R050gui/R050Data.py | grep -v "grep"
fi
