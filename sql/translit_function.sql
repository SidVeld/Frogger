"""
Принимает строку в кириллице с названием мероприятия, переводит его в латиницу,
lower case, между словами "-"
"""

CREATE DEFINER=`ufaile8o_parser`@`%` FUNCTION `ufaile8o_parser`.`translit_function`(`_txt` VARCHAR(250)) RETURNS text CHARSET utf8
BEGIN
	DECLARE _f varchar(5);
	DECLARE _t varchar(15);
	DECLARE done INT DEFAULT FALSE;
	DECLARE cur CURSOR FOR SELECT f,t from translit;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
	open cur;
	the_loop: LOOP

	# get the values of each column into our variables
	FETCH cur INTO _f,_t;
	IF done THEN
	  LEAVE the_loop;
	END IF;
	set _txt=replace(lower(_txt),_f,_t);   
	END LOOP the_loop;
	
	CLOSE cur;
	return _txt;
END