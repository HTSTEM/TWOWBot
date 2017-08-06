cd ..
while true
do

if hash python3 2>/dev/null; then
    python3 "$@"
else
    python "$@"
fi

done
