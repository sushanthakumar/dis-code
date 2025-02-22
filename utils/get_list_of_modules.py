import pkg_resources
import subprocess

for package in pkg_resources.working_set:
    name = package.project_name
    version = package.version
    result = subprocess.run(["pip", "show", name], capture_output=True, text=True)
    
    license_line = next((line for line in result.stdout.split("\n") if "License" in line), "License: Unknown")
    summary_line = next((line for line in result.stdout.split("\n") if "Summary" in line), "Summary: Not Available")
    print(f"{name}=={version}")
    #print(f"{name},{version}, {license_line}, {summary_line}")
