#!/usr/bin/env python
# coding: utf-8

# # Preparation of dataset with job postings from data field

# The goal of this notebook is to prepare the dataset to insert its data into a MySQL databased designed to store the data contained in the dataset.

# In[1]:


import pandas as pd


# In[2]:


df = pd.read_excel('data_jobs_salary_all.xlsx')


# In[3]:


df.head(1).T


# In[4]:


df.shape


# ## Extraction of unique values for different columns  
# The purpose of this part is to extract the unique values from different columns. In order to normalise the data, I need to find the unique values, that will be stored in csv files. These csv files will be loaded into the different tables of the database.
# 
# This procedure will be applied to certain columns of the dataset. In general lines, the procedure is made out of the following steps:
# 1. Extract the unique values.
# 2. Clean these unique values (if necessary)
# 3. Create a 'pandas.Series'
# 4. Export the 'pandas.Series' to csv

# ### Unique 'job_title_short'

# In[5]:


job_titles = ( pd.Series(df.job_title_short.unique(), name = 'job_title')
              .sort_values()
              .reset_index(drop = True)
)


# - The 'autoincrement' values for the tables in SQL start from 1.
# - The default index for the 'pandas.Series' start from 0.
# - By default, the mapping of the 'job_title_id' values in the 'job_postings' dataframe will start from 0 and will raise errors when inserting the data into the database.
# 
# Solution: to add 1 to the indexes of the series so they start from 0. 

# In[6]:


job_titles.index = job_titles.index + 1


# In[7]:


job_titles


# In[8]:


job_titles.to_csv('./csv/job_titles.csv', index = False)


# ### Unique 'company_name'

# In[9]:


# df.company_name.nunique()


# In[10]:


df.company_name = df.company_name.str.replace('\u200b', '').str.strip()


# In[11]:


print(*df.company_name.sort_values().unique(), sep = '\n')


# In[12]:


df.loc[df.company_name == '(THE VANGUARD GROUP/MALVERN,PA)', 'company_name'] = 'THE VANGUARD GROUP'.title()
df.company_name = df.company_name.str.replace('#twiceasnice', 'twiceasnice')


# In[13]:


df.loc[df.company_name.str.startswith('0'), 'company_name']


# '0nward select' has a zero as initial O

# In[14]:


df.loc[df.company_name == '0nward Select', 'company_name'] = 'Onward Select'


# *Openstaff* has a weird font and won't be recognized as simple string

# In[15]:


df.company_name.sort_values().tail(5)


# In[16]:


df.loc[1759, 'company_name'] = 'Openstaff'


# ### Cleaning of the company names using assistant of AI  
# I will create a text file with all the company names and will ask an AI to batch process and try to clean the values and their similar variations.

# Get a text file with all the values for 'company_name'

# In[17]:


with open('df_companies.txt', 'w') as f:
    for value in df.company_name:
        f.write(f'{value}\n')


# Process the file using the script 'clean_companies.py' and then read the output file

# In[18]:


import clean_companies as clean


# In[19]:


# Process the file
clean_companies = clean.process_company_names('df_companies.txt', 'cleaned_companies.txt')


# In[20]:


clean_companies[:10]


# Compare the results of company names before and after cleaning

# In[21]:


sample_companies = df.company_name.sample(10)
indexes = sample_companies.index
clean_companies_series = pd.Series(clean_companies)


# In[22]:


pd.DataFrame({'df' : sample_companies, 'clean' : clean_companies_series[indexes]})


# Finally, reassign the clean company names to the dataframe column

# In[23]:


df.company_name = clean_companies


# Some 'company_name' values are empty (they were Co. Inc., Company... and so on)

# In[24]:


df.company_name[df.company_name == '']


# In[25]:


df.loc[df.company_name == '', 'company_name'] = 'NULL'


# Fix some issues with values that are not estrictly duplicated, but will raise an error as duplicates when loading the data into the database.

# In[26]:


df.company_name[df.company_name.str.contains('Mondel')]


# In[27]:


df.company_name[df.company_name.str.contains('Nestl')]


# In[28]:


df.loc[df.company_name == 'Nestle', 'company_name'] = 'Nestlé'


# In[29]:


df.loc[df.company_name.str.contains('Mondel'), 'company_name'] = 'Mondelez'


# Get list of unique companies:

# In[30]:


companies = (pd.Series(df.company_name.
                       drop_duplicates()
                       .sort_values()
                       .reset_index( drop = True)
                       , name = 'company')
)
companies.index += 1


# In[31]:


companies


# In[32]:


companies.to_csv('./csv/companies.csv', index = False)


# ### Unique locations

# In[33]:


# df.job_country.unique()


# In[34]:


countries = (pd.Series(df.job_country
                       .drop_duplicates()
                       .sort_values()
                       .reset_index(drop = True),
                       name = 'country' )
)
countries.index += 1


# I will add Georgia to the countries table.

# In[35]:


countries = pd.concat([countries, pd.Series('Georgia')])

countries = countries.sort_values().reset_index(drop = True)
countries.index += 1
countries.name = 'country'


# In[36]:


# countries.head()


# In[37]:


countries.to_csv('./csv/countries.csv', index = False)


# #### Unique 'job_location'

# In[38]:


# df.job_location.unique()


# In[39]:


df.job_location = df.job_location.str.strip().fillna('NULL')


# There are a couple of duplicates:  
# Vilnius, Vilnius City Municipality, Lithuania  
# Vilnius, Vilnius city municipality, Lithuania

# In[40]:


df.loc[df.job_location.str.contains('Vilnius'), 'job_location'] = 'Vilnius, Vilnius City Municipality, Lithuania'


# In[41]:


job_locations = (pd.Series(df.job_location
                           .drop_duplicates()
                           .sort_values()
                           .reset_index(drop = True)
                           , name = 'location_name')
)

job_locations.index += 1


# In[42]:


job_locations.to_csv('./csv/locations.csv', index = False)


# I will check if the 'search_location' values are contained either in 'job_country' or 'job_location'

# In[43]:


for s in df.search_location.unique():
    if s not in countries.values:
        print(s)


# I will set the 'search_location' values which contain *United States* (State, United States) to just *United States*

# In[44]:


df.loc[df.search_location.str.contains('United States'), 'search_location'] = 'United States'


# ### Unique 'job_schedule_type'

# In[45]:


# df.job_schedule_type.unique()


# In[46]:


df.job_schedule_type[df.job_schedule_type.isna()].index


# In[47]:


df.job_schedule_type = df.job_schedule_type.fillna('NULL')


# Currently, in the case of several possible job schedules, they are formatted as a string. I need to convert that string into a python list. The purpose it to unlock the option of exploding the dataframe using this column for the rows with several for 'job_schedule_type'.

# In[48]:


def convert_schedule_into_list(row):
    if row != 'NULL':
        row = row.replace(' and ', ',').replace(',,', ',').split(',')

    # for string with only one schedule,
    # convert to a list of only one element
    if isinstance(row, str):
        return [row]

    return row


# In[49]:


df.job_schedule_type = df.job_schedule_type.apply(convert_schedule_into_list)


# Now I want to get the list of unique 'job_schedule_type' values.

# In[50]:


# create a list with all the individual values for job_schedule_type
all_schedules = []
for i in df.job_schedule_type:
    all_schedules += i

# clean the list
all_schedules = [i.strip() for i in all_schedules if i != 'NULL' ]


# In[51]:


job_schedules = (pd.Series(all_schedules,name='schedule_type')
                 .drop_duplicates()
                 .sort_values()
                 .reset_index(drop = True)
)
job_schedules.index += 1


# In[52]:


job_schedules


# In[53]:


job_schedules.to_csv('./csv/job_schedules.csv', index = False)


# ### Unique 'job_via'

# In[54]:


df.job_via = df.job_via.fillna('NULL')


# In[55]:


df.job_via = df.job_via.str.replace('via ', '').str.strip()


# Check the values of 'job_via' so I can find a pattern to clean the data.

# In[56]:


# lowercase_job_via = df.job_via.str.lower().drop_duplicates().sort_values(key = lambda x : -x.str.len())


# In[57]:


# print(*lowercase_job_via, sep='\n')


# In[58]:


# print(*df.job_via.str.lower().drop_duplicates().sort_values(), sep='\n')


# Let's check if there are variations of the main job portals:

# In[59]:


# famous_job_portals = ['ZipRecruiter', 'Indeed', 'LinkedIn', 'Snagajob', 'Ai-Jobs.net', 
#         'Ladders', 'Dice', 'jobServe', 'Upwork', 'BeBee', 
#         'Built In', 'ProActuary', 'Remote OK', 'Get.It']
# famous_job_portals = [i.lower() for i in famous_job_portals]


# In[60]:


# for i in famous_job_portals:
#     for j in df.job_via.str.lower().unique():
#         if i in j:
#             print(j)


# There are some variations of the job portals 'BeBee', 'Indeed', 'JobServe' and 'Built In'

# In[61]:


replacements = {
    'geebo' : 'geebo.com',
    'talentify' : 'Talentify',
    'tarta.ai' : 'tarta.ai',
    'linkedin' : 'LinkedIn',
    'bebee' : 'BeBee',
    'jobserve' : 'jobServer',
    'indeed' : 'Indeed',
    'built in' : 'Built In',
    'dice' : 'dice.com'
    }

for key, value in replacements.items():
    df.loc[df.job_via.str.lower().str.contains(key), 'job_via'] = value


# In[62]:


df.loc[df.job_via.str.lower().str.contains('informs.org'), 'job_via'] = 'informs.org'
df.job_via = df.job_via.str.replace('Www.', 'www.')


# In[63]:


df.job_via[df.job_via.str.endswith('-')]


# In[64]:


df.loc[df.job_via == 'InternsVilla | Hub Of Internships -', 'job_via'] = 'InternsVilla | Hub Of Internships'


# Create the list of unique 'job_via' values

# In[65]:


job_via = pd.Series(df.job_via
                    .drop_duplicates()
                    .sort_values()
                    .reset_index(drop = True),
                    name = 'location_name')
job_via.index += 1


# In[66]:


job_via.to_csv('./csv/job_via.csv', index = False)


# ### Unique 'job_skills'

# In[67]:


df.job_skills.isna().sum()


# In[68]:


df.job_skills = df.job_skills.fillna('NULL')


# In[69]:


all_skills = df.job_skills.to_list()

all_skills = [i.replace('[', '')
              .replace(']', '')
              .replace("'", '')
              for i in all_skills if i != 'NULL']

all_skills = ', '.join(all_skills)
all_skills = all_skills.split(', ')

job_skills = pd.Series(all_skills, name = 'skill')
job_skills = job_skills.drop_duplicates().sort_values().reset_index( drop = True)
job_skills.index += 1


# In[70]:


job_skills


# In[71]:


job_skills.to_csv('./csv/skills.csv', index = False)


# Explode the original dataset to generate a row for every skill required in the job posting.

# In[72]:


def expand_skills(row):
    skills_list = (row.replace('[', '')
                .replace(']', '')
                .replace("'", '')
    )
    skills_list = skills_list.split(', ')
    return skills_list


# In[73]:


df.job_skills = df.job_skills.apply(expand_skills)


# ### Explode the dataset by 'job_skills' and 'job_schedule_type'

# In[74]:


df2 = df.explode('job_schedule_type')
df2 = df2.explode('job_skills')


# ## Normalize columns
# 
# After having extracted the unique values for certains columns, it is the time to normalise the data. Each value in those columns will be replaced by the id value in the unique values series.
# 
# I will replace the values of certains columns:
# - `job_title_short` --> job_titles
# - `job_country` --> countries
# - `job_location` --> job_locations
# - `job_via` --> job_via
# - `job_schedule_type` --> job_schedules
# - `search_location` --> countries
# - `job_company` --> companies
# - `job_skills` --> job_skills

# In[75]:


def normalize_col(series, column):
    s = pd.Series(series.index, index = series.values)
    df2[column] = df2[column].map(s)


# In[76]:


unique_columns = {
    'job_title_short' : job_titles,
    'job_country' : countries,
    'job_location' : job_locations,
    'job_via' : job_via,
    'job_schedule_type' : job_schedules,
    'search_location' : countries,
    'company_name' : companies,
    'job_skills' : job_skills,
}


# In[77]:


for key, value in unique_columns.items():
    normalize_col(value, key)


# In[79]:


df2.sample(3)


# Sort the dataset by `job_posted_date` column.

# In[ ]:


df2 = df2.sort_values('job_posted_date').reset_index(drop = True)


# Rename some columns to fit the columns in the database

# In[ ]:


df2.rename(columns = {
    'job_title_short' : 'job_title_id',
    'job_title' : 'job_title_full',
    'job_location' : 'job_location_id',
    'job_via' : 'job_via_id',
    'job_schedule_type' : 'schedule_id',
    'search_location' : 'search_location_id',
    'job_location' : 'job_location_id',
    'job_work_from_home' : 'work_from_home',
    'job_no_degree_mention' : 'no_degree_mention',
    'job_health_insurance' : 'health_insurance',
    'job_country' : 'job_country_id',
    'company_name' : 'company_id',
    'job_skills' : 'skill_id'
}, inplace = True)


# In[ ]:


df2.to_csv('./csv/job_postings.csv', index = False)

