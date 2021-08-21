#!/bin/bash
if [ "$1" = "celery-beat" ]; then
   echo "Running Celery Beat..."
   celery -A iotdb_cloud beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler
elif [ "$1" = "celery-worker" ]; then
   echo "Running Celery Worker..."
   celery -A iotdb_cloud worker -l INFO
elif [ "$1" = "iotdb-setup" ]; then
  echo "Setting Password..."
   python set_password.py
else
  echo "Start Server"
  # See https://stackoverflow.com/questions/15979428/what-is-the-appropriate-number-of-gunicorn-workers-for-each-amazon-instance-type
  export NUM_THREADS=4
  if [ -z ${NUM_WORKERS+x} ]; then
    echo "NUM_WORKERS is unset, calculating it..."
    export NUM_PROCS=`cat /proc/cpuinfo | grep 'core id' | wc -l`
    export NUM_WORKERS=$((2*$NUM_PROCS+1))
  else
    echo "NUM_WORKERS is set to ${NUM_WORKERS}, using that value"
  fi
  echo "Detected $NUM_PROCS processors, using $NUM_WORKERS workers with $NUM_THREADS threads each"
  python manage.py migrate && gunicorn --statsd-host=localhost:9125 --statsd-prefix=iotdb_cloud --capture-output --error-logfile '-' --access-logfile '-' --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(M)s "%(f)s" "%(a)s"' --enable-stdio-inheritance --env DJANGO_SETTINGS_MODULE=iotdb_cloud.settings --workers $NUM_WORKERS --threads $NUM_THREADS iotdb_cloud.wsgi --bind :8000 --timeout 120
fi