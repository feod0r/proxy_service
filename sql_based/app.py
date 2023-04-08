from flask import Flask, render_template, json, request, session
from flaskext.mysql import MySQL
import time


mysql = MySQL()
app = Flask(__name__)
# MySQL configurations 
app.config['MYSQL_DATABASE_USER'] = 'feodor'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345678'
app.config['MYSQL_DATABASE_DB'] = 'apr'
app.config['MYSQL_DATABASE_HOST'] = '192.168.1.111'
mysql.init_app(app)




@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"



@app.route("/allocate/<proc_id>/<ttl>/<country>")
def allocate_proxy(proc_id, ttl, country):
    conn = mysql.connect()
    cursor = conn.cursor()
    
    post_sql = ''
    if len(country) > 0: 
        post_sql = f"and country = '{country}'"
        
    ttl = int(ttl)
    
    quer = f"""
        select address 
        from proxy
        where address not in (
            SELECT address 
            FROM `access_log` 
            where effective_to > FROM_UNIXTIME('{int(time.time())}')
            and resource_id = {proc_id}
            
        ) {post_sql}
        order by rpw desc
        limit 1;"""
    cursor.execute(quer)
    allocated_proxy = cursor.fetchall()
    
    if len(allocated_proxy) > 0: 
        quer = f"""
        insert into access_log (address, resource_id, effective_from, effective_to)
        values ('{allocated_proxy[0][0]}',
        {proc_id},
        FROM_UNIXTIME('{int(time.time())}'),
        FROM_UNIXTIME('{int(time.time())+ttl}'));
        """
        cursor.execute(quer)
        cursor.execute('commit')
        cursor.close()
        return(allocated_proxy[0][0])
    else: 
        cursor.close()
        return('Proxy has been ended temporally')
    
    
@app.route("/allocate/<proc_id>/<ttl>")
def allocate_proxy_no_country(proc_id, ttl):
    return allocate_proxy(proc_id,ttl,'')


def cleanup_database():
    conn = mysql.connect()
    cursor = conn.cursor()
    quer = f"""
        UPDATE 
            proxy,
            (SELECT access_log.address adr,
            count(access_log.address) cnt 
             from access_log 
             where effective_to < FROM_UNIXTIME('{int(time.time())}')
             group by access_log.address) as tmp
        SET
            proxy.rpw = proxy.rpw + tmp.cnt 
        where 
            proxy.address = tmp.adr
       """
    cursor.execute(quer)
    
    quer = f"""
        delete from access_log 
        where effective_to < FROM_UNIXTIME('{int(time.time())}')
       """
    cursor.execute(quer)
    cursor.execute('commit')
    cursor.close()
    
@app.route("/stat")
def statistics():
    cleanup_database()
    conn = mysql.connect()
    cursor = conn.cursor()
    
    table = []
    cursor.execute('SELECT address, country, rpw FROM `proxy` ORDER BY `rpw` DESC')
    for i in cursor.fetchall():
        table.append(f'<tr><td>{i[0]}</td><td>{i[1]}</td><td>{i[2]}</td></tr>')
    
    body = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Statistics of proxy usage</title>
    </head>
    <body>
        <table>
            {' '.join(table)}
        </table>
    </body>
    </html>"""
    cursor.close()
    return body


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
