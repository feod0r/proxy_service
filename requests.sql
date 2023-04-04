select * 
from proxy
where address not in (
    SELECT address 
    FROM `access_log` 
    where effective_to > now()
)
limit 1;

UPDATE 
	proxy,
    (SELECT access_log.address adr,
 	count(access_log.address) cnt 
     from access_log 
     group by access_log.address) as tmp
SET
	proxy.rpw = proxy.rpw + tmp.cnt 
where 
	proxy.address = tmp.adr