#;!/bin/sh

WORKDIR='/home/pi/projects/memorybox/'
TEMPDIR='/home/pi/projects/tmp/'
ZIPFILE='tsmemory.tar.gz'
SERVICE='/home/pi/projects/memorybox/memorybox.py'

if [ -f $TEMPDIR/$ZIPFILE ]; then
    cd $TEMPDIR
    tar xvzf $ZIPFILE
    if [ $? -eq 0 ]; then
        echo "unzip success"
        rm $ZIPFILE
        mv $TEMPDIR/* $WORKDIR/
    else
        echo "oh, crap"
        rm $ZIPFILE
    fi
fi

while [ 1 ]
do
    sleep 30s
    if ps aux | grep -v grep | grep $SERVICE > /dev/null
    then    
        echo "$SERVICE is running"
    else
        echo "service is not running"
        python $SERVICE &
    fi
done


