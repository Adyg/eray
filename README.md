# django-heroku-s3
Django 1.10 project template with built-in [Heroku](https://heroku.com/), [Vagrant](https://www.vagrantup.com/), [Amazon S3](http://aws.amazon.com/s3/), [Sass](http://sass-lang.com/) and [Solr](http://lucene.apache.org/solr/) support.

What you will end up with
-------------------------

1. Django project skeleton
2. Settings for running the project on [Heroku](https://heroku.com/), using [waitress](http://waitress.readthedocs.org/en/latest/) and [S3](http://aws.amazon.com/s3) for static files.
3. Custom bash scripts for pushing to Heroku, publishing assets to S3 and running the dev server.
4. Vagrant box setup with basic development environment (postgresql, pip, heroku toolbelt, git, sass and solr support)

Prerequisites
-------------

1. A [Heroku](https://heroku.com/) account
2. An [Amazon AWS](http://aws.amazon.com) account
3. [Vagrant](http://www.vagrantup.com/downloads) installed
4. [Ansible](http://docs.ansible.com/ansible/intro_installation.html) installed

Basic Usage
-----------

- Start a new django project with (make sure to change projectname to the actual project name): `$ django-admin startproject --template=https://github.com/Adyg/django-heroku-s3/archive/master.zip --extension sh,py,pp,yml --name Vagrantfile,Procfile projectname`

- Ensure all packages required by Ansible are present by running: `$ ansible-galaxy install -r requirements.yml` (from inside the projectname/vagrant dir)

- Start up the vagrant box with (this might take a while): `$ vagrant up` (from inside the projectname/vagrant dir)

- SSH into the vagrant box with `$ vagrant ssh` (from inside the projectname/vagrant dir). The project will be available under `/vagrant_data`. A postgresql database will be automatically created (the username/pass are the [projectname])

- Use `$ heroku auth:login` to authenticate with Heroku

Amazon S3
---------
- Create an [Amazon S3 bucket ](https://console.aws.amazon.com/s3)
- After creating the bucket, under it's Properties > Permissions section, update it's  CORS configuration to something along the lines of:
```
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <CORSRule>
        <AllowedOrigin>*</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedHeader>*</AllowedHeader>
    </CORSRule>
</CORSConfiguration>
```
- Create a new [IAM User](https://console.aws.amazon.com/iam/home) (remember to download it's access key and secret access key)
- Go to the new IAM User's page and attach a new policy to allow access to S3. Something similar to:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::BUCKET_NAME",
                "arn:aws:s3:::BUCKET_NAME/*"
            ]
        }
    ]
}
```

Heroku
------
- Create an app on [Heroku](https://heroku.com/) (aim for it's name to be the same as the Django project name, otherwise customization to the bash scripts will be needed)
- Inside the vagrant box, go to the `/vagrant_data` dir and run `$ heroku git:remote -a [projectname]`
- Inside the vagrant box, run the `$ ./deploy_heroku.sh` script to push the project to Heroku
- Update the project Heroku settings (can be run inside the vagrant box, under the /vagrant_data dir):
```
$ heroku config:set DJANGO_SETTINGS_MODULE=projectname.settings.heroku
$ heroku config:set AWS_STORAGE_BUCKET_NAME=[S3 bucket name]
$ heroku config:set AWS_ACCESS_KEY_ID=[S3 access key]
$ heroku config:set AWS_SECRET_ACCESS_KEY=[S3 secret access key]
$ heroku config:set SECRET_KEY=random_string
$ heroku config:set DISABLE_COLLECTSTATIC=1
 ```
Note: the static assets will not be pushed to Heroku (the included .slugignore file prevents it). Instead, they should be published to S3 via the included `$ ./publish_assets.sh` (from inside the vagrant box). The reason is to reduce the Heroku slug size as much as possible.

Dev Server
----------
The Django development server can be started inside the Vagrant box by using the `$ /vagrant_data/run_dev_server.sh` script. The development server will be available on the host machine at http://localhost:9198 (you can change the port in the Vagrantfile)

Sass
----
CSS files can be built with 
```
$ cd /vagrant_data/static
$ bundler exec compass compile
```