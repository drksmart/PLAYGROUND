import pandas as pd
import pyodbc
import os.path
import time
import datetime

username = 'dsmart'
password_aims = 'pass1111'
w = "DSN=AIMS_PROD; UID={}; PWD={}".format(username, password_aims)
AIMS = pyodbc.connect(w)


def get_ppma():
    addr_query = \
        """
        SELECT DISTINCT
        K.KEY_TYPE_VAL AS ME,
        U.ENTITY_ID,
        U.COMM_ID,
        U.USG_BEGIN_DT
        FROM
        ENTITY_KEY_ET K, ENTITY_COMM_USG_AT U
        WHERE
        K.KEY_TYPE='ME'
        AND
        K.ACTIVE_IND='Y'
        AND
        K.ENTITY_ID=U.ENTITY_ID
        AND
        U.END_DT IS NULL
        AND
        U.COMM_USAGE='PP'
    
        """
    return pd.read_sql(con=AIMS, sql=addr_query)


def get_undeliverables():
    undel_query = \
        """
        SELECT DISTINCT
        ENTITY_ID,
        COMM_ID
        FROM
        ENTITY_COMM_EXC_CT
        WHERE
        COMM_EXC_CAT_CODE='UNDELIVER'
        AND
        END_DT IS NULL

        """
    return pd.read_sql(con=AIMS, sql=undel_query)


def find_files():
    get_update_time = open("C:\\SAS DATA\\nixie_update_time.txt", "r")
    last_update_time = get_update_time.read()
    file_list = []

    for (root, dirs, files) in os.walk("U:\\Source Files\\Data Analytics\\Mindy\\ACS", topdown=True):
        for f_name in files:
            if (
            f_name.startswith("P205")
            ):
                if (
                    time.strftime('%Y-%m-%d %H:%M:%S',
                        time.localtime(os.path.getmtime(os.path.join(root, f_name)))) > last_update_time
                ):
                    file_list.append(os.path.join(root, f_name))
    return file_list


def acs_import(file_path):
    width = [
    1, 2, 8, 9, 16, 8, 1, 1, 3, 20, 15, 6, 6, 1, 28, 10, 2, 28, 4, 2, 4, 10, 28, 2, 5, 1, 8, 28, 10, 2, 28, 4,
    2, 4, 10, 28, 2, 5, 1, 4, 2, 13, 66, 1, 1, 31, 35, 16, 1, 1, 8, 1, 1, 8, 1, 1, 1, 6, 6, 6, 6, 6, 6, 6, 6,
    6, 6, 6, 6, 1, 81, 1]
    headings = [
    'RECORD_TYPE', 'FILE_VERSION', 'SEQ_NUM', 'MAILER_ID', 'KEYLINE', 'MOVE_EFF_DT', 'MOVE_TYPE', 'DEL_CODE',
    'USPS_SITE_ID', 'LAST_NAME', 'FIRST_NAME', 'PREFIX', 'SUFFIX', 'OLD_ADDR_TYPE', 'OLD_URB', 'OLD_PRIM_NUM',
    'OLD_PRE_DIR', 'OLD_STREET_NM', 'OLD_SUFFIX', 'OLD_POST_DIR', 'OLD_UNIT', 'OLD_SECOND_NUM', 'OLD_CITY',
    'OLD_STATE', 'OLD_ZIP', 'NEW_ADDR_TYPE', 'NEW_PMB', 'NEW_URB', 'NEW_PRIM_NUM', 'NEW_PRE_DIR',
    'NEW_STREET_NM', 'NEW_SUFFIX', 'NEW_POST_DIR', 'NEW_UNIT', 'NEW_SECOND_NUM', 'NEW_CITY', 'NEW_STATE',
    'NEW_ZIP', 'NEW_HYPHEN', 'NEW_PLUS', 'NEW_DEL_POINT', 'NEW_ABBR_CITY', 'NEW_ADDR_LABEL', 'FEE_NOT',
    'NOT_TYPE', 'IMB', 'IMPB', 'ID_TAB', 'HARD_E_FLAG', 'ACS_TYPE', 'FULFILL_DT', 'PROCESS_TYPE',
    'CAPTURE_TYPE', 'AVAIL_DT', 'MAIL_SHAPE', 'MAIL_ACTION_CD', 'NIXIE_FLG', 'PROD_CD_A', 'PROD_CD_FEE_A',
    'PROD_CD_B ', 'PROD_CD_FEE_B ', 'PROD_CD_C ', 'PROD_CD_FEE_C ', 'PROD_CD_D ', 'PROD_CD_FEE_D ',
    'PROD_CD_E ', 'PROD_CD_FEE_E ', 'PROD_CD_F ', 'PROD_CD_FEE_F ', 'DPV', 'FILLER', 'END']

    file = pd.read_fwf(file_path, widths=width, header=None, names=headings)
    filtered_file = file[(file.KEYLINE.str.len() >= 10)].query("NIXIE_FLG == 'N'")
    filtered_file['me_match'] = filtered_file.KEYLINE.str[0:10]
    return filtered_file


def concat_unique(file_list):
    i = 0
    for path in file_list:
        if i == 0:
            base_file = acs_import(path)
            i += 1
        else:
            to_append = acs_import(path)[~acs_import(path)['KEYLINE'].isin(base_file['KEYLINE'])]
            base_file = pd.concat([base_file, to_append])
            i += 1
    return base_file


acs_to_process = concat_unique(find_files())
print(acs_to_process.shape)

acs_nixies = pd.merge(acs_to_process[['me_match']], get_ppma()[['me_match','entity_id','comm_id','usg_begin_dt']], on = 'me_match', how = 'inner')
acs_nixies.drop_duplicates(keep = 'first', inplace = True)
acs_nixies['date_diff'] = (datetime.datetime.now() - acs_nixies.usg_begin_dt).dt.days
acs_nixies = acs_nixies.query('date_diff >= 60')
acs_nixies['multi_key'] = acs_nixies.entity_id.astype(str)+acs_nixies.comm_id.astype(str)
acs_nixies_new = acs_nixies[~acs_nixies['multi_key'].isin(get_undeliverable()['multi_key'])]
acs_nixies_to_load = acs_nixies_new.drop(columns = ['me_match','usg_begin_dt','date_diff','multi_key'])
print(acs_nixies_to_load.shape)
# update_time_file = open("C:\\SAS DATA\\nixie_update_time.txt", "w")
# now = datetime.datetime.now()
# now_str = now.strftime('%Y-%m-%d %H:%M:%S')
# update_time_file.write(now_str)
# update_time_file.close()