#;!/bin/sh

WORKDIR='/home/pi/projects/memorybox/'
TEMPDIR='/home/pi/projects/tmp/'
ZIPFILE='tsmemory.tar.gz'
SERVICE='/home/pi/projects/memorybox/memorybox.py'

if [ -d $WORKDIR ]; then
    echo "work dir exists"
else
    mkdir -p $WORDDIR
fi

if [ -d $TEMPDIR ]; then
    echo "temp dir exists"
else
    mkdir -p $TEMPDIR
fi

if [ -f $TEMPDIR/$ZIPFILE ]; then
    cd $TEMPDIR
    tar xvzf $ZIPFILE
    if [ $? -eq 0 ]; then
        echo "unzip success"
        rm $ZIPFILE
        mv $TEMPDIR/* $WORKDIR/
        chmod a+x $WORKDIR/userinit.sh
    else
        echo "oh, crap"
        rm $ZIPFILE
    fi
fi

while [ 1 ]
do
    if ps aux | grep -v grep | grep $SERVICE > /dev/null
    then    
        echo "$SERVICE is running"
    else
        echo "service is not running"
        python $SERVICE &
    fi
    sleep 30s
done


