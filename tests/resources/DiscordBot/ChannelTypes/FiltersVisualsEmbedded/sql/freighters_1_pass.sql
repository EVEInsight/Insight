SELECT DISTINCT kill_id FROM kills
WHERE kill_id in
      (
        SELECT DISTINCT victims.kill_id FROM victims INNER JOIN types ON victims.ship_type_id = types.type_id
        WHERE group_id in (513, 902)
        )
AND killmail_time >= Datetime('2018-08-01 00:00:00')
AND solar_system_id in 
    (
    SELECT DISTINCT solar_system_id FROM kills INNER JOIN systems s on kills.solar_system_id = s.system_id WHERE s.security_status >= .8
  )
LIMIT 10;