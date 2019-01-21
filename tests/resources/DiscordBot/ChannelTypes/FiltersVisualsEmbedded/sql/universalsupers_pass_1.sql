SELECT DISTINCT kill_id FROM kills
WHERE kill_id in
      (
        SELECT DISTINCT kill_id from attackers INNER JOIN types t on attackers.ship_type_id = t.type_id
        WHERE t.group_id IN (30, 659)
        )
AND killmail_time >= Datetime('2018-08-01 00:00:00')
AND solar_system_id in
    (
      SELECT DISTINCT system_id from systems INNER JOIN constellations c on systems.constellation_id = c.constellation_id
      WHERE c.region_id in (10000060, 10000002)
      )
ORDER BY solar_system_id
LIMIT 100;