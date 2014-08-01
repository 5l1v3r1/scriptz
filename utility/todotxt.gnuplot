#Generate report for todo.txt done.txt
#Thanks to https://stackoverflow.com/questions/24907683/, http://www.gnuplotting.org/code/colored_lines2.gnu, http://gnuplot-surprising.blogspot.fr/2011/09/transparency-in-gnuplot.html
#Set output
set terminal png truecolor size 640,480 enhanced font "WeblySleek UI" 11
set output 'output.png'
set title "todo.txt"

#Border
set style line 101 lc rgb '#808080' lt 1
set border 3 back ls 101
set tics nomirror out scale 0.75
#Grid
set style line 102 lc rgb'#808080' lt 0 lw 1
set grid back ls 102
set xlabel "date"
set ylabel "tasks"
set key left

#Y and X axis range
set xdata time
set timefmt "%Y-%m-%dT%H:%M:%S"
#set xrange ["2014-03-27T01:00:00":"2014-07-26T01:00:00"] noreverse
set yrange [30:80]

set style fill transparent solid 0.8


# output date format
set format x "%Y\n%B-%d"

plot \
    'report.txt' using 1:3 with filledcurves above y1=0 title "done" lt rgb "green" , \
    'report.txt' using 1:2 with filledcurves above y1=0 title "todo" lt rgb "red" 