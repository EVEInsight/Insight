-- kills only - no awox
SELECT DISTINCT kill_id from kills
WHERE kill_id in
   ( --awox
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
        LIMIT 25
   )
or kill_id in 
   (--loss
        SELECT DISTINCT kill_id
        FROM kills
        WHERE kill_id in
              (SELECT kill_id
               FROM victims
               WHERE character_id = 317012339
                  OR corporation_id = 1431056470
                  OR alliance_id = 1727758877
                  OR alliance_id = 498125261)
          AND killmail_time >= 2018 - 08 - 01
        ORDER BY RANDOM()
        LIMIT 25
   );
