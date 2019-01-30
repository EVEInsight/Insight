SELECT DISTINCT kill_id WHERE kill_id in
  (SELECT kill_id from kills
WHERE killmail_time >= Datetime('2018-08-01 00:00:00')
AND npc = False
LIMIT 75)
or kill_id in (
  SELECT DISTINCT v.kill_id FROM kills INNER JOIN victims v on kills.kill_id = v.kill_id INNER JOIN types t on v.ship_type_id = t.type_id
                                                                                                        WHERE group_id == 1876
  and npc = True
  and killmail_time >= Datetime('2018-06-01 00:00:00')
    );