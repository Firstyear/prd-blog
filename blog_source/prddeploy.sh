# tinker --build
rsync -e 'ssh -4' -avP {entry,blog,index.html} barite.prd.blackhats.net.au:/srv/www/vhosts/fy.blackhats.net.au/

