#!/bin/bash
# Camera Feeds & Positions
top_left="screen -dmS top_left sh -c 'omxplayer --win \"0 0 640 400\" eagle.mp4 -b '";
top_right="screen -dmS top_right sh -c 'omxplayer --win \"640 0 1280 400\" eagle.mp4'";
bottom_left="screen -dmS bottom_left sh -c 'omxplayer --win \"0 400 640 800\" eagle.mp4'";
bottom_right="screen -dmS bottom_right sh -c 'omxplayer --win \"640 400 1280 800\" eagle.mp4'";

# Camera Feed Names
# (variable names from above, separated by a space)
camera_feeds=(top_left top_right bottom_left bottom_right)

#---- There should be no need to edit anything below this line ----

# Start displaying camera feeds
case "$1" in
start)
for i in "${camera_feeds[@]}"
do
eval eval '$'$i
done
echo "Camera Display Started"
;;

# Stop displaying camera feeds
stop)
sudo killall omxplayer.bin
echo "Camera Display Ended"
;;

# Restart any camera feeds that have died
repair)
for i in "${camera_feeds[@]}"
do
if !(screen -list | grep -q $i)
then
eval eval '$'$i
echo "$i is now running"
fi
done
;;

*)
echo "Usage: /etc/init.d/displaycameras {start|stop|repair}"
exit 1

;;
esac 
