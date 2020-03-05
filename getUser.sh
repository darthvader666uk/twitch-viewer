curl -H 'Accept: application/vnd.twitchtv.v5+json' \
-H 'Client-ID:'$2 \
-X GET https://api.twitch.tv/kraken/users\?login\=$1
