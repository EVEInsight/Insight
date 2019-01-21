SELECT DISTINCT kill_id FROM kills
WHERE killmail_time >= Datetime('2018-08-01 00:00:00')
AND npc = True
LIMIT 75;