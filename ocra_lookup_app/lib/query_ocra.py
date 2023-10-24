import logging, os
# import pmysql
import pymysql.cursors


log = logging.getLogger(__name__)


class QueryOcra:

    def __init__(self):
        self.db_stuff = DbStuff()

    def get_class_id_entries( self, course_department_code: str, course_number: str ) -> list:
        """ Finds one or more class_id entries from given course_id.
            Example course_department_code, 'BIOL'; example course_number, '1234a'.
            Called by ... """
        class_id_list = []
        ## run query to get class_id entries ----------------------------
        db_connection: pymysql.connections.Connection = self.db_stuff.get_db_connection()  # connection configured to return rows in dictionary format
        sql = f"SELECT * FROM `banner_courses` WHERE `subject` LIKE '{course_department_code}' AND `course` LIKE '{course_number}' ORDER BY `banner_courses`.`term` DESC"
        log.debug( f'sql, ``{sql}``' )
        result_set: list = []
        with db_connection:
            with db_connection.cursor() as db_cursor:
                db_cursor.execute( sql )
                result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
                assert type(result_set) == list
        log.debug( f'result_set, ``{result_set}``' )
        if result_set:
            for entry in result_set:
                class_id = entry.get( 'classid', None )
                if class_id:
                    class_id_str = str( class_id )
                    class_id_list.append( class_id_str )
            if len( result_set ) > 1:
                log.debug( f'more than one class-id found for course_id, ``{course_department_code}.{course_number}``' )
        log.debug( f'class_id_list, ``{class_id_list}``' )
        return class_id_list
        ## end def get_class_id_entries()

    def get_ocra_instructor_email_from_classid( self, class_id: str ) -> list:
        """ Returns email address for given class_id.
            Called by...  """
        ## run query to get email address -------------------------------
        db_connection: pymysql.connections.Connection = self.db_stuff.get_db_connection()  # connection configured to return rows in dictionary format
        sql = f"SELECT classes.classid, instructors.facultyid, instructors.email FROM reserves.classes, reserves.instructors WHERE classes.facultyid = instructors.facultyid AND classid = {class_id}"
        log.debug( f'sql, ``{sql}``' )
        result_set: list = []
        with db_connection:
            with db_connection.cursor() as db_cursor:
                db_cursor.execute( sql )
                result_set = list( db_cursor.fetchall() )  # list() only needed for pylance type-checking
                assert type(result_set) == list
        log.debug( f'result_set, ``{result_set}``' )
        emails = []
        for entry in result_set:
            email = entry.get( 'email', None )
            if email:
                emails.append( email )
        log.debug( f'emails, ``{emails}``' )
        return emails

    ## end class QueryOcra()


class DbStuff:

    def __init__(self):
        self.HOST = os.environ['OCRA_LKP__DB_HOST']
        self.USERNAME = os.environ['OCRA_LKP__DB_USERNAME']
        self.PASSWORD = os.environ['OCRA_LKP__DB_PASSWORD']
        self.DB = os.environ['OCRA_LKP__DB_DATABASE_NAME']
        self.CDL_USERNAME = os.environ['OCRA_LKP__CDL_DB_USERNAME']
        self.CDL_PASSWORD = os.environ['OCRA_LKP__CDL_DB_PASSWORD']
        self.CDL_DB = os.environ['OCRA_LKP__CDL_DB_DATABASE_NAME']

    def get_db_connection( self ) -> pymysql.connections.Connection:
        """ Returns a connection to the database. """
        try:
            db_connection: pymysql.connections.Connection = pymysql.connect(  ## the with auto-closes the connection on any problem
                    host=self.HOST,
                    user=self.USERNAME,
                    password=self.PASSWORD,
                    database=self.DB,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor )  # DictCursor means results will be dictionaries (yay!)
            log.debug( f'made db_connection with PyMySQL.connect(), ``{db_connection}``' )
        except:
            log.exception( f'PyMySQL.connect() failed; traceback follows...' )
            raise   ## re-raise the exception
        return db_connection

    def get_CDL_db_connection( self ):  # yes, yes, i should obviously refactor these two
        db_connection = pymysql.connect(  ## the with auto-closes the connection on any problem
                host=self.HOST,
                user=self.CDL_USERNAME,
                password=self.CDL_PASSWORD,
                database=self.CDL_DB,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor )  # DictCursor means results will be dictionaries (yay!)
        log.debug( f'made db_connection with PyMySQL.connect(), ``{db_connection}``' )
        return db_connection

    ## end class DbStuff()