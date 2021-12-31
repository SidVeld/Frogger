DROP PROCEDURE IF EXISTS `f_get_rvc`;
CREATE DEFINER=`ufaile8o_parser`@`%` PROCEDURE `f_get_rvc`()
BEGIN
	 	
    -- создаем временную таблицу, чтобы обрабатывать дату только новых записей из src_gs_calendar
	DROP TABLE IF EXISTS temp_post;
	CREATE TEMPORARY TABLE temp_post (LIKE f_post);
	ALTER TABLE temp_post ADD event_date TEXT;
    INSERT INTO temp_post (name, site, post_link, descr, is_published, is_deleted, src_id, event_date)
    SELECT src.name,
    	   src.site,
    	   -- переводим название в транслит
    	   (SELECT `f_translit`(src.name)) AS post_link,

    	   src.descr,
    	   false AS is_published,
    	   false AS is_deleted,
    	   d_src.src_id,
    	   src.event_date
      FROM src_rvc src
    
    -- проверяем наличие записи в целевой таблице
    -- если мероприятие уже есть, но какое-то из его полей обновилось на источнике
    -- то оно записывается снова, но с другой отметкой времени timestamp
           LEFT JOIN f_post fp
           ON  src.name = fp.name
           AND src.site = fp.site
           AND src.descr = fp.descr
    
           CROSS JOIN d_src
     WHERE table_name = 'src_rvc' AND fp.name IS Null;

    -- вычисляем даты проведения по исходной строке event_date
	UPDATE temp_post
	   SET date_to = IF(
                        LOCATE('—',SUBSTRING_INDEX(SUBSTRING_INDEX(`event_date`, ' ', 2), ' ', -2)) = 0,
					        STR_TO_DATE(`event_date`, '%d.%m.%Y'),
				            Null
                        );
					  
	UPDATE temp_post
	   SET date_to = IF(
                        LOCATE('—',SUBSTRING_INDEX(SUBSTRING_INDEX(`event_date`, ' ', 2), ' ', -2)) <> 0,
					        STR_TO_DATE(SUBSTRING_INDEX(SUBSTRING_INDEX(`event_date`, ' ', 3), ' ', -1), '%d.%m.%Y'),
                            null
				    ),
	       date_from = IF(
                          LOCATE('—',SUBSTRING_INDEX(SUBSTRING_INDEX(`event_date`, ' ', 2), ' ', -2)) <> 0,
					          STR_TO_DATE(SUBSTRING_INDEX(SUBSTRING_INDEX(`event_date`, ' ', 1), ' ', -1), '%d.%m.%Y'),
                              null
				        );

    -- заносим данные в целевую таблицу	
	INSERT INTO f_post (name, place, site, post_link, date_from, date_to, descr, is_published, is_deleted, src_id)
	SELECT name, place, site, post_link, date_from, date_to, descr, is_published, is_deleted, src_id
      FROM temp_post;
   
END;