import pymysql
import pymysql.cursors
import pymysql.connections


try:
  connection = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    db='db',
    cursorclass=pymysql.cursors.DictCursor
  )
  try:

    with connection.cursor() as cur:
      cur.execute('''
        CREATE TABLE `users` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(32) DEFAULT NULL,
          `password` varchar(32) DEFAULT NULL,
          `email` varchar(32) DEFAULT NULL,
          `roleId` int(5) DEFAULT NULL,
          PRIMARY KEY (`id`));
        ''')
      
      with connection.cursor() as cur:
        cur.execute('INSERT INTO `users` (name, password, email, roleId) VALUES ("Leo","12345","leo@gmail.com", 1);')
        connection.commit()
        cur.execute('INSERT INTO `users` (name, password, email, roleId) VALUES ("flaycker","arbuz123","flaycker@gmail.com", 1);')
        connection.commit()
        cur.execute('INSERT INTO `users` (name, password, email, roleId) VALUES ("Dima","123321","dima@gmail.com", 2);')
        connection.commit()
        cur.execute('INSERT INTO `users` (name, password, email, roleId) VALUES ("Danya","123","danya@gmail.com", 0);')
        connection.commit()

  finally:
    connection.close()
except Exception as ex:
  print('Connection close...')
  print(ex)