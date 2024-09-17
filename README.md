# GUI

# for crontab:
```
@reboot nohup sudo /home/pi/startup.sh > /dev/null 2>&1 &
* * * * * /home/pi/R050gui/checkReformer.sh > /home/pi/R050gui/log.txt 2>&1
# Command for testing that the crontab is executing
* * * * * touch /home/pi/R050gui/checkReformer.sh

```
