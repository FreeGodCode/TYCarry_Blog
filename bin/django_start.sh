
#name of the application
NAME = 'Blog'
#django project directory
DJANGODIR = ''
#we will comunicate using this unix socket
SOCKFILE = ''

USER = root

GROUP = root
#how many worker processes should Gunicorn spawn
NUM_WORKERS = 3
DJANGO_SETTINGS_MODULE = Blog.settings
DJANGO_WSGI_MODULE = Blog.wsgi
echo "Starting $NAME as 'whoami'"

#activate the virtual environment
cd $DJANGODIR
source /var/www/dev/python3/bin/activate
export DJANGO_SETTINGS_MODULE = $DJANGO_SETTINGS_MODULE
export PYTHONPATH = $DJANGODIR: $PYTHONPATH

#Create the run directory if it doesn't exist
RUNDIR = $(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

#Start your Django Unicorn
exec /var/www/dev/python3/bin/gunicorn ${DJANGO_WSGI_MODULE}: application
--name $NAME
--worker $NUM_WORKERS
--user=$USER
--group=$GROUP
--bind=unix: $SOCKFILE
--log-level=debug
--log-file=-