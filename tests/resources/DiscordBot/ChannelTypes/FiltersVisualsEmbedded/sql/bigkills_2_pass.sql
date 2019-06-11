SELECT DISTINCT kill_id FROM kills
WHERE totalValue >= 1500000000
  AND totalValue <= 3000000000
AND killmail_time >= Datetime('2018-08-01 00:00:00')
order by killmail_time desc
LIMIT 50;