# Deployment Approaches for Partner Dashboard

This folder contains various methods for deploying and sharing the Partner Revenue & Activity Dashboard with others who may not have the required Python packages installed.

## Available Deployment Methods

1. **Standalone Executable (Windows)**
   - `build_executable.bat` - Script to build a standalone .exe file
   - `build_exe.py` - Python script used by the batch file for PyInstaller configuration

2. **Docker Container**
   - `Dockerfile` - Configuration for building a Docker image
   - `build_docker.bat` - Script to build the Docker image

3. **Streamlit Cloud**
   - `STREAMLIT_CLOUD_DEPLOYMENT.md` - Instructions for deploying to Streamlit Cloud

4. **Portable Package**
   - `create_portable_package.bat` - Script to create a portable Python environment

## Overview and Recommendations

The `SHARING_OPTIONS.md` file provides an overview of all deployment methods with their pros and cons, as well as recommendations for different use cases.

## Usage

1. These deployment methods don't modify any of the main application code
2. You can run these scripts directly from this folder without affecting the main application
3. Each method produces its outputs in different locations as described in the respective files

## Which Method to Choose?

- For non-technical users: Streamlit Cloud deployment or standalone executable
- For technical users: Docker container
- For offline sharing: Portable package or standalone executable
