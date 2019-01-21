SELECT DISTINCT kill_id FROM kills
WHERE killmail_time >= Datetime('2018-08-01 00:00:00')
AND solar_system_id in
    (
    SELECT DISTINCT solar_system_id FROM kills INNER JOIN systems s on kills.solar_system_id = s.system_id INNER JOIN constellations c on s.constellation_id = c.constellation_id
      WHERE c.region_id >= 12000000 and c.region_id < 13000000
  )
and totalValue >= 1000000000
LIMIT 10;