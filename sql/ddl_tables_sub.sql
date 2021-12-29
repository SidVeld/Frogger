"""
Вспомогательная таблица для функции f_date_rb
Необходима для форматирования даты мероприятия
"""

CREATE TABLE IF NOT EXISTS `elt_month` (
    `eng` varchar(50) NOT NULL,
    `rus` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO `elt_month` (`eng`, `rus`)
VALUES  ('January'  , 'января'),
        ('February' , 'февраля'),
        ('March'    , 'марта'),
        ('April'    , 'апреля'),
        ('May'      , 'мая'),
        ('June'     , 'июня'),
        ('July'     , 'июля'),
        ('August'   , 'августа'),
        ('September', 'сентября'),
        ('October'  , 'октября'),
        ('November' , 'ноября'),
        ('December' , 'декабря')


"""
Вспомогательная таблица для функции f_translit
Необходима для перевода кириллицы в латиницу (нужно для формирования ссылки поста)
"""

CREATE TABLE IF NOT EXISTS `elt_translit` (
    `t` varchar(3) NOT NULL,
    `f` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO `elt_translit` (`t`, `f`) 
VALUES  ('a', 'а'),
        ('b', 'б'),
        ('v', 'в'),
        ('g', 'г'),
        ('d', 'д'),
        ('e', 'е'),
        ('e', 'ё'),
        ('zh', 'ж'),
        ('z', 'з'),
        ('i', 'и'),
        ('y', 'й'),
        ('k', 'к'),
        ('l', 'л'),
        ('m', 'м'),
        ('n', 'н'),
        ('o', 'о'),
        ('p', 'п'),
        ('r', 'р'),
        ('s', 'с'),
        ('t', 'т'),
        ('u', 'у'),
        ('f', 'ф'),
        ('h', 'х'),
        ('c', 'ц'),
        ('ch', 'ч'),
        ('sh', 'ш'),
        ('sh', 'щ'),
        ('', 'ъ'),
        ('i', 'ы'),
        ('', 'ь'),
        ('e', 'э'),
        ('yu', 'ю'),
        ('ya', 'я'),
        ('', '-'),
        ('-', ' '),
        ('', '«'),
        ('', '»'),
        ('', '»'),
        ('', ','),
        ('', '|'),
        ('', '—')