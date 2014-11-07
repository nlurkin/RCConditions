SELECT run.number, runtype.runtypename, run.timestart, run.timestop, CONCAT_WS('+', periodic_select.periodstring, GROUP_CONCAT(DISTINCT nim_select.nimstring SEPARATOR '+')), 
       GROUP_CONCAT(DISTINCT enableddetectors.detectorname ORDER BY enableddetectors.detectorname SEPARATOR '+'),
       run.startcomment, run.endcomment 
FROM run 
LEFT JOIN runtype ON (runtype.id = run.runtype_id)
LEFT JOIN enableddetectors ON enableddetectors.run_id = run.id
LEFT JOIN (SELECT viewperiodic.runid AS periodrunid, CONCAT('Period:', GROUP_CONCAT(DISTINCT viewperiodic.periods SEPARATOR ',')) AS periodstring
       FROM (SELECT runtrigger.run_id AS runid, runtrigger.id, triggerperiodictype.period AS periods
             FROM runtrigger
             INNER JOIN (triggerperiodic, triggerperiodictype) 
             ON (triggerperiodic.runtrigger_id = runtrigger.id AND triggerperiodictype.id = triggerperiodic.triggerperiodictype_id)
            ) AS viewperiodic
       GROUP BY viewperiodic.runid
      ) AS periodic_select 
ON run.id = periodic_select.periodrunid 
LEFT JOIN (SELECT viewnim.runid AS nimrunid, viewnim.triggerstring AS nimstring
       FROM (SELECT viewnimname.runid, CONCAT_WS('x', viewnimname.det_0, viewnimname.det_1, viewnimname.det_2, viewnimname.det_3, viewnimname.det_4) AS triggerstring
             FROM (SELECT DISTINCT viewnimdetail.runid, IF(det_0 = '1', D0.detname, IF(det_0 = 2, CONCAT('!', D0.detname), NULL)) AS det_0,
                                             IF(det_1 = '1', D1.detname, IF(det_1 = 2, CONCAT('!', D1.detname), NULL)) AS det_1,
                                             IF(det_2 = '1', D2.detname, IF(det_2 = 2, CONCAT('!', D2.detname), NULL)) AS det_2,
                                             IF(det_3 = '1', D3.detname, IF(det_3 = 2, CONCAT('!', D3.detname), NULL)) AS det_3,
                                             IF(det_4 = '1', D4.detname, IF(det_4 = 2, CONCAT('!', D4.detname), NULL)) AS det_4
                   FROM (SELECT viewnimtype.runid, viewnimtype.validitystart, viewnimtype.validityend, 
                                SUBSTRING(viewnimtype.mask, 1, 1) AS det_0, SUBSTRING(viewnimtype.mask, 2, 1) AS det_1, SUBSTRING(viewnimtype.mask, 3, 1) AS det_2, 
                                SUBSTRING(viewnimtype.mask, 4, 1) AS det_3, SUBSTRING(viewnimtype.mask, 5, 1) AS det_4
                         FROM (SELECT runtrigger.run_id AS runid, runtrigger.id, runtrigger.validitystart, runtrigger.validityend, triggernimtype.mask
                               FROM runtrigger
                               INNER JOIN (triggernim, triggernimtype) 
                               ON (triggernim.runtrigger_id = runtrigger.id AND triggernim.triggernimtype_id = triggernimtype.id)
                              ) AS viewnimtype
                        ) AS viewnimdetail
                   INNER JOIN (nimdetname AS D0, nimdetname AS D1, nimdetname AS D2, nimdetname AS D3, nimdetname AS D4) 
                   ON (D0.validitystart < viewnimdetail.validitystart AND D1.validitystart < viewnimdetail.validitystart AND D2.validitystart < viewnimdetail.validitystart 
                       AND D3.validitystart < viewnimdetail.validitystart AND D4.validitystart < viewnimdetail.validitystart
                       AND D0.detnumber = 0 AND D1.detnumber = 1 AND D2.detnumber = 2 AND D3.detnumber = 3 AND D4.detnumber = 4
                      )
                   ) AS viewnimname
            ) AS viewnim
      ) AS nim_select 
ON run.id = nim_select.nimrunid 
GROUP BY run.id
ORDER BY run.number
