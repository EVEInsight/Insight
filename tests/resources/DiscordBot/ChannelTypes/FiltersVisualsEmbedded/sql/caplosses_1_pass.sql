SELECT DISTINCT kill_id FROM kills
WHERE kill_id in
      (
        SELECT DISTINCT victims.kill_id FROM victims INNER JOIN types ON victims.ship_type_id = types.type_id
        WHERE group_id in (30, 659, 547, 485, 1538, 902, 883)
        )
AND killmail_time >= Datetime('2018-08-01 00:00:00')
LIMIT 50;