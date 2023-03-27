import pandas as pd
import json

file = './mc-ars.csv'

# skiprows=10 will skip the first 10 lines, which aren't tabular
df = pd.read_csv(file, header=None, skiprows=10)

# change nan values of each row to first column value. This gives player name for each column.
# iterate over each row in the dataframe
for index, row in df.iterrows():
    # iterate over each column in the row
    for col in row.index:
        # if the value in the column is nan, replace it with the value in the first column
        if pd.isna(row[col]):
            df.loc[index, col] = row[0]
            
# select the first half, no extra time + name column
# drop all columns after the 9th column
df_first_half = df.iloc[:, :10]

# select the second half, no extra time.
# get the index of the first column where the value 90 is seen in row 1
idx = (df.iloc[0] == 90).argmax()

# select the previous 10 columns before the column where 90 is seen in row 1,
# as well as the column where 90 is seen in row 1
if idx >= 8:
    df_second_half = df.iloc[:, idx-8:idx+1]
else:
    df_second_half = df.iloc[:, :idx+1]
    
# combine the columns of the two halfs to create a full 90 min data frame.
df_clean = pd.concat([df_first_half, df_second_half], axis=1)

df_clean = df_clean.drop(df_clean[(df_clean.iloc[:, 0] == 'Minute Splits') & (df_clean.index != 0)].index)

# df_mc_total = df_clean[:13]
df_mc_total = pd.concat([df_clean.iloc[:1], df_clean.iloc[1:13]])

df_mc_total_clean = df_mc_total.transpose()

# set the first row as the column names
df_mc_total_clean.columns = df_mc_total_clean.iloc[0]
df_mc_total_clean = df_mc_total_clean[1:]

name_to_change = df.iloc[1, 1]
df_mc_total_clean = df_mc_total_clean.rename(columns={name_to_change: 'Player Name'})

# split the long data frame into multiple data frames with 13 rows each
list_of_dfs = [pd.concat([df_clean.iloc[:1], df_clean.iloc[i:i+12]]) for i in range(1, len(df_clean)-1, 12)]
                         
# list_of_dfs[3]
    
for i, df in enumerate(list_of_dfs):
    df = df.transpose()

    # set the first row as the column names
    df.columns = df.iloc[0]
    df = df[1:]

    name_to_change = df.iloc[1, 1]
    df = df.rename(columns={name_to_change: 'Player Name'})
    list_of_dfs[i] = df

final_result = pd.concat(list_of_dfs)

# Read the CSV file to fetch game detail
df = pd.read_csv(file, header=None, nrows=2)

# Get the value of the specific cell with game detail
game = df.iloc[1, 0]

# Add game detail final_result data frame
final_result['Game'] = value

# Reset index
final_result = final_result.reset_index()

# Take OptaID from Player Name column for joining with player meta data
final_result['optaId'] = pd.Series(dtype='float64')

for i in range(len(final_result. index)):
    string = final_result['Player Name'][i]
    
    # Find the index of the opening and closing brackets
    open_bracket_index = string.index('(')
    close_bracket_index = string.index(')')

    # Extract the substring between the brackets
    optaId = string[open_bracket_index + 1:close_bracket_index]
    final_result['optaId'][i] = optaId

# Extract position information of player from player_meta json file
with open('player_meta.json') as json_data:
    data = json.load(json_data)
    df_home = pd.DataFrame(data['homePlayers'])
    df_away = pd.DataFrame(data['awayPlayers'])
    df = pd.concat([df_home, df_away])
    df = df[['position', 'optaId']]

# # Join player meta data into main data frame for position column with optaId
merged_df = final_result.merge(df, on='optaId')

# # Remove unnecessary columns
merged_df = merged_df.drop(columns=['index'])

# Export final_result to csv
merged_df.to_csv('clean_player_physical.csv', index=False)
