from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
import os
import datetime as dt 
import matplotlib.pyplot as plt 
import json
import yaml
import pandas as pd 

class AzureBlobStorageManager:
    def __init__(self, connection_str:str, container_name:str, download_dir="."):
        
        self.container_name = container_name
        
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_str)
        self.container_client = self.blob_service_client.get_container_client(container_name)

        # The default directory to which to download a blob.
        self.download_dir = download_dir

    def upload_blob(self, file_name:str,  blob_name=None, overwrite=False) -> None:
        """Upload a local file to blob storage in Azure"""

        # Default blob_name = local filename 
        if blob_name is None:
            blob_name = os.path.basename(file_name)
        blob_client = self.container_client.get_blob_client(blob_name)
        
        try:
            # Upload the blob
            with open(file_name, "rb") as data:
                blob_client.upload_blob(data, overwrite=overwrite)
            print(f"Blob {blob_name} uploaded successfully.")
        except Exception as e: # Do something with this exception block (e.g. add logging)
            print(f"An error occurred: {str(e)}")

    def list_blobs(self, name_only=True) -> list: 
        """Wrapper to list blobs in the container"""
        blob_list = self.container_client.list_blobs()
        if name_only: 
            return [blob.name for blob in blob_list]
        else: 
            return list(blob_list)

    def download_blob(self, blob_name:str, download_path=None): 
        """Download a blob from the container. Local download path defaults to blob_name"""

        blob_client = self.container_client.get_blob_client(blob_name)

        if download_path is None:
            download_path = os.path.join(self.download_dir, os.path.basename(blob_name)) 
        
        with open(download_path, "wb") as file:
            download_bytes = blob_client.download_blob().readall()
            file.write(download_bytes)

    def has_blob(self, file_name:str) -> bool: 
        """Check if the container has a blob of the given name"""

        return os.path.basename(file_name) in self.list_blobs(name_only=True)
    
    def get_blob_last_modified(self, blob_name:str):
        """Get the last modified date of a blob in the storage container"""
        # Create a blob client
        blob_client =self.container_client.get_blob_client(blob_name)
       
        try:
            # Get blob properties
            blob_properties = blob_client.get_blob_properties()
            # Retrieve and print last modified date
            last_modified = blob_properties['last_modified']
            return last_modified.date()
           
        except Exception as e: # Do something with this exception block (e.g. add logging)
            print(f"An error occurred: {str(e)}")

        
    def get_blob_url(self, file_name:str, include_sas=False, expiry_hours=1) -> str:
        """Get the url of a blob in the storage container""" 

        blob_base = os.path.basename(file_name)
        blob_client = self.container_client.get_blob_client(blob=blob_base)
        
        url = blob_client.url 
        
        # Generate SAS token (read only)
        if include_sas: 
            expiry_time = dt.datetime.utcnow() + dt.timedelta(hours=expiry_hours)  # Adjust the expiration time as needed
            permissions = BlobSasPermissions(read=True)  # Adjust permissions as needed

            sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=self.container_name,
            blob_name=blob_base,
            account_key=blob_client.credential.account_key,
            permission=permissions,
            expiry=expiry_time,
            start=dt.datetime.utcnow(), 
            protocol='https'
            )

            url += f"?{sas_token}"

            print(blob_client.account_name)

        return url 

def get_hourly_wage(x):
    # Assuming you work a 40 hour week, 52 weeks in a year 
    return f"${(x/52)/40:.2f}"


def create_custom_ticks_labels() -> tuple:     
    ## TO DO: let customize salary ranges 
    ## Create custom ticks for yearly and hourly wages 
    custom_ticks = list(range(30000, 100001, 10000)) 
    if n is not None:
        custom_ticks = custom_ticks[n]
    hourly_wages = [get_hourly_wage(x) for x in custom_ticks]

    custom_labels = [f"${x[0]:,}\n{x[1]}" for x in zip(custom_ticks, hourly_wages)]
    return custom_ticks, custom_labels


def plot_ben_cliff(x, y, 
                   label_curve, 
                   label_x='Income (Annual & Hourly)', 
                   label_y='Net Resources',
                   title='Net Resources'): 


    ## Create figure, axis, and plot data 
    fig, ax = plt.subplots()
    ax.plot(x,y, label=label_curve)

    ## Add break even line 
    plt.axhline(y=0, color='r', linestyle='--', label='Break Even')

    ## Add legend 
    plt.legend()

    ## Create custom ticks for yearly and hourly wages 
    custom_ticks = list(range(30000, 100001, 10000)) 
    def get_hourly_wage(x):
        # Assuming you work a 40 hour week, 52 weeks in a year 
        return f"${(x/52)/40:.2f}"
    hourly_wages = [get_hourly_wage(x) for x in custom_ticks]

    custom_labels = [f"${x[0]:,}\n{x[1]}" for x in zip(custom_ticks, hourly_wages)]

    ## Set custom ticks and labels for x axis 
    ax.set_xticks(custom_ticks)
    ax.set_xticklabels(custom_labels)

    ## Set axis labels and title
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    ax.set_title(title)

    ## Show plot 
    # plt.show()

def print_ben_sum(ben_dict:dict, indent=4):
    ## Print summarized version of the profile for confirmation  
    print(json.dumps({
        x:y for x,y in ben_dict.items() 
            if y != ['NA'] and not (any(str(n) in x for n in range(2,13)) and y == [0])
    }, indent=indent))
        
    
def create_ben_profile_dict(**kwargs) -> dict: 
    """Creates a ben profile using the default yaml template as a base.
    Add keyword arguments to change specific values in the default (recommend a dictionary format).
    Will print summary version of the dictionary for reference."""

    ## Set Default from provided TEST 
    def_ben_profile = {
        'ruleYear': [2023],
        'Year': [2023], # I have not noticed this change anything
        'agePerson1': [30],
        'agePerson2': [8],
        'agePerson3': ['NA'],
        'agePerson4': ['NA'],
        'agePerson5': ['NA'],
        'agePerson6': ['NA'],
        'agePerson7': ['NA'],
        'agePerson8': ['NA'],
        'agePerson9': ['NA'],
        'agePerson10': ['NA'],
        'agePerson11': ['NA'],
        'agePerson12': ['NA'],
        'married': [0],
        'disability1': [0],
        'disability2': [0],
        'disability3': [0],
        'disability4': [0],
        'disability5': [0],
        'disability6': [0],
        'disability7': [0],
        'disability8': [0],
        'disability9': [0],
        'disability10': [0],
        'disability11': [0],
        'disability12': [0],
        'prev_ssi': [0],
        'blind1': [0],
        'blind2': [0],
        'blind3': [0],
        'blind4': [0],
        'blind5': [0],
        'blind6': [0],
        'ssdiPIA1': [0],
        'ssdiPIA2': [0],
        'ssdiPIA3': [0],
        'ssdiPIA4': [0],
        'ssdiPIA5': [0],
        'ssdiPIA6': [0],
        'locations': ['all'],
        'income_start': 1000,
        'income_end': 100000,
        'income_increase_by': 30000,
        'income.investment': [0],
        'income.gift': [0],
        'income.child_support': [0],
        'empl_healthcare': [0],
        'ownorrent': ['rent'],
        'assets.cash': [0],
        'assets.car1': [0],
        'disab.work.exp': [0],
        'k_ftorpt': 'FT',
        'schoolagesummercare': 'PT',
        'headstart_ftorpt': 'PT',
        'preK_ftorpt': 'PT',
        'contelig.headstart': False,
        'contelig.earlyheadstart': False,
        'contelig.ccdf': True,
        'budget.ALICE': 'survivalforcliff',
        'APPLY_CHILDCARE': True,
        'APPLY_HEADSTART': True,
        'APPLY_CCDF': True,
        'APPLY_PREK': True,
        'APPLY_LIHEAP': False,
        'APPLY_HEALTHCARE': True,
        'APPLY_MEDICAID_ADULT': True,
        'APPLY_MEDICAID_CHILD': True,
        'APPLY_ACA': True,
        'APPLY_SECTION8': True,
        'APPLY_RAP': False,
        'APPLY_FRSP': False,
        'APPLY_SNAP': True,
        'APPLY_SLP': True,
        'APPLY_WIC': True,
        'APPLY_EITC': True,
        'APPLY_TAXES': True,
        'APPLY_CTC': True,
        'APPLY_CDCTC': True,
        'APPLY_FATES': False,
        'APPLY_TANF': True,
        'APPLY_SSI': True,
        'APPLY_SSDI': True
    }
    
    ## Make adjustments from kwargs 
    new_ben_profile = def_ben_profile.copy()
    for k,v in kwargs.items(): 
        ## TO-DO: write complete validation function for all key:value parameters 
        if k not in def_ben_profile.keys():
            raise ValueError(f'{k} not a valid key in beneficiary configuration schema')
        else: 
            new_ben_profile[k] = v

    return new_ben_profile

def print_ben_sum(ben_dict:dict, indent=4):
    ## Print summarized version of the profile for confirmation  
    print(json.dumps({
        x:y for x,y in ben_dict.items() 
            if y != ['NA'] and not (any(str(n) in x for n in range(2,13)) and y == [0])
    }, indent=indent))
    

def save_config(ben_profile_dict:dict, project_name:str): 
    """Save to a yaml file and run the R script"""
    ## TO-DO: Use validation schema function to check ben profile 

    ## Save to yaml
    with open(os.path.join('projects', project_name + '.yaml'), 'w') as file: 
        yaml.dump(ben_profile_dict, file, indent=4) # note that unlike the default example file, 
        # the key-value pairs will be in alphabetical order and the file will be missing the comments
    
    print(f'Saved to {os.path.join("projects", project_name + ".yaml")}')
    print(f'Project name: {project_name}')


def read_output(project_name:str) -> pd.DataFrame:
    """Read output of R script based on project (YAML config) name"""
    return pd.read_csv(os.path.join('output', f'results_{project_name}.csv'))


def print_df(df):
    for line in df.to_csv(index=False).splitlines(): 
        print(line.replace(',',', '))