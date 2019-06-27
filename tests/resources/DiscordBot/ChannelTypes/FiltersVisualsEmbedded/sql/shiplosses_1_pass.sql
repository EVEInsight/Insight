SELECT DISTINCT kill_id FROM kills
WHERE kill_id in
      (
        SELECT DISTINCT victims.kill_id FROM victims INNER JOIN types ON victims.ship_type_id = types.type_id
        WHERE type_id in (24698, 587) or group_id in (27)
        )
AND killmail_time >= Datetime('2018-08-01 00:00:00')
AND totalValue >= 150000000
AND totalValue <= 400000000
LIMIT 50;