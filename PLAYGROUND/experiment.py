
import pandas as pd
import pyodbc
import os.path, time
import datetime
# from zipfile import ZipFile

# AIMS connection definition

username = 'dsmart'
password_aims = 'pass1111'
w = "DSN=AIMS_PROD; UID={}; PWD={}".format(username, password_aims)
AIMS = pyodbc.connect(w)

# Create variables for use as parameters in functions below

last_update_time = open("C:\\Users\\dsmart\\OneDrive - American Medical Association\\nixie_update_time.txt", "r").read()
acs_start_path = "U:\\Source Files\\Data Analytics\\Mindy\\ACS"
acs_file_contains = ['P205']
ncoa_start_path = "U:\\SAS_Production\\Acxiom"
ncoa_file_contains = ['box','foreign','invalid','no_forwarding']

# Get all active PPMA addresses from AIMS

def get_ppma():
    addr_query = \
        """
        SELECT DISTINCT
        K.KEY_TYPE_VAL AS ME,
        SUBSTR(K.KEY_TYPE_VAL,1,10) AS ME_MATCH,
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

# Get all active Undeliverable flags from AIMS

def get_undeliverable():
    undel_query = \
        """
        SELECT DISTINCT
        ENTITY_ID,
        COMM_ID,
        BEGIN_DT,
        CAST(ENTITY_ID AS VARCHAR(20))||CAST(COMM_ID AS VARCHAR(20)) AS MULTI_KEY
        FROM
        ENTITY_COMM_EXC_CT
        WHERE
        COMM_EXC_CAT_CODE='UNDELIVER'
        AND
        END_DT IS NULL

        """
    return pd.read_sql(con=AIMS, sql=undel_query)


# Find all files that are within the defined directory structure, have a specific set of characters in the file name,
# and were modified after a specific date - usually the last date this process was run

def find_files(start_path, file_contains, last_update_time):
    file_list = []
    for (root, dirs, files) in os.walk(start_path, topdown=True):
        for f_name in files:
            for item in file_contains:
                if item in f_name:
                    if time.strftime('%Y-%m-%d %H:%M:%S',
                            time.localtime(os.path.getmtime(os.path.join(root, f_name)))) > last_update_time:
                        file_list.append(os.path.join(root, f_name))
    return file_list

# Import spec specifically for ACS files

def acs_import(file_path):
    columns = [(20,30),(215,220),(544,545)]
    headings = ['me_match', 'OLDZIP','NIXIE_FLG']
    file = pd.read_fwf(file_path, colspecs=columns, header=None, names=headings, converters={h:str for h in headings})
    filtered_file = file[(file.me_match.str.len() >= 10)].query("NIXIE_FLG == 'N'")
    filtered_file.drop(columns = 'NIXIE_FLG', inplace = True)
    return filtered_file

# Import spec specifically for NCOA files

def ncoa_import(file_path):
    columns = [(217,227),(325,330)]
    headings = ['me_match','OLDZIP']
    ncoa_file = pd.read_fwf(file_path, colspecs=columns, header=None, names=headings, converters={h:str for h in headings})
    return ncoa_file

# Function that takes all files from a source and concatenates unique records for each ID into one file
# Returns a blank dataframe with appropirately names columns if no files exists

def concat_unique(import_spec, file_list):
    i = 0
    if file_list == []:
        blank_df = pd.DataFrame()
        blank_df[['me_match','OLDZIP']] = pd.DataFrame([['','']], index = blank_df.index)
        return blank_df
    for path in file_list:
        if i == 0:
            base_file = import_spec(path)
            i += 1
        else:
            to_append = import_spec(path)[~import_spec(path)['me_match'].isin(base_file['me_match'])]
            base_file = pd.concat([base_file, to_append])
            i += 1
    return base_file

# Function that merges the concatenated ACS file with current PPMA addresses within business rule timeframes

def acs_ppma_merge(file_to_process):
    nixie_base = pd.merge(file_to_process[['me_match']], ppma[['me_match','entity_id','comm_id','usg_begin_dt']],
                      on = 'me_match', how = 'inner')
    nixie_base.drop_duplicates(keep = 'first', inplace = True)
    nixie_base['date_diff'] = (datetime.datetime.now() - nixie_base.usg_begin_dt).dt.days
    nixie_base = nixie_base.query('date_diff >= 59').copy()
    nixie_base['multi_key'] = nixie_base.entity_id.astype(str)+nixie_base.comm_id.astype(str)
    return nixie_base

# Function that merges the concatenated NCOA file with current PPMA addresses within business rule timeframes

def ncoa_ppma_merge(file_to_process):
    nixie_base = pd.merge(file_to_process[['me_match']], ppma[['me_match','entity_id','comm_id','usg_begin_dt']],
                      on = 'me_match', how = 'inner')
    nixie_base.drop_duplicates(keep = 'first', inplace = True)
    nixie_base['date_diff'] = (datetime.datetime.now() - nixie_base.usg_begin_dt).dt.days
    nixie_base = nixie_base.query('date_diff >= 10').copy()
    nixie_base['multi_key'] = nixie_base.entity_id.astype(str)+nixie_base.comm_id.astype(str)
    return nixie_base

# Function that merges two nixie files then removes records that have already been flagged undeliverable

def merge_and_clean_nixies(nixie_append, nixie_base):
    nixie_to_append = nixie_append[~nixie_append['multi_key'].isin(nixie_base['multi_key'])]
    all_nixie = pd.concat([nixie_base, nixie_to_append])
    nixies_new = all_nixie[~all_nixie['multi_key'].isin(undel['multi_key'])]
    nixies_to_load = nixies_new.drop(columns = ['me_match','usg_begin_dt','date_diff','multi_key'])
    return nixies_to_load

# Get the base data from AIMS required for potential multiple runs of functions below

ppma = get_ppma()


print("ppma is done")
print(ppma.shape)

undel = get_undeliverable()

print("undeliverable is done")
print(undel.shape)

# Uses functions above to get all ACS records to process

acs_to_process = concat_unique(acs_import, find_files(acs_start_path, acs_file_contains, last_update_time))

# Uses functions above to get all NCOA records to process

ncoa_to_process = concat_unique(ncoa_import, find_files(ncoa_start_path, ncoa_file_contains, last_update_time))

# Calls the function to create a dateframe merged between ACS and PPMA addresses

acs_and_ppma = acs_ppma_merge(acs_to_process)

# Calls the function to create a dateframe merged between NCOA and PPMA addresses

ncoa_and_ppma = ncoa_ppma_merge(ncoa_to_process)

# Calls the function that merges and cleans the final nixie files

nixie_final = merge_and_clean_nixies(acs_and_ppma, ncoa_and_ppma)
print(nixie_final.shape)

# Writes the file to the load folder

nixie_final.to_csv(r'U:\\Source Files\\Data Analytics\\BatchLoads\\Undeliverable Load\\NIXIE_FINAL_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.txt',
                          index = None, sep = '|', mode = 'w')

# Writes the file to the archive folder

nixie_final.to_csv(r'U:\\Source Files\\Data Analytics\\BatchLoads\\Undeliverable Load\\Undeliverable Load Archive\\NIXIE_FINAL_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.txt',
                          index = None, sep = '|', mode = 'w')

# Updates the file that contains the Last Update Time used to find unprocessed files

update_time_file = open("C:\\Users\\dsmart\\OneDrive - American Medical Association\\nixie_update_time.txt", "w")
now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
update_time_file.write(now_str)
update_time_file.close()

print("All done!")