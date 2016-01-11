set term png size 1024,768
set output "trigger_written.png"

set key left

set xdata time               
set timefmt "%Y-%m-%d %H%M%S"
set title "Event written on Merger"
set xlabel "Date"
set ylabel "# Events"
set grid
set style line 1 lc rgb 'black' pt 7 ps 0.5 
set style line 2 lc rgb 'red' pt 7 ps 0.5
set style line 3 lc rgb 'blue' pt 7 ps 0.5
set style line 4 lc rgb 'green' pt 7 ps 0.5
plot "file.dat" using 1:3 with points ls 1 title "Written on merger", \
     "file.dat" using 1:4 with points ls 2 title "L2 triggers"