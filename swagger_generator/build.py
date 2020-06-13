from swagger_generator.config_folder import ConfigFolder
import os

class Builder:

    def __init__(self, verbose : bool, dir : str = None):
        self.verbose = verbose
        self.dir = dir
        if dir:
            self.main_config_folder = f"{self.dir}/swagger_generator"
        else:
            self.main_config_folder = "swagger_generator"
        self.config_folders = []


    def build(self):
        if os.path.isdir(self.main_config_folder):
            self.find_valid_config_folders()
            for config_folder in self.config_folders:
                config_folder.build()
        else:
            raise NotADirectoryError(f"The directory '{self.main_config_folder}' dose not exist")


    def find_valid_config_folders(self):
        self.config_folders = []
        potential_config_folders = next(os.walk(f"{self.main_config_folder}/."))[1]
        for folder in potential_config_folders:
            folder_path = f"{self.main_config_folder}/{folder}"
            if os.path.isfile(f"{folder_path}/config.yaml"):
                if self.verbose:
                    print(f"[*] Parsing config folder at : '{folder_path}'")
                config_folder = ConfigFolder(self.verbose, folder_path, self.dir)
                config_folder.parse()
                self.config_folders.append(config_folder)
                if self.verbose:
                    print(f"[*] Adding valid config folder at : '{folder_path}'")
