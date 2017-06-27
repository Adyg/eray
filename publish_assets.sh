env SECRET_KEY=`heroku config:get SECRET_KEY --app=eray` \
    AWS_SECRET_ACCESS_KEY=`heroku config:get AWS_SECRET_ACCESS_KEY --app=eray` \
    AWS_ACCESS_KEY_ID=`heroku config:get AWS_ACCESS_KEY_ID --app=eray` \
    AWS_STORAGE_BUCKET_NAME=`heroku config:get AWS_STORAGE_BUCKET_NAME --app=eray` \
    STATIC_ROOT='/vagrant/assets' \
    python manage.py collectstatic --settings=eray.settings.heroku
cd ..
