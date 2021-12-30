/*
Заполняет фактовую таблицу f_information из таблицы источника rb
*/
DROP PROCEDURE IF EXISTS `f_get_rb`;

CREATE DEFINER=`ufaile8o_parser`@`%` PROCEDURE `ufaile8o_parser`.`f_get_rb`()
BEGIN  
    INSERT INTO f_information (name, site, post_link, date_to, event_type, is_published, is_deleted, src_id)
    SELECT rb.name,
    	   rb.site,
    	   -- переводим название в транслит
    	   (SELECT `f_translit`(rb.name)) as post_link,
    	   
    	   -- получаем дату проведения мероприятия
    	   (SELECT `f_date`(event_day, event_month)) as date_to,
    	   rb.event_type,
    	   false AS is_published,
    	   false AS is_deleted,
    	   d_src.src_id   
      FROM src_rb rb
    
    -- проверяем наличие записи в целевой таблице
    -- если мероприятие уже есть, но какое-то из его полей обновилось на источнике
    -- то оно записывается снова, но с другой отметкой времени timestamp
          LEFT JOIN f_information fi
          ON rb.name = fi.name
          AND rb.site = fi.site
          AND (SELECT `f_date`(event_day, event_month)) = fi.date_to
          AND rb.event_type = fi.event_type
        
          CROSS JOIN d_src
    WHERE table_name = 'src_rb' AND fi.name IS Null;
END