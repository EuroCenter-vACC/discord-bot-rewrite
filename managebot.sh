#! bin/sh

cd /var/www/bot/rewrite
botprocessname="EUCBot"
xprocess1name="BGTasks"

case "$1" in
    -s)
        #check if screens exist, if yes return bot already running, if one is not then reboot that one, if none then boot all
        if screen -list | grep -q $botprocessname; then
            echo "Bot process already running and ignored."
        else
            screen -S "$botprocessname" -d -m python37 bot.py
            echo "Bot process started."
        fi
        if screen -list | grep -q $xprocess1name; then
            echo "Background process already running and ignored."
        else
            screen -S "$xprocess1name" -d -m python37 botBgTasks.py
            echo "Background process started."
        fi
        exit 1
        ;;
    -x)
        # shut all screens down with the specified names, even if not exist bypass error
        if screen -list | grep -q $botprocessname; then
            screen -X -S "$botprocessname" quit
            echo "Bot process found and stopped."
        else
            echo "Bot process not running."
        fi
        if screen -list | grep -q $xprocess1name; then
            screen -X -S "$xprocess1name" quit
            echo "Background process found and stopped."
        else
            echo "Background process not running."
        fi
        exit 1
        ;;
    -r)
        # restart screens
        if screen -list | grep -q $botprocessname; then
            screen -X -S "$botprocessname" quit
        fi
        if screen -list | grep -q $xprocess1name; then
            screen -X -S "$xprocess1name" quit
        fi
        screen -S "$botprocessname" -d -m python37 bot.py
        screen -S "$xprocess1name" -d -m python37 botBgTasks.py
        "Bot and Background processes have been restarted."
        ;;
    -status|-sts)
        # status command
        if screen -list | grep -q $botprocessname; then
            echo "Bot process is running."
        else
            echo "Bot process not running."
        fi
        if screen -list | grep -q $xprocess1name; then
            echo "Background process is running."
        else
            echo "Background process not running."
        fi
        exit 1
        ;;
    *|-*)
        echo "EUC vACC Discord Bot manager."
        echo "The following arguments are available:"
        echo "  -sts -status    |   This gives a status on the bot processes"
        echo "  -s              |   This will start the bot and its additional processes."
        echo "                      This will also start a missing, or crashed process."
        echo ""
        echo "  -x              |   This will kill the bot and its additional processes."
        echo ""
        echo "  -r              |   This will restart the bot and its additional processes."
        exit 1
        ;;
esac