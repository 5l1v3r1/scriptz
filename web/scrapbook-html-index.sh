#!/bin/bash
#source: http://lehollandaisvolant.net/linux/scripts/#scrap
#license: CC-BY

outfile=$HOME/Bureau/log.html

echo '<!DOCTYPE html>
<head>
   <meta charset="UTF-8">
   <title>Mes pages Scrapbookés</title>
   <style type="text/css">
   #list li img { width:16px; height:16px; margin-right: 5px; }
   #list li a { line-height:18px; vertical-align:middle; }
   #list li a { color:gray; text-decoration:none; }
   #list li a:hover { color:black; text-decoration:underline; }
   </style>
</head>
<body>
<ul id="list">' > $outfile

# on liste les pages scrapbookés
i=0
for subfol in $(find $PWD -type d -maxdepth 1 -mindepth 1)
   do 
      listefld[$i]=$subfol
      ((i++))
   done

# on recherche via grep le lien et le titre des pages.
for i in "${listefld[@]}"
   do
      echo "<li><a href=\"$i/index.html\"> <img src=\"$i/favicon.ico\" />
      `grep "^title" "$i/index.dat" | cut -c 7- `</a> - 
      <a href=\"`grep "^source" "$i/index.dat" | cut -c 8- ` \"> (voir en ligne)</a></li>" >> $outfile
   done

echo -e "</ul>\n</body>\n</html>" >> $outfile