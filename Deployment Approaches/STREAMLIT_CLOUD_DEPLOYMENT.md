# Streamlit Cloud Deployment Guide

To deploy your Partner Dashboard to Streamlit Cloud, follow these steps:

1. Create a GitHub repository with your code
2. Push all your files to the repository
3. Sign up for a free account at https://streamlit.io/cloud
4. Connect your GitHub account
5. Deploy from your GitHub repository

## Preparation Steps

1. Make sure your main file is named `app.py`
2. Ensure all requirements are in `requirements.txt`
3. Add a `.streamlit` folder with config if needed

## GitHub Setup

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/partner-dashboard.git
git push -u origin main
```

## Deployment

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select your repository
4. Click "Deploy"

You'll receive a public URL to share with anyone - no installation required!
