SELECT DISTINCT kill_id FROM kills
WHERE killmail_time >= Datetime('2018-08-01 00:00:00')
AND npc = True
AND totalValue >= 5000000000
LIMIT 50;