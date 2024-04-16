# wget-ui

## Database migration 
<pre>
flask db init
flask db migrate
flask db upgrade
</pre>

### Start redis
docker run -p 6379:6379 --name redis -d redis --requirepass 'redispw'


### Start celery worker
In a separate terminal 
<pre>
celery -A app.celery worker --loglevel=info
</pre>

### Run development server
In a separate terminal 
<pre>
flask run
</pre>