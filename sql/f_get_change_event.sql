/*
Заполняет фактовую таблицу f_information из таблицы источника src_change_event
*/
DROP PROCEDURE IF EXISTS `f_get_change_event`;

CREATE DEFINER=`ufaile8o_parser`@`%` PROCEDURE `ufaile8o_parser`.`f_get_change_event`()
BEGIN  
    INSERT INTO f_information (name, site, post_link, date_to, event_type, is_published, is_deleted, src_id)
    SELECT src.name,
    	   src.site,
    	   -- переводим название в транслит
    	   (SELECT `f_translit`(src.name)) as post_link,
    	   
    	   -- получаем дату проведения мероприятия
    	   (SELECT `f_date`(event_day, event_month)) as date_to,
    	   src.event_type,
    	   false AS is_published,
    	   false AS is_deleted,
    	   d_src.src_id  
      FROM src_change_event src
    
    -- проверяем наличие записи в целевой таблице
    -- если мероприятие уже есть, но какое-то из его полей обновилось на источнике
    -- то оно записывается снова, но с другой отметкой времени timestamp
          LEFT JOIN f_information fi
          ON src.name = fi.name
          AND src.site = fi.site
          AND (SELECT `f_date`(event_day, event_month)) = fi.date_to
          AND src.event_type = fi.event_type
        
          CROSS JOIN d_src
    WHERE table_name = 'src_change_event' AND fi.name IS Null;
END