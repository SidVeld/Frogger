DROP PROCEDURE IF EXISTS `f_get_gs_startups`;

CREATE DEFINER=`ufaile8o_parser`@`%` PROCEDURE `ufaile8o_parser`.`f_get_gs_startups`()
BEGIN  
    INSERT INTO f_information (name, site, post_link, event_type, is_published, is_deleted, src_id)
    SELECT src.name,
    	   src.site,
    	   -- переводим название в транслит
    	   (SELECT `f_translit`(src.name)) as post_link,
    	   'Акселератор' AS event_type,
    	   false AS is_published,
    	   false AS is_deleted,
    	   d_src.src_id   
      FROM src_gs_startups src
    
    -- проверяем наличие записи в целевой таблице
    -- если мероприятие уже есть, но какое-то из его полей обновилось на источнике
    -- то оно записывается снова, но с другой отметкой времени timestamp
          LEFT JOIN f_information fi
          ON src.name = fi.name
          AND src.site = fi.site
        
          CROSS JOIN d_src
    WHERE table_name = 'src_gs_startups' AND fi.name IS Null;
END