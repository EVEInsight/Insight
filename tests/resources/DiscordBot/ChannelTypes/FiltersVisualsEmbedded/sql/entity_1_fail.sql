-- fail test case
SELECT DISTINCT kill_id from kills
WHERE kill_id in
      ( -- attacker and victim are tracked
           SELECT DISTINCT kill_id
           FROM kills
           WHERE kill_id in
                 (SELECT kill_id
                  FROM attackers
                  WHERE character_id = 317012339
                     OR corporation_id = 1431056470
                     OR alliance_id = 1727758877
                     OR alliance_id = 498125261)
             AND kill_id in
                 (SELECT kill_id
                  FROM victims
                  WHERE character_id = 317012339
                     OR corporation_id = 1431056470
                     OR alliance_id = 1727758877
                     OR alliance_id = 498125261)
             AND killmail_time >= 2018 - 08 - 01
           ORDER BY RANDOM()
           LIMIT 50
      )
or kill_id in -- not attacker
   (
        SELECT DISTINCT kill_id
        FROM kills
        WHERE kill_id not in
              (SELECT kill_id
               FROM attackers
               WHERE character_id = 317012339
                  OR corporation_id = 1431056470
                  OR alliance_id = 1727758877
                  OR alliance_id = 498125261)
        AND killmail_time >= 2018 - 08 - 01
        ORDER BY RANDOM()
        LIMIT 50
   );
