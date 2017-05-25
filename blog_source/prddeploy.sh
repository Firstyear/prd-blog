tinker --build
rsync -e ssh -avP entry adara.prd.blackhats.net.au:/var/www/william/
rsync -e ssh -avP blog adara.prd.blackhats.net.au:/var/www/william/
rsync -e ssh -avP index.html adara.prd.blackhats.net.au:/var/www/william/

