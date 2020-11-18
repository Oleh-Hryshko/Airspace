import os
import re
import sqlite3
import zipfile


def add_zip_flat(zip, filename):
    dir, base_filename = os.path.split(filename)
    os.chdir(dir)
    zip.write(base_filename)


def get_zodan_class_string(i):
    if i == 20:
        return 'UNKNOWN'
    elif i == 21:
        return 'RESTRICTED'
    elif i == 22:
        return 'DANGER'
    elif i == 23:
        return 'ALERT'
    elif i == i == 24:
        return 'MILITARY'
    elif i == 26:
        return 'PROHIBITED'
    elif i == 27:
        return 'WARNING'
    elif i == 28:
        return 'TSA'
    elif i == 29:
        return 'TRA'
    else:
        return '?'


def get_zone_controlle_class_string(i):
    if i == 0:
        return 'UNKNOWN'
    elif i == 1:
        return 'A'
    elif i == 2:
        return 'B'
    elif i == 3:
        return 'C'
    elif i == 4:
        return 'D'
    elif i == 5:
        return 'E'
    elif i == 6:
        return 'F'
    elif i == 7:
        return 'E'
    elif i == 8:
        return 'ATZ'
    else:
        return '?'


def get_fir_class_string(i):
    if not i == 1400:
        if not i == 1401:
            return '?'
        else:
            return 'FIS'
    else:
        return 'FIR'


def get_class_string(i, i2):
    if i2 == 1:
        return get_zodan_class_string(i)
    elif i2 == 2:
        return get_zone_controlle_class_string(i)
    elif i2 == 3:
        return "Pattern"
    elif i2 == 4:
        return "TMZ"
    elif i2 == 5:
        return "RMZ"
    elif i2 == 6:
        return "Park"
    elif i2 == 7:
        return get_fir_class_string(i)
    elif i2 == 8:
        return "Para"
    elif i2 == 9:
        return "Golf"
    elif i2 == 10:
        return "Ara"
    else:
        return ""


def remove_unreadable_characters(string):
    string = re.sub("[^a-z0-9 -]+", "", string, flags=re.IGNORECASE)
    return string


def comunication(conn, code):
    comunication = conn.cursor()
    sql = "SELECT commtype, frequency FROM comunication WHERE icao = '" + code + "'"
    comunication.execute(sql)

    APP = ''
    TWR = ''
    GND = ''
    for row_comunication in comunication.fetchall():
        row_commtype = row_comunication[0]
        row_frequency = row_comunication[1]

        if row_commtype == 30:
            if APP == '':
                APP = 'APP ' + str(row_frequency).replace(',', '.')
            else:
                APP = ', ' + str(row_frequency).replace(',', '.')
        if row_commtype == 39:
            if TWR == '':
                TWR = 'TWR ' + str(row_frequency).replace(',', '.')
            else:
                TWR = ', ' + str(row_frequency).replace(',', '.')
        if row_commtype == 21:
            if GND == '':
                GND = 'GND ' + str(row_frequency).replace(',', '.')
            else:
                GND = ', ' + str(row_frequency).replace(',', '.')
    comunication = ''
    if len(APP) > 0:
        comunication = comunication + APP + ' MHz '
    if len(TWR) > 0:
        comunication = comunication + TWR + ' MHz '
    if len(GND) > 0:
        comunication = comunication + GND + ' MHz '

    return ' ' + comunication


def coordinate(latitude=0, longitude=0):
    if latitude < 0:
        str_latitude = '{:.13f}'.format(-latitude) + ' S'
    else:
        str_latitude = '{:.13f}'.format(latitude) + ' N'

    if longitude < 0:
        str_longitude = '{:.13f}'.format(-longitude) + ' W'
    else:
        str_longitude = '{:.13f}'.format(longitude) + ' E'

    return 'DP ' + str_latitude + ' ' + str_longitude


def convert(ccode=''):
    if len(ccode) == 0:
        return ''
    file_name_base = 'd:\Install\Para\Airspace\GPS_ILS_VOR\gpsilsvor.db'
    file_save_directory = 'd:\Install\Para\Airspace\GPS_ILS_VOR\Temp'

    conn = sqlite3.connect(file_name_base)
    # _id;ccode;name;res_int0;res_int1;res_float0;res_float1;res_string0
    country_code = conn.cursor()
    sql = "SELECT ccode, name FROM country_codes WHERE ccode = '" + ccode + "'"
    country_code.execute(sql)

    for row_country_code in country_code.fetchall():
        country_codes_ccode = row_country_code[0]
        country_codes_name = row_country_code[1].upper()
        # print(country_codes_id, country_codes_ccode, country_codes_name)

        # print(country_codes_name + ' (' + country_codes_ccode + ')')

        str_country_codes_name = country_codes_name
        str_country_codes_name = str_country_codes_name.replace(' AND ', ' - ')
        str_country_codes_name = str_country_codes_name.replace(',', ' - ')
        str_country_codes_name = str_country_codes_name.replace('/', '')
        str_country_codes_name = str_country_codes_name.replace('"', '')

        there_is_data = False
        airspace_file_name = file_save_directory + '/' + str_country_codes_name + ' (' + country_codes_ccode + ').txt'
        f = open(airspace_file_name, 'w')
        f.write('* Airspace for ' + str_country_codes_name + ' (' + country_codes_ccode + ')' + '\n')
        f.write('* Courtesy of Oleh Hryshko AKA 29a\n')
        f.write('* \n')
        f.write('* UNOFFICIAL, USE AT YOUR OWN RISK\n')
        f.write('* Do not use for navigation, for flight verification only\n')

        # _id;name;code;color;display;country_code;class;type;min_lat;max_lat;min_lon;max_lon;bottom;bottom_type;top;top_type;issue_date;issue_type;res_int0;res_int1;res_float0;res_float1;res_string0;squawk;operTimeTo;user_highlight
        airspaces = conn.cursor()
        sql = "SELECT _id, name, code, class, type, bottom, bottom_type, top, top_type FROM airspaces"

        if len(country_codes_ccode) == 1:
            # sql = sql + "WHERE country_code LIKE '" + country_codes_ccode + "[0-9]'" #not work (((

            sql_country_codes_ccode = ' country_code = "' + country_codes_ccode + '0" '
            i = 1
            while i <= 9:
                sql_country_codes_ccode = sql_country_codes_ccode + ' OR country_code = "' + country_codes_ccode + str(
                    i) + '" '
                i = i + 1

            sql = sql + " WHERE country_code LIKE " + sql_country_codes_ccode
        else:
            sql = sql + " WHERE country_code = '" + country_codes_ccode + "'"

        airspaces.execute(sql)
        for row_airspaces in airspaces.fetchall():
            airspaces_id = row_airspaces[0]
            airspaces_name = row_airspaces[1]
            airspaces_code = row_airspaces[2]
            airspaces_class = row_airspaces[3]
            airspaces_type = row_airspaces[4]
            airspaces_bottom = row_airspaces[5]
            airspaces_bottom_type = row_airspaces[6]
            airspaces_top = row_airspaces[7]
            airspaces_top_type = row_airspaces[8]

            # 1-MSL (Mean Sea Level), 2-FL (Flight Level), 3-AGL (Above Ground Level)
            if airspaces_top == 100000.0:
                str_airspaces_top = 'UNL'
            else:
                str_airspaces_top = str(int(airspaces_top))
                if airspaces_top_type == 2:
                    str_airspaces_top = 'FL' + str_airspaces_top
                else:
                    str_airspaces_top = str_airspaces_top + 'ft '
                    if airspaces_top_type == 3:
                        str_airspaces_top = str_airspaces_top + 'AGL'
                    else:
                        str_airspaces_top = str_airspaces_top + 'AMSL'
            if airspaces_bottom == -100000.0:
                str_airspaces_bottom = 'GND'
            else:
                if airspaces_bottom_type == 2:
                    str_airspaces_bottom = 'FL' + str(int(airspaces_bottom))
                else:
                    str_airspaces_bottom = str(int(airspaces_bottom)) + 'ft '
                    if airspaces_bottom_type == 3:
                        str_airspaces_bottom = str_airspaces_bottom + 'AGL'
                    else:
                        str_airspaces_bottom = str_airspaces_bottom + 'AMSL'

            try:
                airspaces_class = int(airspaces_class)
            except:
                airspaces_class = 0

            try:
                airspaces_type = int(airspaces_type)
            except:
                airspaces_type = 0

            str_class = get_class_string(airspaces_class, airspaces_type)

            if str_class == '':
                str_class = 'UNKNOWN'

            if str_class == 'UNKNOWN':
                if airspaces_name.find(' CTR') > -1:
                    str_class = 'CTR'
                elif airspaces_name.find(' MCTR') > -1:
                    str_class = 'MCTR'
                elif airspaces_name.find(' TMA') > -1:
                    str_class = 'TMA'
                elif airspaces_name.find(' FIR') > -1:
                    str_class = 'FIR'
                elif airspaces_name.find(' FIS') > -1:
                    str_class = 'FIS'
                elif airspaces_name.find(' UTA') > -1:
                    str_class = 'UTA'
                elif airspaces_name.find(' TSA') > -1:
                    str_class = 'TSA'
                elif airspaces_name.find(' TRA') > -1:
                    str_class = 'TRA'
                elif airspaces_name.find(' ATZ') > -1:
                    str_class = 'ATZ'
                elif airspaces_name.find(' OCEANIC') > -1:
                    str_class = 'OCEANIC'
                elif airspaces_name.find(' RADAR AREA') > -1:
                    str_class = 'RADAR AREA'
                elif airspaces_name.find(' SECTOR') > -1:
                    str_class = 'SECTOR'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('TRA') > -1:
                    str_class = 'TRA'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('TSA') > -1:
                    str_class = 'TSA'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('P') > -1:
                    str_class = 'P'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('T') > -1:
                    str_class = 'T'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('R') > -1:
                    str_class = 'R'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('D') > -1:
                    str_class = 'D'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('A') > -1:
                    str_class = 'A'
                elif airspaces_class >= 20 and airspaces_class <= 29 and airspaces_code.find('M') > -1:
                    str_class = 'M'
            str_airspaces_name = airspaces_name
            if airspaces_name == airspaces_code:
                if airspaces_class >= 20 and airspaces_class <= 29:
                    str_airspaces_name = country_codes_ccode + '-' + airspaces_code
            else:
                if airspaces_class >= 20 and airspaces_class <= 29:
                    str_airspaces_name = country_codes_ccode + '-' + airspaces_code + ' ' + airspaces_name
                else:
                    str_airspaces_name = country_codes_ccode + ' ' + airspaces_name

            str_airspaces_name = str_airspaces_name + comunication(conn, airspaces_code)
            # write airspace zone
            # print(str_airspaces_name)
            there_is_data = True
            f.write('\n')
            f.write('AC ' + remove_unreadable_characters(str_class) + '\n')
            f.write('AN ' + remove_unreadable_characters(str_airspaces_name) + '\n')
            f.write('AH ' + remove_unreadable_characters(str_airspaces_top) + '\n')
            f.write('AL ' + remove_unreadable_characters(str_airspaces_bottom) + '\n')

            # _id;main_id;type;latitude;longitude;item_order;res_int0
            airspaces_coord = conn.cursor()
            sql = "SELECT latitude, longitude FROM airspaces_coord " \
                  "WHERE main_id = '" + str(airspaces_id) + "'"
            airspaces_coord.execute(sql)
            for row_airspaces_coord in airspaces_coord.fetchall():
                row_airspaces_coord_latitude = row_airspaces_coord[0]
                row_airspaces_coord_longitude = row_airspaces_coord[1]

                f.write(coordinate(row_airspaces_coord_latitude, row_airspaces_coord_longitude) + '\n')

        # close file
        f.close()
        if not there_is_data:
            os.remove(airspace_file_name)
            return ''
        else:
            name_zip_file = file_save_directory + '/' + str_country_codes_name + ' (' + country_codes_ccode + ').zip'
            zip_file = zipfile.ZipFile(name_zip_file, 'w', zipfile.ZIP_DEFLATED)
            add_zip_flat(zip_file, airspace_file_name)
            zip_file.close()
            os.remove(airspace_file_name)
            return name_zip_file

    return ''


def countries_list():
    file_name_base = 'd:\Install\Para\Airspace\GPS_ILS_VOR\gpsilsvor.db'

    conn = sqlite3.connect(file_name_base)
    # _id;ccode;name;res_int0;res_int1;res_float0;res_float1;res_string0
    country_code = conn.cursor()
    sql = "SELECT ccode, name FROM country_codes"
    country_code.execute(sql)

    countries_list = {}

    for row_country_code in country_code.fetchall():
        country_codes_ccode = row_country_code[0]
        country_codes_name = row_country_code[1].upper()
        # print(country_codes_id, country_codes_ccode, country_codes_name)

        # print(country_codes_name + ' (' + country_codes_ccode + ')')

        str_country_codes_name = country_codes_name
        str_country_codes_name = str_country_codes_name.replace(' AND ', ' - ')
        str_country_codes_name = str_country_codes_name.replace(',', ' - ')
        str_country_codes_name = str_country_codes_name.replace('/', '')
        str_country_codes_name = str_country_codes_name.replace('"', '')

        countries_list[country_codes_ccode] = str_country_codes_name
    return countries_list
