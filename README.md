
cat /proc/cpuinfo | grep "model name" | cut -d":" -f2 | awk '{ print tolower($0) }' | head -n 1
