
import re


def parse_schema_to_string(schema: str) -> str:
    """
    Parses the schema from the input string and formats it into the desired output.

    Args:
        schema (str): The input schema string.

    Returns:
        str: The formatted schema string.
    """

    # Match each table and its columns
    table_pattern = re.compile(r"table\s+(\w+)\s")
    # table_pattern = re.compile(r"table\s+`?(\w+|\S+?)`?\s*")

    tables = table_pattern.findall(schema)
    # print(tables)


    # Process each table and its columns
    formatted_tables = []
    for table in tables:
        # column_names = re.findall(f"{table}\.(\w+) ", schema)
        pattern = rf"{re.escape(table)}\.(?:(?:'|\")([^'\"]+)['\"]?|([\w]+))"
        matchs = re.findall(pattern, schema)
        # for match in matchs:
        column_names = {f"`{item[0]}`" for item in matchs if item[0]} | {f"`{item[1]}`" for item in matchs if item[1]}  # 提取非空字符串并去重

        # print(column_names)
        # print(len(column_names))
    
        formatted_tables.append(f"table {table}, columns = [{', '.join(column_names)}]")

    # Combine all tables into the final string
    return "\n".join(formatted_tables)

# json_data =  "database schema :\\ntable frpm , columns = [ frpm.cdscode ( text | primary key | values : 01100170109835 , 01100170112607 ) , frpm.'academic year' ( text | values : 2014-2015 ) , frpm.'county code' ( text | values : 01 , 02 ) , frpm.'district code' ( integer | values : 10017 , 31609 ) , frpm.'school code' ( text | values : 0109835 , 0112607 ) , frpm.'county name' ( text | values : Alameda , Alpine ) , frpm.'district name' ( text ) , frpm.'school name' ( text | values : FAME Public Charter ) , frpm.'district type' ( text | values : State Special Schools ) , frpm.'school type' ( text | values : K-12 Schools (Public) , High Schools (Public) ) , frpm.'educational option type' ( text | values : Traditional , Juvenile Court School ) , frpm.'nslp provision status' ( text | values : Breakfast Provision 2 , Provision 2 ) , frpm.'charter school (y/n)' ( integer | values : 1 , 0 ) , frpm.'charter school number' ( text | values : 0728 , 0811 ) , frpm.'charter funding type' ( text | values : Directly funded , Locally funded ) , frpm.irc ( integer | values : 1 , 0 ) , frpm.'low grade' ( text | values : K , 9 ) , frpm.'high grade' ( text | values : 12 , 8 ) , frpm.'enrollment (k-12)' ( real | values : 1087.0 , 395.0 ) , frpm.'free meal count (k-12)' ( real | values : 565.0 , 186.0 ) , frpm.'percent (%) eligible free (k-12)' ( real | values : 0.519779208831647 , 0.470886075949367 ) , frpm.'frpm count (k-12)' ( real | values : 715.0 , 186.0 ) , frpm.'percent (%) eligible frpm (k-12)' ( real | values : 0.657773689052438 , 0.470886075949367 ) , frpm.'enrollment (ages 5-17)' ( real | values : 1070.0 , 376.0 ) , frpm.'free meal count (ages 5-17)' ( real | values : 553.0 , 182.0 ) , frpm.'percent (%) eligible free (ages 5-17)' ( real | values : 0.516822429906542 , 0.484042553191489 ) , frpm.'frpm count (ages 5-17)' ( real | values : 702.0 , 182.0 ) , frpm.'percent (%) eligible frpm (ages 5-17)' ( real | values : 0.65607476635514 , 0.484042553191489 ) , frpm.'2013-14 calpads fall 1 certification status' ( integer | values : 1 ) ]\\nttable satscores , columns = [ satscores.cds ( text | primary key | values : 10101080000000 , 10101080109991 ) , satscores.rtype ( text | values : D , S ) , satscores.sname ( text | comment : school name | values : FAME Public Charter ) , satscores.dname ( text | comment : district name | values : Alameda Unified ) , satscores.cname ( text | comment : county name | values : Alameda , Amador ) , satscores.enroll12 ( integer | comment : enrollment (1st-12nd grade) | values : 398 , 62 ) , satscores.numtsttakr ( integer | comment : number of test takers | values : 88 , 17 ) , satscores.avgscrread ( integer | comment : average scores in reading | values : 418 , 503 ) , satscores.avgscrmath ( integer | comment : average scores in math | values : 418 , 546 ) , satscores.avgscrwrite ( integer | comment : average scores in writing | values : 417 , 505 ) , satscores.numge1500 ( integer | comment : number of test takers whose total sat scores are greater or equal to 1500 | values : 14 , 9 ) ]\\nttable schools , columns = [ schools.cdscode ( text | primary key | values : 01100170000000 , 01100170109835 ) , schools.ncesdist ( text | comment : national center for educational statistics school district identification number | values : 0691051 , 0600002 ) , schools.ncesschool ( text | comment : national center for educational statistics school identification number | values : 10546 , 10947 ) , schools.statustype ( text | values : Active , Closed ) , schools.county ( text | values : Alameda , Alpine ) , schools.district ( text ) , schools.school ( text | values : FAME Public Charter ) , schools.street ( text | values : 313 West Winton Avenue ) , schools.streetabr ( text | comment : street address | values : 313 West Winton Ave. ) , schools.city ( text | values : Hayward , Newark ) , schools.zip ( text | values : 94544-1136 , 94560-5359 ) , schools.state ( text | values : CA ) , schools.mailstreet ( text | values : 313 West Winton Avenue ) , schools.mailstrabr ( text | comment : mailing street address | values : 313 West Winton Ave. ) , schools.mailcity ( text | comment : mailing city | values : Hayward , Newark ) , schools.mailzip ( text | comment : mailing zip | values : 94544-1136 , 94560-5359 ) , schools.mailstate ( text | comment : mailing state | values : CA ) , schools.phone ( text | values : (510) 887-0152 , (510) 596-8901 ) , schools.ext ( text | comment : extension | values : 130 , 1240 ) , schools.website ( text | values : www.acoe.org , www.envisionacademy.org/ ) , schools.opendate ( date | values : 2005-08-29 , 2006-08-28 ) , schools.closeddate ( date | values : 2015-07-31 , 2015-06-30 ) , schools.charter ( integer | values : 1 , 0 ) , schools.charternum ( text | values : 0728 , 0811 ) , schools.fundingtype ( text | values : Directly funded , Locally funded ) , schools.doc ( text | comment : district ownership code | values : 00 , 31 ) , schools.doctype ( text | comment : the district ownership code type | values : State Special Schools ) , schools.soc ( text | comment : school ownership code | values : 65 , 66 ) , schools.soctype ( text | comment : school ownership code type | values : K-12 Schools (Public) , High Schools (Public) ) , schools.edopscode ( text | comment : education option code | values : TRAD , JUV ) , schools.edopsname ( text | comment : educational option name | values : Traditional , Juvenile Court School ) , schools.eilcode ( text | comment : educational instruction level code | values : ELEMHIGH , HS ) , schools.eilname ( text | comment : educational instruction level name | values : High School ) , schools.gsoffered ( text | comment : grade span offered | values : K-12 , 9-12 ) , schools.gsserved ( text | comment : grade span served. | values : K-12 , 9-12 ) , schools.virtual ( text | values : P , N ) , schools.magnet ( integer | values : 0 , 1 ) , schools.latitude ( real | values : 37.658212 , 37.521436 ) , schools.longitude ( real | values : -122.09713 , -121.99391 ) , schools.admfname1 ( text | comment : administrator's first name 1 | values : L Karen , Laura ) , schools.admlname1 ( text | comment : administrator's last name 1 | values : Monroe , Robell ) , schools.admemail1 ( text | comment : administrator's email address 1 | values : lkmonroe@acoe.org , laura@envisionacademy.org ) , schools.admfname2 ( text | comment : administrator's first name 2 | values : Sau-Lim (Lance) , Jennifer ) , schools.admlname2 ( text | comment : administrator's last name 2 | values : Tsang , Koelling ) , schools.admemail2 ( text | comment : administrator's email address 2 | values : stsang@unityhigh.org , jkoelling@efcps.net ) , schools.admfname3 ( text | comment : administrator's first name 3 | values : Drew , Irma ) , schools.admlname3 ( text | comment : administrator's last name 3 | values : Sarratore , Munoz ) , schools.admemail3 ( text | comment : administrator's email address 3 | values : gmunoz@piedmont.k12.ca.us ) , schools.lastupdate ( date | values : 2015-06-23 , 2015-09-01 ) ]\\nforeign keys :\\nfrpm.cdscode = schools.cdscode\\nsatscores.cds = schools.cdscode"

# parse_schema_to_string(json_data)

def get_spider_schema():
    prompt=''

    return prompt