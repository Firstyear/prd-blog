tinker --build
rsync -e ssh -avP entry adara.ipa.blackhats.net.au:/var/www/william/
rsync -e ssh -avP blog adara.ipa.blackhats.net.au:/var/www/william/
rsync -e ssh -avP index.html adara.ipa.blackhats.net.au:/var/www/william/

