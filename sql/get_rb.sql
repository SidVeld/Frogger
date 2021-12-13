"""
Заполняет фактовую таблицу f_information из таблицы источника rb
"""

CREATE DEFINER=`ufaile8o_parser`@`%` PROCEDURE `ufaile8o_parser`.`get_rb`()
BEGIN  
    INSERT INTO f_information (name, site, post_link, date_to, event_type, is_published, is_deleted, src_id)
    select rb.name,
    	   rb.site,
           -- переводим название в транслит   
    	   (SELECT translit_function(rb.name)) as post_link,

           -- получаем дату проведения мероприятия   
    	   (SELECT `date_rb_function`(event_day, 'октября')) as date_to,
    	   rb.event_type,
    	   false as is_published,
    	   false as is_deleted,
    	   d_src.src_id   
    from rb
    
    -- проверяем наличие записи в целевой таблице
    -- если мероприятие уже есть, но какое-то из его полей обновилось на источнике
    -- то оно записывается снова, но с другой отметкой времени timestamp
    left join f_information fi
    on rb.name = fi.name
    and rb.site = fi.site
    and (SELECT `date_rb_function`(event_day, 'октября')) = fi.date_to
    and rb.event_type = fi.event_type
    
    cross join d_src
    where table_name = 'rb' and fi.name is Null;
END