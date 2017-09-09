cd ..
while true
do

    if (which python3>/dev/null); then
        python3 "bot.py"
    else
        python "bot.py"
    fi

done
