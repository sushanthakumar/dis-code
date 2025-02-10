# Smart Config Nxt Phase 1 Delivery

# Release Package Artifacts
- Architectural Document
- Demo video: Discovery phase features using device simulation
- Release_Images: Docker images for different micro services of smart config software
- Docker compose file

# Installation Steps
## Prerequisites 
Ensure that docker and docker-compose are installed and running. 

- Follw docker engine installation steps [here](https://docs.docker.com/engine/install/)

- Follow docker-compose installation steps [here](https://docs.docker.com/compose/install/standalone/)

## Steps 
   ### Air Gap Deployment
   For the secure deplyment environment with limited external access, docker images can be directly loaded to local repository.
   Follow below steps

  a) Extract the release images package

        tar -xvf SCN.v.0.1.0.Release.Images.tar.gz
        cd SCN.v.0.1.0.Release.Images
     
  b) Execute below commands to load these images to local repository
    
        docker load -i SCN.v.0.1.0.release.images.tar.gz
  c) Proceed to Step 1

   ### Normal Deployment
   For normal deployment with external accessibility, docker images will be directly pulled during software installation. Proceed to Step 1


1) Execute below command to bring up all the micro services of smart config
   
        docker-compose up -d

2) Connect to "127.0.0.1:8080" port to access web portal of the software

# Uninstallation Steps
1) Execute below command to bring down all the micro services of smart config
   
        docker-compose down
