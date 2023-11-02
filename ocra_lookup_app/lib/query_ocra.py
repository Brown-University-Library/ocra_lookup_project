import logging, pprint, os
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
        log.debug( f'starting get_ocra_instructor_email_from_classid() with class_id, ``{class_id}``' )
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
    
    def make_inverted_ocra_classid_email_map( self, existing_classid_to_email_map ) -> dict:
        """ Converts `existing_classid_to_email_map` to `inverted_ocra_classid_email_map
            Takes a dict like:
                {   '10638': 'person_A@brown.edu',
                    '8271': 'person_A@brown.edu',
                    '8500': 'person_B@brown.edu'
                    '8845': 'person_A@brown.edu' }
            ...and returns a dict like:
                {   'person_A@brown.edu': '10638',
                    'person_B@brown.edu': '8500'  }
            Allows for multiple class_ids per email, and returns the highest (latest) class_id. 
            Called by main() """
        ## convert keys to integers and sort them -----------------------
        int_keys = sorted( [int(key) for key in existing_classid_to_email_map.keys()] )
        temp_int_dict = {}
        for key in int_keys:
            temp_int_dict[key] = existing_classid_to_email_map[str(key)]
        inverted_ocra_classid_email_map = {}
        for ( class_id_key, email_val ) in temp_int_dict.items():
            inverted_ocra_classid_email_map[email_val] = str( class_id_key )
        log.debug( f'inverted_ocra_classid_email_map, ``{pprint.pformat(inverted_ocra_classid_email_map)}``' )
        return inverted_ocra_classid_email_map

    def filter_article_table_results( self, all_articles_results: list ):
        """ Takes all article results and puts them in proper buckets.
            Called by main() """
        assert type(all_articles_results) == list
        log.debug( f'count of all_articles_results, ``{len(all_articles_results)}``' )
        ( article_results, audio_results, ebook_results, excerpt_results, video_results, website_results ) = ( [], [], [], [], [], [] )
        for result in all_articles_results:
            if 'format' in result.keys():
                if result['format'].strip() == 'article':
                    article_results.append( result )
                elif result['format'].strip() == 'audio':
                    audio_results.append( result )
                elif result['format'].strip() == 'ebook':
                    ebook_results.append( result )
                elif result['format'].strip() == 'excerpt':
                    excerpt_results.append( result )
                elif result['format'].strip() == 'video':
                    video_results.append( result )
                elif result['format'].strip() == 'website':
                    website_results.append( result )
                else:
                    log.debug( f'unknown format, ``{result["format"]}``' )
            else:   # no format
                log.debug( f'no format, ``{result}``' )
        log.debug( f'count of article_results, ``{len(article_results)}``' )
        log.debug( f'count of audio_results, ``{len(audio_results)}``' )
        log.debug( f'count of ebook_results, ``{len(ebook_results)}``' )
        log.debug( f'count of excerpt_results, ``{len(excerpt_results)}``' )
        log.debug( f'count of video_results, ``{len(video_results)}``' )
        log.debug( f'count of website_results, ``{len(website_results)}``' )
        filtered_results = {
            'article_results': article_results,
            'audio_results': audio_results,
            'ebook_results': ebook_results,
            'excerpt_results': excerpt_results,
            'video_results': video_results,
            'website_results': website_results }    
        # log.debug( f'filtered_results, ``{pprint.pformat(filtered_results)}``' )
        return filtered_results  
    ## end def filter_article_table_results()  

    def check_for_ocra_data( self, all_course_results: dict ):
        """ Checks if there's any ocra data in the course_results.
            all_course_results is a dict like:
                { '1234': 
                    {'article_results': [], 'book_results: [], etc...},
                '2468': 
                    {'article_results': [], 'book_results: [], etc...},
                }
            Called by main() """
        assert type( all_course_results ) == dict
        ocra_data_found_check = False
        for ( class_id, classid_results ) in all_course_results.items():
            for ( format, format_results ) in classid_results.items():
                if len(format_results) > 0:
                    ocra_data_found_check = True
        log.debug( f'ocra_data_found_check, ``{ocra_data_found_check}``' )
        return ocra_data_found_check

    ## end class QueryOcra()


class DbStuff:

    def __init__(self):
        self.HOST = os.environ['OCRA_LKP__DB_HOST']
        self.USERNAME = os.environ['OCRA_LKP__OCRA_DB_USERNAME']
        self.PASSWORD = os.environ['OCRA_LKP__OCRA_DB_PASSWORD']
        self.DB = os.environ['OCRA_LKP__OCRA_DB_DATABASE_NAME']
        self.CDL_USERNAME = os.environ['OCRA_LKP__CDL_DB_USERNAME']
        self.CDL_PASSWORD = os.environ['OCRA_LKP__CDL_DB_PASSWORD']
        self.CDL_DB = os.environ['OCRA_LKP__CDL_DB_DATABASE_NAME']

    def get_db_connection( self ) -> pymysql.connections.Connection:
        """ Returns a connection to the database. """
        log.debug( 'starting get_db_connection()' )
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
        log.debug( 'starting get_CDL_db_connection()' )
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