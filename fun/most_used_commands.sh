#!/bin/bash
history | awk '{print $2}' | sort | uniq -c | sort -rn | head -n 20
#alternative: history | awk '{a[$2]++}END{for(i in a){print a[i] " " i}}' | sort -rn | head