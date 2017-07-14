env SECRET_KEY=`heroku config:get SECRET_KEY --app=eraya` \
    AWS_SECRET_ACCESS_KEY=`heroku config:get AWS_SECRET_ACCESS_KEY --app=eraya` \
    AWS_ACCESS_KEY_ID=`heroku config:get AWS_ACCESS_KEY_ID --app=eraya` \
    AWS_STORAGE_BUCKET_NAME=`heroku config:get AWS_STORAGE_BUCKET_NAME --app=eraya` \
    STATIC_ROOT='/vagrant/assets' \
    python3 manage.py collectstatic --settings=eray.settings.heroku
cd ..
